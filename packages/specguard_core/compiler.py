"""Formal EARS Specification Compiler (`.kiro/specs/**/requirements.md` -> `VerificationDAG`)."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import List, Optional

from .models import EARSClause, EARSKeyword, VerificationDAG


class SpecCompilationError(ValueError):
    """Raised when a specification document contains zero valid EARS clauses or syntax errors."""

    def __init__(self, message: str, failed_lines: Optional[List[int]] = None) -> None:
        super().__init__(message)
        self.failed_lines = failed_lines or []


class EARSCompiler:
    """Compiles EARS (`WHEN/IF/WHILE/WHERE ... THE <actor> SHALL <obligation>`) markdown specs."""

    _EARS_PATTERN = re.compile(
        r"^(?:[-*]\s+|\d+\.\s+)?(?P<keyword>WHEN|IF|WHILE|WHERE)\s+"
        r"(?P<condition>.+?)(?:,\s*|\s+)"
        r"(?:THEN\s+)?THE\s+(?P<actor>[A-Za-z0-9_`\-]+)\s+SHALL\s+"
        r"(?P<obligation>.+?)\.?\s*$",
        re.IGNORECASE,
    )

    def compile_text(
        self,
        markdown_text: str,
        spec_name: str = "inline-spec",
        source_path: str = "inline",
    ) -> VerificationDAG:
        """Compile raw markdown containing EARS clauses into a deterministic VerificationDAG."""
        clauses: List[EARSClause] = []
        candidate_failed_lines: List[int] = []

        for idx, raw_line in enumerate(markdown_text.splitlines(), start=1):
            stripped = raw_line.strip()
            if not stripped:
                continue
            match = self._EARS_PATTERN.match(stripped)
            if match:
                kw_raw = match.group("keyword").upper()
                keyword: EARSKeyword = kw_raw  # type: ignore[assignment]
                condition = " ".join(match.group("condition").strip().rstrip(",").split())
                actor = match.group("actor").strip("` ")
                obligation = " ".join(match.group("obligation").strip().rstrip(".").split())

                raw_id = f"{spec_name}:{keyword}:{condition}:{actor}:{obligation}"
                short_hash = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:10]
                clause_id = f"EARS-{ len(clauses) + 1:02d}-{short_hash}"

                clauses.append(
                    EARSClause(
                        clause_id=clause_id,
                        keyword=keyword,
                        condition=condition,
                        system_actor=actor,
                        obligation=obligation,
                        source_file=source_path,
                        line_number=idx,
                    )
                )
            elif any(tok in stripped.upper() for tok in ("SHALL", "WHEN ", "IF ", "WHILE ", "WHERE ")):
                if not stripped.startswith("#") and not stripped.startswith(">"):
                    candidate_failed_lines.append(idx)

        if not clauses:
            raise SpecCompilationError(
                f"No valid EARS ('WHEN/IF/WHILE/WHERE ... THE <actor> SHALL ...') clauses found in {source_path}.",
                failed_lines=candidate_failed_lines or [1],
            )

        canonical_payload = json.dumps(
            [
                {
                    "keyword": c.keyword,
                    "condition": c.condition,
                    "system_actor": c.system_actor,
                    "obligation": c.obligation,
                }
                for c in clauses
            ],
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()

        return VerificationDAG(
            spec_name=spec_name,
            source_path=source_path,
            clauses=clauses,
            digest=digest,
        )

    def compile_file(self, file_path: str | pathlib.Path) -> VerificationDAG:
        """Compile a markdown requirements file on disk."""
        path = pathlib.Path(file_path)
        text = path.read_text(encoding="utf-8")
        spec_name = path.parent.name if path.parent.name else path.stem
        return self.compile_text(text, spec_name=spec_name, source_path=str(path))

    @staticmethod
    def render_dag_to_markdown(dag: VerificationDAG) -> str:
        """Render a VerificationDAG back into canonical EARS markdown (round-trip support)."""
        lines = [f"# Compiled EARS Specification: {dag.spec_name}", ""]
        for idx, clause in enumerate(dag.clauses, start=1):
            lines.append(f"{idx}. {clause.to_ears_markdown()}")
        return "\n".join(lines) + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entrypoint invoked by `.kiro/hooks/spec-to-schema-sync.yaml`."""
    parser = argparse.ArgumentParser(description="Validate and compile .kiro/specs EARS files.")
    parser.add_argument("--validate-all", action="store_true", help="Compile all .kiro/specs/**/requirements.md files")
    parser.add_argument("--root", default=".", help="Repository root path")
    args = parser.parse_args(argv)

    compiler = EARSCompiler()
    root = pathlib.Path(args.root).resolve()
    spec_files = sorted(root.glob(".kiro/specs/*/requirements.md"))
    if not spec_files:
        print("No .kiro/specs/*/requirements.md files found.", file=sys.stderr)
        return 1

    total_clauses = 0
    for spec_file in spec_files:
        dag = compiler.compile_file(spec_file)
        total_clauses += len(dag.clauses)
        print(f"[OK] {spec_file.relative_to(root)} -> {len(dag.clauses)} EARS clauses (digest={dag.digest[:12]})")

    print(f"Validated {len(spec_files)} spec files ({total_clauses} total EARS invariants).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
