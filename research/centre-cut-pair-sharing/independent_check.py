#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate integer/explicit-vector replay of the selected cut-sharing census.

Prepared for Dennis (@antunishdPursuit) with substantial OpenAI Codex assistance.
Imports neither the primary checker nor any supplier/ceiling implementation.
It checks the finite identity/rank accounting, not numerical root enclosures.
"""
from collections import Counter
import hashlib
import io
import itertools
import gzip
import json
from pathlib import Path
import tarfile

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
ARCHIVE='research/community-frontier1094-audit/selected-replay.tar.gz'
PREFIX='candidate/strict/global/base/providers/gauge44/'


def check(ok,why):
    if not ok:
        raise ValueError(why)


def hashbytes(b):
    return hashlib.sha256(b).hexdigest()


def vectors(basis):
    # Enumerate all coefficient tuples; no row-elimination routine is used.
    values=set()
    for bits in itertools.product((0,1),repeat=len(basis)):
        value=0
        for enabled,x in zip(bits,basis):
            if enabled:
                value ^= x
        values.add(value)
    return values


def copy_rank(space,readers,ports):
    kernel=[x for x in space if all((x&ports[t]).bit_count()%2==0 for t in readers)]
    check(len(space)&(len(space)-1)==0 and len(kernel)&(len(kernel)-1)==0,'subspace/kernel cardinalities')
    return (len(space).bit_length()-1)-(len(kernel).bit_length()-1)


def replay():
    sources=json.loads((P/'SOURCES.json').read_bytes())
    pins={r['path']:r['sha256'] for r in sources['files'] if r['usage']=='input'}
    raw=(ROOT/ARCHIVE).read_bytes()
    check(hashbytes(raw)==pins[ARCHIVE],'archive drift')
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as t:
        check(len(t.getnames())==len(set(t.getnames())),'duplicate archive path')
        b=t.extractfile(PREFIX+'CANONICAL-WORD.json.gz').read()
    w=json.loads(gzip.decompress(b))
    check((w['v'],w['h'],w['R'])==(112,9,480),'correct selected word')
    slot='research/gauge44-slots/construction/slots/SLOT-PINS-k8.json'
    rawslot=(ROOT/slot).read_bytes();check(hashbytes(rawslot)==pins[slot],'slot pins drift')
    check(hashbytes(gzip.decompress(b))==json.loads(rawslot)['canonical_sha256'],'slot payload binding')
    labels=w['ports']
    mapping={q:k for k,q in enumerate(w['centers'])}
    original=[[0]*8 for _ in range(112)]
    for event in w['cut']:
        check(event[4]==4 and abs(event[3])==1,'integer quarter-coefficient alphabet')
        target=event[1]-112;term=mapping[event[2]]
        check(original[target][term]==0,'duplicate cut')
        original[target][term]=event[3]
    spaces=[vectors(w['frames'][f]) for f in w['center_frames']]
    check(all(len(s)==256 for s in spaces),'eight rank-eight gathers')
    for k in range(8):
        check(copy_rank(spaces[k],[t for t in range(112) if original[t][k]],labels)==8,'baseline copied rank')
    records=[];pattern_counts=Counter();pair_sizes=Counter();entries=0
    for i in range(8):
        for j in range(i+1,8):
            full={a^b for a in spaces[i] for b in spaces[j]}
            check(full==set(range(512)),'joint gathering requires all nine dimensions')
            shared=[t for t in range(112) if original[t][i] and original[t][j]]
            pair_sizes[len(shared)]+=1
            for sign in (-1,1):
                group=[t for t in shared if original[t][j]==sign*original[t][i]]
                for length in range(1,len(group)+1):
                    for selected in itertools.combinations(group,length):
                        active=set(selected)
                        remaining=[row[:] for row in original]
                        ninth=[0]*112
                        for t in active:
                            ninth[t]=remaining[t][i]
                            remaining[t][i]=remaining[t][j]=0
                        for t in range(112):
                            expected=original[t]
                            actual=remaining[t][:]
                            actual[i]+=ninth[t]
                            actual[j]+=sign*ninth[t]
                            check(expected==actual,'all eight basis coefficients preserved')
                            entries+=8
                        ranks=[]
                        for k in range(8):
                            readers=[t for t in range(112) if remaining[t][k]]
                            ranks.append(copy_rank(spaces[k],readers,labels))
                        nr=copy_rank(full,list(selected),labels)
                        check(nr>0,'new centre costs nonzero rank')
                        pattern=tuple(sorted(ranks))+(nr,)
                        pattern_counts[pattern]+=1
                        records.append(dict(pair=[i,j],lambda_value=str(sign),
                            shared_targets=list(selected),original_residual_copy_ranks=ranks,
                            new_total_copy_rank=nr,gather_join_dimension=9,
                            centre_charge=sum(ranks)+nr,endpoint_entries_checked=896))
    check(dict(pair_sizes)=={0:16,6:4,8:8},'complete pair-support census')
    check(len(records)==296 and entries==265216,'complete finite coverage')
    # These six types suffice for the pointwise cost comparison written in the
    # README: unchanged 8x8 plus a positive child; or 6x8 + 2x7 + rank 2/3.
    expected={(8,)*8+(1,):88,(8,)*8+(2,):116,(8,)*8+(3,):68,(8,)*8+(4,):16,
              (7,7)+(8,)*6+(2,):4,(7,7)+(8,)*6+(3,):4}
    check(dict(pattern_counts)==expected,'exact six-pattern classification')
    receipt=json.loads((P/'RESULT.json').read_bytes())
    table=sorted(records,key=lambda c:(tuple(c['pair']),c['lambda_value'],tuple(c['shared_targets'])))
    digest=hashbytes(json.dumps(table,sort_keys=True,separators=(',',':')).encode())
    check(digest==receipt['candidate_table_sha256'],'complete primary/secondary case binding')
    check(receipt['endpoint_entries_checked']==entries and receipt['nonempty_candidate_count']==len(records),'receipt coverage')
    # Four concrete equal-mass cases require the ninth COPY, even though the
    # two old copies each shrink. Omitting it changes 64 to 62.
    ties=[c for c in records if c['centre_charge']==64]
    check(len(ties)==4 and all(sum(c['original_residual_copy_ranks'])==62 and
                              c['new_total_copy_rank']==2 for c in ties),'no uncharged replacement')
    witness=receipt['best_favorable_witness']
    check(witness in ties,'best witness is a real equal-mass candidate')
    t=witness['shared_targets'][0];i,j=witness['pair'];sign=int(witness['lambda_value'])
    wrong=original[t][i]*(-sign)
    check(wrong!=original[t][j],'opposite mixing sign fails')
    check(original[t][i]*5!=0,'uncleared mixed scratch changes endpoint')
    check(sum(witness['original_residual_copy_ranks'])!=witness['centre_charge'],'omitted ninth-copy invoice fails')
    print('PASS_CENTRE_CUT_PAIR_SHARING_INDEPENDENT cases=296 entries=265216 patterns=6 equal_mass=4 controls=3')


if __name__=='__main__':
    replay()
