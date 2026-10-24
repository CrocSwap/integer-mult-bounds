#!/usr/bin/env python3
"""Check a single-code projected quarter turn with arbitrary complements."""

import hashlib
import importlib.util
import json
from fractions import Fraction as F
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("odd_stream_producer",HERE/"check_odd_width.py")
ops = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ops
spec.loader.exec_module(ops)


def layout(n,width):
    if width%2:
        return ops.layout(n,width)[:3]
    f = width//2
    bit = lambda i,j: n*width-1-(i*width+j)
    changes = [(bit(i,j),bit(i,j+f)) for i in range(n) for j in range(f)]
    return changes,{right:-1 for _,right in changes},0


def turn(x,y,n,width,power=0):
    changes,signs,pivot = layout(n,width)
    trace = []
    a,xd = ops.encode(ops.address_change(x,changes,1),signs,1,trace)
    b,yd = ops.encode(ops.address_change(y,changes,1),signs,1,trace)
    bit = ops.leaf_bit(pivot,signs) if width%2 else 0
    if power:
        a_new = [-v for v in ops.c_power(b,bit,1,-power)]
        b_new = ops.c_power(a,bit,1,power)
        trace.extend(a_new+b_new)
    else:
        b = [v+u for u,v in zip(a,b)]
        trace.extend(b)
        a = [u-v for u,v in zip(a,b)]
        trace.extend(a)
        b = [v+u for u,v in zip(a,b)]
        trace.extend(b)
        a_new,b_new = a,b
    xx = ops.address_change(ops.decode(a_new,xd,1,trace),changes,1)
    yy = ops.address_change(ops.decode(b_new,yd,1,trace),changes,1)
    return xx,yy,trace


def projector(values,n,width):
    changes,signs,_ = layout(n,width)
    a,details = ops.encode(ops.address_change(values,changes,1),signs,1,[])
    zero_details = [(bit,sign,[ops.ZERO]*len(detail)) for bit,sign,detail in details]
    return ops.address_change(ops.decode(a,zero_details,1,[]),changes,1)


def frame_action(values,n,width,power):
    result = list(values)
    for _ in range(power%4):
        result = ops.native_line(result,n,width,1)
        result = [ops.UNITS[(-(width//2))%4]*v for v in result]
    return result


def check_case(n,width,power):
    length = 1 << (n*width)
    for column in range(2*length):
        x = [ops.ONE if j==column else ops.ZERO for j in range(length)]
        y = [ops.ONE if j+length==column else ops.ZERO for j in range(length)]
        xx,yy,_ = turn(x,y,n,width,power)
        px,py = projector(x,n,width),projector(y,n,width)
        dpx = frame_action(px,n,width,power) if power else px
        dipy = frame_action(py,n,width,-power) if power else py
        ops.require(xx==[u-v-w for u,v,w in zip(x,px,dipy)],"source projected map")
        ops.require(yy==[u-v+w for u,v,w in zip(y,py,dpx)],"target projected map")
    x = [ops.G(F((7*j+2)%17-8,8),F((11*j+3)%19-9,8)) for j in range(length)]
    y = [ops.G(F((13*j+5)%23-11,8),F((17*j+1)%13-6,8)) for j in range(length)]
    old = x,y
    maximum = max(map(ops.magnitude,x+y))
    _,signs,_ = layout(n,width)
    grid = 1 << (3+len(signs)+int(bool(power)))
    for _ in range(4):
        x,y,trace = turn(x,y,n,width,power)
        ops.require(all((a*grid).denominator==1 for v in trace+x+y for a in (v.re,v.im)),
                    "single-code denominator grid")
    ops.require((x,y)==old,"quarter turn fourth power")
    _,_,trace = turn(*old,n,width,power)
    ops.require(max(map(ops.magnitude,trace))<=4*maximum,"two magnitude bits")
    return {"n":n,"tensor_width":width,"leaf_power":power,
            "complete_columns":2*length,"fractional_bits":len(signs)+int(bool(power))}


def main():
    cases = [check_case(*case) for case in ((2,2,0),(2,3,0),(2,3,1),(3,1,3))]
    result = {"status":"PASS_ONE_CODE_PROJECTED_TURN","cases":cases,
              "pins":{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                      for name in ("ONE-PASS-TURN.md","check_odd_width.py")},
              "scope":"Producer replay using the frozen code primitives. No independent review or supplier claim."}
    (HERE/"ONE-PASS-TURN.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(result["status"])


if __name__=="__main__":
    main()
