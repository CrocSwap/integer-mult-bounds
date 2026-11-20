"""Authenticate the exact source bytes and the two narrow allocator seams."""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(test, message):
    if not test:
        raise ValueError(message)


def authenticate(row, data):
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    need(blob == row["git_blob"] and hashlib.sha256(data).hexdigest() == row["sha256"],
         "source-byte mismatch: " + row["path"])


def method(tree, cls, name):
    owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
    return next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == name)


def check():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    live = [row for row in manifest["files"] if "local_input" in row]
    declared = json.loads((HERE / "VERIFY.json").read_text())["inputs"]
    need(sorted(row["local_input"] for row in live) == sorted(declared), "every vendored input declared for CI invalidation")
    for row in live:
        need(row["origin_commit"] == "ee6005fe241ab947e511fe9f6d86f5f4fa58478b", "exact immediate source head")
        need(row["pin"] == "head:" + row["origin_commit"] + ":" + row["origin_path"]
             and row["path"] == row["origin_path"], "upstream provenance matches the input origin")
        authenticate(row, (ROOT / row["local_input"]).read_bytes())
    word_tree = ast.parse((HERE / "inputs/old-words.py").read_text())
    for name, callee in (("literal", "zero"), ("free_many", "free")):
        body = method(word_tree, "Arena", name)
        need(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and n.func.attr == callee and isinstance(n.func.value, ast.Name)
                 and n.func.value.id == "self" for n in ast.walk(body)), "inherited dynamic lifecycle dispatch")
    producer = ast.parse((HERE / "inputs/old-producer.py").read_text())
    need(not any(isinstance(n, ast.Attribute) and n.attr == "available" for n in ast.walk(producer)),
         "current producer never decodes a host free stack")
    lifecycle_names = sorted({n.func.attr for n in ast.walk(producer)
                             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                             and n.func.attr in {"zero", "copy", "free", "free_many", "literal"}})
    need(lifecycle_names == ["copy", "free", "free_many", "literal", "zero"], "complete exact current lifecycle vocabulary")
    binder = ast.parse((HERE / "inputs/binding.py").read_text())
    simple = next(n for n in ast.walk(binder) if isinstance(n, ast.FunctionDef) and n.name == "reserve_simple")
    need([x.arg for x in simple.args.args] == ["self", "arena", "a", "b", "output"], "exact #7596 simple reservation signature")
    old = ast.parse((HERE / "inputs/old-binding.py").read_text())
    reserve = method(old, "Binding", "reserve")
    need([x.arg for x in reserve.args.args] == ["self", "arena", "n", "d"], "exact inherited two-result signature")
    changed = bytearray((ROOT / live[0]["local_input"]).read_bytes())
    changed[-1] ^= 1
    try:
        authenticate(live[0], bytes(changed))
    except ValueError:
        pass
    else:
        raise ValueError("source corruption escaped")
    return {"authenticated_inputs": len(live), "current_lifecycle_methods": lifecycle_names,
            "reservation_seams": ["reserve_simple", "reserve"], "source_mutation_rejected": True}


if __name__ == "__main__":
    print(json.dumps({"status": "PASS_LITERAL_CRT_LIFECYCLE_SOURCES", **check()}, indent=2, sort_keys=True))
