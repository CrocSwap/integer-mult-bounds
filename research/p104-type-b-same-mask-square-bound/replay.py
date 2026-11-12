"""Replay the exact Type B same-mask price, projector and physical obstruction."""

from argparse import ArgumentParser
from fractions import Fraction
from gzip import decompress
from hashlib import sha1, sha256
from json import loads
from pathlib import Path
from shutil import copyfile
from subprocess import run
from sys import executable
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    value = dict(pairs)
    require(len(value) == len(pairs), "duplicate JSON key")
    return value


def read(raw):
    return loads(raw, object_pairs_hook=unique)


def authenticate():
    pins = read((HERE / "LOCAL-PINS.json").read_bytes())
    for rel, pin in pins.items():
        path = (HERE / rel).resolve()
        require(path.is_relative_to(HERE) and sha256(path.read_bytes()).hexdigest() == pin,
                f"changed local dependency {rel}")
    provenance = read((HERE / "PROVENANCE.json").read_bytes())
    for rel, entry in provenance["files"].items():
        require(rel in pins, f"unpinned public source {rel}")
        raw = (HERE / rel).read_bytes()
        if entry["uncompress"]:
            raw = decompress(raw)
        blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(sha256(raw).hexdigest() == entry["sha256"] and blob == entry["git_blob"],
                f"changed public source {rel}")
    for rel, entry in provenance["generated"].items():
        require(rel in pins and sha256((HERE / rel).read_bytes()).hexdigest() == entry["receipt_sha256"],
                f"changed predecessor receipt {rel}")


def entry(projector, i, j):
    return Fraction(dict(projector["inverse_column"]).get(i,0))*Fraction(dict(projector["prefix_row"]).get(j,0))


def reconcile(price, prefix, interval, physical):
    require(price["head"] == prefix["head"] == interval["head"] == physical["head"] == HEAD, "changed comparator")
    require(prefix["status"] == interval["status"] == "EXHAUSTED"
            and prefix["counts"] == interval["counts"] == {"excluded":9}, "incomplete literal tests")
    require(not any(doc[name] for doc in (prefix,interval) for name in ("unvisited","survivors"))
            and prefix["old_endpoint_basis_columns"] == interval["old_arbitrary_input_endpoint_columns"] == 36,
            "lost all-column old endpoint or exhaustive scope")
    require(price["whole_disjoint_cases"] == 9 and len({key["stage"] for key in price["cases"]}) == 9 and
            sum(price["old_paid"].values()) == 110519 and sum(price["old_targets"].values()) == 22461,
            "changed complete stock")
    for key, a, b, c in zip(price["cases"],prefix["decisions"],interval["results"],physical["cases"],strict=True):
        require(a["key"] == b["key"] == c["key"] == key and a["status"] == b["status"] == "excluded",
                "changed frozen key")
        d = a["obstruction"]
        i,j = d["matrix_coordinate"]
        old,new = (entry(a[end],i,j) for end in ("earlier","later"))
        require(old == Fraction(d["earlier_projector_entry"]) and new == Fraction(d["later_projector_entry"])
                and new-old == Fraction(d["later_minus_earlier"]) and old != new,
                "invalid exact transported projector witness")
        require(b["column_off_axis"] and b["row_off_axis"], "missing direct interval witnesses")
        i,value = b["column_off_axis"][0]
        x = Fraction(value)
        require(x and i != key["role"] and c["matrix_coordinate"] == [i,key["role"]]
                and Fraction(c["retained_square_interval_entry"]) == x
                and Fraction(c["two_original_idles_interval_entry"]) == -x
                and Fraction(c["original_minus_square"]) == -2*x
                and c["target_body_degree"] == c["target_inverse_body_degree"] == 0
                and not c["interior_matching_body_events"], "invalid physical sign witness")


def replay(output):
    require(__debug__, "assertions must be enabled")
    authenticate()
    output.mkdir(parents=True, exist_ok=False)
    with TemporaryDirectory(prefix="type-b-same-mask-square-") as directory:
        root = Path(directory)
        lead = root / "lead"
        inputs = lead / "inputs"
        inputs.mkdir(parents=True)
        price_path = root / "price/PRICE.json"
        price_path.parent.mkdir()
        copyfile(HERE / "inputs/R85-PRICE.json", lead / "PRICE.json")
        for name in ("7334-ADMITTED.json","7334-READBACK.json","pricing.py"):
            copyfile(HERE / "inputs" / name, inputs / name)
        caller_path = inputs / "7113-CALLER.json"
        caller = decompress((HERE / "inputs/7113-CALLER.json.gz").read_bytes())
        caller_path.write_bytes(caller)
        admission = inputs / "7334-ADMITTED.json"

        def stage(name, script, *args):
            result = run([executable,"-I","-B",str(HERE / "engines" / script),*map(str,args)],
                         cwd=root, check=True, capture_output=True, timeout=22)
            require(result.stdout == (HERE / "receipts" / name).read_bytes(), f"changed receipt {name}")
            (output / name).write_bytes(result.stdout)
            return result.stdout

        price = stage("PRICE.json","quote.py",lead)
        price_path.write_bytes(price)
        prefix = stage("PREFIX.json","same_mask_gate.py",root)
        interval = stage("INTERVAL.json","interval.py","--price",price_path,"--caller",caller_path,
                         "--admission",admission)
        physical = stage("PHYSICAL.json","physical_character.py","--price",price_path,"--caller",caller_path,
                         "--interval",output / "INTERVAL.json")
        reconcile(*map(read,(price,prefix,interval,physical)))

        for mutated in (price_path,caller_path):
            original = mutated.read_bytes()
            mutated.write_bytes(original + b"\n")
            reject = run([executable,"-I","-B",str(HERE / "engines/same_mask_gate.py"),str(root)],
                         cwd=root,capture_output=True,timeout=10)
            require(reject.returncode == 1 and not reject.stdout
                    and f"changed dependency {mutated.relative_to(root)}".encode() in reject.stderr,
                    f"changed source accepted {mutated.relative_to(root)}")
            mutated.write_bytes(original)
    print("PASS_TYPE_B_SAME_MASK_SQUARE pairs=9 excluded=9 physical_witnesses=9 unresolved=0 kappa_change=0")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args = parser.parse_args()
    if args.out:
        replay(args.out.resolve())
    else:
        with TemporaryDirectory(prefix="same-mask-receipts-") as directory:
            replay(Path(directory) / "out")


if __name__ == "__main__":
    main()
