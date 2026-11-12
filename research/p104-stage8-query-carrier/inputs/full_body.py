"""Replay every basis column of the chosen correction over Gaussian Laurent polynomials."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import sys

DIRECT = "70de991b8443ed9d4f4455b9755743c6262379fd16adc68763048f5d34298fe3"
FIRST, SECOND = 1580, 1659
ZERO = (0,) * 17


def checked_code(path, digest):
    if sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError("changed direct predecessor")
    return run_path(str(path))


def term(stage_list=()):
    assert len(stage_list) == len(set(stage_list))
    return tuple(int(j in stage_list) for j in range(1,18))


def add_scaled(dst, src, scalar=Q(1), turn=0, exponent=ZERO):
    for (source_turn, powers), value in src.items():
        combined = (turn + source_turn) % 4
        new_powers = tuple(a+b for a,b in zip(powers,exponent))
        key = combined%2, new_powers
        new_value = dst.get(key,0) + value*scalar*(-1 if combined>=2 else 1)
        if new_value:
            dst[key] = new_value
        else:
            dst.pop(key,None)


def operators(caller, phase, replace):
    gates = []
    for clock in range(FIRST, SECOND+1):
        kind, op, *args = caller["events"][clock]
        if kind=="J":
            a,b,c,d = args[0]
            gates.extend([("ADD",b,a,Q(1),-phase,ZERO),("ADD",c,d,Q(-1),phase,ZERO)])
            gates.extend(("SCALE",r,r,Q(1),0,term((op,))) for r in (a,b,c,d))
        elif kind=="A":
            d,*params = args
            if op=="ADD":
                gates.append((op,d,params[0],Q(params[1]),0,ZERO))
            elif op=="QUERY":
                s,power=params
                if clock in (FIRST,SECOND):
                    assert (d,s,power)==(0,1,-1)
                gates.append(("ADD",d,s,Q(1),0 if replace and clock in (FIRST,SECOND) else phase*power,ZERO))
            elif op=="SWAP":
                gates.append((op,d,params[0],Q(1),0,ZERO))
            elif op=="SCALE":
                gates.append((op,d,d,Q(params[0]),0,ZERO))
            elif op=="LAMBDA":
                assert params[0] in (-1,1)
                gates.append(("SCALE",d,d,Q(1),params[0] if phase%2 else 0,ZERO))
            elif op in ("IDLE_ONE","IDLE_ODD"):
                gates.append(("SCALE",d,d,Q(1),phase*params[1] if op=="IDLE_ODD" else 0,term(params[0])))
            else:
                raise ValueError(op)
        else:
            assert kind=="B"
    return gates


def apply(gates, v, undo=False):
    for op,d,s,c,t,b in reversed(gates) if undo else gates:
        if op=="SWAP":
            v[d],v[s]=v[s],v[d]
        elif op=="ADD":
            assert d!=s
            add_scaled(v[d],v[s],-c if undo else c,t,b)
        else:
            assert op=="SCALE" and c
            new={}
            if undo:
                add_scaled(new,v[d],1/c,-t,tuple(-x for x in b))
            else:
                add_scaled(new,v[d],c,t,b)
            v[d]=new
    return v


def basis(j):
    return [{(0,ZERO):Q(1)} if r==j else {} for r in range(36)]


def predicted(j, phase, mut=False):
    v=basis(j)
    for i in range(36):
        u = -1 if i==0 else 2 if 2<=i<=8 else 1 if i==19 else 0
        if j==1:
            c,turn = u+(i==0),0
        elif j==18:
            c,turn = (-1 if not mut else 1)*u, (1 if phase%2 else 0)
        else:
            continue
        one={(0,ZERO):Q(1)}
        add_scaled(v[i],one,c,turn-phase)
        add_scaled(v[i],one,-c,turn)
    return v


def main():
    root=Path(sys.argv[1])
    p=checked_code(root/"lead/fixed_cut.py",DIRECT)
    price=p["checked"](root/"price/PRICE.json",p["PRICE"])
    caller=p["checked"](root/"price/inputs/7113-CALLER.json",p["CALLER"])
    assert price["head"]==p["HEAD"] and price["caller_sha256"]==p["CALLER"]
    counts=[]
    for phase in range(4):
        original,even=(operators(caller,phase,flag) for flag in (False,True))
        corrections=[]
        for j in range(36):
            original_col=apply(original,basis(j))
            actual=apply(even,[v.copy() for v in original_col],undo=True)
            assert actual==predicted(j,phase),(phase,j,actual)
            assert apply(even,[v.copy() for v in actual])==original_col
            if actual!=basis(j):
                corrections.append(j)
        assert corrections==([] if phase==0 else [1,18])
        if phase:
            assert predicted(18,phase,mut=True)!=predicted(18,phase)
        counts.append(dict(q_i_power=phase,columns=36,nonzero_correction_columns=corrections))
    print(json.dumps(dict(head=p["HEAD"],caller_sha256=p["CALLER"],price_sha256=p["PRICE"],
          fixed_cut=FIRST, later=SECOND, phase_checks=counts, independent_basis_columns=144,
          arbitrary_body_variables=17, unchanged_recovered_action=True, sign_control="passed"),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
