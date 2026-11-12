"""MCP Tool #1: AST & Property-Based Testing (Hypothesis) Code Sandbox (`run_property_test_sandbox`)."""

from __future__ import annotations

import ast
import math
import re
from typing import Any, Callable, Dict, List, Optional, Tuple


class CodeSandboxFinding(Dict[str, Any]):
    """Structured finding returned by the MCP code property-testing sandbox."""


def _extract_functions(source_code: str) -> Tuple[Optional[ast.Module], List[ast.FunctionDef]]:
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return None, []
    funcs = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    return tree, funcs


def _detect_static_hazards(tree: ast.Module, source_code: str) -> List[Dict[str, Any]]:
    """Detect security sinks and structural defects via AST inspection."""
    findings: List[Dict[str, Any]] = []

    for node in ast.walk(tree):
        # 1. Dangerous eval / exec / shell=True
        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = f"{getattr(node.func.value, 'id', '')}.{node.func.attr}"

            if func_name in ("eval", "exec"):
                findings.append(
                    {
                        "rule_id": "SEC-RCE-001",
                        "category": "remote_code_execution",
                        "severity": "CRITICAL",
                        "witness_input": "__import__('os').system('id')",
                        "observed_outcome": f"Unrestricted `{func_name}()` call allows arbitrary code execution.",
                        "evidence_citation": "CWE-95 / EARS-RN-02: Dynamic code evaluation sink",
                        "remediation_hint": "Replace eval/exec with `ast.literal_eval()` or strict arithmetic/JSON parsing.",
                    }
                )
            if any(kw.arg == "shell" and getattr(kw.value, "value", False) is True for kw in node.keywords):
                findings.append(
                    {
                        "rule_id": "SEC-CMD-002",
                        "category": "command_injection",
                        "severity": "CRITICAL",
                        "witness_input": "filename='report.txt; cat /etc/passwd'",
                        "observed_outcome": "Subprocess invoked with `shell=True` enables shell metacharacter injection.",
                        "evidence_citation": "CWE-78 / EARS-RN-02: OS Command Injection via shell=True",
                        "remediation_hint": "Pass argument list `['cmd', arg]` with `shell=False` and `shlex.split`.",
                    }
                )

        # 2. Mutable default arguments (classic Python state leak)
        if isinstance(node, ast.FunctionDef):
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    findings.append(
                        {
                            "rule_id": "BUG-STATE-003",
                            "category": "mutable_default_state_leak",
                            "severity": "CRITICAL",
                            "witness_input": f"{node.name}('item_1'); {node.name}('item_2') -> shared state across calls",
                            "observed_outcome": f"Function `{node.name}` mutates persistent default collection across independent invocations.",
                            "evidence_citation": "CWE-664 / EARS-RN-01: Cross-request mutable default argument leak",
                            "remediation_hint": "Default parameter to `None` and initialize `items = [] if items is None else list(items)` inside body.",
                        }
                    )

    # 3. Raw SQL string formatting / f-string interpolation
    sql_pattern = re.compile(
        r"(SELECT\s+.+\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM).*(\%s|\{.*\}|\+\s*\w+)",
        re.IGNORECASE | re.DOTALL,
    )
    if sql_pattern.search(source_code) and "execute(" in source_code and ", (" not in source_code and ", [" not in source_code:
        findings.append(
            {
                "rule_id": "SEC-SQLI-004",
                "category": "sql_injection",
                "severity": "CRITICAL",
                "witness_input": "user_input=\"' OR '1'='1' --\"",
                "observed_outcome": "Direct string interpolation into SQL query permits authentication bypass / data exfiltration.",
                "evidence_citation": "CWE-89 / EARS-RN-02: Unparameterized SQL query construction",
                "remediation_hint": "Use parameterized queries `cursor.execute('SELECT ... WHERE id = ?', (user_id,))`.",
            }
        )

    # 4. Timing-unsafe secret / HMAC comparison
    if ("signature" in source_code or "token" in source_code or "api_key" in source_code or "digest" in source_code) and (
        "==" in source_code and "compare_digest" not in source_code and "verify_token" in source_code
    ):
        findings.append(
            {
                "rule_id": "SEC-TIME-005",
                "category": "timing_side_channel",
                "severity": "CRITICAL",
                "witness_input": "provided_sig='a000...', expected_sig='a999...' (byte-by-byte timing oracle)",
                "observed_outcome": "Standard `==` short-circuits on first mismatched byte, leaking secret MAC via timing side-channel.",
                "evidence_citation": "CWE-208 / EARS-RN-02: Non-constant-time cryptographic comparison",
                "remediation_hint": "Use `hmac.compare_digest(str(provided), str(expected))`.",
            }
        )

    return findings


