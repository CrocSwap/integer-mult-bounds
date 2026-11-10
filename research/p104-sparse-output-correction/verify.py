"""Check the exact source, full word, correction and bounded search.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha1, sha256
import copy
import gzip
import json
import runpy
import sys

P = Path(__file__).resolve().parent
C = runpy.run_path(str(P/'correction.py'))
need = C['need']


def authenticate(raw, pin):
    need(sha256(raw).hexdigest() == pin['sha256'], 'Frozen SHA256')
    need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'], 'Frozen Git blob')


def reject(f):
    try:
        f()
    except (ValueError, IndexError, KeyError):
        return
    raise ValueError('Invalid control was accepted')


def growth(word):
    rows = [{i: Q(1)} for i in range(word['public']+word['owned_fields'])]
    peak = Q(1); coefficient = Q(1); at = -1
    for k, e in enumerate(word['program']):
        op, r = e[:2]
        if op == 'MOVE':
            continue
        if op in ('INIT', 'CLEAR'):
            rows[r] = {}
        elif op == 'SCALE':
            rows[r] = {j: Q(e[2])*v for j, v in rows[r].items()}
        else:
            if op == 'COPY':
                rows[r] = {}
            C['add'](rows[r], rows[e[2]], Q(e[3]))
        value = sum(abs(x) for x in rows[r].values())
        if value > peak:
            peak, at = value, k
        coefficient = max(coefficient, max((abs(x) for x in rows[r].values()), default=Q(0)))
    return dict(maximum_row_l1=str(peak), first_event=at, maximum_entry=str(coefficient))


def columns(program, n):
    # Direct scalar values for each basis input. This does not use row addition.
    out = []
    for j in range(n):
        v = [Q(int(i == j)) for i in range(n)]
        for e in program:
            if e[0] == 'SCALE':
                v[e[1]] *= Q(e[2])
            else:
                v[e[1]] += Q(e[3])*v[e[2]]
        out.append(v)
    return out


def run():
    pins = json.loads((P/'SOURCES.json').read_text())['retained_predecessors']
    for pin in pins:
        raw = (P/pin['local']).read_bytes(); authenticate(raw, pin)
        reject(lambda raw=raw, pin=pin: authenticate(bytes([raw[0]^1])+raw[1:], pin))
    old_word = json.loads(gzip.decompress((P/'inputs/pr6529-WORD.json.gz').read_bytes()))
    construction = json.loads((P/'inputs/pr6529-CONSTRUCTION.json').read_text())
    old = construction['correction']; cut = construction['raw_event_count']
    need(old_word['program'][cut:] == old and len(old) == 569, 'Exact source correction tail')
    d = C['data'](old)
    # Exhaust every unit pivot and dyadic scale in this declared finite domain.
    best = None; count = 0; minimizers = []
    for a in range(-4, 5):
        for b in range(-4, 5):
            for sx in (-1, 1):
                for sy in (-1, 1):
                    x, y = sx*Q(2)**a, sy*Q(2)**b
                    for p in sorted(d[0]):
                        if abs(d[0][p]) != 1:
                            continue
                        for q in sorted(d[1]):
                            if abs(d[1][q]) != 1:
                                continue
                            for order in (-1, 1):
                                candidate = C['construct'](d, p, q, x, y, order)
                                key = (C['allowance'](candidate), len(candidate))
                                count += 1
                                spec = [p, q, str(x), str(y), order]
                                if best is None or key < best:
                                    best, minimizers = key, [spec]
                                elif key == best:
                                    minimizers.append(spec)
    # Among the minimum-cost programs, minimize the correction prefix norm.
    ranked = []
    for spec in minimizers:
        p, q, x, y, order = spec
        candidate = C['construct'](d, p, q, Q(x), Q(y), order)
        matrix, peak = C['matrix'](candidate, 770)
        need(matrix == C['matrix'](old, 770)[0], 'Every minimum program has the exact source map')
        ranked.append((peak, spec, candidate))
    peak, spec, new = min(ranked, key=lambda t: (t[0], t[1]))
    need(best == (696, 74), 'Complete declared optimization')
    need(columns(old, 799) == columns(new, 799), 'All independent scalar columns')
    want = C['matrix'](old, 770)[0]
    for i in range(len(new)):
        bad = new[:i]+new[i+1:]
        need(C['matrix'](bad, 770)[0] != want, 'Every omitted gate changes the operator')
        bad = copy.deepcopy(new); bad[i][-2] = str(2*Q(bad[i][-2]))
        need(C['matrix'](bad, 770)[0] != want, 'Every doubled gate changes the operator')
    for spec0 in [(383, 1, Q(1), Q(1), 1), (3, 1, Q(0), Q(1), 1), (3, 1, Q(1), Q(1), 0)]:
        reject(lambda spec0=spec0: C['construct'](d, *spec0))
    reject(lambda: C['allowance']([['SCALE', 3, '3', 127]]))
    reject(lambda: C['allowance']([['ADD', 3, 1, '1/3', 127]]))
    new_word = copy.deepcopy(old_word); new_word['program'] = old_word['program'][:cut]+new
    need(all(new_word[k] == old_word[k] for k in old_word if k != 'program'), 'Exact boundary and frame headers')
    need([e for e in old_word['program'] if e[0] in ('MOVE', 'INIT', 'CLEAR', 'COPY')]
         == [e for e in new_word['program'] if e[0] in ('MOVE', 'INIT', 'CLEAR', 'COPY')], 'Exact native and owned events')
    L = runpy.run_path(str(P/'inputs/local.py'))
    old_local, new_local = L['replay'](old_word), L['replay'](new_word)
    source_result = json.loads((P/'inputs/pr6529-RESULT.json').read_text())
    need(json.loads(json.dumps(old_local)) == source_result['local'], 'Complete predecessor scalar receipt')
    need({k:v for k,v in old_local.items() if k != 'real_scalar_allowance'}
         == {k:v for k,v in new_local.items() if k != 'real_scalar_allowance'}, 'Every other local charge is fixed')
    need(old_local['real_scalar_allowance']-new_local['real_scalar_allowance'] == 4962, 'Complete scalar saving')
    transpose = L['reverse_columns'](new_word)
    for index in (cut, len(new_word['program'])-1):
        bad = copy.deepcopy(new_word); del bad['program'][index]
        reject(lambda bad=bad: L['replay'](bad))
    bad = copy.deepcopy(new_word); bad['program'][cut][-1] = 0
    reject(lambda: L['replay'](bad))
    old_growth, new_growth = growth(old_word), growth(new_word)
    return dict(status='PASS_P104_74_GATE_CORRECTION', source_head='44b0d0e8961201ac1656490b4384a7752e1cd9c5',
                rank=2, changed_rows=28, invariant_pairings=4, forms=[{str(k):str(v) for k,v in f.items()} for f in d[:2]],
                programs_searched=count, minimizing_programs=len(minimizers), selected=spec,
                correction=new, correction_before=dict(gates=len(old), scalar=C['allowance'](old), prefix_l1=str(C['matrix'](old,770)[1])),
                correction_after=dict(gates=len(new), scalar=C['allowance'](new), prefix_l1=str(peak)),
                complete_before=old_local, complete_after=new_local, complete_growth_before=old_growth, complete_growth_after=new_growth,
                transpose=transpose, independent_correction_columns=799, omission_controls=74, doubled_controls=74,
                whole_word_controls=3, invalid_controls=5, source_corruptions=len(pins),
                saved_real_scalar_per_native=4962, saved_eighteen_calls=89316,
                scope='Exact source-bound ordinary correction reduction. Native paid profile and kappa are unchanged.')


if __name__ == '__main__':
    result = run()
    result = json.loads(json.dumps(result))
    if '--write-result' in sys.argv:
        (P/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(result == json.loads((P/'RESULT.json').read_text()), 'Exact complete receipt')
    print(json.dumps({k:result[k] for k in ('status','programs_searched','selected','correction_before','correction_after','complete_growth_before','complete_growth_after','saved_real_scalar_per_native')},sort_keys=True))
