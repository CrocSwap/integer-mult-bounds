"""Replay exact pricing and both signed odd/even idle support exclusions."""
from argparse import ArgumentParser
from fractions import Fraction
from gzip import decompress
from hashlib import sha1, sha256
from json import loads
from pathlib import Path
from shutil import copytree
from subprocess import run
from sys import executable
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
BLOB = "9451ceaf6e8e037894680b549f3ef41c21b260d7"
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"


def check(ok, reason):
    if not ok:
        raise ValueError(reason)


def unique(items):
    obj = dict(items)
    check(len(obj) == len(items), "duplicate JSON path or key")
    return obj


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def replay(output):
    check(__debug__, "CPython assertions are required")
    for rel, pin in decode((HERE / "LOCAL-PINS.json").read_bytes()).items():
        path = HERE / rel
        check(path.resolve().is_relative_to(HERE) and digest(path.read_bytes()) == pin, f"changed input {rel}")
    expected = decode((HERE / "receipts/SHA256.json").read_bytes())
    first = decode((HERE / "receipts/MASK-ADMISSION.json").read_bytes())
    caller = decompress((HERE / "price/inputs/7113-CALLER.json.gz").read_bytes())
    check(digest(caller) == CALLER and sha1(f"blob {len(caller)}".encode() + bytes(1) + caller).hexdigest() == BLOB,
          "changed exact #7113 caller")
    output.mkdir(parents=True, exist_ok=False)
    with TemporaryDirectory(prefix="type-b-odd-even-") as tmp:
        work = Path(tmp)
        for name in ("inputs", "price", "lead", "independent"):
            copytree(HERE / name, work / name)
        inputs = work / "price/inputs"
        for name in ("7113-CALLER.json", "R53-PRICE.json", "R59-PRICE.json"):
            p = inputs / (name + ".gz")
            p.with_suffix("").write_bytes(decompress(p.read_bytes()))
        r53, r59 = (decode((inputs / name).read_bytes()) for name in ("R53-PRICE.json", "R59-PRICE.json"))
        mask53 = {str(t): mask for t, _, mask in r53["job_masks"] if len(mask) > 1}
        mask59 = {t: mask for t, (_, mask) in r59["even_jobs"].items()}
        check(mask53.keys() == mask59.keys() and all(sorted(mask53[t]) == sorted(mask59[t]) for t in mask53) and
              sum(mask53[t] != mask59[t] for t in mask53) == first["opposite_orders"] == 14,
              "mask admission control differs")

        def stage(name, script, *args):
            child = run([executable, "-I", "-B", str(script), *map(str, args)], cwd=work,
                        capture_output=True, check=True, timeout=25)
            check(digest(child.stdout) == expected[name], "changed receipt " + name)
            (output / name).write_bytes(child.stdout)
            return decode(child.stdout)

        price = stage("PRICE.json", work / "price/quote.py")
        price_path = work / "price/PRICE.json"
        price_path.write_bytes((output / "PRICE.json").read_bytes())
        lead = stage("LEAD.json", work / "lead/projector_gate.py", work)
        args = ("--price", price_path, "--admission", inputs / "7334-ADMITTED.json",
                "--caller", inputs / "7113-CALLER.json")
        second = stage("INDEPENDENT.json", work / "independent/direct_impulse.py", *args)
        check(price["head"] == lead["head"] == second["head"] == HEAD and lead["q"] == second["q"] == 1 and
              second["old_endpoint_columns"] == 36 and lead["counts"] == second["counts"] == {"excluded": 180} and
              not any((lead["provisional"], lead["unvisited"], second["survivors"], second["unvisited"])),
              "incomplete exact 180-case scope")
        prime = lead["modulus"]
        for key, left, right in zip(price["keys"], lead["decisions"], second["outcomes"], strict=True):
            axis, col, coefficient = right["exact_off_axis"]
            q = Fraction(coefficient)
            residue = q.numerator * pow(q.denominator, -1, prime) % prime
            check(left["key"] == key and right["key"] == [key["odd"], key["even"]] and
                  right["mask_size"] == key["size"] and axis == "column" and
                  left["outside_column"] == [col - 36, residue] and residue != 0,
                  "rational and modular witnesses differ")
        (inputs / "7113-CALLER.json").write_bytes(caller + b" ")
        mutant = run([executable, "-I", "-B", str(work / "independent/direct_impulse.py"), *map(str, args)],
                     cwd=work, capture_output=True, timeout=20)
        check(mutant.returncode and b"changed input 7113-CALLER.json" in mutant.stderr and not mutant.stdout,
              "changed caller accepted")
    check({p.name for p in output.iterdir()} == set(expected), "wrong output set")
    print("PASS_TYPE_B_ODD_EVEN_IDLE_FUSION cases=180 excluded=180 unresolved=0 kappa_change=0")


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("--out", type=Path)
    a = p.parse_args()
    if a.out:
        replay(a.out.resolve())
    else:
        with TemporaryDirectory(prefix="type-b-odd-even-receipts-") as tmp:
            replay(Path(tmp) / "out")
