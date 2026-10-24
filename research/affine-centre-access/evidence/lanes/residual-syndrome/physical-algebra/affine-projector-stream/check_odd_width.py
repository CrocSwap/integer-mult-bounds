#!/usr/bin/env python3
"""Check odd-width Haar codes and their physical leaf actions."""

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path


HERE = Path(__file__).resolve().parent


@dataclass(frozen=True)
class G:
    re: F = F(0)
    im: F = F(0)

    def __add__(self, other):
        other = as_g(other)
        return G(self.re+other.re, self.im+other.im)

    __radd__ = __add__

    def __neg__(self):
        return G(-self.re, -self.im)

    def __sub__(self, other):
        return self + -as_g(other)

    def __mul__(self, other):
        other = as_g(other)
        return G(self.re*other.re-self.im*other.im,
                 self.re*other.im+self.im*other.re)

    __rmul__ = __mul__

    def __truediv__(self, divisor):
        return G(self.re/divisor, self.im/divisor)


def as_g(value):
    return value if isinstance(value, G) else G(F(value))


ZERO, ONE = G(), G(F(1))
ALPHA, BETA = G(F(1,2), F(1,2)), G(F(1,2), F(-1,2))
UNITS = (ONE, G(F(0), F(1)), G(F(-1)), G(F(0), F(-1)))


def require(value, label):
    if not value:
        raise ValueError(label)


def magnitude(value):
    return max(abs(value.re), abs(value.im))


def inserted(value, bit, digit):
    low = (1 << bit)-1
    return (value & low) | ((value & ~low) << 1) | (digit << bit)


def layout(n, width, chunk=1, rho=0):
    half = width//2
    def bit(row, column):
        return (n*width-1-(row*width+column))*chunk+rho
    changes = [(bit(i,j), bit(i,j+half))
               for i in range(n) for j in range(half)]
    signs = {right: -1 for _, right in changes}
    pivot = bit(0, width-1)
    for i in range(1,n):
        donor = bit(i, width-1)
        changes.append((pivot, donor))
        signs[donor] = 1
    return changes, signs, pivot, bit


def changed_address(address, changes):
    for target, source in changes:
        if (address >> source) & 1:
            address ^= 1 << target
    return address


