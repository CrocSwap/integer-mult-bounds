"""Rebuild both signed histograms from literal words and certify their separation."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path

OLD = "2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef"
NEW = "bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
TARIFF = "60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5"
SIGNED = "0b072ea1a1cfcb74ec48a6b9485eaa03b61b74d9f456a6a75177020e30cdf4e3"
CAP = Q(".00376669")
OLD_CLAIM = Q(".003647969120276")


def unique(pairs):
    record = dict(pairs)
    assert len(record) == len(pairs), "duplicate JSON key"
    return record


def read(path, digest=None, compressed=False):
    data = Path(path).read_bytes()
    if compressed:
        data = decompress(data)
    if digest:
        assert sha256(data).hexdigest() == digest, Path(path).name
    return json.loads(data, object_pairs_hook=unique)


def rank_span(frame):
    span = {0}
    for v in frame:
        assert v not in span and 0 < v < 512
        span |= {x ^ v for x in span}
    return span


def profile(word, caller):
    spans = list(map(rank_span, word["frames"]))
    dims = [len(f).bit_length() - 1 for f in spans]
    native = Counter()
    helper = Counter()
    charts = dict(enumerate(word["initial"]))
    public = set(charts)
    hosted = word["hosted"]
    mains = set(word["live"]) | {r + 112 for r in word["live"]} | set(hosted["X2"]) | set(hosted["Y2"])
    for role in public - mains:
        start, end = word["initial"][role], word["final"][role]
        assert spans[start] < spans[end]
        helper[dims[end] - dims[start]] += 1
    for op, role, *args in word["program"]:
        if op == "MOVE":
            before, after, owned = args
            assert charts[role] == before and owned == (role not in public)
            assert spans[before] < spans[after] or (owned and spans[after] < spans[before])
            native[abs(dims[after] - dims[before])] += 1
            charts[role] = after
        elif op == "INIT":
            assert role not in charts and role not in public
            charts[role] = args[0]
        elif op == "CLEAR":
            assert role not in public and charts.pop(role) == args[0]
        elif op == "SCALE":
            assert charts[role] == args[-1]
        else:
            assert op in {"ADD", "COPY"} and charts[role] == charts[args[0]] == args[-1]
    assert set(charts) == public and list(charts.values()) == word["final"]

    assert caller["types"]["A"]["ports"] == hosted["Dports"]
    assert set(caller["types"]["B"]["ports"]) == set(range(104)) - set(hosted["Dports"])
    productive, paid, stages = Counter(), Counter(), 0
    for e in caller["events"]:
        if e[0] == "J":
            stages += 1
            productive.update(helper)
            paid.update(native)
        else:
            op = e[1]
            ports = len(caller["types"][e[0]]["ports"])
            if op == "QUERY":
                paid[1] += ports
            elif op in ("IDLE_ONE", "IDLE_ODD"):
                paid[8*len(e[3]) + (op == "IDLE_ODD")] += ports
            else:
                assert op in {"ADD", "SCALE", "SWAP", "LAMBDA"}
    assert stages == caller["stages"] == 17
    empty = 0
    for ty in caller["types"].values():
        for sign, zero, *mask in ty["diagonal"]:
            assert zero == 0
            rank = sign % 2 + 8 * sum(mask)
            productive[rank] += len(ty["ports"])
            if not any(mask):
                empty += len(ty["ports"])
    surplus = sum(r * (productive[r] - paid[r]) for r in productive.keys() | paid.keys())
    return {"T": dict(productive), "P": dict(paid), "S": surplus, "empty_root_credits": empty}, native


def signed_hist(profile):
    return {r: profile["T"].get(r, 0) - profile["P"].get(r, 0)
            for r in profile["T"].keys() | profile["P"].keys()}


def descending(tariff, hist, cap=CAP):
    bounds = (0, 0)
    for rank, count in hist.items():
        log = tariff["log"](rank)
        power = tariff["power"](rank, cap if count > 0 else Q(0))
        bounds = tariff["add"](bounds, tariff["smul"](tariff["mul"](log, power), -count))
    assert bounds[1] < 0
    return tariff["show"](bounds)


def locate(tariff, hist, low, high, precision):
    moment = tariff["moment"]
    assert moment(hist, low)[0] > 0 > moment(hist, high)[1]
    while high - low > precision:
        mid = (low + high) / 2
        m = moment(hist, mid)
        if m[0] > 0:
            low = mid
        elif m[1] < 0:
            high = mid
        else:
            raise AssertionError("directed sign unresolved")
    return low, high


def audit(args):
    old, new = read(args.old, OLD, True), read(args.new, NEW, True)
    caller = read(args.caller, CALLER)
    signed = read(args.signed, SIGNED)
    assert sha256(args.tariff.read_bytes()).hexdigest() == TARIFF
    tariff = run_path(str(args.tariff))
    span = old["program"][40950:40953]
    assert span == [["MOVE", 902, 618, 789, False], ["MOVE", 902, 789, 913, False], ["ADD", 985, 902, "-1", 913]]
    assert new == dict(old, program=old["program"][:40950] + [["MOVE", 902, 618, 913, False]] + old["program"][40952:])
    assert 902 in old["hosted"]["Y2"]
    before, prior_native = profile(old, caller)
    after, native = profile(new, caller)
    for key, value in before.items():
        expected = signed["price"]["after"][key]
        if type(value) is dict:
            expected = {int(k): v for k, v in expected.items()}
        assert value == expected, key
    assert before["T"] == after["T"] and before["S"] == after["S"] == 1424
    assert not before["empty_root_credits"] and not after["empty_root_credits"]
    paid = Counter(after["P"])
    paid.subtract(before["P"])
    assert {r:c for r,c in paid.items() if c} == {2:-34, 4:17}
    assert sum(after["P"].values()) == 110468 and sum(after["T"].values()) == 22461
    native_delta = native.copy()
    native_delta.subtract(prior_native)
    assert {r:c for r,c in native_delta.items() if c} == {2:-2, 4:1}
    old_hist, new_hist = signed_hist(before), signed_hist(after)
    old_lo, old_hi = map(Q, signed["price"]["gate"]["raw_bracket"])
    assert tariff["moment"](old_hist, old_lo)[0] > 0 > tariff["moment"](old_hist, old_hi)[1]
    assert tariff["moment"](new_hist, old_hi)[0] > 0
    search_low, search_high = locate(tariff, new_hist, old_hi, CAP, Q(1, 10**35))
    scale = 10**32
    ll = (search_low * scale).__floor__()
    hh = (search_high * scale).__ceil__()
    lo, hi = Q(ll, scale), Q(hh, scale)
    assert tariff["moment"](new_hist, lo)[0] > 0 > tariff["moment"](new_hist, hi)[1]
    # Mirror the inherited claim convention: greatest 15-digit-grid claim
    # with tested point claim + 7e-17 below the exact crossing.
    claim_limit = lo - Q(7,10**17)
    claim = Q((claim_limit*10**15).__floor__(), 10**15)
    tested = claim + Q(7,10**17)
    gate = tariff["gate"](after, claim, tested, lo, hi)
    assert claim > old_hi > old_lo > OLD_CLAIM
    assert tariff["moment"](old_hist, claim)[1] < 0
    fixed = Counter({r: 17 * count for r, count in native.items()})
    remainder = Counter(after["P"])
    remainder.subtract(fixed)
    assert min(remainder.values()) >= 0 and max(remainder) <= 145
    mass = sum(r*c for r,c in remainder.items())
    assert mass == 109088
    relaxed = Counter(after["T"])
    relaxed.subtract(fixed)
    relaxed[145] -= Q(mass,145)
    end = Q(1,32)
    ceiling_derivative = descending(tariff, relaxed, end)
    ceiling = locate(tariff, relaxed, claim, end, Q(1,10**12))
    return {
        "status": "PASS_ROLE902_INDEPENDENT_DIRECTED_RECURRENCE",
        "inputs": {"old_word_canonical": OLD, "new_word_canonical": NEW, "caller": CALLER,
                   "interval_tariff": TARIFF, "prior_signed_receipt": SIGNED},
        "before": before, "after": after,
        "strict_old_raw_crossing": [str(old_lo), str(old_hi)],
        "strict_new_raw_crossing": [str(lo), str(hi)],
        "strict_new_raw_crossing_decimal": [f".{ll:032d}", f".{hh:032d}"],
        "old_raw_crossing_rejects_new_claim": True,
        "old_margin_at_new_claim": tariff["show"](tariff["moment"](old_hist, claim)),
        "new_margin_at_old_upper": tariff["show"](tariff["moment"](new_hist, old_hi)),
        "derivative_old": descending(tariff, old_hist),
        "derivative_new": descending(tariff, new_hist),
        "claim": str(claim), "tested": str(tested),
        "claim_decimal": f".{int(claim*10**15):015d}",
        "gain": str(claim - OLD_CLAIM), "percentage_gain": str(100 * (claim - OLD_CLAIM)/OLD_CLAIM),
        "headroom": {"ambient_cap": 145, "remainder_rank_mass": mass,
                     "raw_ceiling": list(map(str, ceiling)), "derivative": ceiling_derivative},
        "gate": gate,
    }


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    for name in ("old", "new", "caller", "signed", "tariff"):
        parser.add_argument(name,type=Path)
    print(json.dumps(audit(parser.parse_args()), indent=2, sort_keys=True))
