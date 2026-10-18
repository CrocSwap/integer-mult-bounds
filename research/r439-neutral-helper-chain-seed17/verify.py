#!/usr/bin/env python3
"""Exact frozen-domain helper-chain census and complete R439 scalar invoice.

Apache-2.0. Prepared for ToikY with substantial OpenAI Codex assistance.
This is a finite circuit experiment, not supplier adoption or a new kappa.
"""
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import heapq
import importlib.util
import itertools
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = 'research/r439-bsection-stars-seed01/candidate.json.gz'
SEARCH = 'research/r439-bsection-stars-seed01/candidate_search.json'
CHECKER = 'research/e8-bit-p111-tuned/code/xcheck_p.py'
EXPORTER = 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'
PROFILE = {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}
INPUT_PATHS = {PARENT,SEARCH,CHECKER,EXPORTER,
               'research/r439-bsection-stars-seed01/README.md',
               'research/r439-helper-stars-seed19/PROOF.md',
               'research/r439-post-helper-shear-seed03/README.md',
               'certificates/selected-result.json',
               'research/community-frontier1094-audit/ASSEMBLY.json',
               'docs/research/community-batch1099-review.md'}
PACKAGE_PATHS = {'verify.py','independent.py','test_package.py'}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            need(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw,
                      object_pairs_hook=unique)


