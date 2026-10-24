#!/usr/bin/env python3
"""Check each paid-row monomial certificate and its literal frozen event.

This checks the emitted complete rows; census.py owns their chronological
derivation. No claim of independent row-derivation is made for this checker.
"""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import gzip,hashlib,json

P=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def need(p,s):
    if not p:raise ValueError(s)
def rank(columns):
    basis={}
    for x in columns:
        while x:
            j=x.bit_length()-1
            if j in basis:x^=basis[j]
            else:basis[j]=x;break
    return len(basis)
def main():
    receipt=json.loads((P/'RESULT-v2.json').read_bytes())
    cap=P.parent/'09-capsule-cold/capsule-v1'
    raw=(cap/'snapshot/research/kappa-joint-relations-20261023/WORD.json.gz').read_bytes()
    need(sha(raw)==receipt['word_sha256'],'word hash')
    word=json.loads(gzip.decompress(raw));pivots=set(map(int,word['relation_basis']))
    retained={('L',i) for i in range(632) if i not in pivots}
    gens=word['canonical']['warps']
    need(len(gens)==72 and {g['op'] for g in gens}==set(range(1,73)),'72 native generators')
    need(all(len(g['G_columns'])==9 and rank(g['G_columns'])==9 for g in gens),'invertible source binary maps')
    expected=[(i,e) for i,e in enumerate(word['programs']['backward']) if e[0] in ('climb','center')]
    trace=(P/receipt['row_trace']['file']).read_bytes();need(sha(trace)==receipt['row_trace']['sha256'],'trace hash')
    records=[json.loads(line) for line in gzip.decompress(trace).splitlines()]
    need([(r['event'],r['literal']) for r in records]==expected,'complete ordered literal paid-event census')
    roles=set();hist=Counter();lengths=Counter();bad_control=False
    for r in records:
        row=r['row'];canonical=json.dumps(row,sort_keys=True,separators=(',',':')).encode()
        need(sha(canonical)==r['row_sha256'],'row hash')
        need(len(row)==r['terms'],'term count')
        keys=[(tuple(t[0]),tuple(t[1])) for t in row]
        need(len(set(keys))==len(keys),'collected distinct free monomials')
        need(all(Fraction(t[2],t[3]) for t in row),'all coefficients nonzero')
        need(all(all(1<=abs(g)<=72 for g in t[1]) and all(a!=-b for a,b in zip(t[1],t[1][1:])) for t in row),'reduced known generator words')
        w=r['independent_monomial_certificate'];role=tuple(w[0])
        same=[t for t in row if tuple(t[0])==role]
        need(same==[w] and role in retained,'selected coefficient is exactly one invertible monomial on an independent retained input')
        hist[r['literal'][-1]]+=1;roles.add(role);lengths[len(w[1])]+=1
        # A fabricated certificate with opposite rational coefficient must fail.
        mutated=[*w[:2],-w[2],w[3]]
        need(same!=[mutated],'wrong-sign certificate rejected');bad_control=True
    out=dict(status='PASS_FROZEN_PAID_SINGLE_MONOMIAL_CERTIFICATES',
             source_receipt_sha256=sha((P/'RESULT-v2.json').read_bytes()),
             checker_sha256=sha(Path(__file__).read_bytes()),
             checked_paid_rows=len(records),paid_histogram=dict(sorted(hist.items())),
             selected_retained_entry_roles=len(roles),selected_word_lengths=dict(sorted(lengths.items())),
             invertible_binary_source_generators=72,wrong_sign_certificate_control=bad_control,
             logical_scope='All positive tensor widths through nonzero scalar times invertible monomial coefficient; no lower-rank claim')
    (P/'CERTIFICATE-CHECK-v1.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out))
if __name__=='__main__':main()
