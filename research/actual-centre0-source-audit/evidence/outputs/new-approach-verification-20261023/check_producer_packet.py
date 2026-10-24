#!/usr/bin/env python3
"""Independent source-packet audit, not a native producer or emitted word.

Reverse sensitivities extract literal centre suffix factors. Exact rational
low-rank algebra checks source-supplied edit specifications independently.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import os
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPO = ROOT / 'integer-mult-bounds'
HEAD = '86e474038e05f99a76d41f71d81946ad2327e4a4'
BASE = 'research/native-involutive-dual/'
PACKET = ROOT / 'outputs/seven-mode-producer-feasibility-20261023'
PINS = {
 'INITIAL-DERIVATION.json': '2ea2e0a05f7fcdd16fc00857abf0cf37371dcf63a82e5d37c00902092864d3bd',
 'CORRECTED-DERIVATION.json': 'd40187525bd50b77f277de46575097c6d34a18af96802e7aec7b4f49213465d4',
}
SOURCE_PINS = {
 'SOURCE-WORD.json.gz': '7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05',
 'R.json': '7b33b6dfb494c6eafe6d87a08d6a2c2e0681e56429495b2b27949040f0f63cd1',
 'INVOLUTIVE-WORD.json.gz': 'ff2999f022e93e05a250160808aa3c32a08041039d7edfb01068c0308f50c138',
 'BACKWARD-WORD.json.gz': 'dfedcaf1d2318cf6c45da87e0947668c1dae9496f299789528a78d4ab7ba4096',
 'NORMALIZERS.json': 'ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da',
}


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def packet_hashes():
    hashes = {p: sha256((PACKET/p).read_bytes()).hexdigest() for p in PINS}
    require(hashes == PINS, 'construction packet changed')
    return hashes


def read(name):
    b = subprocess.check_output(['git', '-C', str(REPO), 'show', HEAD+':'+BASE+name],
                                env=os.environ | {'GIT_NO_LAZY_FETCH': '1'})
    require(sha256(b).hexdigest() == SOURCE_PINS[name], name + ': source pin')
    return b


def field(x):
    require(x[0] in ('L','C'), 'unrecognized field')
    require(x[0] != 'C' or x[1] == 0, 'unrecognized scratch')
    return 632 if x[0] == 'C' else x[1]


def accum(dst, src, factor):
    for key, q in list(src.items()):
        v = dst.get(key, Q()) + q*factor
        if v:
            dst[key] = v
        else:
            dst.pop(key, None)


def pull_scalar(rows, event):
    op = event[1]
    d = field(op[1])
    sensitivity = rows[d].copy()
    if op[0] == 'clear':
        rows[d] = {}
    elif op[0] == 'copy':
        rows[d] = {}
        accum(rows[field(op[2])], sensitivity, Q(1))
    elif op[0] == 'add':
        accum(rows[field(op[2])], sensitivity, Q(op[3],op[4]))
    elif op[0] == 'scale':
        rows[d] = {k:q*Q(op[2],op[3]) for k,q in sensitivity.items() if q*Q(op[2],op[3])}
    else:
        raise RuntimeError('unknown scalar opcode '+str(op))


def pull_warp(rows, event):
    d, g = field(event[1]), event[2]
    # Words are stored in chronological order. Traversing backward prepends g.
    rows[d] = {(label, word[1:] if word and word[0] == -g else (g,)+word):q
               for (label,word),q in rows[d].items()}


def suffix_factors(program):
    # All 633 final fields are observed, so X/helper/scratch leakage is checked.
    rows = [{(i,()): Q(1)} for i in range(633)]
    found = {}
    first = next(i for i,e in enumerate(program) if e[0] == 'center')
    for index in range(len(program)-1, first-1, -1):
        event = program[index]
        if event[0] == 'scalar':
            pull_scalar(rows, event)
        elif event[0] == 'warp':
            pull_warp(rows, event)
        elif event[0] == 'center':
            found[index] = rows[632].copy()
            rows[632] = {}  # independent impulse at this literal overwritten output
        else:
            # These change native charts or label phases, and have identity
            # action on the authenticated normalized scalar/free-word model.
            require(event[0] in ('climb','phase','adapter','residual_adapter'), 'unknown source event')
    require(len(found) == 8, 'eight literal centres')
    vectors = []
    for index, sensitivity in sorted(found.items()):
        require(all(not word for (_,word) in sensitivity), 'nonempty centre suffix word')
        require(all(112 <= out < 224 for out,_ in sensitivity), 'centre leaks beyond Y bank')
        vectors.append((index,[sensitivity.get((112+i,()),Q()) for i in range(112)]))
    return vectors


def prefix_factor(program, centre_index):
    copy = program[centre_index-1]
    require(copy[0] == 'scalar' and copy[1][:2] == ['copy',['C',0]], 'centre copy')
    rows = [{} for _ in range(633)]
    rows[field(copy[1][2])] = {(0,()):Q(1)}
    for event in reversed(program[:centre_index-1]):
        if event[0] == 'scalar':
            pull_scalar(rows,event)
        elif event[0] == 'warp':
            pull_warp(rows,event)
        else:
            require(event[0] in ('climb','phase','adapter','residual_adapter'), 'unexpected earlier centre')
    require(all(not word for row in rows for (_,word) in row), 'nonempty prefix word')
    return [row.get((0,()),Q()) for row in rows]


def mm(a,b):
    return [[sum((x*y for x,y in zip(row,col)),Q()) for col in zip(*b)] for row in a]


def main():
    before = packet_hashes()
    initial = json.loads((PACKET/'INITIAL-DERIVATION.json').read_text())
    corrected = json.loads((PACKET/'CORRECTED-DERIVATION.json').read_text())
    raw = {p:read(p) for p in SOURCE_PINS}
    source = json.loads(gzip.decompress(raw['SOURCE-WORD.json.gz']))
    involutive = json.loads(gzip.decompress(raw['INVOLUTIVE-WORD.json.gz']))
    R = [[Q(v) for v in row] for row in json.loads(raw['R.json'])]
    p, ip = source['programs']['forward'], involutive['program']
    canonical = source['canonical']
    J = involutive['selected_ports']
    require(J == [0,7,20,23,86,93,108,111], 'selected row set')
    K = [[R[k][i]/4 for k in range(8)] for i in range(112)]
    U = [[K[i][k]*(1-12*(i in J)) for k in range(8)] for i in range(112)]
    require(mm(R,K) == [[Q(14*(i==j)) for j in range(8)] for i in range(8)], 'RK=14I')
    require(mm(R,U) == [[Q(2*(i==j)) for j in range(8)] for i in range(8)], 'RU=2I')
    F = [[Q(i==j)-sum(U[i][k]*R[k][j] for k in range(8)) for j in range(112)] for i in range(112)]
    require(F == [[Q(v) for v in row] for row in involutive['F']], 'source F matrix')
    suffix = suffix_factors(p)
    r0 = [row[0] for row in R]
    target = [sum(r0[k]*R[k][i] for k in range(8)) for i in range(112)]
    centre_minors = []
    for k,(index,v) in enumerate(suffix):
        require(index == initial['centers'][k]['source_index'], 'source centre index')
        require(v == [Q(q) for q in initial['centers'][k]['output_column']], 'independent suffix')
        require(v == [R[k][i]/4 for i in range(112)], 'physical centre aligns row k of R')
        minor = next(((i,j,v[i]*target[j]-v[j]*target[i]) for i in range(112)
                      for j in range(i+1,112) if v[i]*target[j] != v[j]*target[i]), None)
        require(minor is not None, 'a physical centre unexpectedly matches PORT0 mode')
        centre_minors.append({'centre':k, 'source_index':index, 'rows':list(minor[:2]),
                              'determinant':str(minor[2])})
    n0, v0 = suffix[0]
    cov = prefix_factor(p,n0)
    require(cov[:112] == R[0], 'centre0 prefix main factor')
    require(not any(cov[112:224]) and cov[632] == 0, 'prefix Y/scratch inputs')
    helper = {i:q for i,q in enumerate(cov[224:632],224) if q}
    require(len(helper) == 45, 'helper inventory')
    require(helper == {int(i):Q(q) for i,q in initial['center0_input_factor']['helper'].items()}, 'helper factor')
    require(all(canonical['start'][i] == 0 for i in helper), 'ground helper inputs')
    N = 6596
    require(len(ip) == N+len(p)+456, 'literal source composition length')
    centre_edit = initial['constructible_edit_spec']['center_restore']
    require(centre_edit['involutive_index'] == N+n0 == 17907, 'restoration index')
    require(ip[N+n0] == centre_edit['old'] == ['scalar',['clear',['C',0]],0], 'old literal clear')
    require(centre_edit['new'] == p[n0], 'restored literal source centre')
    pre = {}
    for event in ip[:N]:
        require(event[0] == 'scalar' and event[1][0] == 'add' and event[2] == 0, 'precomp event type/frame')
        op = event[1]
        key = (field(op[1]),field(op[2]))
        require(key not in pre, 'duplicate old precomp coefficient')
        pre[key] = Q(op[3],op[4])
    require(len(pre) == N, 'initial precomp count')
    original_pre = pre.copy()
    deltas = {}
    for i,v in enumerate(v0):
        if v:
            for h,q in helper.items():
                key = (112+i,h)
                old,delta = pre.get(key,Q()), -v*q
                new = old+delta
                deltas[key] = (old,delta,new)
                if new:
                    pre[key] = new
                else:
                    pre.pop(key,None)
    require(len(deltas) == 2520 and len(pre) == 7202, 'revised helper precomp count')
    declared_deltas = {(i,h):(Q(old),Q(delta),Q(new)) for i,h,old,delta,new
                       in initial['constructible_edit_spec']['precomp_deltas']}
    require(deltas == declared_deltas, 'all declared helper delta coefficients')
    require(all(canonical['start'][i] == canonical['start'][h] == 0 for i,h in pre), 'precomp frame binding')

    tail_start = N+len(p)
    require(tail_start == 28045, 'repair tail source start')
    retunes = []
    for z,owner in enumerate(J):
        block = ip[tail_start+57*z:tail_start+57*(z+1)]
        require(len(block) == 57, 'repair block width')
        coefficients = {}
        for event in block:
            if event[0] == 'scalar' and event[1][0] == 'add' and event[1][1] == ['C',0]:
                op = event[1]
                require(op[2][0] == 'L' and 0 <= op[2][1] < 112, 'repair source owner')
                require(op[2][1] not in coefficients, 'duplicate repair source')
                coefficients[op[2][1]] = Q(op[3],op[4])
        old = {j:3*sum(R[k][owner]*R[k][j] for k in range(8)) for j in range(112)}
        old = {j:q for j,q in old.items() if q}
        require(coefficients == old, 'source repair coefficient factor')
        new = {j:3*sum(R[k][owner]*R[k][j] for k in range(1,8)) for j in range(112)}
        new = {j:q for j,q in new.items() if q}
        spec = corrected['repair_retunes'][z]
        require(spec['port'] == owner and {int(j):Q(q) for j,q in spec['new_coefficients'].items()} == new,
                'corrected repair coefficient map')
        require(spec['old_rank1_event'] == next(e for e in block if e[0] == 'center'), 'retained rank1 event')
        retunes.append({'owner':owner,'changed':old != new,'old_ADDs':len(old),'new_ADDs':len(new)})
    require(sum(x['changed'] for x in retunes) == 4, 'four actual repair rows change')
    require(sum(x['old_ADDs'] for x in retunes) == corrected['repair_ADDs_old'] == 424,
            'old repair ADD count')
    require(sum(x['new_ADDs'] for x in retunes) == corrected['repair_ADDs_new'] == 532,
            'new repair ADD count')
    backward = json.loads(gzip.decompress(raw['BACKWARD-WORD.json.gz']))
    bp = backward['program']
    backward_pre = {}
    for event in bp[:N]:
        require(event[0] == 'scalar' and event[1][0] == 'add' and event[2] == 0,
                'backward precomp event type/frame')
        op = event[1]
        key = (field(op[1]),field(op[2]))
        require(key not in backward_pre, 'duplicate backward precomp coefficient')
        backward_pre[key] = Q(op[3],op[4])
    require(backward_pre == {(h,i):-q for (i,h),q in original_pre.items()}, 'source negative-transpose precomp')
    back_restore = corrected['backward']['source_restore']
    require(back_restore['source_index'] == 11332 and back_restore['backward_word_index'] == 17928,
            'backward centre indices')
    require(bp[17928] == back_restore['old'], 'backward old centre clear')
    require(source['programs']['backward'][11332] == back_restore['new'] == ['center',0,0,254,8],
            'backward actual source centre')
    for z,(forward_spec,back_spec) in enumerate(zip(corrected['repair_retunes'],corrected['backward']['repair_retunes'])):
        require({int(j):Q(q) for j,q in back_spec['new_coefficients'].items()} ==
                {int(j):-Q(q) for j,q in forward_spec['new_coefficients'].items()},
                'corrected backward repair exact negative coefficients')
        block = bp[tail_start+57*z:tail_start+57*(z+1)]
        require(back_spec['center'] == next(e for e in block if e[0] == 'center'),
                'retained conjugate backward rank1 event')

    failed = [[F[i][j]+v0[i]*R[0][j]-Q(3*(i==0))*target[j] for j in range(112)] for i in range(112)]
    require([str(q) for q in failed[0]] == initial['center0_actual']['row0'], 'failed G row0')
    require([str(row[0]) for row in failed] == initial['center0_actual']['col0'], 'failed G col0')
    x = [row[0] for row in failed]
    square00 = sum(failed[0][j]*x[j] for j in range(112))
    require(x[:2] == [Q(1,4),Q(-1,2)] and square00 == 10, 'failed G witness')
    # Construction's desired Pi_PORT0 pullback at (0,0) equals 1, in contrast to 1/4.
    desired00 = F[0][0] + U[0][0]*target[0]/4 + sum(U[0][k]*r0[k]*target[0]/4 for k in range(1,8))
    require(desired00 == 1 and failed[0][0] != desired00, 'PORT0 projector mismatch')

    actual = [[F[i][j]+U[i][0]*R[0][j] for j in range(112)] for i in range(112)]
    require(actual == [[Q(q) for q in row] for row in corrected['F_actual']], 'corrected source endpoint')
    require(any(actual[0][j] != Q(j==0) for j in range(112)), 'old fixed-unit shortcut must stay held')
    # RU=2I and D^2=D imply (I-UDR)^2=I, without executing an owner code.
    profile = Counter()
    for event in ip:
        if event[0] == 'climb':
            profile[event[5]] += 1
        elif event[0] == 'center':
            profile[event[4]] += 1
    profile[8] += 1
    require({int(k):v for k,v in corrected['paid_profile'].items()} == dict(profile), 'changed profile')
    require(profile == Counter({1:2209,2:412,3:510,4:127,5:40,8:1}), 'one H8 with all eight H1 repairs')
    require(corrected['retained_rank1_calls'] == 8, 'retained repair count')
    helper_ranks = Counter(len(canonical['frames'][canonical['final'][i]])
                           -len(canonical['frames'][canonical['start'][i]]) for i in range(224,632))
    require({int(k):v for k,v in corrected['full_independent_inputs']['helper_native_target_rank_profile'].items()}
            == dict(helper_ranks), 'independent helper endpoint census')
    after = packet_hashes()
    result = {'status':'PASS_SOURCE_PACKET_AUDIT_ONLY', 'source_head':HEAD,
              'source_pins':SOURCE_PINS, 'packet_hashes_before':before,'packet_hashes_after':after,
              'method':'reverse sensitivities of literal source suffix/prefix plus independent rational algebra; no emitter/native execution',
              'all_eight_physical_centres_reject_PORT0_match':centre_minors,
              'centre0_factors':{'suffix':'R[0,:]^T/4','prefix_main':'R[0,:]',
                                 'independent_helper_inputs':len(helper),'non_Y_output_leakage':False},
              'helper_precomp':{'original_nonzero_ADDs':N,'coefficient_deltas':len(deltas),
                                'revised_nonzero_ADDs':len(pre),'all_deltas_match':True},
              'failed_initial_candidate':{'G00':str(x[0]),'G10':str(x[1]),'G_squared_00':str(square00),
                                          'status':'REJECTED_AS_REQUIRED'},
              'corrected_candidate':{'endpoint':'I-U(I-E0)R','involution':'RU=2I and (I-E0)^2=I-E0',
                                     'repair_retunes':retunes,'paid_profile':dict(sorted(profile.items())),
                                     'helper_native_rank_profile':dict(sorted(helper_ranks.items())),
                                     'backward_negative_transpose_source_specification':'PASS',
                                     'status':'SOURCE_SPECIFICATION_VERIFIED_NO_NATIVE_RUN'},
              'old_fixed_e0_unit_fixture':'HOLD_INVALID_FOR_CORRECTED_FAMILY',
              'native_execution':False,'caller_or_compiler_admission':False,'new_kappa':None}
    out = HERE/('PRODUCER-PACKET-RESULT-OPTIMIZED.json' if sys.flags.optimize else 'PRODUCER-PACKET-RESULT.json')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'result':str(out),'failed_G_squared_00':str(square00)}))


if __name__ == '__main__':
    main()
