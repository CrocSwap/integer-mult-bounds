"""Independent exact backward-row and integer-rank gate for the R71 stock."""
from collections import Counter
from fractions import Fraction
from functools import reduce
from hashlib import sha256
from math import gcd, lcm
from pathlib import Path
import argparse
import gzip
import json
from time import monotonic

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
WORD = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PRICE = "4a7841699dd17688f6aada5c902a2a91e94558b2b1b4460c46b0e55aa95b3f9f"
ADMISSION = "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13"
G68 = "ce9604444161b3532d02eb788cb3a24fbbdaf4c1354d596ac08a2c9edeb72c76"
G69 = "a2dd10737f5bfbd3818e6766df3890e445fd46f661af9521f5d724b7c56c1d45"
R70_LEAD = "34738b6d9031b3170a58f0cb590d81c01ea2c1038810008483d1c24dc7574150"
R70_INDEPENDENT = "dc227ae7aca5f470f148db76a32304ed21c6d4143af3a1d0e7cfd6947856edfb"
R71_LEAD = "ac659b807f526dfb79f9bb173c3861bc743f112a7f40bc42a8b5dc57f48a058d"
CASE_CAP = 43
TIME_CAP = 20


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def read(path, pin):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == pin, f"SHA-256 mismatch: {path.name}")
    return raw


def site_key(site):
    return (site["h"], *site["move_clocks"], site["clock"])


def backward(body, roles, output):
    values = {role: Fraction(role == output) for role in roles}
    for event in reversed(body):
        op, dst = event[:2]
        if op == "ADD":
            values[event[2]] += Fraction(event[3]) * values[dst]
        else:
            require(op == "SCALE", "not a normalized scalar event")
            values[dst] *= Fraction(event[2])
    return values


def integral(row):
    d = lcm(*(x.denominator for x in row))
    return [int(d * x) for x in row]


def rank(rational):
    matrix = [integral(row) for row in rational]
    if not matrix:
        return 0
    r = 0
    for c in reversed(range(len(matrix[0]))):
        choices = [i for i in range(r, len(matrix)) if matrix[i][c]]
        if not choices:
            continue
        i = min(choices, key=lambda i: abs(matrix[i][c]))
        matrix[r], matrix[i] = matrix[i], matrix[r]
        pivot = matrix[r][c]
        for i in range(r + 1, len(matrix)):
            a = matrix[i][c]
            if a:
                updated = [pivot * b - a * q for b, q in zip(matrix[i], matrix[r], strict=True)]
                content = reduce(gcd, updated, 0) or 1
                matrix[i] = [b // content for b in updated]
        r += 1
        if r == len(matrix):
            return r
    return r


def controls():
    q = Fraction
    donors = [(q(1, 3), q(2, 7), q(0)), (q(1, 3), q(-2, 7), q(0))]
    require(rank(donors) == rank(donors + [(q(2, 3), q(0), q(0))]) == 2,
            "true two-row combination rejected")
    require(rank(donors + [(q(2, 3), q(0), q(1, 13))]) == 3, "missing coordinate accepted")
    toy = [["SCALE", 3, "2", 1], ["ADD", 3, 5, "1/2", 1]]
    require(backward(toy, [3, 5], 3) == {3: q(2), 5: q(1, 2)}, "adjoint-order control")
    return ["two-donor rational combination", "extra exterior coordinate", "backward SCALE then ADD"]


def selected(receipt, which, status, sites):
    out = set()
    for row in receipt[which]:
        key = tuple(row["key"])
        site = sites[key[:4]]
        require(key[4] in site["low"], "key has no eligible low peer")
        if row["status"] == status and len(site["high"]) > 1:
            out.add(key[:5])
    return out


def main(args):
    control_pass = controls()
    admission = json.loads(read(args.admission, ADMISSION))
    require(admission["head"] == HEAD, "admission has wrong head")
    price = json.loads(read(args.price, PRICE))
    require(price["head"] == HEAD, "price has wrong head")
    geo = [json.loads(read(path, pin)) for path, pin in ((args.g68, G68), (args.g69, G69))]
    sites = {site_key(site): site for data in geo for site in data["survivors"]}
    require(len(sites) == sum(len(data["survivors"]) for data in geo) == 456, "wrong or duplicate geometry keys")
    prior_a = json.loads(read(args.r70_lead, R70_LEAD))
    prior_b = json.loads(read(args.r70_independent, R70_INDEPENDENT))
    require(not prior_a["unresolved"] and not prior_b["unvisited"], "R70 support was capped")
    left = selected(prior_a, "outcomes", "dirty return readout failed", sites)
    right = selected(prior_b, "decisions", "dirty_return_readout_failed", sites)
    target = json.loads(read(args.r71_lead, R71_LEAD))
    require(left == right == {tuple(row["key"]) for row in target["outcomes"]} and len(left) == CASE_CAP,
            "different exact R70/R71 key inventories")
    start = monotonic()
    word = json.loads(gzip.decompress(read(args.word, WORD)))["program"]
    verdicts = []
    keys = sorted(left)
    for key in keys:
        if len(verdicts) == CASE_CAP or monotonic() - start >= TIME_CAP:
            break
        h, _, _, _, p = key
        site = sites[key[:4]]
        high = set(site["high"])
        roles = site["roles"]
        body = [word[clock] for clock in site["block"]]
        require(all(e[-1] == site["chart_path"][1] for e in body), "literal coframe mismatch")
        matrix = {i: backward(body, roles, i) for i in roles}
        exterior = set(roles) - high - {h}
        nonzero = [i for i in sorted(exterior) if matrix[i][p]]
        lam = -matrix[nonzero[0]][h] / matrix[nonzero[0]][p] if nonzero else Fraction(0)
        require(all(matrix[i][h] + lam * matrix[i][p] == 0 for i in exterior),
                "conditioned key does not have exact forward support")
        columns = [i for i in roles if i != h]
        donor_rows = [tuple(matrix[i][j] for j in columns) for i in sorted(high)]
        readout = tuple(matrix[h][j] for j in columns)
        r0, r1 = rank(donor_rows), rank(donor_rows + [readout])
        require(r1 == r0 + 1, "found a dirty-readout survivor")
        verdicts.append({"key": key, "high": sorted(high), "lambda": str(lam),
                         "rank_high_exterior": r0, "rank_with_target": r1})
    lead_keys = [tuple(row["key"]) for row in target["outcomes"] if row["status"] == "exterior readout rank obstruction"]
    require([row["key"] for row in verdicts] == lead_keys[:len(verdicts)], "lead verdict does not match")
    print(json.dumps({
        "status": "EXHAUSTED" if len(verdicts) == len(keys) else "CAPPED",
        "head": HEAD, "inputs": {"word": WORD, "price": PRICE, "admission": ADMISSION,
        "r68_geometry": G68, "r69_geometry": G69, "r70_lead": R70_LEAD,
        "r70_independent": R70_INDEPENDENT, "r71_lead": R71_LEAD},
        "cap_keys": CASE_CAP, "cap_seconds": TIME_CAP, "controls": control_pass,
        "tested": len(verdicts), "rank_obstructions": verdicts,
        "rank_distribution": dict(Counter(str(row["rank_high_exterior"]) for row in verdicts)),
        "unvisited": keys[len(verdicts):],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    for name in ("admission", "price", "g68", "g69", "r70-lead", "r70-independent", "r71-lead", "word"):
        p.add_argument("--" + name, type=Path, required=True)
    main(p.parse_args())
