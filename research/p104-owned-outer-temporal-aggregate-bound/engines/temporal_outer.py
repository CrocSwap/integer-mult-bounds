"""Exact input-244 impulse over both outer banks of the owned two-write pair."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from signal import SIGALRM,alarm,signal
from time import monotonic

ROOT=Path(__file__).resolve().parent
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER="07a76c5e2738882c0cb322278e56f6cae3c9885d"
PINS={
    "inputs/PLAN.md":"33ae20a2ff97879168287fe72badb5f921944012fa2d1d7026b5f08dedcbb001",
    "inputs/R122-PRICE.json":"08a403b6c8d5a3332212042ec69624ab5cf343fb7b6aa6e94f42583653f77912",
    "inputs/R122-RESULT.json":"6d040aae3e99a8261152c17965b692b964d18ed7139c7a003da50934ec8d2098",
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PAYLOAD="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
U,V,H=41996,44242,1531
A,B,C=594,117,534
LIFETIME=[32607,44247]
WRITES=[[41997,["ADD",H,1291,"-2",B]],[44241,["ADD",H,732,"-1",B]]]
EVENTS, BANK_CUTS, SECONDS=76466,4494,20
AXIS=244
ZERO=Q(0)


def unique(items):
    out=dict(items)
    if len(out)!=len(items):
        raise ValueError("duplicate JSON key")
    return out


def checked(root,name):
    raw=(root/name).read_bytes()
    if sha256(raw).hexdigest()!=PINS[name]:
        raise ValueError("changed dependency "+name)
    return raw


def quote(root):
    checked(root,"inputs/PLAN.md")
    p,w=[loads(checked(root,f"inputs/R122-{key}.json"),object_pairs_hook=unique)
         for key in ("PRICE","RESULT")]
    assert (p["head"],p["caller"])==(w["head"],w["caller"])==(HEAD,CALLER)
    assert p["word_sha256"]==PINS["inputs/7334-WORD.json.gz"]
    assert p["row"]["key"]==[U,V,H] and p["row"]["charts"]==[A,B,C]
    assert p["row"]["lifetime"]==LIFETIME and p["row"]["paid_ranks"]==[4,1]
    assert p["paid_delta"]=={"1":-17,"4":-17,"5":17}
    assert (p["paid"],p["productive"],p["surplus"],p["compatible_edits"])==(110502,22461,1424,1)
    assert p["bank_cuts"]==[[U,A],[V,C]] and w["old_adds"]==WRITES and not w["unvisited"]
    assert all(r["witness"]==[AXIS,"-1/2"] for r in w["results"])
    assert w["aggregate"][str(AXIS)]=="-1/2"
    assert Q(p["complete_probe_margin"][0])>0>Q(p["complete_fixed_target_upper"])
    assert Q(p["extra_rank_one_upper"])<0
    keys=("paid_delta","paid","productive","surplus","gain_at_old_crossing","complete_probe_margin",
          "complete_fixed_target_upper","extra_rank_one_upper","compatible_edits")
    return {"head":HEAD,"caller":CALLER,"pins":PINS,**{k:p[k] for k in keys},
            "switches":{"early":U,"late":V},"inclusive_cuts":[U,V],
            "bank_charts":[A,C],"owner":H,"input_axis":AXIS,
            "caps":{"events":EVENTS,"schedules":2,"bank_cuts":BANK_CUTS,"seconds":SECONDS}}


@cache
def q(s):
    return Q(s)


def legality(t,chart):
    if chart==A:
        return ["early pre-switch","late"] if t==U else (
            ["late pre-switch"] if t==V else ["late"])
    assert chart==C
    return ["early post-switch"] if t==U else (
        ["early","late post-switch"] if t==V else ["early"])


def contacts(event):
    return event[1:3] if event[0] in ("ADD","COPY") else event[1:2]


def coverage(t,chart,stock,values,born,n):
    live=sorted(stock[chart]-{H})
    return dict(legality=legality(t,chart),roles=live,
        owned_births=[[r,born[r]] for r in live if r>=n],
        nonzero=[[r,str(values[r])] for r in live if values[r]])


def controls():
    assert legality(U,A)==["early pre-switch","late"]
    assert legality(U,C)==["early post-switch"]
    assert legality(V,A)==["late pre-switch"]
    assert legality(V,C)==["early","late post-switch"]
    data=coverage(U,A,{A:{1,4,H}},[ZERO,Q(-1,2),ZERO,ZERO,ZERO],{4:0},3)
    assert data["roles"]==[1,4] and data["nonzero"]==[[1,"-1/2"]]
    assert data["owned_births"]==[[4,0]]
    assert -2*Q(1,2)-Q(-1,2)==Q(-1,2)
    return ["within-clock schedule boundary","read-only owner exclusion","signed nonzero donor retained",
            "old signed source sum"]


def validate_window(tape,frames,n):
    assert H>=n and tape[U]==["MOVE",H,A,B,True] and tape[V]==["MOVE",H,B,C,True]
    assert tape[LIFETIME[0]][:2]==["INIT",H] and tape[LIFETIME[1]][:2]==["CLEAR",H]
    assert [[t,tape[t]] for t in range(U+1,V) if H in contacts(tape[t])]==WRITES
    assert not [t for t in range(LIFETIME[0]+1,LIFETIME[1]) if tape[t][:2] in (["INIT",H],["CLEAR",H])]
    sets=[]
    for chart in (A,B,C):
        stock={0}
        for v in frames[chart]:
            assert v not in stock
            stock|={u^v for u in stock}
        sets.append(stock)
    assert sets[0]<sets[1]<sets[2] and [len(frames[x]) for x in (A,B,C)]==[1,5,6]


def sweep(word,deadline,out):
    n,m,tape=(word[k] for k in ("public","owned_fields","program"))
    assert (n,m,len(tape))==(1501,68,EVENTS)
    validate_window(tape,word["frames"],n)
    state=word["initial"]+[None]*m
    stock=defaultdict(set)
    for role,chart in enumerate(state):
        if chart is not None:
            stock[chart].add(role)
    values=[Q(i==AXIS) for i in range(n+m)]
    born={}
    fresh=set()
    changes=Counter()
    banks={A:[],C:[]}
    out["aliases"]=banks
    watched=dict(WRITES)
    old_sources=[]
    diag=None

    def change(role,before,after):
        assert state[role]==before
        if before is not None:
            stock[before].remove(role)
        if after is not None:
            stock[after].add(role)
        state[role]=after

    for t,event in enumerate(tape):
        out["first_unvisited_event"]=t
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError("forward impulse")
        if U<=t<=V:
            if t==U:
                diag=values[H]
            for chart in (A,C):
                data=coverage(t,chart,stock,values,born,n)
                entries=banks[chart]
                if entries and entries[-1]["epoch"]==changes[chart] and entries[-1]["legality"]==data["legality"]:
                    entry=entries[-1]
                    assert entry["last"]==t-1 and all(entry[k]==v for k,v in data.items())
                    entry["last"]=t
                else:
                    entries.append(dict(first=t,last=t,epoch=changes[chart],**data))
                out["bank_cuts"]+=1
                out["donor_incidences"]+=len(data["roles"])
        if t in watched:
            assert event==watched[t]
            src,coefficient=event[2:4]
            old_sources.append([t,src,coefficient,str(values[src]),str(q(coefficient)*values[src])])
        op,d,*a=event
        touch=[r for r in contacts(event) if r!=H]
        before={state[r] for r in touch}
        if op=="MOVE":
            old,new,owned=a
            assert owned==(d>=n)
            change(d,old,new)
            fresh.discard(d)
        elif op=="INIT":
            assert d>=n and d not in born
            change(d,None,a[0])
            values[d]=ZERO
            born[d]=t
            fresh.add(d)
        elif op=="CLEAR":
            assert d>=n
            change(d,a[0],None)
            values[d]=ZERO
            del born[d]
            fresh.discard(d)
        elif op=="SCALE":
            assert state[d]==a[-1]
            values[d]*=q(a[0])
            fresh.discard(d)
        else:
            s,coefficient,chart=a
            assert op in ("ADD","COPY") and d!=s and state[d]==state[s]==chart
            assert op!="COPY" or d>=n and d in fresh and values[d]==0
            values[d]=(values[d] if op=="ADD" else ZERO)+q(coefficient)*values[s]
            fresh.discard(d)
        if U<=t<V:
            after={state[r] for r in touch}
            for chart in (before|after)&{A,C}:
                changes[chart]+=1
        out["events"]+=1
    assert state==word["final"]+[None]*m and not born and not fresh
    assert out["bank_cuts"]==BANK_CUTS
    assert all(sum(row["last"]-row["first"]+1 for row in banks[c])==V-U+1 for c in (A,C))
    assert diag==0 and sum(q(row[-1]) for row in old_sources)==Q(-1,2)
    out["first_unvisited_event"]=None
    out["owner_diagonal"]=[U,str(diag)]
    out["old_source_responses"]=old_sources
    out["aggregate_response"]="-1/2"
    out["unresolved"]=[
        [chart,r["first"],r["last"],r["legality"]]
        for chart in (A,C) for r in banks[chart] if r["nonzero"]]
    out["status"]="support unresolved" if out["unresolved"] else "both schedules excluded"


def main():
    assert __debug__
    cli=ArgumentParser(description=__doc__)
    cli.add_argument("--root",type=Path,default=ROOT)
    modes=cli.add_mutually_exclusive_group()
    modes.add_argument("--price-only",action="store_true")
    modes.add_argument("--controls-only",action="store_true")
    args=cli.parse_args()
    tests=controls()
    price=quote(args.root)
    expected=(dumps(price,indent=2,sort_keys=True)+"\n").encode()
    if args.price_only:
        print(expected.decode(),end="")
        return
    if args.controls_only:
        print(dumps(tests))
        return
    assert (args.root/"PRICE.json").read_bytes()==expected
    result=dict(head=HEAD,caller=CALLER,price_sha256=sha256(expected).hexdigest(),
        pins=PINS,controls=tests,caps=price["caps"],events=0,bank_cuts=0,donor_incidences=0,
        first_unvisited_event=0)

    def stop(*_):
        raise TimeoutError("20-second hard cap")

    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline=monotonic()+SECONDS-1
    try:
        raw=decompress(checked(args.root,"inputs/7334-WORD.json.gz"))
        assert sha256(raw).hexdigest()==PAYLOAD
        sweep(loads(raw,object_pairs_hook=unique),deadline,result)
    except TimeoutError as e:
        result.update(status="cap reached",reason=str(e),unresolved="unvisited and nonzero bank cuts")
    finally:
        alarm(0)
    print(dumps(result,indent=2,sort_keys=True))
    if result["status"]=="cap reached":
        raise SystemExit(2)


if __name__=="__main__":
    main()
