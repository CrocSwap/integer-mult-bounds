"""Check the two-transfer route through chart 531, using only the pinned native graph."""
import gzip
from hashlib import sha256
import json
from pathlib import Path


def insert(basis, x):
    while x:
        n=x.bit_length()-1
        if n not in basis:
            basis[n]=x
            return
        x^=basis[n]


def remainder(basis, x):
    for n in sorted(basis, reverse=True):
        if x>>n & 1:
            x^=basis[n]
    return x


def main():
    path=Path(__file__).resolve().parent/"pinned"/"strong-bit.json.gz"
    data=path.read_bytes()
    assert sha256(data).hexdigest()=="74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326"
    src=json.loads(gzip.decompress(data))
    tape=src["program"]
    assert tape[8068:8076]==[
        ["INIT",2326,326],["ADD",2326,1855,326],["ADD",2326,1857,326],
        ["ADD",2326,2224,326],["MOVE",2326,326,531],["INIT",2327,326],
        ["ADD",2327,1855,326],["MOVE",2327,326,1]]
    assert [src["frames"][str(c)]["dim"] for c in (326,531,1)]==[6,7,8]
    def run(mode):
        return interpret(src, tape, mode)
    old=run("original")
    alt=run("changed")
    oracle=run("oracle")
    assert old["package_at_8075"]==alt["package_at_8075"]==oracle["package_at_8075"]
    assert old["first_state"]==oracle["first_state"]
    assert old["final"]==oracle["final"]
    assert old["clears"]==oracle["clears"] and len(old["clears"])==3433
    assert all(v==((1<<i)^((1<<(i-111)) if 111<=i<222 else 0))
               for i,v in old["final"].items())
    different=[i for i in old["first_state"][1] if old["first_state"][1][i]!=alt["first_state"][1][i]]
    assert different==[2326]
    assert old["first_state"][0]==alt["first_state"][0]
    errors=[i for i in range(630) if alt["final"][i]!=old["final"][i]]
    assert errors==[0,11,117,223,224,230,249,250,251]
    for row in alt["checks"].values():
        assert not row["residual_in_retained_history"]
    outgoing=list(old["contract_rows"])
    demand={}
    for row in outgoing: insert(demand,row)
    assert len(demand)==3
    receipts=[i for i,(op,d,*args) in enumerate(tape) if i<=10141 and op=="MOVE" and args[1]==531]
    assert receipts==[8072,8098] and 531 not in src["start"]
    report={"route_dimensions":[6,7,8],"preserved_receipt":2327,
            "displaced_owner":2326,"displaced_read_clocks":[10137,30079],
            "residual_input_support":[i for i in range(630) if alt["residual"]>>i&1],
            "checks":alt["checks"],"uncorrected_wrong_public_rows":errors,
            "only_wrong_owner_at_first_reader":different,"oracle_first_state_exact":True,
            "oracle_final_map_exact":True,"oracle_original_clear_values_preserved":3433,
            "early_hub_arrivals":receipts,"three_original_readout_demands_rank":len(demand)}
    print(json.dumps(report,indent=2))


def interpret(src, tape, mode):
    chart=dict(enumerate(src["start"]))
    vals={i:1<<i for i in chart}
    stock={}
    for i,c in chart.items():
        if c==531:
            insert(stock,vals[i])
    residual=None
    checks={}
    clears=[]
    contract=[]
    read_clocks=[i for i,(op,target,*args) in enumerate(tape) if
        i>8072 and op=="ADD" and args[0]==2326]
    assert read_clocks==[10137,30079]
    for i,row in enumerate(tape):
        if i==8068:
            residual=vals[1857]^vals[2224]
        if i==10137:
            if mode=="oracle":
                vals[2326]^=residual
                insert(stock,vals[2326])
            first_state=(chart.copy(),vals.copy())
        if i in (8075,10138,10141):
            contract.append(vals[row[1]])
        if i in read_clocks:
            live={}
            for owner,c in chart.items():
                if c==531 and owner!=2326:
                    insert(live,vals[owner])
            checks[i]={
                "residual_in_retained_history":remainder(stock,residual)==0,
                "residual_in_live_other_owners":remainder(live,residual)==0,
                "historical_rank":len(stock),"other_live_rank":len(live)}
        if mode!="original" and i in (8070,8071):
            continue
        if mode!="original":
            row={8073:["INIT",2327,531],8074:["ADD",2327,2326,531],
                 8075:["MOVE",2327,531,1]}.get(i,row)
        op,d,*args=row
        if op=="INIT":
            assert d not in chart
            chart[d],vals[d]=args[0],0
        elif op=="CLEAR":
            assert chart.pop(d)==args[0]
            clears.append((i,d,args[0],vals[d]))
            vals.pop(d)
        elif op=="ADD":
            a,c=args
            assert chart[a]==c==chart[d]
            vals[d]^=vals[a]
        elif op=="MOVE":
            a,b=args
            assert chart[d]==a
            chart[d]=b
        else:
            assert op=="SWAP"
            a,=args
            vals[a],vals[d]=vals[d],vals[a]
            chart[a],chart[d]=chart[d],chart[a]
            if chart[a]==531:
                insert(stock,vals[a])
        if chart.get(d)==531:
            insert(stock,vals[d])
        if i==8075:
            package_at_8075=vals[2327]
    assert chart==dict(enumerate(src["final"]))
    assert residual
    return {"checks":checks,"residual":residual,"first_state":first_state,"final":vals,
            "clears":clears,"package_at_8075":package_at_8075,"contract_rows":contract}


if __name__=="__main__":
    main()
