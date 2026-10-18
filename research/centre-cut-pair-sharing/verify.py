#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact bounded screen of one added proportional pair-total at the PR1094 cut.

Prepared for Dennis (@antunishdPursuit) with substantial OpenAI Codex assistance.
The retained ceiling engine is explicitly imported and source-pinned, not claimed
as an independent numerical implementation. Ordinary verification is read-only.
"""
import argparse
from collections import Counter, defaultdict
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import io
import itertools
import json
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
SLOT = 'research/gauge44-slots/construction/slots/SLOT-PINS-k8.json'
ENGINE = 'research/complex-local-word-ceiling/ceiling.py'
PREFIX = 'candidate/strict/global/base/providers/gauge44/'
BASE = {1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def binary_rank(rows):
    rows = [r for r in rows if r]
    rank = 0
    while rows:
        pivot = max(rows)
        bit = pivot.bit_length()-1
        rows = [r ^ pivot if (r >> bit) & 1 else r for r in rows if r != pivot]
        rows = [r for r in rows if r]
        rank += 1
    return rank


def span(vectors):
    values = {0}
    for x in vectors:
        values |= {y ^ x for y in values}
    return frozenset(values)


def copied_rank(frame, targets, ports):
    rows = [sum(((x & ports[t]).bit_count() % 2) << j
                for j,x in enumerate(frame)) for t in sorted(targets)]
    return binary_rank(rows)


def vector_rank_check(frame, targets, ports):
    common = span(frame)
    for t in targets:
        common = frozenset(x for x in common if not (x & ports[t]).bit_count() % 2)
    return binary_rank(frame) - (len(common).bit_length()-1)


def inputs():
    inventory = json.loads((PACKAGE/'SOURCES.json').read_bytes())
    rows = [r for r in inventory['files'] if r['usage']=='input']
    require({r['path'] for r in rows} == {ARCHIVE,SLOT,ENGINE}, 'exact input inventory')
    raw = {}
    for row in rows:
        data = (ROOT/row['path']).read_bytes()
        require(sha(data)==row['sha256'], 'source drift: '+row['path'])
        raw[row['path']] = data
    with tarfile.open(fileobj=io.BytesIO(raw[ARCHIVE]),mode='r:gz') as archive:
        names = [m.name for m in archive.getmembers()]
        require(len(names)==len(set(names)), 'duplicate archived path')
        def member(name):
            m = archive.getmember(PREFIX+name)
            require(m.isfile(), 'archive input is not regular')
            return archive.extractfile(m).read()
        compressed = member('CANONICAL-WORD.json.gz')
        program_bytes = member('LOCAL-PROGRAMS.json.gz')
        replay = json.loads(member('INDEPENDENT-LOCAL-REPLAY.json'))
    payload = gzip.decompress(compressed)
    pins = json.loads(raw[SLOT])
    require(sha(payload)==pins['canonical_sha256'], 'selected canonical payload pin')
    require(replay['canonical_word_sha256']==sha(compressed) and
            replay['local_programs_sha256']==sha(program_bytes), 'native source bindings')
    word = json.loads(payload)
    require((word['v'],word['h'],word['R'])==(112,9,480), 'selected 480-helper word')
    require({int(k):v for k,v in word['local_profile'].items()}==BASE, 'selected paid profile')
    require(len(set(word['centers']))==len(word['centers'])==len(word['center_frames'])==8, 'centre inventory')
    # Cross-read the canonical and emitted forward support/coefficient tables.
    matrix = [[Q(0) for _ in range(8)] for _ in range(112)]
    carrier = {q:k for k,q in enumerate(word['centers'])}
    for gate in word['cut']:
        require(gate[0]=='add' and gate[2] in carrier and 112<=gate[1]<224, 'cut grammar')
        t,k = gate[1]-112,carrier[gate[2]]
        require(matrix[t][k]==0, 'duplicate cut entry')
        matrix[t][k]=Q(gate[3],gate[4])
        require(matrix[t][k]!=0, 'zero cut entry')
    emitted = [[Q(0) for _ in range(8)] for _ in range(112)]
    programs = json.loads(gzip.decompress(program_bytes))
    for event in programs['forward']:
        if event[0]=='scalar':
            gate,frame = event[1:]
            if gate[0]=='add' and gate[2][0]=='C':
                require(gate[1][0]=='L' and 112<=gate[1][1]<224 and frame==0, 'native scatter grammar')
                t,k = gate[1][1]-112,gate[2][1]
                require(emitted[t][k]==0, 'duplicate emitted cut entry')
                emitted[t][k]=Q(gate[3],gate[4])
    require(matrix==emitted and sum(bool(x) for row in matrix for x in row)==176, 'canonical/native cut equality')
    for t,p in enumerate(word['ports']):
        require(span(word['frames'][word['final'][112+t]]) ==
                frozenset(x for x in range(512) if not (x&p).bit_count()%2), 'target final hyperplane')
    spec = importlib.util.spec_from_file_location('pinned_centre_ceiling',ROOT/ENGINE)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    return word,matrix,engine,dict(canonical_payload_sha256=sha(payload),
                                  canonical_container_sha256=sha(compressed),
                                  local_programs_sha256=sha(program_bytes))


def candidate(matrix,i,j,ratio,subset):
    require(0<=i<j<8 and ratio!=0 and subset, 'nonempty pair-sharing domain')
    require(all(matrix[t][i]!=0 and matrix[t][j]==ratio*matrix[t][i] for t in subset), 'proportional sharing support')
    residual = [row[:] for row in matrix]
    extra = [Q(0) for _ in matrix]
    for t in subset:
        extra[t]=matrix[t][i]
        residual[t][i]=residual[t][j]=Q(0)
    return residual,extra


def endpoint_check(matrix,residual,extra,i,j,ratio):
    checked = 0
    # All eight independent carrier basis columns, all 112 target rows.
    for t in range(len(matrix)):
        for k in range(8):
            value = residual[t][k] + extra[t]*(int(k==i)+ratio*int(k==j))
            require(value==matrix[t][k], 'exact cut endpoint mismatch')
            checked += 1
    return checked


def all_candidates(matrix):
    for i,j in itertools.combinations(range(8),2):
        groups = defaultdict(list)
        for t,row in enumerate(matrix):
            if row[i]!=0 and row[j]!=0:
                groups[row[j]/row[i]].append(t)
        for ratio,targets in sorted(groups.items()):
            for mask in range(1,1<<len(targets)):
                yield i,j,ratio,[t for bit,t in enumerate(targets) if (mask>>bit)&1]


def evaluate(word,matrix,i,j,ratio,subset):
    residual,extra = candidate(matrix,i,j,ratio,subset)
    columns = endpoint_check(matrix,residual,extra,i,j,ratio)
    frames = [word['frames'][f] for f in word['center_frames']]
    # A common-frame linear combination of carriers requires their join.
    joined = frames[i]+frames[j]
    require(binary_rank(joined)==9, 'two distinct gather frames join to full nine')
    ranks = []
    for k in range(8):
        targets = {t for t,row in enumerate(residual) if row[k]!=0}
        r = copied_rank(frames[k],targets,word['ports'])
        require(r==vector_rank_check(frames[k],targets,word['ports']), 'primal/dual rank disagreement')
        ranks.append(r)
    targets = {t for t,value in enumerate(extra) if value!=0}
    new_rank = copied_rank(joined,targets,word['ports'])
    require(new_rank==vector_rank_check(joined,targets,word['ports']), 'new-total rank disagreement')
    require(0<new_rank<=9, 'positive new-total copied rank')
    return dict(pair=[i,j],lambda_value=str(ratio),shared_targets=subset,
                original_residual_copy_ranks=ranks,new_total_copy_rank=new_rank,
                gather_join_dimension=9,centre_charge=sum(ranks)+new_rank,
                endpoint_entries_checked=columns)


def screen(engine,ranks,new_rank):
    # Delete all eight incumbent centre descents and insert the complete new
    # nine-term rank vector. Everything else is explicitly retained.
    local = Counter(BASE)
    local[8]-=8
    local.update(r for r in ranks+[new_rank] if r>0)
    local = {r:n for r,n in sorted(local.items()) if n}
    charge = sum(ranks)+new_rank
    quantities = engine.model(local,73,896,9,charge)
    low,high = engine.ceiling(local,73,896,9,charge)
    return dict(local_profile={str(r):n for r,n in local.items()},centre_charge=charge,
                local_rank_mass=str(quantities['local_mass']),
                idle_rank_mass=str(quantities['idle_mass']),deficit=str(quantities['deficit']),
                primitive_ceiling_bracket=[str(low),str(high)],
                additional_overhead_assumed_zero=['mixed-total preparation/source access',
                    'carrier common-frame adaptation','temporary dirty-state repair/restoration',
                    'phase/precision/scalar work','physical hosting/stock overhead'])


def controls(word,matrix,engine):
    exemplar = next(all_candidates(matrix))
    i,j,ratio,subset = exemplar
    residual,extra = candidate(matrix,i,j,ratio,subset)
    checks=[]
    def rejection(name,operation):
        try:
            operation()
        except ValueError as exc:
            checks.append(dict(name=name,reason=str(exc)))
        else:
            raise ValueError('accepted negative control: '+name)
    rejection('wrong_mixing_ratio',lambda: candidate(matrix,i,j,ratio+Q(1,2),subset))
    rejection('empty_sharing_subset',lambda: candidate(matrix,i,j,ratio,[]))
    exclusive=next(t for t,row in enumerate(matrix) if row[i] and not row[j])
    rejection('nonshared_target_substitution',lambda: candidate(matrix,i,j,ratio,[exclusive]))
    fi=span(word['frames'][word['center_frames'][i]])
    fj=span(word['frames'][word['center_frames'][j]])
    rejection('old_gather_frame_used_for_mixed_total',
              lambda: require(fj<=fi, 'second carrier frame is not contained in first; common-frame addition needs the join'))
    bad=copy.deepcopy(residual);bad[subset[0]][j]=matrix[subset[0]][j]
    rejection('second_original_scatter_not_removed',lambda: endpoint_check(matrix,bad,extra,i,j,ratio))
    badextra=extra[:];badextra[subset[0]]=0
    rejection('shared_scatter_omitted',lambda: endpoint_check(matrix,residual,badextra,i,j,ratio))
    actual=evaluate(word,matrix,*exemplar)
    # Reprice with and without the extra COPY. The latter is not legal and
    # would falsely recover the unchanged profile, mass and ceiling.
    paid=screen(engine,actual['original_residual_copy_ranks'],actual['new_total_copy_rank'])
    unpaid=screen(engine,actual['original_residual_copy_ranks'],0)
    require(Q(paid['primitive_ceiling_bracket'][1])<Q(unpaid['primitive_ceiling_bracket'][0]), 'omitted copy changes decision')
    checks.append(dict(name='omitted_ninth_copy_invoice',reason='uncharged COPY falsely recovers baseline; counted charge strictly lowers ceiling'))
    t=subset[0];d=Q(5);x=Q(2);y=Q(3)
    clean=matrix[t][i]*(x+ratio*y)
    dirty=matrix[t][i]*(d+x+ratio*y)
    require(dirty-clean==matrix[t][i]*d!=0, 'uncleared shared temporary leaks dirt')
    checks.append(dict(name='omitted_private_temporary_clear',reason='nonzero dirt leaks to a shared target; clean preparation is only granted free by the screen'))
    return checks


def compute():
    word,matrix,engine,source = inputs()
    frames=[word['frames'][f] for f in word['center_frames']]
    baseline_ranks=[copied_rank(frames[k],{t for t,row in enumerate(matrix) if row[k]},word['ports']) for k in range(8)]
    require(baseline_ranks==[8]*8, 'unchanged selected cut cost')
    baseline=screen(engine,baseline_ranks,0)
    candidates=[evaluate(word,matrix,*args) for args in all_candidates(matrix)]
    require(candidates, 'nonempty finite candidate domain')
    types={}
    for c in candidates:
        key=tuple(sorted(c['original_residual_copy_ranks']))+(c['new_total_copy_rank'],)
        if key not in types:
            types[key]=screen(engine,list(key[:8]),key[8])
    low,high=map(Q,baseline['primitive_ceiling_bracket'])
    gate=Q(21,20)*low
    # Fail the construction gate even against the favorable baseline lower end.
    require(all(Q(s['primitive_ceiling_bracket'][1])<gate for s in types.values()), 'at least one candidate needs construction investigation')
    # This stronger outcome is empirical/exhaustive only for the declared class.
    require(all(c['centre_charge']>=64 for c in candidates), 'candidate reduced total copied rank')
    patterns=Counter((tuple(sorted(c['original_residual_copy_ranks'])),c['new_total_copy_rank']) for c in candidates)
    require(sum(n for (ranks,r),n in patterns.items() if ranks==(8,)*8)==288, 'unchanged-rank case coverage')
    require(patterns[((7,7)+(8,)*6),2]==4 and
            patterns[((7,7)+(8,)*6),3]==4 and len(patterns)==6, 'two-rank-drop case coverage')
    require(all(Q(s['primitive_ceiling_bracket'][1])<low for s in types.values()), 'candidate does not strictly lose to baseline')
    counts=Counter(c['new_total_copy_rank'] for c in candidates)
    best=max(candidates,key=lambda c:Q(types[tuple(sorted(c['original_residual_copy_ranks']))+(c['new_total_copy_rank'],)]['primitive_ceiling_bracket'][1]))
    profile_screens=[dict(rank_vector=list(key),**value) for key,value in sorted(types.items())]
    return dict(status='PASS_CENTRE_CUT_PAIR_SHARING_SCREEN',outcome='negative-result',
                source=source,baseline=baseline,screen_gate_multiplier='21/20',
                screen_gate_against_baseline_lower=str(gate),
                unordered_pairs_considered=28,nonempty_candidate_count=len(candidates),
                new_copy_rank_histogram={str(k):v for k,v in sorted(counts.items())},
                endpoint_entries_checked=sum(c['endpoint_entries_checked'] for c in candidates),
                profile_screens=profile_screens,
                rank_vector_convention='first eight entries sorted original-copy ranks; final entry is the added total rank',
                best_favorable_witness=best,
                rejected_controls=controls(word,matrix,engine),
                candidate_table_sha256=sha(json.dumps(sorted(candidates,key=lambda c:(tuple(c['pair']),c['lambda_value'],tuple(c['shared_targets']))),sort_keys=True,separators=(',',':')).encode()),
                candidate_table_fields=['pair','lambda_value','shared_targets','original_residual_copy_ranks',
                                        'new_total_copy_rank','gather_join_dimension','centre_charge','endpoint_entries_checked'],
                scope='Complete finite clean proportional pair-sharing cut family; retained non-centre work and zero extra overhead. No physical synthesis, generalized nine-term exclusion, new supplier or kappa.')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--receipt',action='store_true')
    args=ap.parse_args()
    result=compute()
    if args.receipt:
        print(json.dumps(result,indent=2,sort_keys=True))
    else:
        require(result==json.loads((PACKAGE/'RESULT.json').read_bytes()),'exact receipt mismatch')
        print(result['status'],'candidates='+str(result['nonempty_candidate_count']),
              'best_centre_charge='+str(result['best_favorable_witness']['centre_charge']),
              'gate=FAIL_SYNTHESIS_NOT_STARTED controls='+str(len(result['rejected_controls'])))


if __name__=='__main__':
    main()
