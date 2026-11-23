"""Replay the fixed setup receipt correction on the prepared Round 415 source."""
from argparse import ArgumentParser
import ast
from hashlib import sha256
import json
from pathlib import Path

PREIMAGE = "438945be65f7647f85ba0f9bf5cd6dad7db60b39ea148885d7142a7b694184aa"
LEGACY = 217364570380528137475793294892811967875864032914108887556978854854656
EXPANDED = 217364571993743287866367176320080817069553173293686105666269057384448
OLD = "    setup = native_clock()\n"
NEW = """    setup = native_clock()
    indexed_setup_actions = 2**68 + 2**40
    lookup = 8 * (4 * setup["max_datum_bits"] * indexed_setup_actions) * 512 * 128
    setup["all_setup"] = (
        (indexed_setup_actions + 1)
        * (lookup + setup["local_arithmetic"] + 2**120)
        * 2**32
    )
"""


def digest(data):
    return sha256(data).hexdigest()


def patch_source(source):
    if digest(source) != PREIMAGE:
        raise ValueError("Prepared receipt source differs")
    if source.count(OLD.encode()) != 1:
        raise ValueError("Expected exactly one setup receipt anchor")
    output = source.replace(OLD.encode(), NEW.encode())
    compile(output, "receipt.py", "exec")
    return output


def setup_slice(source, native_clock):
    tree = ast.parse(source)
    for body in (node.body for node in tree.body if isinstance(node, ast.FunctionDef)):
        for i, node in enumerate(body):
            if not isinstance(node, ast.Assign) or ast.unparse(node.value) != "native_clock()":
                continue
            end = i + 1
            while end < len(body) and isinstance(body[end], ast.Assign):
                if ast.unparse(body[end].targets[0]) not in (
                    "indexed_setup_actions", "lookup", "setup['all_setup']",
                ):
                    break
                end += 1
            namespace = {"native_clock": native_clock}
            exec(compile(ast.Module(body=body[i:end], type_ignores=[]), "receipt.py", "exec"),
                 namespace)
            return namespace["setup"]["all_setup"]
    raise ValueError("Missing setup calculation")


def check(source):
    updated = patch_source(source)
    w = 2**38
    h = 2*w + 2
    local = 2**16*(h+4)*(7*h+9) + 8*2**16*(h+4)**2

    def inherited():
        return dict(max_datum_bits=w, all_setup=LEGACY, local_arithmetic=local)

    assert setup_slice(source, inherited) == LEGACY
    assert setup_slice(updated, inherited) == EXPANDED < 2**228
    mutated = updated.replace(b"4 * setup[\"max_datum_bits\"] * indexed_setup_actions",
                              b"4 * setup[\"max_datum_bits\"] * 2**68")
    assert mutated != updated
    stale = setup_slice(mutated, inherited)
    assert LEGACY < stale < EXPANDED
    return {
        "scope": "Literal prepared receipt calculation and missing-lookup control; installed execution unrun",
        "preimage": PREIMAGE, "corrected_sha256": digest(updated),
        "legacy_setup_transitions": LEGACY, "expanded_setup_transitions": EXPANDED,
        "stale_lookup_mutation_transitions": stale, "stale_lookup_rejected": stale != EXPANDED,
    }, updated


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--output", type=Path, help="Write the correction to a new path")
    args = parser.parse_args()
    receipt, updated = check(args.receipt.read_bytes())
    if args.output:
        with args.output.open("xb") as stream:
            stream.write(updated)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