def address_change(values, changes, polynomial):
    result = [ZERO]*len(values)
    for address in range(len(values)//polynomial):
        target = changed_address(address, changes)
        result[target*polynomial:(target+1)*polynomial] = (
            values[address*polynomial:(address+1)*polynomial])
    return result


def encode(values, signs, polynomial, trace):
    active, details = list(values), []
    for bit in sorted(signs, reverse=True):
        sign = signs[bit]
        zero, one = [], []
        for address in range(len(active)//polynomial):
            (one if (address >> bit)&1 else zero).extend(
                active[address*polynomial:(address+1)*polynomial])
        require(len(zero)==len(one), "complete signed split")
        first, detail = [], []
        for u,v in zip(zero,one):
            plus, minus = u+sign*v, u-sign*v
            trace.extend((plus,minus))
            first.append(plus/2)
            detail.append(minus/2)
        details.append((bit,sign,detail))
        active = first
    return active, details


def decode(active, details, polynomial, trace):
    for bit,sign,detail in reversed(details):
        result = [ZERO]*(2*len(active))
        require(len(active)==len(detail), "complete detail shape")
        for address in range(len(active)//polynomial):
            for j in range(polynomial):
                a,d = active[address*polynomial+j],detail[address*polynomial+j]
                u,v = a+d,sign*(a-d)
                trace.extend((u,v))
                result[inserted(address,bit,0)*polynomial+j] = u
                result[inserted(address,bit,1)*polynomial+j] = v
        active = result
    return active


def c_power(values, bit, polynomial, power):
    power %= 4
    if power==0:
        return list(values)
    result = [ZERO]*len(values)
    for address in range(len(values)//polynomial):
        other = address ^ (1 << bit)
        for j in range(polynomial):
            u,v = values[address*polynomial+j],values[other*polynomial+j]
            result[address*polynomial+j] = (v if power==2 else
                (ALPHA*u+BETA*v if power==1 else BETA*u+ALPHA*v))
    return result


def leaf_bit(pivot, signs):
    return pivot-sum(bit<pivot for bit in signs)


def shear(x,y,changes,signs,pivot,polynomial,phase=0,power=0,add_sign=1):
    trace = []
    a,sd = encode(address_change(x,changes,polynomial),signs,polynomial,trace)
    b,td = encode(address_change(y,changes,polynomial),signs,polynomial,trace)
    correction = c_power(a,leaf_bit(pivot,signs),polynomial,power)
    correction = [UNITS[phase%4]*v for v in correction]
    b = [v+add_sign*u for u,v in zip(correction,b)]
    trace.extend(correction+b)
    xx = address_change(decode(a,sd,polynomial,trace),changes,polynomial)
    yy = address_change(decode(b,td,polynomial,trace),changes,polynomial)
    sd.clear()
    td.clear()
    require(not sd and not td,"details consumed")
    return xx,yy,trace


def direct_projector(values,n,width,chunk,rho,polynomial):
    half = width//2
    _,_,_,bit = layout(n,width,chunk,rho)
    generators = [((1 << bit(i,j)) | (1 << bit(i,j+half)),-1)
                  for i in range(n) for j in range(half)]
    generators += [((1 << bit(0,width-1)) | (1 << bit(i,width-1)),1)
                   for i in range(1,n)]
    shifts = [(0,1)]
    for mask,sign in generators:
        shifts += [(old^mask,old_sign*sign) for old,old_sign in shifts]
    result = [ZERO]*len(values)
    for address in range(len(values)//polynomial):
        for j in range(polynomial):
            value = values[address*polynomial+j]
            if value==ZERO:
                continue
            for shift,sign in shifts:
                result[(address^shift)*polynomial+j] += sign*value/len(shifts)
    return result


def native_line(values,n,width,q,inverse=False):
    result = list(values)
    _,_,_,bit = layout(n,width)
    for column in range(width):
        shift = sum(1 << bit(i,column) for i in range(n) if (q >> i)&1)
        aa,bb = (BETA,ALPHA) if inverse else (ALPHA,BETA)
        result = [aa*result[a]+bb*result[a^shift] for a in range(len(result))]
    return result


def native_translation(values,n,width,delta):
    _,_,_,bit = layout(n,width)
    shift = sum(1 << bit(i,j) for i in range(n) for j in range(width)
                if (delta >> i)&1)
    return [values[a^shift] for a in range(len(values))]


def check_case(n,width,chunk,rho,spectator,polynomial):
    changes,signs,pivot,_ = layout(n,width,chunk,rho)
    length = (1 << (n*width*chunk+spectator))*polynomial
    for column in range(2*length):
        x = [ONE if j==column else ZERO for j in range(length)]
        y = [ONE if j+length==column else ZERO for j in range(length)]
        xx,yy,_ = shear(x,y,changes,signs,pivot,polynomial)
        require(xx==x,"full arbitrary source restoration")
        expected = direct_projector(x,n,width,chunk,rho,polynomial)
        require(yy==[u+v for u,v in zip(y,expected)],"full direct projector")
    x = [G(F((7*j+3)%17-8,8), F((11*j+2)%13-6,8)) for j in range(length)]
    y = [G(F((13*j+1)%19-9,8),F((17*j+4)%23-11,8)) for j in range(length)]
    for phase,power in ((0,0),(1,1),(3,3),(2,2)):
        xx,yy,trace = shear(x,y,changes,signs,pivot,polynomial,phase,power)
        back_x,back_y,_ = shear(xx,yy,changes,signs,pivot,polynomial,
                               phase,power,-1)
        require((back_x,back_y)==(x,y),"frame-matched inverse shear")
        maximum = max(map(magnitude,x+y))
        require(max(map(magnitude,trace))<=4*maximum,"two magnitude bits")
        denominator = 1 << (3+len(signs)+int(power%2))
        require(all((z*denominator).denominator==1 for v in trace+xx+yy
                    for z in (v.re,v.im)),"fractional guard")
    a,details = encode(address_change(x,changes,polynomial),signs,polynomial,[])
    restored = address_change(decode(a,details,polynomial,[]),changes,polynomial)
    require(restored==x,"code inverse")
    # Arbitrary encoded coordinates test the other inverse order.
    a = [v+G(F(j+1,8)) for j,v in enumerate(a)]
    details = [(b,s,[v+G(F(j+3,16)) for j,v in enumerate(d)])
               for b,s,d in details]
    reconstructed = decode(a,details,polynomial,[])
    other_a,other_details = encode(reconstructed,signs,polynomial,[])
    require((other_a,other_details)==(a,details),"inverse code order")
    return {"n":n,"tensor_width":width,"chunk_bits":chunk,
            "selected_offset":rho,"spectator_bits":spectator,
            "polynomial_coefficients":polynomial,"columns":2*length,
            "codimension":len(signs),"leaf_records":length>>len(signs)}


def sparse_leaf(address,changes,signs):
    address = changed_address(address,changes)
    sign = 1
    for bit in sorted(signs,reverse=True):
        if (address >> bit)&1:
            sign *= signs[bit]
        low = (1 << bit)-1
        address = (address & low) | ((address >> 1) & ~low)
    return address,G(F(sign,1 << len(signs)))


def native_column(address,n,width,q):
    _,_,_,bit = layout(n,width)
    terms = {address:ONE}
    for column in range(width):
        shift = sum(1 << bit(i,column) for i in range(n) if (q >> i)&1)
        out = {}
        for a,value in terms.items():
            out[a] = out.get(a,ZERO)+ALPHA*value
            out[a^shift] = out.get(a^shift,ZERO)+BETA*value
        terms = out
    return terms


def check_leaf_actions(n,width):
    half = width//2
    changes,signs,pivot,bit = layout(n,width)
    selected = leaf_bit(pivot,signs)
    checks = 0
    for address in range(1 << (n*width)):
        a,value = sparse_leaf(address,changes,signs)
        for q in range(1,1 << n):
            if q.bit_count()%2==0:
                continue
            got = {}
            for b,coefficient in native_column(address,n,width,q).items():
                c,weight = sparse_leaf(b,changes,signs)
                got[c] = got.get(c,ZERO)+coefficient*weight
            expected = {a:UNITS[half%4]*ALPHA*value,
                        a^(1 << selected):UNITS[half%4]*BETA*value}
            require({k:v for k,v in got.items() if v!=ZERO}==expected,
                    "complete native line leaf kernel")
            checks += 1
        for delta in range(1 << n):
            shift = sum(1 << bit(i,j) for i in range(n) for j in range(width)
                        if (delta >> i)&1)
            got_a,got_value = sparse_leaf(address^shift,changes,signs)
            parity = delta.bit_count()%2
            require((got_a,got_value)==(a^(parity << selected),
                    ((-1)**(half*parity))*value),"translation leaf kernel")
            checks += 1
    return {"n":n,"tensor_width":width,"complete_column_equalities":checks}


def check_physical_shear():
    n,width = 2,3
    changes,signs,pivot,_ = layout(n,width)
    length = 1 << (n*width)
    # O_source=C_1, O_target=i X_1 C_1 C_2.
    # Their leaf ratio is i^(1+f) (-1)^f C^(1+2)=C^3 at f=1.
    for column in range(2*length):
        x = [ONE if j==column else ZERO for j in range(length)]
        y = [ONE if j+length==column else ZERO for j in range(length)]
        xx,yy,_ = shear(x,y,changes,signs,pivot,1,0,3)
        # f=1 makes the two scalar factors cancel, so the ratio is C^3.
        corrected = native_line(x,n,width,1,True)
        corrected = direct_projector(corrected,n,width,1,0,1)
        corrected = native_line(corrected,n,width,1)
        corrected = native_line(corrected,n,width,2)
        corrected = native_translation(corrected,n,width,1)
        corrected = [UNITS[1]*v for v in corrected]
        require(xx==x and yy==[u+v for u,v in zip(y,corrected)],
                "typed physical operator shear")
    return {"n":n,"tensor_width":width,"complete_columns":2*length,
            "source_frame":"C_1", "target_frame":"i X_1 C_1 C_2",
            "leaf_ratio":"C_u^3"}


def main():
    cases = [check_case(*args) for args in
             ((2,1,2,1,1,2),(2,3,1,0,1,2),(3,1,1,0,1,2),(3,3,1,0,0,1))]
    phases = [check_leaf_actions(n,width) for n,width in ((2,1),(2,3),(3,3))]
    typed = check_physical_shear()
    pins = {name:hashlib.sha256((HERE/name).read_bytes()).hexdigest()
            for name in ("STREAM.md","AMENDMENT.md","STREAM.json",
                         "ODD-WIDTH.md")}
    result = {"status":"PASS_ODD_WIDTH_PROJECTOR_STREAM",
              "dependencies":pins,"cases":cases,"leaf_actions":phases,
              "physical_frame_shear":typed,
              "scope":"Exact finite arbitrary-input maps, inverse codes, native leaf phases, and guards. General stream cost is proved in ODD-WIDTH.md. No full supplier claim."}
    (HERE/"ODD-WIDTH.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(result["status"])


if __name__=="__main__":
    main()
