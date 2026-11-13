"""Align exact #7542 edits onto #7481 and validate the literal composite."""
from collections import Counter
from difflib import SequenceMatcher
from fractions import Fraction as Q
from gzip import compress, decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal
import sys

PINS = {
    "7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "7542-edits.json": "04404c0456d3d211beaae5464dedd50d3ae0bbb92bdccbc9b1777055409d1546",
    "7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
PEER_PINS = {
    "7542": "71f5acb0409daf208a865482f3349049dbd3251c",
    "7481": "89eaa9d8cae37c1540de98f2d29a3abaabb96a2b",
    "7334": "aaeec8c0acf01e99a5f331ef363a698d9c084ace",
    "7113": "07a76c5e2738882c0cb322278e56f6cae3c9885d",
}
HERE = Path(__file__).resolve().parent


def sha(raw):
    return sha256(raw).hexdigest()


def load_pinned(path):
    raw = path.read_bytes()
    assert sha(raw) == PINS[path.name], path.name
    return raw


def unique_pairs(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs)
    return result


def loads(raw):
    return json.loads(raw, object_pairs_hook=unique_pairs)


def span(basis):
    values = {0}
    for value in basis:
        assert value not in values
        values |= {value ^ item for item in values}
    return values


def touched(events):
    return {e[1] for e in events} | {e[2] for e in events if e[0] in ("ADD", "COPY")}


def inventory(word):
    spaces = [span(chart) for chart in word["frames"]]
    public = word["public"]
    chart = dict(enumerate(word["initial"]))
    owned = {}
    life = []
    paid = Counter()
    peak = 0
    for clock, (op, role, *args) in enumerate(word["program"]):
        if op == "INIT":
            assert role >= public and role not in chart, (clock, role)
            chart[role] = args[0]
            owned[role] = (clock, args[0])
            peak = max(peak, len(owned))
        elif op == "CLEAR":
            assert role in owned and chart.pop(role) == args[0], (clock, role)
            start, frame = owned.pop(role)
            life.append((role, start, clock, frame, args[0]))
        elif op == "MOVE":
            low, high, owned_flag = args
            assert chart[role] == low and bool(owned_flag) == (role in owned), (clock, role)
            nested = spaces[low] < spaces[high] if not owned_flag else (
                spaces[low] < spaces[high] or spaces[high] < spaces[low]
            )
            assert nested, (clock, role, low, high)
            paid[abs(len(word["frames"][low])-len(word["frames"][high]))] += 1
            chart[role] = high
        elif op in ("ADD", "COPY"):
            assert args[0] != role and chart[role] == chart[args[0]] == args[2], (clock, role)
        else:
            assert op == "SCALE" and chart[role] == args[1], (clock, role)
    assert not owned and chart == dict(enumerate(word["final"]))
    return paid, life, peak


def main():
    assert __debug__ and sys.version_info[:2] == (3,12)
    root, output = map(Path, sys.argv[1:])
    def cap(_sig, _frame):
        print('{"status":"UNRESOLVED_CAP","cap_seconds":30}', flush=True)
        raise SystemExit(124)
    signal.signal(signal.SIGALRM, cap)
    signal.alarm(30)
    raw = {name:load_pinned((HERE if name.startswith(("7334","7542")) else root)/name) for name in PINS}
    base = loads(decompress(raw["7334-WORD.json.gz"]))
    entire = decompress(raw["7481-WORD.json.gz"])
    incumbent = loads(entire)
    app = loads(raw["7481-APPLICATION.json"])
    caller = loads(raw["7113-CALLER.json"])
    peer = loads(raw["7542-edits.json"])
    assert sha(entire) == app["candidate_canonical_sha256"]
    assert app["caller_head"] == PEER_PINS["7113"] and caller["stages"] == 17
    before, after = base["program"], incumbent["program"]
    assert len(before) == peer["base_events"] == 76466 and len(after) == 76475
    assert {k:v for k,v in base.items() if k!="program"} == {k:v for k,v in incumbent.items() if k!="program"}

    anchors = {}
    incumbent_mutated = set()
    for tag, a, b, c, d in SequenceMatcher(a=list(map(tuple,before)), b=list(map(tuple,after)),
                                           autojunk=False).get_opcodes():
        if tag == "equal":
            anchors.update(zip(range(a,b),range(c,d),strict=True))
        else:
            incumbent_mutated.update(touched(before[a:b]+after[c:d]))
    deleted, inserts = dict(peer["delete"]), dict(peer["insert_before"])
    assert len(deleted) == len(peer["delete"]) == 11 and len(inserts) == len(peer["insert_before"]) == 9
    peer_mutated = touched(list(deleted.values())+[x for group in inserts.values() for x in group]+peer["append"])
    assert not incumbent_mutated & peer_mutated
    relevant = {i:anchors[i] for i in sorted(deleted.keys() | inserts.keys())}
    assert all(a==b if a<33163 else a+9==b for a,b in relevant.items())
    assert all(before[i] == after[anchors[i]] == event for i,event in deleted.items())
    delete_new = {anchors[i] for i in deleted}
    insert_new = {anchors[i]:events for i,events in inserts.items()}
    program = []
    for i,event in enumerate(after):
        program.extend(insert_new.get(i,()))
        if i not in delete_new:
            program.append(event)
    program.extend(peer["append"])
    assert len(program) == 76491
    candidate = incumbent | {"program":program}

    old_paid,old_life,old_peak = inventory(incumbent)
    new_paid,new_life,new_peak = inventory(candidate)
    assert len(old_life) == len(new_life) == 74 and old_peak == new_peak == 50
    assert [entry[0::3] + (entry[4],) for entry in old_life] == [
        entry[0::3] + (entry[4],) for entry in new_life
    ]
    old_owned = [event for event in after if any(role>=1501 for role in touched([event]))]
    new_owned = [event for event in program if any(role>=1501 for role in touched([event]))]
    assert old_owned == new_owned
    delta = {r:new_paid[r]-old_paid[r] for r in sorted(old_paid.keys() | new_paid.keys())
             if new_paid[r]!=old_paid[r]}
    assert delta == {1:-2,5:-1,7:1} and sum(r*c for r,c in delta.items()) == 0
    signed = {r:17*c for r,c in delta.items()}
    lo,hi = map(Q,app["directed_crossing_bracket"])
    H = run_path(str(root/"pricing.py"))["power_bounds"]
    lower = upper = Q(0)
    for r,n in signed.items():
        if n<0:
            lower -= n*H(r,hi)[0]
            upper -= n*H(r,lo)[1]
        else:
            lower -= n*H(r,lo)[1]
            upper -= n*H(r,hi)[0]
    assert Q("0.34407309706774592") <= lower <= upper <= Q("0.34407309706774593")
    signed_hash = "e5c8d8c0cf4d3f3fc60ffe70eb084cf6c9eadf8e646c74b48762501bf5367474"
    peer_invoice_hash = "a642ac7f9a7faed3bcf071b8a2a4e061623e97904fbd7617e10bb3f259b4dc2d"
    signed_raw = (HERE/"7481-SIGNED-RESULT.json").read_bytes()
    peer_invoice_raw = (HERE/"7542-INVOICE.json").read_bytes()
    assert sha(signed_raw) == signed_hash == app["receipt_sha256"]["validation_signed/RESULT.json"]
    assert sha(peer_invoice_raw) == peer_invoice_hash
    old_invoice = loads(signed_raw)["checks"]["ODD-ADMISSION-PARTIAL.json"]["invoice"]
    peer_invoice = loads(peer_invoice_raw)
    peer_paid = {int(r):n for r,n in peer_invoice["paid"].items()}
    old_signed_paid = {int(r):n for r,n in old_invoice["P"].items()}
    signed_productive = {int(r):n for r,n in old_invoice["T"].items()}
    assert signed_productive == {int(r):n for r,n in peer_invoice["targets"].items()}
    combined_paid = Counter(old_signed_paid)
    combined_paid.update(signed)
    assert sum(combined_paid.values()) == 110485 and sum(signed_productive.values()) == 22461
    assert sum(r*(signed_productive.get(r,0)-combined_paid[r])
               for r in signed_productive.keys() | combined_paid.keys()) == 1424
    assert old_invoice["empty_root_credits"] == 0

    def margin(paid, k):
        bounds = [Q(0),Q(0)]
        for r in sorted(paid.keys() | signed_productive.keys()):
            coeff = signed_productive.get(r,0)-paid.get(r,0)
            if coeff:
                low,high = H(r,k)
                bounds[0] += min(coeff*low, coeff*high)
                bounds[1] += max(coeff*low, coeff*high)
        return bounds

    candidate_claim = Q("0.003647968255")
    peer_claim = Q("0.0036475398277")
    quote = margin(combined_paid,candidate_claim)
    old_quote = margin(old_signed_paid,candidate_claim)
    peer_quote = margin(peer_paid,candidate_claim)
    if not (quote[0] > 0 > peer_quote[1] and old_quote[1] < 0):
        candidate_claim = Q("0.00364796")
        quote = margin(combined_paid,candidate_claim)
        old_quote = margin(old_signed_paid,candidate_claim)
        peer_quote = margin(peer_paid,candidate_claim)
    assert quote[0] > 0 > peer_quote[1] and old_quote[1] < 0
    canonical = json.dumps(candidate,sort_keys=True,separators=(",",":")).encode()
    packed = compress(canonical,mtime=0)
    output.mkdir(parents=True,exist_ok=True)
    (output/"COMPOSED-WORD.json.gz").write_bytes(packed)
    record = dict(status="LITERAL_CHRONOLOGY_AND_PRICE_PASS", heads=PEER_PINS, pins=PINS, anchor_map=relevant,
                  overlap=sorted(incumbent_mutated & peer_mutated), peer_modified_roles=sorted(peer_mutated),
                  incumbent_modified_roles=sorted(incumbent_mutated), candidate_events=len(program),
                  canonical_sha256=sha(canonical), gzip_sha256=sha(packed), native_paid=dict(sorted(new_paid.items())),
                  paid_delta_native=delta, paid_delta_signed=signed, productive_delta_signed={},
                  quote_pins={"7481-SIGNED-RESULT.json":signed_hash,"7542-INVOICE.json":peer_invoice_hash},
                  tested_price_only_claim=candidate_claim, margin_composite=quote,
                  margin_7481=old_quote, margin_7542=peer_quote,
                  gain_over_peer_claim=candidate_claim-peer_claim,
                  ordinary_and_grid="unrecomputed", scientific_verification="unrun",
                  paid_positions=app["paid_calls"]+sum(signed.values()), owned_lifetimes=len(new_life), owned_peak=new_peak,
                  optimistic_gross_raw=[lower,upper], cap_seconds=30)
    text = json.dumps(record,sort_keys=True,default=str)
    (output/"COMPOSITION.json").write_text(text+"\n")
    print(text,flush=True)
    signal.alarm(0)


if __name__ == "__main__":
    main()
