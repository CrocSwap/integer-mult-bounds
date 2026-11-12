"""Price and check the full chart-local receiver reconstruction."""
from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import argv
from time import monotonic

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/R159-IMPULSE.json": "cbd68f70602a75234718642adf6dce528a1e8c4ce8ea043aca029c8fd8b1db38",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/aggregate.py": "8bf1b91d7fc0937305466686522f5fb3920c66c71830acfc94adde84ba4f49e1",
    "inputs/donor_span.py": "4d5306e2c0b7e91c79d22c82e8e760aed2c311979298c558e631975d4d1ae5b1",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
CUT, CHART, CARRIER, RECEIVER = 42651, 652, 930, 793


def read(name):
    raw = (ROOT/name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError(f"changed dependency {name}")
    return raw


def stop(*_):
    raise TimeoutError("20-second hard cap")


def price():
    base = loads(read("inputs/R92-PRICE.json"))
    read("inputs/pricing.py")
    cost = run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    p,t = (Counter({int(k):n for k,n in base[key].items()}) for key in ("old_paid","old_targets"))
    invoice = t.copy()
    invoice.subtract(p)
    assert (sum(p.values()),sum(t.values()),sum(r*n for r,n in invoice.items())) == (110519,22461,1424)
    delta = {1:17,2:17,4:17,7:-17}
    invoice.update(delta)
    quote = {k:list(map(str,cost(invoice,Q(base[k])))) for k in ("old_crossing_upper","probe","moonshot")}
    assert Q(quote["probe"][0]) > 0 and Q(quote["old_crossing_upper"][1]) < 1
    reserve = 17*(8*340+1000+64)
    assert reserve == 64328 and 782715464+reserve < 10**9
    return dict(pins=PINS,head=base["head"],caller=base["caller_head"],paid_after=110485,productive=22461,
                rank_surplus=1424,paid_delta={r:-n for r,n in delta.items()},complete=quote,
                ordinary_reserve=reserve,one_owned_slot_at_cut=True)


def main():
    assert __debug__ and argv[1:] in ([],["--price"])
    signal(SIGALRM, stop)
    alarm(20)
    deadline = monotonic()+20
    quote = price()
    if argv[1:]:
        print(dumps(quote,sort_keys=True,indent=2))
        return
    prior = loads(read("inputs/R159-IMPULSE.json"))
    assert (prior["carrier"],prior["receiver"],prior["donors"]) == ("-1","1/2",{"165":"0","586":"0"})
    word = loads(decompress(read("inputs/WORD.json.gz")))
    assert word["program"][CUT]==["ADD",793,930,"1/2",652]
    read("inputs/donor_span.py")
    read("inputs/aggregate.py")
    helper = run_path(str(ROOT/"inputs/donor_span.py"))
    alg = run_path(str(ROOT/"inputs/aggregate.py"))
    controls = alg["controls"](helper)
    banks, targets = helper["snapshot"](word,{CUT:{(CHART,RECEIVER)}},{CUT:{CARRIER,RECEIVER}},deadline)
    stock = banks[CUT,CHART,RECEIVER]
    carrier, receiver = targets[CUT,CARRIER], targets[CUT,RECEIVER]
    assert stock.pop(CARRIER)==carrier and sorted(stock)==[165,586]
    target = receiver.copy()
    helper["axpy"](target,carrier,Q(1,2))
    assert 930 not in target and target[893]==Q(1,2)
    assert all(893 not in row for row in stock.values())
    separation = alg["exact_span"](target,stock,deadline,helper)
    assert separation and separation["decision"]=="outside donor span"
    alarm(0)
    print(dumps(dict(price=quote,chart=CHART,cut=CUT,donor_roles=sorted(stock),coordinate=893,
                     target_coefficient="1/2",donor_coefficients=["0","0"],controls=controls,
                     exact=separation,scope=1,runner_seconds=20),sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
