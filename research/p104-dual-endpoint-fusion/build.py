"""Explicit regeneration of the literal fused word and new native recipes."""

from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model as M


def construct():
    M.authenticate()
    source = M.read_json(M.PACKAGE / "inputs/PR2586-WORD.json")
    word, runs, pairs = M.fuse(source)
    M.replay(word)
    compiler = M.native_module("clifford_exact.py")
    recipes = []
    for (old, new), events in sorted(M.native_edges(pairs).items()):
        ordinary = compiler.canonical_frame(9, old).adjoint().then(compiler.canonical_frame(9, new))
        gates = M.conjugate(ordinary.circuit)
        operator = compiler.ident(9)
        for gate in gates:
            tag = gate[0]
            if tag == "P":
                primitive = compiler.perm(9, gate[1])
            elif tag == "D":
                primitive = compiler.diag(9, gate[1], gate[2])
            elif tag == "C":
                primitive = compiler.cgate(9, gate[1], gate[2])
            elif tag == "X":
                primitive = compiler.xgate(9, gate[1])
            else:
                M.require(tag == "phase", "compiler gate")
                primitive = compiler.Op(9, compiler.identity(9), [gate])
            operator = operator.then(primitive)
        recipe, _ = compiler.lower_child(operator)
        M.require(recipe["rank"] == len(new) - len(old), "new native child rank")
        recipes.append(dict(old=list(old), new=list(new), events=events, recipe=recipe))
    return word, dict(schema_version=1, transports=recipes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    M.require(not any((args.out_dir / name).exists() for name in ("WORD.json", "NATIVE.json")),
              "outputs must be new")
    word, native = construct()
    M.write_json_new(args.out_dir / "WORD.json", word)
    M.write_json_new(args.out_dir / "NATIVE.json", native)
    print("BUILT_P104_DUAL_ENDPOINT_FUSION", len(word["program"]), len(native["transports"]))


if __name__ == "__main__":
    main()
