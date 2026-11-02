"""Archive identity and source-anchor check. Never imports archived code."""
from pathlib import Path
import ast
import hashlib
import json

ROOT = Path(__file__).resolve().parent

def need(condition, message):
    if condition is not True:
        raise RuntimeError(message)

def main():
    manifest = json.loads((ROOT / "ARTIFACTS.json").read_text())
    actual = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file() and p.name != "ARTIFACTS.json")
    need(actual == sorted(row["path"] for row in manifest["files"]), "archive file set changed")
    for row in manifest["files"]:
        raw = (ROOT / row["path"]).read_bytes()
        need(len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"], "archive byte identity changed: " + row["path"])
    findings = json.loads((ROOT / "SOURCE-FINDINGS.json").read_text())
    for row in findings["anchors"]:
        raw = (ROOT / row["path"]).read_text()
        tree = ast.parse(raw)
        nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == row["function"]]
        need(len(nodes) == 1, "source function missing or ambiguous")
        node = nodes[0]
        segment = "\n".join(raw.split("\n")[node.lineno-1:node.end_lineno])
        need(row["literal"] in segment, "pinned source anchor changed: " + row["id"])
    for row in findings["constants"]:
        tree = ast.parse((ROOT / row["path"]).read_text())
        assignments = [n.value for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == row["name"] for t in n.targets)]
        need(len(assignments) == 1, "literal binding missing or ambiguous")
        value = ast.literal_eval(assignments[0])
        if "expected_length" in row:
            need(type(value) is tuple and len(value) == row["expected_length"], "literal inventory cardinality changed")
        else:
            if type(value) is tuple:
                value = list(value)
            need(type(value) is type(row["expected"]) and value == row["expected"], "literal value changed")
    # These are structural readings of authenticated text, not original execution.
    parent = ast.parse((ROOT / "snapshot/parent_completion_v1.py.txt").read_text())
    need(not any(isinstance(n, ast.If) and "__name__" in ast.unparse(n.test) and "__main__" in ast.unparse(n.test) for n in parent.body), "unexpected executable parent main guard")
    need(findings["full_C05"] is False and findings["full_V03"] is False and findings["original_execution"] is False, "scope changed")
    print("PASS_SOURCE_IDENTITIES_AND_PINNED_ANCHORS", len(manifest["files"]), len(findings["anchors"]))

if __name__ == "__main__":
    main()
