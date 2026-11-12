"""Standard JSON-RPC 2.0 Model Context Protocol (MCP) Server for SpecGuard-Crew."""

from __future__ import annotations

import json
import pathlib
import sys
from typing import Any, Dict

from packages.specguard_core.compiler import EARSCompiler
from .tools_clinical_kb import query_clinical_guidelines_db
from .tools_code_sandbox import run_property_test_sandbox


MCP_TOOLS_SCHEMA = [
    {
        "name": "run_property_test_sandbox",
        "description": "Execute AST security analysis and Hypothesis Property-Based Testing probes on Python source code to shrink minimal falsifying counterexamples.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source_code": {"type": "string", "description": "Python function or module source code"}
            },
            "required": ["source_code"],
        },
    },
    {
        "name": "query_clinical_guidelines_db",
        "description": "Query the Zero-PHI Clinical Pharmacology Knowledge Base for renal (eGFR) dosing, pregnancy teratogenicity, allergy cross-reactivity, and drug-drug interactions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "clinical_text": {"type": "string", "description": "Synthetic clinical vignette or medication plan"}
            },
            "required": ["clinical_text"],
        },
    },
    {
        "name": "list_compiled_ears_invariants",
        "description": "Compile all .kiro/specs/**/requirements.md files into formal EARS VerificationDAGs.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


def handle_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single JSON-RPC 2.0 MCP request."""
    req_id = request.get("id", 1)
    method = request.get("method", "")
    params = request.get("params", {}) or {}

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "specguard-local-mcp", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": MCP_TOOLS_SCHEMA},
        }

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {}) or {}

        if tool_name == "run_property_test_sandbox":
            result = run_property_test_sandbox(arguments.get("source_code", ""))
        elif tool_name == "query_clinical_guidelines_db":
            result = query_clinical_guidelines_db(arguments.get("clinical_text", ""))
        elif tool_name == "list_compiled_ears_invariants":
            compiler = EARSCompiler()
            root = pathlib.Path(__file__).resolve().parents[2]
            dags = [
                compiler.compile_file(p).model_dump()
                for p in sorted(root.glob(".kiro/specs/*/requirements.md"))
            ]
            result = {"dags": dags}
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                "structuredContent": result,
            },
        }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Unsupported method: {method}"},
    }


def main() -> None:
    """Stdio JSON-RPC loop for MCP clients (Kiro IDE / Kiro CLI)."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_mcp_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as exc:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
