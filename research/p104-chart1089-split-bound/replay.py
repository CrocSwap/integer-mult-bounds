"""Regenerate the signed 3+6 price and two chart-1089 exclusion receipts."""
from argparse import ArgumentParser
from gzip import decompress
from hashlib import sha1, sha256
from json import loads
from pathlib import Path
from shutil import copytree
from subprocess import run
from sys import executable
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
WORD_BLOB = "73f43007192eb5a38eb5abb591b871df3e52c7cd"
BANK = [85, 319, 1081]
KEYS = [[k, 1089, 1081] for k in range(44588, 44600)]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    obj = dict(pairs)
    require(len(obj) == len(pairs), "Duplicate JSON key or path")
    return obj


def read(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def replay(output):
    require(__debug__, "CPython assertions required")
    for rel, wanted in read((HERE / "LOCAL-PINS.json").read_bytes()).items():
        path = HERE / rel
        require(path.resolve().is_relative_to(HERE) and digest(path.read_bytes()) == wanted,
                f"Changed pinned input {rel}")
    expected = read((HERE / "receipts/SHA256.json").read_bytes())
    word_raw = (HERE / "inputs/7334-WORD.json.gz").read_bytes()
    require(sha1(f"blob {len(word_raw)}".encode() + bytes(1) + word_raw).hexdigest() == WORD_BLOB,
            "Changed exact #7334 Git object")
    output.mkdir(parents=True, exist_ok=False)
    with TemporaryDirectory(prefix="p104-chart1089-") as tmp:
        work = Path(tmp)
        for sub in ("inputs", "price", "lead", "independent"):
            copytree(HERE / sub, work / sub)
        price_root = work / "price"
        for name in ("OCCUPANCY.json", "AFFECTED-CHARTS.json"):
            packed = price_root / "inputs" / (name + ".gz")
            packed.with_suffix("").write_bytes(decompress(packed.read_bytes()))

        def stage(name, script, *args, timeout=25):
            process = run([executable, "-I", "-B", str(script), *map(str, args)], cwd=work,
                          check=True, capture_output=True, timeout=timeout)
            require(digest(process.stdout) == expected[name], f"Changed receipt {name}")
            (output / name).write_bytes(process.stdout)
            return read(process.stdout)

        price = stage("PRICE.json", price_root / "quote.py")
        price_path = price_root / "PRICE.json"
        price_path.write_bytes((output / "PRICE.json").read_bytes())
        direct = stage("LEAD.json", work / "lead/low_chart.py", work, timeout=50)
        word = work / "inputs/7334-WORD.json.gz"
        options = ("--price", price_path, "--cohort", price_root / "inputs/OCCUPANCY.json", "--word", word)
        independent = stage("INDEPENDENT.json", work / "independent/chart1089.py", *options, timeout=55)
        require(price["head"] == direct["head"] == independent["head"] == HEAD and
                price["stock"] == KEYS and price["productive_delta"] == {"3": 17, "6": 17, "9": -17} and
                not price["paid_delta"], "Changed comparator, price or exact cut keys")
        require(not direct["unvisited"] and not direct["prefix_survivors"] and not independent["unvisited"] and
                not independent["survivors"] and independent["allowed_boundary_count"] == 615 and
                independent["observed_scalar_denominators_invertible"], "Incomplete scope")
        for a, b, key in zip(direct["decisions"], independent["rows"], KEYS, strict=True):
            require(a["key"] == b["key"] == key and a["public_bank"] == b["bank"]["public"] == BANK and
                    a["owned_bank_excluded"] == b["bank"]["owned"] == [] and
                    a["prefix_exterior_rank"] == b["prefix_modular_rank"] == 3 and not a["prefix_kernel_dim"] and
                    a["decision"] == "no nonzero pure prefix" and
                    b["status"] == "no_nonzero_pure_prefix_modular_minor" and
                    b["exterior_minor_columns"] == [98, 962, 1467] and b["exterior_minor_det_mod_p"] == 500001,
                    "Exact independent rank certificates disagree")
        word.write_bytes(word_raw + bytes(1))
        negative = run([executable, "-I", "-B", str(work / "independent/chart1089.py"), *map(str, options)],
                       cwd=work, capture_output=True, timeout=20)
        require(negative.returncode and b"changed pinned input 7334-WORD.json.gz" in negative.stderr and
                not negative.stdout, "Changed compressed word accepted")
    require({p.name for p in output.iterdir()} == set(expected), "Wrong replay receipt set")
    print("PASS_P104_CHART1089_FIXED_PAID cuts=12 rank=3 excluded=12 unresolved=0 kappa_change=0")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.out:
        replay(args.out.resolve())
    else:
        with TemporaryDirectory(prefix="p104-chart1089-receipts-") as tmp:
            replay(Path(tmp) / "out")


if __name__ == "__main__":
    main()
