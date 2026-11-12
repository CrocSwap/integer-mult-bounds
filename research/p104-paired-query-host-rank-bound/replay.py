"""Authenticate the exact caller, regenerate the directed price and replay every host."""
from argparse import ArgumentParser
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
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
PRIME = 65521


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "Duplicate JSON key")
    return result


def read(raw):
    return loads(raw, object_pairs_hook=unique)


def blob(raw):
    return sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def determinant3(m):
    (a, b, c), (d, e, f), (g, h, i) = m
    return (a * (e * i - f * h) + b * (f * g - d * i) + c * (d * h - e * g)) % PRIME


def replay(out):
    for rel, pin in read((HERE / "LOCAL-PINS.json").read_bytes()).items():
        file = HERE / rel
        require(file.resolve().is_relative_to(HERE) and sha256(file.read_bytes()).hexdigest() == pin,
                f"Changed dependency {rel}")
    caller = decompress((HERE / "inputs/7113-CALLER.json.gz").read_bytes())
    require(sha256(caller).hexdigest() == CALLER and blob(caller) == "9451ceaf6e8e037894680b549f3ef41c21b260d7",
            "Changed exact #7113 caller")
    require(blob((HERE / "engines/phase_a.py").read_bytes()) == "4404d8b35a20377990452f508d602cdf6141cde4",
            "Changed exact #7309 endpoint engine")
    require(blob((HERE / "inputs/QUERY-CENSUS.json").read_bytes()) == "9e3320bb7ceb8c4277977ccfb4a67e61cc8716c8",
            "Changed exact #7309 phase receipt")
    out.mkdir(parents=True, exist_ok=False)
    with TemporaryDirectory(prefix="paired-query-host-") as tmp:
        work = Path(tmp)
        price = work / "price"
        inputs = price / "inputs"
        inputs.mkdir(parents=True)
        for name in ("QUERY-CENSUS.json", "7334-ADMITTED.json", "7334-READBACK.json", "pricing.py"):
            copyfile(HERE / "inputs" / name, inputs / name)
        for name in ("quote.py", "quote_predecessor.py"):
            copyfile(HERE / "engines" / name, price / name)
        materialized = inputs / "7113-CALLER.json"
        materialized.write_bytes(caller)

        def stage(name, script, *args, expected=None):
            result = run([executable, "-I", "-B", str(script), *map(str, args)], cwd=work,
                         check=True, capture_output=True, timeout=22)
            reference = expected or HERE / "receipts" / name
            require(result.stdout == reference.read_bytes(), f"Changed receipt {name}")
            (out / name).write_bytes(result.stdout)
            return result.stdout

        previous = stage("PREDECESSOR-PRICE.json", price / "quote_predecessor.py")
        (inputs / "PREVIOUS-PRICE.json").write_bytes(previous)
        raw_quote = stage("PRICE.json", price / "quote.py")
        (price / "PRICE.json").write_bytes(raw_quote)
        phase = read(stage("PHASE.json", HERE / "engines/phase_a.py", "--caller", materialized,
                           expected=HERE / "inputs/QUERY-CENSUS.json"))
        require(phase["caller_sha256"] == CALLER and phase["dimension"] == 36
                and phase["q_plus_endpoint"] == "+I" and phase["q_minus_endpoint"] == "-I"
                and len(set(phase["ports"])) == 96 and phase["subsets_tested"] == 15
                and not phase["unvisited_subsets"] and len(phase["controls"]) == 2
                and all(phase["controls"].values()), "Lost predecessor endpoint controls")
        blocks = phase["relative_j_blocks"]
        queries = phase["query_events"]
        require(len(blocks) == 17 and all(b["relative_defect_rank"] == b["plus_identity_restricted_rank"] == 2 for b in blocks)
                and len(queries) == 4 and all(q["relative_defect_rank"] == 1 for q in queries.values()),
                "Changed slack inputs")
        required_host_rank = phase["dimension"] + 2 - (16 * 2 + 2)
        require(required_host_rank == 4, "Changed analytical host rank floor")
        quote = read(raw_quote)
        got = read(stage("RESULT.json", HERE / "engines/host_rank.py", work))
        require(got["head"] == quote["head"] == HEAD and got["caller_sha256"] == CALLER
                and got["price_sha256"] == sha256(raw_quote).hexdigest(), "Changed comparison or price")
        require(quote["one_pair_optimistic_gross"] == 192 and quote["disjoint_two_pair_optimistic_gross"] == 384
                and quote["one_pair_price"]["paid_delta"] == {"1": -192}
                and not quote["one_pair_price"]["target_delta"], "Changed complete stock")
        require(len(got["tested"]) == len(quote["keys"]) == 102 and not got["unvisited"] and not got["survivors"]
                and got["phase_values"] == [1, -1] and got["body"] == "all one"
                and got["field_prime"] == PRIME and len(got["controls"]) == 2, "Incomplete signed host screen")
        for case, key in zip(got["tested"], quote["keys"], strict=True):
            witness = case["witness"]
            require(case["key"] == key and case["decision"] == "rank at least three"
                    and all(len(set(witness[k])) == 3 for k in ("row_keys", "column_keys")),
                    "Changed case or minor coordinates")
            exact = determinant3(witness["minor"])
            require(exact != 0 and exact == witness["determinant_mod_prime"], "Changed exact minor")
        materialized.write_bytes(caller + b"\n")
        negative = run([executable, "-I", "-B", str(HERE / "engines/host_rank.py"), str(work)],
                       cwd=work, capture_output=True, timeout=22)
        require(negative.returncode != 0 and b"changed dependency: 7113-CALLER.json" in negative.stderr
                and not negative.stdout, "Changed caller was accepted")
    print("PASS_PAIRED_QUERY_HOST_BOUND cases=102 excluded=102 unresolved=0 host_rank_floor=4 kappa_change=0")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.out:
        replay(args.out.resolve())
    else:
        with TemporaryDirectory(prefix="paired-query-host-receipts-") as tmp:
            replay(Path(tmp) / "out")


if __name__ == "__main__":
    main()
