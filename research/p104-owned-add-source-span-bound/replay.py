"""Reprice and independently reconstruct every signed donor-span exclusion."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha1, sha256
from json import dumps, loads
from pathlib import Path
from shutil import copyfile
from subprocess import run
from sys import executable
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
WORD = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
ADMISSION = "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13"
PRIME = 65521


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    values = dict(pairs)
    require(len(values) == len(pairs), "Duplicate JSON key")
    return values


def read(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def verify_pins():
    for name, want in read((HERE / "LOCAL-PINS.json").read_bytes()).items():
        path = (HERE / name).resolve()
        require(path.is_relative_to(HERE) and digest(path.read_bytes()) == want, f"Changed local input {name}")
    for name, proof in read((HERE / "PROVENANCE.json").read_bytes())["files"].items():
        path = (HERE / name).resolve()
        require(path.is_relative_to(HERE), f"Unsafe source path {name}")
        raw = path.read_bytes()
        if proof.get("uncompress"):
            raw = decompress(raw)
        blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(digest(raw) == proof["sha256"] and blob == proof["git_blob"], f"Changed public source {name}")
    admission = (HERE / "inputs/ADMITTED.json").read_bytes()
    require(digest(admission) == ADMISSION, "Changed comparator admission")
    verified = read(admission)
    require(verified["head"] == HEAD and verified["caller_sha256"] == CALLER
            and len(verified["stages"]) == 4 and verified["exit"] == 0, "Incomplete comparator admission")
    base = read((HERE / "inputs/READBACK.json").read_bytes())
    require(base["head"] == HEAD and base["native_grid"] == [1125, 25]
            and set(base["assumptions"]) == set(verified["assumptions"]) == {
                "native_all_columns", "owned_erasure", "compiler", "precision_tape", "analytic_recovery"},
            "Changed comparator contract")


def certify(quote, lead, independent):
    require(quote["head"] == lead["head"] == independent["head"] == HEAD
            and quote["word_sha256"] == lead["word_sha256"] == independent["word_sha256"] == WORD,
            "Changed science comparator")
    price_hash = digest((HERE / "receipts/PRICE.json").read_bytes())
    require(lead["price_sha256"] == independent["price_sha256"] == price_hash, "Changed predecode quote")
    require(lead["status"] == "EXHAUSTED" and not lead["unvisited"] and not lead["survivors"]
            and not independent["unresolved"] and not independent["survivors"]
            and independent["timeout"] is None and independent["prime"] == PRIME, "Incomplete exact sweep")
    require(len(quote["keys"]) == len(lead["decisions"]) == len(independent["cases"]) == 33,
            "Changed key census")
    gross = list(map(Fraction, quote["gross_upper_all_three"]))
    require(0 < gross[0] <= gross[1] < 1
            and Fraction(quote["extra_rank_one_upper"][1]) < 0
            and sum(quote["paid_all_three"].values()) == 110468, "Changed complete stock upper")
    rows = independent["requested_integer_rows"]
    require(len(rows) == independent["distinct_requested_rows"] == 69, "Changed exact row count")
    bins = Counter()

    for key, forward, reverse in zip(quote["keys"], lead["decisions"], independent["cases"], strict=True):
        require(forward["key"] == reverse["key"] == key and forward["target_chart"] == reverse["proposed_chart"]
                and forward["source"] == [reverse["literal_read_clock"], reverse["literal_read_peer"]],
                "Changed cut or source")
        target = rows[reverse["target_row_id"]]
        bank = [(role, rows[idx]) for role, idx in reverse["donor_role_row_ids"]]
        require(forward["decision"] == "outside donor span" and forward["matching_coefficients"] is None
                and forward["residual"] and forward["rank"] == reverse["donor_rank"]
                and reverse["augmented_rank"] == reverse["donor_rank"] + 1
                and forward["bank_roles"] == [role for role, row in bank if row[0]]
                and forward["source_nnz"] == len(target[0]) and len(bank) == reverse["donors"]
                and all(role != key[0] for role, _ in bank), "Bank or rank mismatch")
        require(all(row[1] > 0 and row[1] % PRIME for _, row in bank) and target[1] > 0 and target[1] % PRIME,
                "Nonunit denominator")

        if reverse["status"] == "absent_exterior_coordinate":
            j = str(reverse["coordinate"])
            residue = target[0][j] * pow(target[1], -1, PRIME) % PRIME
            require(all(j not in row[0] for _, row in bank)
                    and Fraction(target[0][j], target[1]) == Fraction(reverse["target_coefficient"])
                    and residue == reverse["target_residue_mod_prime"] != 0, "Invalid exterior certificate")
        else:
            require(reverse["status"] == "exact_rank_exclusion", "Unexpected witness kind")
            dual = {j: Fraction(x) for j, x in reverse["separating_covector"].items()}

            def dot(row):
                return sum((row[0].get(j, 0) * value for j, value in dual.items()), Fraction(0)) / row[1]

            require(all(dot(row) == 0 for _, row in bank)
                    and dot(target) == Fraction(reverse["separated_target"]) == -2, "Invalid rational dual")
        bins[reverse["status"]] += 1
    require(bins == {"absent_exterior_coordinate": 24, "exact_rank_exclusion": 9},
            "Unexpected certificate census")
    return dict(cases=33, rows=69, witness_counts=dict(bins), exact_donor_rank_agreements=33,
                survivors=0, unresolved=0, supported_credit=0, gross_optimistic_stock=quote["gross_upper_all_three"])


def replay(out):
    require(__debug__, "Run with assertions")
    verify_pins()
    wanted = read((HERE / "receipts/SHA256.json").read_bytes())
    out.mkdir(parents=True, exist_ok=False)
    with TemporaryDirectory(prefix="owned-add-span-") as tmp:
        root = Path(tmp)
        (root / "inputs").mkdir()
        price_inputs = root / "price/inputs"
        price_inputs.mkdir(parents=True)
        for name in ("R82-CONTACTS.json", "R82-PRICE.json", "READBACK.json", "pricing.py"):
            copyfile(HERE / "inputs" / name, price_inputs / name)
        quote_runner = root / "price/quote.py"
        copyfile(HERE / "engines/quote.py", quote_runner)

        def stage(name, script, *args):
            cmd = [executable, "-I", "-B", str(script), *map(str, args)]
            result = run(cmd, cwd=root, capture_output=True, check=True, timeout=22)
            exact = HERE / "receipts" / (name if name == "PRICE.json" else name + ".gz")
            raw = exact.read_bytes()
            expected = raw if name == "PRICE.json" else decompress(raw)
            require(result.stdout == expected and digest(result.stdout) == wanted[name], f"Changed receipt {name}")
            (out / name).write_bytes(result.stdout)
            return result.stdout

        raw_quote = stage("PRICE.json", quote_runner)
        price = root / "price/PRICE.json"
        price.write_bytes(raw_quote)
        word = root / "inputs/7334-WORD.json.gz"
        copyfile(HERE / "inputs" / word.name, word)
        require(digest(decompress(word.read_bytes())) == PAYLOAD, "Changed canonical native payload")
        lead = read(stage("FORWARD.json", HERE / "engines/forward.py", root))
        independent = read(stage("REVERSE.json", HERE / "engines/reverse.py", "--word", word, "--price", price))
        result = certify(read(raw_quote), lead, independent)
        for target in (price, word):
            raw = target.read_bytes()
            target.write_bytes(raw + b"\n")
            mutation = run([executable, "-I", "-B", str(HERE / "engines/reverse.py"), "--word", str(word),
                            "--price", str(price)], cwd=root, capture_output=True, timeout=22)
            require(mutation.returncode != 0 and not mutation.stdout
                    and f"changed input {target.name}".encode() in mutation.stderr, "Changed pinned input passed")
            target.write_bytes(raw)
    result["mutations_rejected"] = ["price bytes", "compressed native word bytes"]
    raw = (dumps(result, sort_keys=True, indent=2) + "\n").encode()
    require(raw == (HERE / "receipts/COMPARE.json").read_bytes()
            and digest(raw) == wanted["COMPARE.json"], "Changed comparison receipt")
    (out / "COMPARE.json").write_bytes(raw)
    print("PASS_OWNED_ADD_SOURCE_SPAN_BOUND cases=33 excluded=33 unresolved=0 kappa_change=0")


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    if args.out:
        replay(args.out.resolve())
    else:
        with TemporaryDirectory(prefix="owned-add-span-receipts-") as tmp:
            replay(Path(tmp) / "out")


if __name__ == "__main__":
    main()