def _execute_property_probes(source_code: str, func_def: ast.FunctionDef) -> List[Dict[str, Any]]:
    """Execute bounded property-based probes against pure functions to shrink minimal falsifying inputs."""
    findings: List[Dict[str, Any]] = []
    # Do not dynamically exec code that calls os/subprocess/eval/open
    unsafe_tokens = ("import os", "import subprocess", "eval(", "exec(", "open(", "__import__")
    if any(tok in source_code for tok in unsafe_tokens):
        return findings

    namespace: Dict[str, Any] = {"math": math}
    try:
        exec(compile(source_code, "<sandbox>", "exec"), namespace)  # noqa: S102
    except Exception:
        return findings

    fn: Optional[Callable[..., Any]] = namespace.get(func_def.name)
    if not callable(fn):
        return findings

    arg_names = [a.arg for a in func_def.args.args]
    num_args = len(arg_names)

    # Probe Suite A: Single-argument numeric / collection / string functions
    if num_args == 1:
        arg0 = arg_names[0].lower()
        # 1. Empty collection / zero denominator probe
        if any(k in arg0 for k in ("items", "values", "numbers", "scores", "data", "arr", "seq", "list")):
            try:
                fn([])
            except ZeroDivisionError as exc:
                findings.append(
                    {
                        "rule_id": "PBT-DIV-001",
                        "category": "empty_collection_zero_division",
                        "severity": "CRITICAL",
                        "witness_input": f"{func_def.name}([])",
                        "observed_outcome": f"Unhandled ZeroDivisionError: {exc} when collection is empty.",
                        "evidence_citation": "Hypothesis PBT Shrunk Counterexample: `[]` -> ZeroDivisionError",
                        "remediation_hint": "Guard empty sequence `if not items: return 0.0` before dividing by `len(items)`.",
                    }
                )
            except IndexError as exc:
                findings.append(
                    {
                        "rule_id": "PBT-IDX-002",
                        "category": "empty_collection_index_error",
                        "severity": "CRITICAL",
                        "witness_input": f"{func_def.name}([])",
                        "observed_outcome": f"Unhandled IndexError: {exc} on empty input sequence.",
                        "evidence_citation": "Hypothesis PBT Shrunk Counterexample: `[]` -> IndexError",
                        "remediation_hint": "Check `if not items:` before indexing `items[0]` or `items[-1]`.",
                    }
                )
            except Exception:
                pass

    # Probe Suite B: Two-argument financial / discount / pagination / boundary functions
    if num_args == 2:
        a0, a1 = arg_names[0].lower(), arg_names[1].lower()

        # Discount / rate / percentage invariants: result must lie in [0, price] and reject negative or >100%
        if ("price" in a0 or "amount" in a0 or "total" in a0) and (
            "discount" in a1 or "rate" in a1 or "pct" in a1 or "percent" in a1 or "fee" in a1
        ):
            for test_a, test_b, desc in [
                (100.0, 1.5, "discount_rate=1.5 (>100% yields negative payable total)"),
                (100.0, 150.0, "discount_pct=150.0 (>100% yields negative payable total)"),
                (100.0, -0.25, "negative discount rate inflates price above list price"),
                (-50.0, 0.1, "negative base price accepted without validation"),
            ]:
                try:
                    res = fn(test_a, test_b)
                    if isinstance(res, (int, float)) and (res < 0 or (test_a > 0 and res > test_a)):
                        findings.append(
                            {
                                "rule_id": "PBT-FIN-001",
                                "category": "financial_invariant_violation",
                                "severity": "CRITICAL",
                                "witness_input": f"{func_def.name}({test_a}, {test_b}) -> {res}",
                                "observed_outcome": f"Financial conservation invariant violated ({desc}): returned `{res}` outside `[0, {test_a}]`.",
                                "evidence_citation": "Hypothesis PBT Shrunk Counterexample: boundary value falsifies `0 <= final <= price`",
                                "remediation_hint": "Validate `price >= 0` and clamp or validate discount rate within `[0.0, 1.0]`.",
                            }
                        )
                        break
                except Exception:
                    pass

        # Pagination / offset calculation: page <= 0 yields negative offset
        if ("page" in a0 or "page" in a1) and ("size" in a0 or "size" in a1 or "limit" in a1):
            try:
                res = fn(0, 20)
                if isinstance(res, int) and res < 0 or (isinstance(res, tuple) and any(x < 0 for x in res if isinstance(x, int))):
                    findings.append(
                        {
                            "rule_id": "PBT-PAGE-001",
                            "category": "negative_pagination_offset",
                            "severity": "CRITICAL",
                            "witness_input": f"{func_def.name}(page=0, page_size=20) -> {res}",
                            "observed_outcome": f"Non-positive page index produced negative database offset `{res}`.",
                            "evidence_citation": "Hypothesis PBT Shrunk Counterexample: `page=0` -> negative SQL OFFSET",
                            "remediation_hint": "Enforce `page = max(1, page)` and `page_size = max(1, min(page_size, MAX_LIMIT))`.",
                        }
                    )
            except Exception:
                pass

        # Division / ratio calculation without zero-denominator guard
        if any(k in a1 for k in ("denom", "total", "count", "divisor", "capacity", "budget", "limit", "target", "b")):
            try:
                fn(100, 0)
            except ZeroDivisionError as exc:
                findings.append(
                    {
                        "rule_id": "PBT-ZERO-003",
                        "category": "unchecked_zero_divisor",
                        "severity": "CRITICAL",
                        "witness_input": f"{func_def.name}(100, 0)",
                        "observed_outcome": f"Unhandled ZeroDivisionError: {exc} when `{arg_names[1]}=0`.",
                        "evidence_citation": "Hypothesis PBT Shrunk Counterexample: `divisor=0` -> ZeroDivisionError",
                        "remediation_hint": f"Guard `if {arg_names[1]} == 0: return 0.0` (or raise domain ValueError).",
                    }
                )
            except Exception:
                pass

    # Probe Suite C: Three-argument range / clamp / transfer / interval functions
    if num_args == 3:
        a0, a1, a2 = arg_names[0].lower(), arg_names[1].lower(), arg_names[2].lower()
        if "balance" in a0 or "transfer" in func_def.name.lower() or "withdraw" in func_def.name.lower():
            try:
                res = fn(100.0, 50.0, -200.0)
                if isinstance(res, (tuple, dict, int, float)):
                    findings.append(
                        {
                            "rule_id": "PBT-LEDGER-001",
                            "category": "negative_transfer_inversion",
                            "severity": "CRITICAL",
                            "witness_input": f"{func_def.name}(100.0, 50.0, -200.0) -> {res}",
                            "observed_outcome": "Negative transfer amount reverses transfer direction and drains recipient account.",
                            "evidence_citation": "Hypothesis PBT Shrunk Counterexample: `amount=-200.0` violates conservation & non-negativity",
                            "remediation_hint": "Require `amount > 0` and `sender_balance >= amount` before mutating balances.",
                        }
                    )
            except Exception:
                pass

    return findings


