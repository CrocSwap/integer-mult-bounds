"""Regenerate only the new literal word and its two new native recipes."""
from pathlib import Path
import argparse
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import model as M


def write_word(path, word):
    """Keep one event per line, matching the predecessor's reviewable format."""
    lines = ["{"]
    lines.extend("  " + M.encoded(key) + ": " + M.encoded(value) + ","
                 for key, value in word.items() if key != "program")
    lines.append('  "program": [')
    lines.append(",\n".join("    " + M.encoded(event) for event in word["program"]))
    lines.extend(["  ]", "}"])
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write("\n".join(lines) + "\n")


def construct():
    M.authenticate()
    candidate = M.rewrite(M.read(M.P / "inputs/PR2662-WORD.json"))
    compiler = M.native_module("clifford_exact.py")
    records = []
    for role, old, new, rank in M.EDGES:
        ordinary = compiler.canonical_frame(9, old).adjoint().then(compiler.canonical_frame(9, new))
        operator = compiler.ident(9)
        for gate in M.conjugate(ordinary.circuit):
            if gate[0] == "P":
                primitive = compiler.perm(9, gate[1])
            elif gate[0] == "C":
                primitive = compiler.cgate(9, gate[1], gate[2])
            elif gate[0] == "D":
                primitive = compiler.diag(9, gate[1], gate[2])
            elif gate[0] == "X":
                primitive = compiler.xgate(9, gate[1])
            else:
                M.need(gate[0] == "phase", "compiler gate")
                primitive = compiler.Op(9, compiler.identity(9), [gate])
            operator = operator.then(primitive)
        recipe, _ = compiler.lower_child(operator)
        M.need(recipe["rank"] == rank, "new child rank")
        records.append(dict(role=role, old=list(old), new=list(new), recipe=recipe))
    return candidate, dict(schema_version=1, transports=records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name in ("WORD.json", "NATIVE.json"):
        M.need(not (args.out_dir/name).exists(), "exclusive output")
    word, native = construct()
    write_word(args.out_dir/"WORD.json", word)
    M.write_new(args.out_dir/"NATIVE.json", native)
    print("BUILT_P104_DUAL_ADD_RETIMING")
