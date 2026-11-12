"""Independently reconstruct the one-port paid quote and literal J1 phase obstruction."""
from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
NATIVE_PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PINS = {
    "inputs/WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/CALLER.json":"255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/independent.py":"21f46a8340331abb1486b50bd4e04453f1968b0a5950d86ff7780dd368590874",
    "inputs/upstream_application.py":"d98987db98553dc55bfc80e3ca47abfcd51c57af6f8cda61101391d8eae94184",
    "inputs/check_odd_physical_binding.py":"5c80c3b0415a7f91d216395248dd6f13297eed637732098e1ca8fb0548951b98",
}


def unique(items):
    result = dict(items)
    assert len(result) == len(items), "Duplicate JSON key"
    return result


def timeout(*_):
    raise TimeoutError("15-second R170 cap")


def eye(n):
    return [[Q(r == s) for s in range(n)] for r in range(n)]


def minus(a,b):
    return [[x-y for x,y in zip(ar,br)] for ar,br in zip(a,b)]


def mul(a,b):
    return [[sum(x*y for x,y in zip(ar,col)) for col in zip(*b)] for ar in a]


def inv2(m):
    (a,b),(c,d) = m
    det = a*d-b*c
    assert det != 0
    return [[d/det,-b/det],[-c/det,a/det]]


def relative(pair):
    return mul(inv2(pair[1]), pair[-1])


def block(a,b):
    return [row+[Q(0),Q(0)] for row in a]+[[Q(0),Q(0)]+row for row in b]


def scalar(q):
    return str(Q(q))


def signed_contact(w,c,clock,e,sources):
    assert clock == 43 and e == ["J",1,[1,0,18,19],[36,37,"-1","1/2"]]
    A,B = c["types"]["A"],c["types"]["B"]
    native = w["hosted"]
    a,b,a2,b2 = [Q(native[k]) for k in ("alpha","beta","alpha2","beta2")]
    assert (a,b,a2,b2) == (-1,Q(1,2),-1,0)
    assert list(map(Q,e[3][2:])) == [a,b] and (Q(A["alpha2"]),Q(A["beta2"])) == (a2,b2)
    assert len(set(e[2]))==4 and all(A["offset"]<=x<A["offset"]+A["roles"] for x in e[2])
    assert len(set(e[3][:2]))==2 and all(B["offset"]<=x<B["offset"]+B["roles"] for x in e[3][:2])

    # Independently use the two physical native endpoint operations in the
    # authenticated reference: first y += Q^-1 x, second x += alpha2 Q y;
    # B applies x += alpha Q y then y += beta Q^-1 x on the updated x.
    native_source = sources["inputs/independent.py"].decode()
    physical_source = sources["inputs/upstream_application.py"].decode()
    for token in ("padd(rows[y],rows[x],q=-1)", "padd(rows[u],rows[v]",
                  "padd(rs,rows[t],(al,F(0)),q=1)", "padd(rt,rows[s],(be,F(0)),q=-1)"):
        assert token in native_source
    for token in ("second plane identical boundary frames", "injective native inputs",
                  "fresh helper input", "all four contact operators"):
        assert token in physical_source

    p = min(B["ports"])
    assert p==15 and p not in native["Dports"]
    r,s = w["live"][p],w["live"][p]+112
    assert (r,s,w["ports"][p])==(17,129,81)
    charts = [[w["initial"][j],w["final"][j]] for j in (r,s)]
    assert charts==[[16,127],[3,143]]
    assert w["frames"][charts[0][0]]==[81] and w["frames"][charts[1][0]]==[]
    assert w["frames"][charts[0][1]]==[1<<i for i in range(9)]
    assert len(w["frames"][charts[1][1]])==8 and all((u&81).bit_count()%2==0 for u in w["frames"][143])
    assert r not in native["X2"]+native["Y2"] and s not in native["X2"]+native["Y2"]

    bm,am1,am2 = {},{},{}
    for q in (Q(1),Q(-1)):
        bm[q] = mul([[Q(1),Q(0)],[b/q,Q(1)]], [[Q(1),a*q],[Q(0),Q(1)]])
        am1[q] = [[Q(1),Q(0)],[1/q,Q(1)]]
        am2[q] = [[Q(1),a2*q],[Q(0),Q(1)]]
    rb = relative(bm)
    ra = block(relative(am1),relative(am2))
    assert rb==[[0,1],[-1,0]]
    assert mul(rb,rb)==[[-1,0],[0,-1]] and mul(mul(rb,rb),mul(rb,rb))==eye(2)
    db,da = minus(rb,eye(2)),minus(ra,eye(4))
    sb,sa = mul(db,db),mul(da,da)
    assert sb==[[0,-2],[2,0]] and sa==[[0]*4 for _ in range(4)] and da!=[[0]*4 for _ in range(4)]
    # An uncoupled identity block cannot hide the B summand. Even allowing
    # an arbitrary invertible signed direct-sum helper leaves the B block
    # in (R-I)^2 unchanged, so its other block cannot cancel this witness.
    assert mul(minus(block(rb,eye(2)),eye(4)),minus(block(rb,eye(2)),eye(4)))==block(sb,[[0,0],[0,0]])
    return {"port_index":p,"q_axis":w["ports"][p],"native_main_slots":[r,s],
            "native_main_chart_pairs":charts,"caller_J_clock":clock,"stage":1,
            "A_caller_roles":e[2],"B_caller_roles":e[3][:2],"specialized_phases":[1,-1],
            "B_relative":rb,"A_relative":ra,"B_relative_minus_I_squared":sb,"A_relative_minus_I_squared":sa,
            "scope":"One literal native slot at unit body. Phase-even left and right invertible wrappers have identical normalized actions at q=±1. Any other helper action is uncoupled from the original B main pair inside the slot."}