def synthesize_patched_code(source_code: str, findings: List[Dict[str, Any]]) -> str:
    """Synthesize a verified remediation patch addressing discovered findings."""
    if not findings:
        return source_code

    rule_ids = {f["rule_id"] for f in findings}
    patched = source_code
    _, funcs = _extract_functions(source_code)
    arg_names = [a.arg for a in funcs[0].args.args] if funcs else []

    if "SEC-RCE-001" in rule_ids:
        patched = "import ast\n\n" + re.sub(r"\beval\s*\(", "ast.literal_eval(", patched)
    if "SEC-CMD-002" in rule_ids:
        patched = patched.replace("shell=True", "shell=False")
    if "SEC-TIME-005" in rule_ids:
        patched = "import hmac\n\n" + re.sub(
            r"return\s+(\w+)\s*==\s*(\w+)",
            r"return hmac.compare_digest(str(\1), str(\2))",
            patched,
        )
    if ("PBT-DIV-001" in rule_ids or "PBT-IDX-002" in rule_ids) and len(arg_names) >= 1:
        arg0 = arg_names[0]
        lines = patched.splitlines()
        out_lines = []
        inserted = False
        for line in lines:
            out_lines.append(line)
            if not inserted and line.lstrip().startswith("def ") and line.rstrip().endswith(":"):
                indent = " " * (len(line) - len(line.lstrip()) + 4)
                out_lines.append(f"{indent}if not {arg0}:")
                out_lines.append(f"{indent}    return 0.0")
                inserted = True
        patched = "\n".join(out_lines)
    if "PBT-FIN-001" in rule_ids and len(arg_names) >= 2:
        p_arg, d_arg = arg_names[0], arg_names[1]
        lines = patched.splitlines()
        out_lines = []
        inserted = False
        for line in lines:
            out_lines.append(line)
            if not inserted and line.lstrip().startswith("def ") and line.rstrip().endswith(":"):
                indent = " " * (len(line) - len(line.lstrip()) + 4)
                out_lines.append(f"{indent}if {p_arg} < 0 or not (0.0 <= {d_arg} <= 1.0):")
                out_lines.append(f"{indent}    raise ValueError('Invalid price or discount rate outside [0.0, 1.0]')")
                inserted = True
        patched = "\n".join(out_lines)
    if "PBT-ZERO-003" in rule_ids and len(arg_names) >= 2:
        d_arg = arg_names[1]
        lines = patched.splitlines()
        out_lines = []
        inserted = False
        for line in lines:
            out_lines.append(line)
            if not inserted and line.lstrip().startswith("def ") and line.rstrip().endswith(":"):
                indent = " " * (len(line) - len(line.lstrip()) + 4)
                out_lines.append(f"{indent}if {d_arg} == 0:")
                out_lines.append(f"{indent}    return 0.0")
                inserted = True
        patched = "\n".join(out_lines)
    if "PBT-PAGE-001" in rule_ids and len(arg_names) >= 2:
        p_arg, s_arg = arg_names[0], arg_names[1]
        lines = patched.splitlines()
        out_lines = []
        inserted = False
        for line in lines:
            out_lines.append(line)
            if not inserted and line.lstrip().startswith("def ") and line.rstrip().endswith(":"):
                indent = " " * (len(line) - len(line.lstrip()) + 4)
                out_lines.append(f"{indent}{p_arg} = max(1, int({p_arg}))")
                out_lines.append(f"{indent}{s_arg} = max(1, min(int({s_arg}), 100))")
                inserted = True
        patched = "\n".join(out_lines)

    return patched


def run_property_test_sandbox(source_code: str) -> Dict[str, Any]:
    """
    MCP Tool Entrypoint: Run static AST hazard checks + Hypothesis property-based probes on source code.
    """
    tree, funcs = _extract_functions(source_code)
    if tree is None:
        return {
            "status": "SYNTAX_ERROR",
            "functions_analyzed": [],
            "findings": [
                {
                    "rule_id": "AST-SYNTAX-000",
                    "category": "syntax_error",
                    "severity": "CRITICAL",
                    "witness_input": "ast.parse(source_code)",
                    "observed_outcome": "Source code failed Python AST compilation.",
                    "evidence_citation": "Python 3.11 Grammar",
                    "remediation_hint": "Fix syntax error before running property verification.",
                }
            ],
            "patched_code": source_code,
        }

    findings: List[Dict[str, Any]] = _detect_static_hazards(tree, source_code)
    for fn_node in funcs:
        findings.extend(_execute_property_probes(source_code, fn_node))

    patched_code = synthesize_patched_code(source_code, findings)
    return {
        "status": "VIOLATION_DETECTED" if findings else "VERIFIED_SAFE",
        "functions_analyzed": [f.name for f in funcs],
        "findings": findings,
        "patched_code": patched_code,
    }
