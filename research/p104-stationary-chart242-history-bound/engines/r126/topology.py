"""Reverse literal public-bank census after the chart-242 maximal cut."""
from argparse import ArgumentParser
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
WORD = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PRICE = "plan/PRICE.json"
NATIVE = "inputs/7334-WORD.json.gz"


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def authenticate(root, path, digest, zipped=False):
    raw = (root / path).read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise ValueError(f"changed dependency {path}")
    if zipped:
        raw = decompress(raw)
        assert sha256(raw).hexdigest() == PAYLOAD
    return loads(raw, object_pairs_hook=unique)


def abort(*_):
    raise TimeoutError("hard topology cap")


def census(word, chart, maximum, deadline):
    tape = word["program"]
    n, owned = word["public"], word["owned_fields"]
    state = word["final"][:] + [None] * owned
    residents = {r for r, c in enumerate(state) if c == chart}
    public_bank = {r for r in residents if r < n}
    final_public, final_owned = sorted(public_bank), sorted(residents - public_bank)
    waiting, copy_audit = {}, []
    contacts, generators, gates = [], [], {}
    typed_cuts = len(public_bank)
    suffix_events = len(tape) - maximum

    @cache
    def span(frame):
        result = {0}
        for value in word["frames"][frame]:
            assert value not in result
            result |= {value ^ x for x in result}
        return result

    for t in range(len(tape) - 1, -1, -1):
        if t % 128 == 0 and monotonic() >= deadline:
            raise TimeoutError(f"reverse cap before event {t}")
        op, dst, *args = tape[t]
        after = state[dst]
        if dst in waiting:
            assert op == "INIT" and after == waiting[dst]["chart"], ("nonfresh owned COPY", waiting[dst], t)
            row = waiting.pop(dst)
            copy_audit.append(row | {"preceding_write": t})
        if op == "MOVE":
            before, new, flag = args
            assert after == new and flag == (dst >= n)
        elif op == "INIT":
            assert dst >= n and after == args[0]
            before = None
        elif op == "CLEAR":
            assert dst >= n and after is None
            before, = args
        else:
            before = after
            assert after == args[-1] and after is not None
            assert op in ("ADD", "COPY", "SCALE")
            if op in ("ADD", "COPY"):
                src = args[0]
                assert dst != src and state[src] == after
            if op == "COPY":
                assert dst >= n
                waiting[dst] = {"clock": t, "destination": dst, "source": src, "chart": after}
        if t >= maximum and chart in (before, after):
            after_bank = sorted(public_bank)
            kind, generator = None, None
            if op == "MOVE":
                lo, hi = span(before), span(after)
                assert lo < hi or dst >= n and hi < lo
                if dst < n:
                    if after == chart:
                        kind, generator = "public ingress", (t+1, dst)
                    else:
                        kind = "public egress"
                else:
                    kind = "owned move"
            elif op in ("INIT", "CLEAR"):
                kind = "owned lifetime"
            else:
                assert Fraction(args[-2])
                if op in ("ADD", "COPY") and src < n <= dst:
                    kind, generator = f"public to owned {op}", (t+1, src)
                elif dst < n and (op == "SCALE" or src < n):
                    kind = "invertible public scalar"
                elif dst < n:
                    assert op == "ADD"
                    kind = "owned to public ADD"
                else:
                    kind = "owned scalar"
            if generator is not None:
                assert generator[1] in public_bank
                generators.append({"key": list(generator), "reason": kind})
        else:
            kind = None
        if before != after:
            if after == chart:
                residents.remove(dst)
                public_bank.discard(dst)
            if before == chart:
                residents.add(dst)
                if dst < n:
                    public_bank.add(dst)
        state[dst] = before
        if kind is not None:
            contacts.append({"clock": t, "event": tape[t], "kind": kind,
                             "public_before": sorted(public_bank), "public_after": after_bank})
        if t >= maximum:
            typed_cuts += len(public_bank)
        if t == maximum:
            gates = {"public": sorted(public_bank), "owned": sorted(residents-public_bank)}

    assert not waiting and state == word["initial"] + [None] * owned
    return {"maximal_cut": maximum, "maximal_inventory": gates, "tail_events": suffix_events,
            "final_cut": len(tape), "final_inventory": {"public": final_public, "owned": final_owned},
            "public_cut_role_pairs": typed_cuts, "contacts": contacts[::-1],
            "generators": generators[::-1], "copy_audit": copy_audit[::-1],
            "full_reverse_events": len(tape)}


def controls():
    stop = monotonic() + 5
    toy = {"frames": [[1], [1, 2], [1, 2, 4]], "public": 2, "owned_fields": 1,
           "initial": [1, 1], "final": [2, 1],
           "program": [["ADD", 1, 0, "1/2", 1], ["MOVE", 0, 1, 2, False]]}
    out = census(toy, 1, 0, stop)
    assert out["generators"] == [] and out["final_inventory"]["public"] == [1]
    toy = toy | {"initial": [0, 1], "final": [1, 1], "program": [
        ["MOVE", 0, 0, 1, False], ["INIT", 2, 1], ["COPY", 2, 0, "1", 1],
        ["ADD", 1, 2, "-1", 1], ["CLEAR", 2, 1]]}
    out = census(toy, 1, 0, stop)
    assert [row["key"] for row in out["generators"]] == [[1, 0], [3, 0]]
    assert out["copy_audit"] == [{"clock": 2, "destination": 2, "source": 0, "chart": 1, "preceding_write": 1}]
    bad = toy | {"program": toy["program"][:2] + [["ADD", 2, 1, "1", 1]] + toy["program"][2:]}
    try:
        census(bad, 1, 0, stop)
    except AssertionError as exc:
        assert exc.args[0][0] == "nonfresh owned COPY"
    else:
        raise AssertionError("dirty COPY accepted")
    return ["internal scalar and public egress preserve containment",
            "public ingress and fresh public-to-owned COPY create candidate generators",
            "reject an intervening write before COPY"]


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--price-sha256")
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    tested = controls()
    if args.controls_only:
        print(dumps(tested))
        return
    if not args.price_sha256 or len(args.price_sha256) != 64:
        parser.error("provide the frozen price SHA-256")
    started = monotonic()
    signal(SIGALRM, abort)
    alarm(20)
    price = authenticate(args.root, PRICE, args.price_sha256)
    assert (price["head"], price["caller"], price["word_sha256"]) == (HEAD, CALLER, WORD)
    assert price["limits"]["topology_seconds"] == 20 and price["limits"]["literal_events"] == 76466
    assert (price["maximal_cut"], price["retirement"]["chart"]) == (45472, 242)
    word = authenticate(args.root, NATIVE, WORD, zipped=True)
    assert (len(word["program"]), word["public"], word["owned_fields"]) == (76466, 1501, 68)
    result = census(word, 242, 45472, started + 18)
    assert result["maximal_inventory"] == {"public": price["maximal_bank"], "owned": []}
    alarm(0)
    print(dumps(result | {
        "head": HEAD, "caller": CALLER, "pins": {PRICE: args.price_sha256, NATIVE: WORD}, "controls": tested,
        "status": "new generators pending" if result["generators"] else "full suffix contained",
        "retirement_cut": price["retirement"]["cut"], "chart": 242,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
