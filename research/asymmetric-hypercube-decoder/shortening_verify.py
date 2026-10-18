#!/usr/bin/env python3
"""Exact finite research verification; Python 3.10+, standard library only.

Copyright 2026 Sam Sung. Apache-2.0. Substantial OpenAI Codex assistance.
Finite checks supplement the written proofs; they are not formal proofs.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
from itertools import combinations, product
from math import comb
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ports(p, k):
    return [sum(1 << (2*i+s) for i,s in zip(pairs, signs))
            for pairs in combinations(range(p),k) for signs in product((0,1),repeat=k)]


def add(word, pivots):
    while word:
        p=word.bit_length()-1
        if p in pivots:
            word ^= pivots[p]
        else:
            pivots[p]=word
            return True
    return False


def contains(word, pivots):
    while word:
        p=word.bit_length()-1
        if p not in pivots:
            return False
        word ^= pivots[p]
    return True


def shorten(p, k, empty):
    family=ports(p,k)
    cube=[j for j,t in enumerate(family) if t >> (2*k)==0]
    require(len(cube)==1<<k,'cube cardinality')
    # The first ordinary cube is first in this explicit port order.
    require(cube==list(range(1<<k)),'chosen cube column order')
    cube_mask=(1<<(1<<k))-1
    outside_pivots={}
    shortened={}
    generators=0
    for degree in range(0 if empty else 1,k):
        for face in ports(p,degree):
            generators+=1
            word=sum(1<<j for j,t in enumerate(family) if t&face==face)
            # Reduce by outside pivot while preserving the entire codeword.
            while word >> (1<<k):
                pivot=word.bit_length()-1
                if pivot not in outside_pivots:
                    outside_pivots[pivot]=word
                    break
                word ^= outside_pivots[pivot]
            else:
                require(word&~cube_mask==0,'outside reduction')
                add(word,shortened)
    rm={}
    degree_bound=k-(p-k)-1
    for degree in range(max(0,degree_bound+1)):
        for variables in combinations(range(k),degree):
            face=sum(1<<(2*i) for i in variables)
            word=sum(1<<j for j in cube if family[j]&face==face)
            add(word,rm)
    exceptional=(not empty and degree_bound==0 and k&(k-1)==0)
    if exceptional:
        rm={}
    require(len(shortened)==len(rm),f'dimension p={p} k={k} empty={empty}: {len(shortened)} != {len(rm)}')
    require(all(contains(w,rm) for w in shortened.values()),'shortening subset RM')
    require(all(contains(w,shortened) for w in rm.values()),'RM subset shortening')
    rank=len(outside_pivots)+len(shortened)
    expected_rank=sum(comb(p,j)*comb(p-j,min(k-1-j,p-k)) for j in range(k))
    expected_rank-=int(not empty and k&(k-1)==0 and p>=2*k-1)
    require(rank==expected_rank,'independent full rank crosscheck of PR772 formula')
    return dict(p=p,k=k,q=p-k,empty=empty,ports=len(family),generators=generators,
                rank=rank,shortened_rank=len(shortened),rm_order=degree_bound,
                empty_star_exception=exceptional)



def verify():
    cases = [shorten(k+q, k, empty) for k in range(2, 7) for q in range(4)
             for empty in (False, True)]
    cases += [shorten(9, 5, empty) for empty in (False, True)]
    return dict(status="PASS", scope="Exact full-generator shortenings on 42 ordinary cubes; "
                "both inclusions against independently generated Reed-Muller spaces. "
                "Full ranks are also compared with the pinned PR772 formula.", cases=cases)

RECEIPT = 'SHORTENING-RESULTS.json'


def self_test(result):
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        script = directory / Path(__file__).name
        script.write_bytes(Path(__file__).read_bytes())
        receipt = directory / RECEIPT
        receipt.write_text(json.dumps(result))
        command = [sys.executable, "-I", "-O", "-B", str(script)]
        run = subprocess.run(command, capture_output=True, text=True)
        require(run.returncode == 0, f"isolated optimized relocated replay failed: {run.stderr}")
        receipt.write_text(json.dumps(dict(result, status="CORRUPTED")))
        protected = directory / "protected.json"
        protected.write_text("preserve this output\n")
        run = subprocess.run(command + ["--check", str(receipt), "--write", str(protected)],
                             capture_output=True, text=True)
        require(run.returncode != 0, "corrupt receipt accepted")
        require(protected.read_text() == "preserve this output\n", "failed check overwrote output")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = json.loads(json.dumps(verify()))
    if args.check or not args.write:
        receipt = args.check or Path(__file__).resolve().with_name(RECEIPT)
        require(json.loads(receipt.read_text()) == result, f"receipt mismatch: {receipt}")
    if args.self_test:
        self_test(result)
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS", Path(__file__).name)


if __name__ == "__main__":
    main()
