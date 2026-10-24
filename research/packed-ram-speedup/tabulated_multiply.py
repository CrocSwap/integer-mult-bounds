"""Independent radix-product replay; constructor/evaluator use no multiplication.
The multiplication in expected() is the specification only.
"""
import json
import random

def need(ok, message):
    if not ok:
        raise ValueError(message)

def build(b):
    B = 1 << b
    table = []
    for a in range(B):
        v = 0
        for _ in range(B):
            table.append(v)
            v += a
    return table

def digits(x, b, k):
    mask = (1 << b) - 1
    answer = []
    for _ in range(k):
        answer.append(x & mask)
        x >>= b
    need(x == 0, "operand exceeds fixed digit bank")
    return answer

def product(x, y, b, k, table, corrupt=False):
    B = 1 << b
    aa, bb = digits(x, b, k), digits(y, b, k)
    cc = [0 for _ in range(k + k)]
    largest = 0
    for i in range(k):
        carry = 0
        for j in range(k):
            z = cc[i+j] + table[(aa[i] << b) + bb[j]] + carry
            need(0 <= z < (1 << (b+b)), "temporary overflow")
            largest = max(largest, z)
            cc[i+j] = z & (B-1)
            carry = z >> b
        need(cc[i+k] == 0, "unexpected existing terminal carry")
        cc[i+k] = 0 if corrupt else carry
    result = 0
    for d in reversed(cc):
        result = (result << b) | d
    return result, largest

def expected(x, y):
    return x * y

def main():
    rng = random.Random(20261022)
    cases = 0
    for b in range(1, 7):
        table = build(b)
        B = 1 << b
        for a in range(B):
            for j in range(B):
                need(table[(a << b) + j] == expected(a,j), "table mismatch")
        for k in range(1, 9):
            limit = 1 << (b*k)
            samples = [(0,0),(1,1),(limit-1,limit-1),(limit-1,1)]
            samples += [(rng.randrange(limit),rng.randrange(limit)) for _ in range(50)]
            for x,y in samples:
                got,_=product(x,y,b,k,table)
                need(got==expected(x,y), "radix product mismatch")
                cases+=1
    bad,_=product(15,15,2,2,build(2),True)
    need(bad!=expected(15,15), "carry mutation survived")
    print(json.dumps({"status":"PASS","product_cases":cases,
        "b_range":[1,6],"k_range":[1,8],"carry_mutation_rejected":True,
        "proof_status":"Finite reference replay, not emitted RamStd code or Lean proof."},indent=2))

if __name__=="__main__":
    main()