def canonical(value):
    # JSON object keys are strings on disk, including integer histogram keys.
    # Normalize that boundary before sorting while preserving bool/int values.
    normalized = json.loads(json.dumps(value))
    return json.dumps(normalized, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def split(word):
    need((word['v'], word['R']) == (111,439), 'fixed dimensions')
    p, e, n = 236,306,111
    D = word['D']
    need(len(D) == 2*p+2*e+n, 'complete D partition')
    prep, target, middle = D[:p],D[p:p+e],D[p+e:p+e+n]
    need(D[-p:] == prep[::-1] and D[p+e+n:-p] == target[::-1], 'literal parent restoration')
    need(all(f == 0 and d >= 222 and len(ss) == 1 and ss[0] >= 222
             for f,d,ss in prep), 'helper preparation')
    need(all(f == 0 and 111 <= d < 222 and all(111 <= s < 222 for s in ss)
             for f,d,ss in target), 'target preparation')
    columns = [0]*439
    for i,(f,d,ss) in enumerate(middle):
        need(f == 0 and d == 111+i and len(set(ss)) == len(ss), 'middle rows')
        for s in ss:
            need(type(s) is int and 222 <= s < 661, 'middle helper access')
            columns[s-222] |= 1 << i
    need(sum(c.bit_count() for c in columns) == 4464, 'frozen middle weight')
    representative = list(range(439))
    def find(i):
        while representative[i] != i:
            representative[i] = representative[representative[i]]
            i = representative[i]
        return i
    for _,d,ss in prep:
        a,b = find(d-222),find(ss[0]-222)
        representative[max(a,b)] = min(a,b)
    comp = [find(i) for i in range(439)]
    helpers = [i for i in range(439) if i+222 not in word['ret']]
    need(len(helpers) == 430, 'non-retained helper count')
    return prep,target,middle,columns,comp,helpers


def census(word):
    _,_,_,columns,component,helpers = split(word)
    weights = [c.bit_count() for c in columns]
    pair_gain = [[weights[b]-(columns[b]^columns[a]).bit_count()-2 for b in range(439)]
                 for a in range(439)]
    histogram = Counter()
    distinct = eligible = positive = 0
    sha = hashlib.sha256()
    buffer = bytearray()
    nominees = []
    for a in helpers:
        A,ca = columns[a],component[a]
        for b in helpers:
            cb = component[b]
            if ca == cb:
                continue
            B,ab = columns[b],pair_gain[a][b]
            AB = A ^ B
            for c in helpers:
                if component[c] == ca or component[c] == cb:
                    continue
                distinct += 1
                if ab > 0 or pair_gain[b][c] > 0:
                    continue
                gain = weights[b]+weights[c]-AB.bit_count()-(columns[c]^AB).bit_count()-4
                eligible += 1
                histogram[gain] += 1
                buffer.extend(struct.pack('<4i',a,b,c,gain))
                if len(buffer) >= 65536:
                    sha.update(buffer); buffer.clear()
                if gain > 0:
                    positive += 1
                    tie = int.from_bytes(hashlib.sha256(struct.pack('<4i',17,a,b,c)).digest(),'big')
                    item = (gain,-tie,-a,-b,-c)
                    if len(nominees) < 32:
                        heapq.heappush(nominees,item)
                    elif item > nominees[0]:
                        heapq.heapreplace(nominees,item)
    sha.update(buffer)
    chosen = [[-a,-b,-c,gain,-tie] for gain,tie,a,b,c in sorted(nominees,reverse=True)]
    return dict(ordered_distinct_helpers=430*429*428, distinct_parent_components=distinct,
                unilateral_nonpositive=eligible, positive_joint=positive,
                maximum_joint_gain=max(histogram), gain_histogram=dict(sorted(histogram.items())),
                records_sha256=sha.hexdigest(), nominee_order='gain descending, SHA256(<4i seed17,a,b,c) ascending',
                nominees=chosen, helper_index_offset=222)


def construct(parent, triple, wrong_substitution=False, wrong_restore=False):
    a,b,c = triple
    need(len(set(triple)) == 3 and all(type(x) is int and 0 <= x < 439 for x in triple), 'chain operands')
    prep,target,_,cols,_,_ = split(parent)
    A,B,C = [cols[i] for i in triple]
    cols[b] = B ^ A
    cols[c] = C ^ (B if wrong_substitution else B ^ A)
    helper = [[0,a+222,[b+222]],[0,b+222,[c+222]]]
    middle = [[0,111+i,[222+j for j,col in enumerate(cols) if col >> i & 1]] for i in range(111)]
    out = deepcopy(parent)
    out['D'] = prep + helper + target + middle + target[::-1] + (helper if wrong_restore else helper[::-1]) + prep[::-1]
    return out


def stream(word):
    out = [('add',d,s) for section in ('D','A') for _,d,ss in word[section] for s in ss]
    for j,center in enumerate(word['ret']):
        out.append(('copy',661,center))
        out.extend(('add',111+i,661) for i,ss in enumerate(word['scatter']) if j in ss)
        out.append(('erase',661,center))
    out.extend(('add',d,s) for section in ('B','C') for _,d,ss in word[section] for s in ss)
    return out


def literal(word, reverse=False, boundary=True):
    rows = [1 << i for i in range(661)] + [0]
    values = [1]*662
    peak = 1
    instructions = stream(word)
    for kind,d,s in reversed(instructions) if reverse else instructions:
        if reverse:
            kind = {'copy':'erase','erase':'copy'}.get(kind,kind)
        if kind == 'add':
            if boundary: rows[d] ^= rows[s]
            values[d] += values[s]
        elif kind == 'copy':
            if boundary:
                need(rows[d] == 0, 'COPY into live scratch');rows[d] = rows[s]
            values[d] = values[s]
        else:
            if boundary:
                need(rows[d] == rows[s], 'ERASE mismatch');rows[d] = 0
            values[d] = 0
        peak = max(peak,values[d])
    if boundary:
        need(rows[-1] == 0, 'scratch remains live')
    return rows[:-1],peak


def dmap(word):
    rows = [1 << i for i in range(661)]
    for f,d,ss in word['D']:
        need(f == 0, 'D common zero frame')
        for s in ss:
            rows[d] ^= rows[s]
    return rows


def admitted(F,B):
    return 64*F**3*B**2 < 1 << 104 and (1 << 18)*F**5*B**4 < 1 << 192


def invoice(word):
    _,F = literal(word,boundary=False)
    _,B = literal(word,True,boundary=False)
    local,nine = 64*F**3*B**2,(1 << 18)*F**5*B**4
    return dict(ADDs=sum(x[0] == 'add' for x in stream(word)),D_ADDs=sum(len(x[2]) for x in word['D']),
                F=F,B=B,local_bound=str(local),nine_stage_bound=str(nine),
                local_bits=local.bit_length(),nine_stage_bits=nine.bit_length(),
                admitted=admitted(F,B),
                COPYs=9,ERASEs=9,helpers=439)


def paths(word):
    paths_ = [[x] for x in word['start']]
    frames = [set(x) for x in word['frames']]
    for section in ('D','A','B','C'):
        for f,d,ss in word[section]:
            for r in (d,*ss):
                if paths_[r][-1] != f:
                    need(frames[paths_[r][-1]] < frames[f], 'illegal frame move')
                    paths_[r].append(f)
    for r,f in enumerate(word['final']):
        if paths_[r][-1] != f:
            need(frames[paths_[r][-1]] < frames[f], 'illegal final move')
            paths_[r].append(f)
    return paths_


def owner(word):
    spec = importlib.util.spec_from_file_location('seed17_own',ROOT/CHECKER)
    mod = importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    dim,labels,flow,hyp,con,_ = mod.check(word)
    profile = Counter(dim.fdim[b]-dim.fdim[a] for p in paths(word) for a,b in itertools.pairwise(p))
    profile.update(t['rank'] for t in flow['totals'])
    return dict(hypotheses=hyp,conclusions=con,profile=dict(sorted(profile.items())),
                rank_mass=sum(r*n for r,n in profile.items()),copy_ranks=[t['rank'] for t in flow['totals']])


def exported(word):
    """Price the actual retained record exporter; keep its assertions enabled."""
    with tempfile.TemporaryDirectory(prefix='seed17 exported records ') as temp:
        root = Path(temp); path = root/'word.json.gz'
        path.write_bytes(gzip.compress(canonical(word),mtime=0))
        out = root/'records';out.mkdir()
        subprocess.run([sys.executable,'-I','-B',str(ROOT/EXPORTER),str(path),str(out)],
                       capture_output=True,text=True,check=True,timeout=60)
        raw = (out/'249-records.bin').read_bytes()
        need(len(raw) % 24 == 0, 'export record alignment')
        records = list(struct.iter_unpack('<6i',raw))
        counts = Counter(x[0] for x in records)
        rank_profile = Counter(x[4] for x in records if x[0] == 0)
        rank_profile.update(x[5] for x in records if x[0] == 2)
        need(dict(sorted(rank_profile.items())) == PROFILE, 'literal exporter paid profile')
        bounds = []
        for reverse in (False,True):
            values,peak,active = [1]*662,1,False
            for op,a,b,c,frame,phase in reversed(records) if reverse else records:
                if op == 0: continue
                if reverse and op in (2,3): op = 5-op
                if op == 1:
                    values[a] += abs(c)*values[b];peak = max(peak,values[a])
                elif op == 2:
                    need(not active, 'nested exporter COPY');values[b] = values[a];active = True
                else:
                    need(op == 3 and active, 'unmatched exporter ERASE');values[b] = 0;active = False
            need(not active, 'exporter unclosed copy')
            bounds.append(peak)
        bill = invoice(word)
        need(counts[1] == bill['ADDs'] and counts[2] == counts[3] == 9, 'actual primitive bill')
        need(bounds == [bill['F'],bill['B']], 'exporter complete positive bounds')
        return dict(ADDs=counts[1],MOVEs=counts[0],COPYs=counts[2],ERASEs=counts[3],
                    F=bounds[0],B=bounds[1],profile=dict(sorted(rank_profile.items())),
                    records_sha256=hashlib.sha256(raw).hexdigest())


def interaction_proof_checks(columns,triple):
    a,b,c = [columns[x] for x in triple]
    u,v = b.bit_count()-(a^b).bit_count()-2,c.bit_count()-(b^c).bit_count()-2
    G = b.bit_count()+c.bit_count()-(a^b).bit_count()-(a^b^c).bit_count()-4
    interaction = 2*(a & (b^c)).bit_count()-a.bit_count()
    active = (a | b | c).bit_count()
    need(u <= 0 and v <= 0 and G == u+v+interaction, 'exact joint interaction')
    slacks = []
    for A,B,C in itertools.product((0,1),repeat=3):
        U,V,Z = B-(B^A),C-(C^B),B+C-(B^A)-(C^B^A)
        slack = 2+2*U+V-3*Z
        need(slack >= 0, 'row inequality');slacks.append(slack)
    need(3*G <= 2*active+2*u+v-6, 'active-row cap')
    # Abstract sharp111-row support fixture, not columns asserted in the word.
    A = (1 << 72)-1
    B = ((1 << 111)-1) ^ ((1 << 35)-1)
    C = ((1 << 35)-1) | (((1 << 39)-1) << 72)
    U,V = B.bit_count()-(B^A).bit_count()-2,C.bit_count()-(C^B).bit_count()-2
    sharp = B.bit_count()+C.bit_count()-(B^A).bit_count()-(C^B^A).bit_count()-4
    need((U,V,sharp) == (0,0,72), 'sharp abstract cap')
    return dict(unilateral_gains=[u,v],joint_gain=G,interaction=interaction,
                active_rows=active,pattern_slacks=slacks,abstract_111_row_cap=72,
                sharp_abstract_support_sizes=[72,76,74])


def pins():
    record = load(HERE/'SOURCES.json')
    need(record['base_commit'] == 'ef5f39403610d231a0c27e8a6b4f08c10209bcd6', 'exact source base')
    for key,expected in [('inputs',INPUT_PATHS),('package_sources',PACKAGE_PATHS)]:
        paths_ = [entry['path'] for entry in record[key]]
        need(len(paths_) == len(set(paths_)) and set(paths_) == expected,
             'exact source inventory '+key)
    for entry in record['inputs']:
        raw = (ROOT/entry['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == entry['sha256'],
             'source pin '+entry['path'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == entry['git_blob'],
             'source Git blob '+entry['path'])
    for entry in record.get('package_sources',[]):
        need(hashlib.sha256((HERE/entry['path']).read_bytes()).hexdigest() == entry['sha256'],
             'package source pin '+entry['path'])
    return len(record['inputs'])+len(record.get('package_sources',[]))


def witness_only():
    """Fast local witness replay. This deliberately does not repeat the census."""
    source_count = pins()
    result,parent = load(HERE/'CERTIFICATE.json'),load(ROOT/PARENT)
    need(type(result['source_pins']) is int and result['source_pins'] == source_count, 'source pin coverage')
    need(result['new_kappa'] is False, 'scope marker')
    winner = result['winner'];a,b,c = winner['triple']
    _,_,_,cols,component,helpers = split(parent)
    need(all(i in helpers for i in (a,b,c)) and len({component[i] for i in (a,b,c)}) == 3,
         'winner component domain')
    interaction = interaction_proof_checks(cols,[a,b,c])
    need(type(winner['gain']) is int and winner['gain'] == interaction['joint_gain'], 'winner exact gain')
    word = construct(parent,[a,b,c])
    need(canonical(load(HERE/'CANDIDATE.json.gz')) == canonical(word), 'actual winning payload')
    need(canonical(invoice(word)) == canonical(winner['invoice']), 'actual complete invoice')
    need(winner['invoice']['admitted'] is True, 'both strict guards')
    expected = [(1 << i) ^ ((1 << (i-111)) if 111 <= i < 222 else 0) for i in range(661)]
    for reverse in (False,True):
        need(literal(word,reverse)[0] == expected, 'dirty witness endpoint')
    need(dmap(word) == dmap(parent) and paths(word) == paths(parent), 'D and frame boundaries')
    need(canonical(owner(word)) == canonical(result['owner']), 'actual owner invoice')
    need(canonical(exported(word)) == canonical(result['winner_export']), 'actual exported invoice')
    print('PASS_R439_CHAIN_WITNESS_ONLY columns=661 ADDs=11489 full_census_not_replayed')


def run():
    source_count = pins()
    parent = load(ROOT/PARENT)
    need(invoice(parent)['ADDs'] == 11500, 'frozen complete price')
    report = census(parent)
    baseline = invoice(parent)
    trials = []
    for a,b,c,gain,tie in report['nominees']:
        word = construct(parent,[a,b,c])
        bill = invoice(word)
        need(bill['ADDs'] == 11500-gain, 'complete chain price')
        need(dmap(word) == dmap(parent), 'arbitrary-dirt D compensation')
        trials.append(dict(triple=[a,b,c],gain=gain,tie=str(tie),invoice=bill))
    winner = next((x for x in trials if x['invoice']['admitted']),None)
    need(winner is not None, 'no admitted nominee; research receipt needs a scoped negative outcome')
    word = construct(parent,winner['triple'])
    expected = [(1 << i) ^ ((1 << (i-111)) if 111 <= i < 222 else 0) for i in range(661)]
    for reverse in (False,True):
        need(literal(parent,reverse)[0] == literal(word,reverse)[0] == expected, 'all661 dirty columns')
    need(paths(word) == paths(parent), 'ordered paths preserved')
    need(all(word[k] == parent[k] for k in parent if k != 'D'), 'only D changes')
    own0,own = owner(parent),owner(word)
    need(own == own0 and own['profile'] == PROFILE and own['rank_mass'] == 5129, 'retained owner/profile')
    baseline_export,winner_export = exported(parent),exported(word)
    need(baseline_export['MOVEs'] == winner_export['MOVEs'], 'no added MOVE')
    _,_,_,columns,component,helpers = split(parent)
    a,b,c = winner['triple']
    need(all(i in helpers for i in (a,b,c)) and len({component[i] for i in (a,b,c)}) == 3,
         'winner in exact frozen domain')
    interaction = interaction_proof_checks(columns,winner['triple'])
    controls = []
    def reject(name,fn):
        try: fn()
        except (ValueError,KeyError,TypeError,IndexError): controls.append(name);return
        raise ValueError('accepted negative control '+name)
    reject('same-order helper undo',lambda:need(dmap(construct(parent,winner['triple'],wrong_restore=True)) == dmap(parent),'dirty helper restoration'))
    reject('commuting column substitution',lambda:need(dmap(construct(parent,winner['triple'],wrong_substitution=True)) == dmap(parent),'ordered covectors'))
    bad = deepcopy(word);bad['D'].pop(236)
    reject('omitted preparation',lambda:need(dmap(bad) == dmap(parent),'D boundary'))
    bad = deepcopy(word);bad['D'].pop(237)
    reject('omitted second preparation',lambda:need(dmap(bad) == dmap(parent),'D boundary'))
    bad = deepcopy(word);bad['D'].pop(-237)
    reject('omitted restoration',lambda:need(dmap(bad) == dmap(parent),'D boundary'))
    bad = deepcopy(word);bad['D'].pop(-238)
    reject('omitted first restoration',lambda:need(dmap(bad) == dmap(parent),'D boundary'))
    bad = deepcopy(word);bad['D'][236][0] = 1
    reject('nonzero D frame',lambda:dmap(bad))
    reject('undercharged wrapper',lambda:need(winner['invoice']['ADDs'] == 11500-winner['gain']-4,'four paid gates'))
    reject('repeated helper',lambda:construct(parent,[0,0,1]))
    reject('boolean helper',lambda:construct(parent,[True,2,3]))
    need(admitted((1 << 24)-1,1 << 13) and admitted((1 << 18)-1,1 << 21), 'strict guard positive controls')
    reject('local guard exact equality',lambda:need(admitted(1 << 24,1 << 13),'local104 strict equality'))
    reject('nine-stage guard exact equality',lambda:need(admitted(1 << 18,1 << 21),'nine192 strict equality'))
    bad = deepcopy(word);bad['A'][0][2] = []
    reject('changed raw continuation',lambda:need(all(bad[k] == parent[k] for k in parent if k != 'D'),'only D changes'))
    return dict(base_commit='ef5f39403610d231a0c27e8a6b4f08c10209bcd6',seed=17,status='finite-construction',
                census=report,baseline=baseline,trials=trials,winner=winner,owner=own,
                full_word_sha256=digest(word),full_endpoint_sha256=digest(expected),negative_controls=controls,
                baseline_export=baseline_export,winner_export=winner_export,interaction=interaction,
                source_pins=source_count,new_kappa=False,scope='Finite scalar word and conditional original rank profile; no hosted supplier adoption.')


def main():
    need(sys.argv[1:] in ([],['--write'],['--witness-only']), 'usage: verify.py [--write|--witness-only]')
    if sys.argv[1:] == ['--witness-only']:
        witness_only();return
    result = run()
    path = HERE/'CERTIFICATE.json'
    if sys.argv[1:] == ['--write']:
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        parent = load(ROOT/PARENT)
        (HERE/'CANDIDATE.json.gz').write_bytes(gzip.compress(canonical(construct(parent,result['winner']['triple'])),mtime=0))
    else:
        need(canonical(load(path)) == canonical(result), 'complete certificate mismatch')
        parent = load(ROOT/PARENT)
        need(canonical(load(HERE/'CANDIDATE.json.gz')) == canonical(construct(parent,result['winner']['triple'])), 'candidate payload mismatch')
    print('PASS_R439_NEUTRAL_HELPER_CHAIN ADDs=11500->%d gain=%d eligible=%d columns=661 controls=%d no_new_kappa' %
          (result['winner']['invoice']['ADDs'],result['winner']['gain'],result['census']['unilateral_nonpositive'],len(result['negative_controls'])))


if __name__ == '__main__':
    main()