def price(w,c,base):
    n = w["public"]
    rank = [len(basis) for basis in w["frames"]]
    first = set(w["live"])|{r+112 for r in w["live"]}
    second = set(w["hosted"]["X2"])|set(w["hosted"]["Y2"])
    assert n==1501 and len(first)==208 and len(second)==192 and not first&second
    helpers = set(range(n))-first-second
    assert len(helpers)==1101
    helper = Counter(rank[w["final"][r]]-rank[w["initial"][r]] for r in helpers)
    assert min(helper)==1 and helper[1]==18
    A,B = c["types"]["A"],c["types"]["B"]
    assert A["ports"]==w["hosted"]["Dports"] and B["ports"]==sorted(set(range(104))-set(A["ports"]))
    assert (len(A["ports"]),len(B["ports"]))==(96,8)
    native = Counter(abs(rank[e[3]]-rank[e[2]]) for e in w["program"] if e[0]=="MOVE")
    assert min(native)==1 and native.total()==6279
    per_paid = {kind:Counter() for kind in ("A","B")}
    calls = []
    for i,e in enumerate(c["events"]):
        if e[0]=="J":
            calls.append((i,e))
        elif e[1]=="QUERY":
            per_paid[e[0]][1] += 1
        elif e[1] in ("IDLE_ONE","IDLE_ODD"):
            assert e[3] and len(set(e[3]))==len(e[3])
            per_paid[e[0]][8*len(e[3])+int(e[1]=="IDLE_ODD")] += 1
        else:
            assert e[1] in ("ADD","SWAP","SCALE","LAMBDA")
    assert [e[1] for _,e in calls]==list(range(1,18))
    per_target = {kind:Counter((r[0]%2)+8*sum(r[2:]) for r in desc["diagonal"]) for kind,desc in c["types"].items()}
    assert per_target["A"]==per_target["B"] and sum(per_target["A"].values())==36
    assert all(any(row[2:]) for ty in c["types"].values() for row in ty["diagonal"])
    paid,targets = [Counter({r:n*len(calls) for r,n in hist.items()}) for hist in (native,helper)]
    for kind,desc in c["types"].items():
        p = len(desc["ports"])
        paid.update({r:n*p for r,n in per_paid[kind].items()})
        targets.update({r:n*p for r,n in per_target[kind].items()})
    for key,hist in (("old_paid",paid),("old_targets",targets)):
        assert hist==Counter({int(r):n for r,n in base[key].items()})
    old = targets.copy()
    old.subtract(paid)
    assert (paid.total(),targets.total(),sum(r*n for r,n in old.items()))==(110519,22461,1424)
    new_paid = per_paid["A"].copy()
    new_paid.subtract(per_paid["B"])
    new_paid = {r:n for r,n in new_paid.items() if n}
    # Two added independent main owners at each J displace at least two
    # positive helper jobs, with H1 exactly one. The rank-one allowance is
    # favorable and does not allocate legal new physical owner contracts.
    lost = 2*len(calls)
    assert lost==34 and helper[1]>=2*len(B["ports"])
    delta = Counter({r:-n for r,n in new_paid.items()})
    delta[1] -= lost
    cost = run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    quoted = {}
    for k in ("old_crossing_upper","probe","moonshot"):
        exponent = Q(base[k])
        gross = cost(delta,exponent)
        assert gross[0]>0
        cells = []
        for m in range(1,9):
            candidate = old.copy()
            candidate.update({r:n*m for r,n in delta.items()})
            complete = cost(candidate,exponent)
            cells.append(dict(ports=m,helper_rank_one_credits_lost=m*lost,
                              complete_margin=list(map(scalar,complete))))
        quoted[k] = dict(kappa=scalar(exponent),gain_upper=list(map(scalar,gross)),multiplicities=cells)
    return dict(per_port_paid=per_paid,per_port_target=per_target,native_paid=native,native_helpers=helper,
                native_word_paid=6279,native_public=1501,old_main_owners=400,old_independent_helpers=1101,
                paid_delta_per_port=new_paid,paid_total_after_one=paid.total()+sum(new_paid.values()),
                target_total_after_one=targets.total()-lost,optimistic_lost_rank_one_helpers_per_port=lost,
                quoted=quoted),calls[0]


def main():
    assert __debug__
    signal(SIGALRM,timeout)
    alarm(15)
    sources = {}
    for name,digest in PINS.items():
        raw = (ROOT/name).read_bytes()
        assert sha256(raw).hexdigest()==digest
        sources[name]=raw
    native = decompress(sources["inputs/WORD.json.gz"])
    assert sha256(native).hexdigest()==NATIVE_PAYLOAD
    w,c,base = [loads(raw,object_pairs_hook=unique) for raw in
                (native,sources["inputs/CALLER.json"],sources["inputs/R92-PRICE.json"])]
    assert base["head"]==HEAD and base["caller_head"]==CALLER
    assert len(w["program"])==76466 and len(c["events"])==4783
    bill,j = price(w,c,base)
    gate = signed_contact(w,c,*j,sources)
    alarm(0)
    print(dumps({"comparator":HEAD,"caller_head":CALLER,"native_payload":NATIVE_PAYLOAD,
                 "pins":PINS,"budget":{"native_words":1,"callers":1,"ports_scoped":1,
                                        "J_contacts":1,"phase_count":2,"seconds":15},
                 "price":bill,"signed_contact":gate,"result":"EXCLUDED_SAME_NATIVE_EVEN_WRAPPER_CONTACT"},
                default=scalar,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
