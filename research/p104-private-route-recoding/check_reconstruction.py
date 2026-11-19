"""Construct general two-chain repairs and verify each terminal as a rational form."""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import A, B, C, E, Y, add, check_causality, construct, read_word, require, span


def changed_cone(w, forms, seeds):
    sensitive = set(seeds)
    for k in w['schedule']:
        if sensitive.intersection(forms[k]):
            sensitive.add(k)
    return sensitive


def reduced_rows(w, forms, cone):
    # Every unchanged wire outside the union of dependency cones can serve as a
    # formal symbol, shared by both programs. Equality here implies operator equality.
    symbolic = {~j:{~j:1} for j in range(len(w['initial']))}
    for k in w['schedule']:
        if k not in cone:
            symbolic[k] = {k:1}
            continue
        row = {}
        for j,q in forms[k].items():
            add(row,symbolic[j],q)
        symbolic[k] = row
    return symbolic


def pullback(word, forms, k):
    row = {k:1}
    for j in reversed(word['schedule']):
        q = row.pop(j,0)
        if q:
            add(row,forms[j],q)
    return row


def main():
    w, old, native, ends = read_word()
    spaces = list(map(span,w['frames']))
    ranks = [len(f) for f in w['frames']]
    grade = lambda uv: abs(ranks[uv[0]]-ranks[uv[1]])
    profile = Counter(map(grade,native.values()))
    require(profile == dict(enumerate((3842,792,487,230,314,40,3,1),1)), 'original profile')
    old_seeds = {A,B,C,E}
    affected = changed_cone(w,old,old_seeds)
    reference = {k:pullback(w,old,k) for k in Y}
    interval = [j for j,s in enumerate(spaces) if spaces[278]<=s<=spaces[127]]
    longest = {}
    for j in sorted(interval,key=ranks.__getitem__,reverse=True):
        longest[j] = (j,) + max((longest[v] for v in interval if spaces[j] < spaces[v]),
                                key=len,default=())
    direct = (278,127)
    private = (278,288,127)
    detour = (278,561,288,239,127)
    cases = [(direct,private,0),(direct,private,Fraction(-1,2)),
             (direct,private,Fraction(1,2)),(longest[278],detour,Fraction(11,7))]
    totals = 0
    for dead in (A,B):
        for primary,auxiliary,slope in cases:
            require(all(spaces[a]<spaces[b] for p in (primary,auxiliary) for a,b in zip(p,p[1:])),
                    'all legs legal')
            nw,nf,nr = construct(w,old,native,dead,primary,auxiliary,slope)
            check_causality(nw,nf,nr,ends)
            seeds = old_seeds | (nr.keys()-native.keys())
            both = affected | changed_cone(nw,nf,seeds)
            left,right = reduced_rows(w,old,both),reduced_rows(nw,nf,both)
            require(all(left[k] == right[k] for k in ends),'every terminal operator')
            require(all(reference[k] == pullback(nw,nf,k) for k in Y),'independent full adjoint')
            expect = profile.copy()
            for k in (dead,C,E):
                expect[grade(native[k])] -= 1
            for p in (primary,auxiliary):
                expect.update(grade(edge) for edge in zip(p,p[1:]))
            require(Counter(map(grade,nr.values())) == expect,'entire new tariff profile')
            totals += 1
        # Independent public-coordinate sign ablation on one output.
        k = next(iter(Y))
        altered = dict(nf[k])
        j = max(altered)
        altered[j] = -altered[j]
        require(pullback(nw,nf|{k:altered},k) != reference[k], 'reader sign control')
    print(f'PASS {totals} causal whole words, {totals*len(ends)} exact terminal comparisons, '
          'independent adjoint expansion, all paid histograms and two sign controls.')


if __name__ == '__main__':
    main()
