"""Reconstruct terminal shared divisors from the two pinned class datasets."""
from fractions import Fraction
from math import gcd,lcm,prod
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def require(ok,detail):
    if not ok:
        raise ValueError(detail)


def data(name):
    path=ROOT/"retained"/name
    for item in json.loads((ROOT/"SOURCE-PINS.json").read_text()):
        if item["local"]=="retained/"+name:
            require(hashlib.sha256(path.read_bytes()).hexdigest()==item["sha256"],"source pin")
            return json.loads(path.read_text())
    raise ValueError("unknown source")


def split(H):
    exponent=(H & -H).bit_length()-1
    return H>>exponent,exponent


def transformed():
    tbl=data("CLASS-ALGEBRA.json")
    schedule=data("SCHEDULE.json")
    classes=tbl["classes"]
    mass=sum(c["size"] for c in classes)
    bs=schedule["norm_optimal_dyadic_fraction_bits"]
    schedules={
      "schedule51":[Fraction(n,1<<bs) for n in schedule["norm_optimal_dyadic_numerators"]]+
                   [Fraction(*schedule["norm_optimal_final_reciprocal"])],
      "schedule52":[Fraction(n,1<<b) for n,b in schedule["dyadic_steps_numerator_and_fraction_bits"]]}
    packets=[]
    for row in tbl["characters"]:
        n,rem=divmod(sum(c["size"]*v*v for c,v in zip(classes,row,strict=True)),mass)
        require(not rem and row[0]%n==0,"character norm")
        eig=Fraction(sum(c["size"]*v*(-64)**c["fixed"] for c,v in zip(classes,row,strict=True)),
                     row[0]*16**12)
        packets.append((row,row[0]//n,eig))
    def inverse(values):
        H=lcm(*(v.denominator for v in values))
        coeff=[(v*H).numerator*d for v,(_,d,_) in zip(values,packets,strict=True)]
        return tuple(Fraction(sum(c*row[j] for c,(row,_,_) in zip(coeff,packets,strict=True)),H*mass)
                     for j in range(len(classes)))
    eigen=[e for _,_,e in packets]
    result={"canonical":[inverse([1/e for e in eigen])]}
    for name,steps in schedules.items():
        residual=[prod(1-h*e for h in steps) for e in eigen]
        correction=[(1-p)/e for p,e in zip(residual,eigen,strict=True)]
        result[name]=[inverse(residual),inverse(correction)]
    return result


def five(width,groups):
    odd=width%2
    sign=(-1)**((width+1)//4 if odd else width//4)
    t=sign*(1<<((width-(1 if odd else 2))//2))
    names=("Sp10",) if odd else (("Sp10","P5") if width%4==0 else ("O10+","O10-"))
    blocks=[]
    for name in names:
        g=groups[name]
        values=[sum(a*t**i for i,a in enumerate(p)) for p in g["polys"]]
        multiple=lcm(*values)
        weights=[multiple//v for v in values]
        m=sum(c[0] for c in g["columns"])*multiple
        h=gcd(m,*(sum(x*y for x,y in zip(c[2:],weights,strict=True)) for c in g["columns"]))
        blocks.append(split(m//h)[0])
    return lcm(*blocks)
