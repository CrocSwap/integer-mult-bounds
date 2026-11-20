"""Finite exact evidence for the rational grammar and common-grid lemma."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from word import Word, encode, parse
from execute import execute, depth


def need(ok,message):
    if not ok:
        raise RuntimeError(message)


def cmul(a,b):
    return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]


def oracle(rows,axes):
    """Dense closed tensor numerator; no recursion or instruction engine."""
    h = len(axes)
    coefficients = []
    for distance in range(h+1):
        value = (1,0)
        for _ in range(h-distance):
            value = cmul(value,(1,1))
        for _ in range(distance):
            value = cmul(value,(1,-1))
        coefficients.append(value)
    mask = sum(1<<a for a in axes)
    result = []
    for row in rows:
        out = []
        for target in range(len(row)):
            total = [0,0]
            for address,z in enumerate(row):
                if (address^target)&~mask:
                    continue
                term = cmul(z,coefficients[((address^target)&mask).bit_count()])
                total[0] += term[0]
                total[1] += term[1]
            out.append(tuple(total))
        result.append(out)
    return result


def fixtures():
    paid = tuple(("paid",reg,axis) for axis in range(2) for reg in range(2))
    simple = Word(2,2,0,(("scale",0,1,0,3),)+paid+(("scale",0,3,0,1),))
    before = (("add",2,1),("scale",2,7,3,15),("add",0,2),("clear",2))
    after = (("add",2,1),("scale",2,7,3,15),("sub",0,2),("clear",2))
    identities = (("x",0,0),)*2+(("s",1,1),)*4+(("cz",0,0,1),)*2
    identities += (("cx",1,0,1),)*2+(("unit",0),)*4
    private = (("add",2,0),("scale",2,-1,1,7),("paid",2,0),("clear",2))
    mixed = Word(2,2,1,before+identities+paid+after+private)
    even = Word(2,2,0,(("scale",0,7,-3,30),)+paid+(("scale",0,210,90,58),))
    return simple,mixed,even


def rejected(action):
    try:
        action()
    except (ArithmeticError,ValueError):
        return True
    return False


def sample(rows,ambient):
    return [[((7*i+3*r)%17-8,(5*i-2*r)%19-9) for i in range(1<<ambient)]
            for r in range(rows)]


def main():
    simple,mixed,even = fixtures()
    for word in (simple,mixed,even):
        need(word.valid_syntax() and word.all_columns(),"fixture all-column identity")
        need(parse(encode(word))==word,"signed unary codec")
        need(not word.funded(),"fixture unexpectedly funded")
    codec_cases = 0
    for a,b,q in product(range(-3,4),range(-2,3),range(1,6)):
        word = Word(2,2,0,(("scale",0,a,b,q),))
        need(parse(encode(word))==word,"coefficient codec")
        codec_cases += 1
    for code in ("","0","abc0","1110110","111111111111111111111111111111110"):
        need(parse(code) is None,"malformed code accepted")
    cases = [(simple,3,(2,)),(simple,3,(2,0)),(mixed,3,(4,0,2)),
             (mixed,5,(5,0,3,1)),(even,4,(3,1,0,2)),(simple,8,tuple(reversed(range(8))))]
    records = []
    for word,count,axes in cases:
        data = sample(count,max(axes)+1)
        actual,receipt = execute(word,data,axes)
        expected = oracle(data,axes)
        need(actual==expected,"closed tensor oracle mismatch")
        receipt["output_sha256"] = hashlib.sha256(json.dumps(actual,separators=(',',':')).encode()).hexdigest()
        receipt["ambient_axes"] = max(axes)+1
        records.append(receipt)
    paid = tuple(("paid",reg,axis) for axis in range(2) for reg in range(2))
    phase = Word(2,2,0,(("unit",0),("scale",0,0,-1,1))+paid)
    need(not phase.all_columns(),"column/scalar phase incorrectly collapsed")
    one, _ = execute(phase,sample(2,2),(0,1),require_identity=False)
    two, _ = execute(phase,sample(4,4),(0,1,2,3),require_identity=False)
    need(one==oracle(sample(2,2),(0,1)),"phase control must agree at f=1")
    need(two!=oracle(sample(4,4),(0,1,2,3)),"phase control must fail at f=2")
    dirty = Word(2,2,1,paid+(("add",2,0),))
    need(not dirty.all_columns(),"nonzero private endpoint accepted")
    need(rejected(lambda: execute(dirty,sample(2,2),(0,1),require_identity=False)),"private execution control")
    need(rejected(lambda: execute(simple,sample(4,4),(0,1,2,3),odd_exponent=0)),"missing odd lift")
    wrong,_ = execute(simple,sample(2,2),(0,1),retire_odd=False)
    need(wrong!=oracle(sample(2,2),(0,1)),"unretired odd scale went undetected")
    need(rejected(lambda: execute(simple,sample(3,4),(0,1,2,3))),"row-stock guard")
    need(not Word(2,2,0,(("scale",0,1,0,0),)).valid_syntax(),"zero denominator")
    need(not Word(2,2,0,(("cx",0,1,1),)).valid_syntax(),"aliased CNOT axes")
    empty = Word(2,2,0,())
    need(empty.funded() and not empty.all_columns(),"funding alone wrongly proves semantics")
    output = {"status":"PASS_RATIONAL_ALL_COLUMN_C_WORD","records":records,
              "codec_cases":codec_cases,"funded_fixture":False,"no_new_kappa":True,
              "controls":["column/scalar phase","nonzero private endpoint","omitted odd lift",
                          "omitted odd retirement","insufficient row stock","zero denominator",
                          "aliased native axes","funding without identity"]}
    print(json.dumps(output,sort_keys=True,indent=2))


if __name__ == '__main__':
    main()
