"""Verify a frozen receiver's import order as source text."""

import ast
from hashlib import sha256
from pathlib import Path


GATES = (
    "VALIDATION_CONFIGURATION", "VALIDATION_SOURCE_REVIEW",
    "VALIDATION_EXECUTION", "VALIDATION_FUNDING",
)
ERROR = "Variant receiver is unconfigured; import and execution withheld"
DEFERRED = (
    "# Deferred source-owned PRE-CAPTURE binding successor. No receiver may run here.\n"
    "# The unchanged validate_variant_producer gate and original parent gate/closure\n"
    "# enforce exact installed values before its first actual call.\n"
).encode("ascii")
GUARD = (
    "if (VALIDATION_CONFIGURATION is None or VALIDATION_SOURCE_REVIEW is None or\n"
    "        VALIDATION_EXECUTION is None or VALIDATION_FUNDING is None):\n"
    f"    raise RuntimeError({ERROR!r})\n"
).encode("ascii")


def need(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def prelude(raw, guarded):
    """Check the exact statements up to the first import; execute no subject."""
    tree = ast.parse(raw)
    doc, *statements = tree.body
    need(isinstance(doc, ast.Expr) and isinstance(doc.value, ast.Constant) and
         type(doc.value.value) is str, "unexpected receiver docstring")
    declarations = "\n".join(f"{gate} = None" for gate in GATES)
    expected = ast.parse(declarations + "\n" + (GUARD.decode("ascii") if guarded else "")).body
    need([ast.dump(node) for node in statements[:len(expected)]] ==
         [ast.dump(node) for node in expected], "unexpected gate declarations or first branch")
    imports = statements[len(expected):len(expected) + 3]
    need([ast.dump(node) for node in imports] == [ast.dump(node) for node in
         ast.parse("import hashlib\nimport json\nimport sealed_elf_profile_v2 as elf").body],
         "first imports differ")
    return statements[len(expected):]


def main():
    src = Path(__file__).parent / "reference/deferred_receiver.py.txt"
    deferred = src.read_bytes()
    need(sha256(deferred).hexdigest() ==
         "37f12c53804047ac1f76474639e801802ded977126f33f3e64aabc7cc83864e5",
         "pinned deferred receiver differs")
    need(deferred.count(DEFERRED) == 1, "exact deferred prelude differs")
    guarded = deferred.replace(DEFERRED, GUARD, 1)
    need(sha256(guarded).hexdigest() ==
         "5e099fbe13f9e6f548a36ba2202bceef2f5d479bed85529ce57b26654f7c0a98",
         "restored guarded template differs")
    need([ast.dump(node) for node in prelude(deferred, False)] ==
         [ast.dump(node) for node in prelude(guarded, True)], "receiver suffix changed")

    image = guarded
    for index, gate in enumerate(GATES):
        before = f"{gate} = None\n".encode("ascii")
        after = f"{gate} = _PY_GATE_VALUES[{index}]\n".encode("ascii")
        need(image.count(before) == 1, "declaration not unique")
        image = image.replace(before, after, 1)
    need(sha256(image).hexdigest() ==
         "e06d247513370fb6ea3a2af9d8e490fcde26d1988885ff669b26edb57586375e",
         "guarded derivative differs")
    restored = image
    for index, gate in enumerate(GATES):
        after = f"{gate} = _PY_GATE_VALUES[{index}]\n".encode("ascii")
        before = f"{gate} = None\n".encode("ascii")
        need(restored.count(after) == 1, "inverse declaration not unique")
        restored = restored.replace(after, before, 1)
    need(restored == guarded, "full declaration inverse differs")
    print("Pinned source and full inverse match.")
    for gate in GATES:
        print(f"{gate}: deferred first attempts hashlib; guarded first raises RuntimeError.")
    print("Source inspection only. No subject was imported, compiled, or run.")


if __name__ == "__main__":
    main()
