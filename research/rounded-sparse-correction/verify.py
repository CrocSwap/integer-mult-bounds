"""Prove the actual rounding classes and exact additive-error budgets."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import gzip
import json
import random
import runpy
import sys

sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
sys.path.insert(0,str(P))
from precision import transfer,reverse_transfer,rounded,exact,inverse,nearest,merge,need


def encode(x):
    if isinstance(x,Q): return str(x)
    if isinstance(x,dict): return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [encode(v) for v in x]
    return x


def digest(rows):
    h = sha256()
    for row in rows:
        h.update(json.dumps([[k,str(v)] for k,v in sorted(row.items())],separators=(',',':')).encode()+b'\n')
    return h.hexdigest()


def authenticate():
    for pin in json.loads((P/'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            path = Path(pin['path']).relative_to('research/rounded-sparse-correction')
            need(sha256((P/path).read_bytes()).hexdigest() == pin['sha256'],'Source hash: '+str(path))


def classes(program,forms):
    a,b = forms;rows = [{i:Q(1)} for i in range(799)];sources = []
    for t,e in enumerate(program):
        r,s = e[1:3];c = Q(e[3])
        if c.denominator > 1:
            source = rows[s]
            alpha,beta = source.get(3,Q(0)),source.get(1,Q(0))
            wanted = {};merge(wanted,a,alpha);merge(wanted,b,beta)
            need(source == wanted and alpha.denominator == beta.denominator == 1,
                 'Every fractional source is an exact integral combination of the two input forms')
            need(c.denominator in (2,4),'Quarter-grid divisors')
            sources.append([t,str(alpha),str(beta),str(c)])
        merge(rows[r],rows[s],c)
        if c.denominator > 1: rows[r][799+t] = Q(1)
    return sources


def observed(program,initial,whole_accumulator=False):
    # Fraction.__round__ is separate from the integer runtime quantizer.
    actual = list(initial);ideal = list(map(Q,initial));peak = Q(0);patterns = []
    for e in program:
        r,s = e[1:3];c = Q(e[3]);ideal[r] += c*ideal[s]
        actual[r] = round(Q(actual[r])+c*actual[s]) if whole_accumulator else actual[r]+round(c*actual[s])
        defect = Q(actual[r])-ideal[r];peak = max(peak,abs(defect));patterns.append(defect)
    return actual,ideal,peak,patterns


def rejects(action):
    try: action()
    except ValueError: return
    raise ValueError('Negative control accepted')


def main():
    authenticate();C = runpy.run_path(str(P/'inputs/correction.py'))
    old_word = json.loads(gzip.decompress((P/'inputs/pr6529-WORD.json.gz').read_bytes()))
    construction = json.loads((P/'inputs/pr6529-CONSTRUCTION.json').read_text())
    source = json.loads((P/'inputs/RESULT.json').read_text())
    old,new = construction['correction'],source['correction'];cut = construction['raw_event_count']
    need(old_word['program'][cut:] == old and len(new) == 74,'Actual source correction tail')
    need(all(e[0] == 'ADD' and e[-1] == old_word['final'][e[1]] == old_word['final'][e[2]] == 127 for e in new),
         'Every operand at the actual common output frame')
    data = C['data'](old);a,b = data[:2]
    need(all(v.denominator == 1 for form in (a,b) for v in form.values()),'Integral input forms')
    need(a.get(3) == b.get(1) == 1 and a.get(1,0) == b.get(3,0) == 0,'Independent residue representatives')
    candidates = []
    for p,q,x,y,order in product(sorted(a),sorted(b),(-1,1),(-1,1),(-1,1)):
        if abs(a[p]) != 1 or abs(b[q]) != 1: continue
        candidate = C['construct'](data,p,q,Q(x),Q(y),order)
        if (C['allowance'](candidate),len(candidate)) != (696,74): continue
        forward = transfer(candidate);back = transfer(inverse(candidate))
        candidates.append(dict(spec=[p,q,x,y,order],forward=forward[2:],inverse=back[2:]))
    need(len(candidates) == source['minimizing_programs'] == 44,'All unit-scale source minimizers')
    need(all(r['forward'] == r['inverse'] == (Q(28),Q(1),Q(1)) for r in candidates),
         'Every minimum-cost candidate has the same sharp fractional budget')
    budgets = {};witnesses = {};checks = 0;source_matrix = None
    for label,program in (('old',old),('new',new),('old_inverse',inverse(old)),('new_inverse',inverse(new))):
        for noise in ('all','fractional'):
            rows,prefix,signal,peak,output = transfer(program,noise=noise)
            for r,row in enumerate(rows):
                need(row == reverse_transfer(program,r,noise=noise),'Forward and backward exact error transfers')
                checks += len(row)
            peak_prefix_witness = None
            for t,(r,signal_bound,error_bound) in enumerate(prefix):
                functional = reverse_transfer(program[:t+1],r,noise=noise)
                need(sum(abs(v) for j,v in functional.items() if j<799) == signal_bound
                     and sum(abs(v) for j,v in functional.items() if j>=799) == error_bound,
                     'Separate check of every prefix bound')
                if error_bound == peak and peak_prefix_witness is None:
                    signs = {j-799:Q(1 if v>0 else -1) for j,v in functional.items() if j>=799}
                    need(exact(program[:t+1],[0]*799,signs)[r] == peak,'Attained prefix error witness')
                    peak_prefix_witness = dict(event=t,target=r,errors=signs,value=peak)
            matrix = [{j:v for j,v in row.items() if j < 799} for row in rows]
            if label == 'old': source_matrix = matrix
            if label == 'new': need(matrix == source_matrix,'Exact source correction on all799fields')
            key = label+'_'+noise
            budgets[key] = dict(peak_signal=signal,peak_error=peak,output_error=output,
                                output_signal=max(sum(abs(v) for j,v in row.items() if j<799) for row in rows),
                                prefix=prefix,output_masses=[sum(abs(v) for j,v in row.items() if j>=799) for row in rows],
                                transfer_hash=digest(rows))
            target = next(r for r,row in enumerate(rows) if sum(abs(v) for j,v in row.items() if j>=799) == output)
            signs = {j-799:Q(1 if v>0 else -1) for j,v in rows[target].items() if j>=799}
            actual = exact(program,[0]*799,signs)
            need(actual[target] == output,'Attained additive-error output witness')
            witnesses[key] = dict(target=target,errors=signs,value=output)
            witnesses[key+'_prefix'] = peak_prefix_witness
            if label == 'new' and noise == 'fractional':
                target = max(range(799),key=lambda r:sum(abs(v) for j,v in rows[r].items() if j<799))
                signs = {j:Q(1 if v>0 else -1) for j,v in rows[target].items() if j<799}
                values = [signs.get(j,Q(0)) for j in range(799)]
                need(exact(program,values)[target] == 15,'Sharp incoming-error gain')
                witnesses['input_gain'] = dict(target=target,inputs=signs,value=15)
    fraction_sources = {name:classes(program,(a,b)) for name,program in (('forward',new),('inverse',inverse(new)))}
    need(all(len(v) == 25 for v in fraction_sources.values()),'All25fractional products')
    residue_cases = 0;largest = Q(0);actual_witness = None;trace = {}
    patterns = {}
    for direction,program in (('forward',new),('inverse',inverse(new))):
        for av,bv in product(range(8),repeat=2):
            initial = [0]*799;initial[3]=av;initial[1]=bv
            result,ideal,peak,pattern = observed(program,initial)
            need(peak <= Q(1,2),'All-prefix nearest-grid error in every residue class')
            need(rounded(program,initial[:],32,trace=trace) == result,'Separate rounding implementations')
            need(rounded(program,result[:],32,reverse=True) == initial,'Exact data return')
            for form in (a,b):
                need(sum(v*result[j] for j,v in form.items()) == sum(v*initial[j] for j,v in form.items()),
                     'Both integer input forms remain exact invariants')
            if peak > largest:
                largest = peak;actual_witness = dict(direction=direction,a=av,b=bv,peak=peak)
            patterns[direction,av,bv] = pattern
            residue_cases += 1
    dirty = [1]*799
    bad = observed(new,dirty,True)[0]
    wrong = observed(inverse(new),bad,True)[0]
    wrong_witness = dict(input='all799fields equal one',changed_fields=[i for i in range(799) if wrong[i]!=dirty[i]])
    need(largest == Q(1,2) and wrong_witness['changed_fields'],'Sharp actual error and wrong-rounding control')
    rng = random.Random(106537);large_cases = 0
    for direction,program in (('forward',new),('inverse',inverse(new))):
        for bits in (1,4,16,64,128):
            for _ in range(4):
                initial = [rng.randrange(-(1 << bits)+1,1 << bits) for _ in range(799)]
                bound = max(map(abs,initial));width = max(2,1+(84*bound).bit_length())
                result,ideal,peak,pattern = observed(program,initial)
                av = int(sum(v*initial[j] for j,v in a.items())) % 8
                bv = int(sum(v*initial[j] for j,v in b.items())) % 8
                need(pattern == patterns[direction,av,bv],'Actual error depends only on the64proved residue classes')
                need(rounded(program,initial[:],width) == result,'Large signed words')
                need(rounded(program,result[:],width,reverse=True) == initial,'Large exact data return')
                large_cases += 1
    for numerator,denominator in product(range(-513,514),(1,2,4)):
        need(nearest(numerator,denominator) == round(Q(numerator,denominator)),'Exact symmetric nearest rounding')
        need(nearest(-numerator,denominator) == -nearest(numerator,denominator),'Odd rounding for inverse signs')
    need(abs(Q(3,4)-(3//4)) > Q(1,2),'Floor is not a nearest quantizer')
    rejects(lambda:rounded(new,[1]*799,2))
    rejects(lambda:rounded([['ADD',0,1,'1/3',127]],[0,1],16))
    rejects(lambda:rounded([['SCALE',0,'1/2',127]],[1],16))
    rejects(lambda:rounded(new,[Q(1,2)]+[0]*798,16))
    unit = [0]*799;unit[1] = 1
    need(exact(new,unit)[342] == Q(1,2),'Half-integer output gives the global uniform grid lower bound')
    result = dict(status='PASS_ROUNDED_SPARSE_CORRECTION',source_head='8bc9f991afe9fde83700ff86e520230eaa4595e7',
                  scalar_gates=74,fractional_products=25,minimum_cost_candidates=44,
                  budget_summary={k:{j:v for j,v in row.items() if j not in ('prefix','output_masses')} for k,row in budgets.items()},
                  compared_transfer_entries=checks,actual_residue_cases=residue_cases,large_signed_cases=large_cases,
                  exact_quantizer_cases=3081,actual_sharp_error=Q(1,2),actual_witness=actual_witness,
                  wrong_accumulator_rounding_witness=wrong_witness,rounded_work=trace,negative_controls=6,
                  scope='Correction-only nearest-grid data bijection and sharp error; no full native or physical tariff or kappa')
    payload = dict(budgets=budgets,witnesses=witnesses,candidates=candidates,fractional_sources=fraction_sources)
    for filename,value in (('BUDGETS.json',payload),('RESULT.json',result)):
        value = encode(value)
        if '--write' in sys.argv: (P/filename).write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
        else: need(value == json.loads((P/filename).read_text()),'Exact '+filename)
    print(json.dumps(encode(result),sort_keys=True))


if __name__ == '__main__': main()
