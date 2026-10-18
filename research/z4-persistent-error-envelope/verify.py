"""Exact error impulses at every ADD/cut of the pinned z4 echo words.

Apache-2.0. Prepared for ywz65 with substantial OpenAI Codex assistance.
The pinned emitter is reused; the error analysis is new and independent.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIDTH = 56


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def pins():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            raw = (ROOT/row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source drift: '+row['path'])


def words():
    path = ROOT/'research/z4-persistent-pair-seed57/inputs/PR1391-verify.py'
    spec = importlib.util.spec_from_file_location('pinned_pr1391',path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    def emit(states, blocks):
        body = mod.lift_word(mod.batch_word(states,blocks=blocks),list(range(8))+list(range(32,56)))
        return ([('ADD',32+i,8+i,1) for i in range(24)] + body +
                [('ADD',32+i,8+i,-1) for i in range(24)] + mod.inverse_word(body))
    one = emit([0,1,2,3,0,0],(0,1,2,0,1))
    joint = emit([0,1,2,3,0,1,2,3,0,1,0],(0,1,2,0,1)*2)
    separate = one+one
    receipt = json.loads((ROOT/'research/z4-persistent-pair-seed57/RESULT.json').read_text())
    for name,word,key in [('separate',separate,'two_separate_calls'),('joint',joint,'ten_child_joint')]:
        digest = hashlib.sha256(json.dumps(word,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
        need(digest == receipt[key]['word_sha256'], 'literal word hash: '+name)
    return {'separate':separate,'joint':joint,
            'separate_inverse':mod.inverse_word(separate),'joint_inverse':mod.inverse_word(joint)}


def combine(a,b,sign):
    out = dict(a)
    for i,v in b.items():
        out[i] = out.get(i,0)+sign*v
        if not out[i]:
            del out[i]
    return out


def scan(word,n):
    state = [{i:1} for i in range(n)]
    errors = [{} for _ in range(n)]
    weights = []
    l1 = [1]*n
    gamma = [0]*n
    weighted = [0]*n
    amplitude = 1
    gpeak = dict(value=0,cut=0,row=0,coefficients=[])
    mpeak = dict(value=0,cut=0,row=0,coefficients=[])
    for index,(kind,d,s,sign) in enumerate(word):
        need(type(d) is int and 0 <= d < n, 'destination')
        if kind == 'ADD':
            need(type(s) is int and 0 <= s < n and s != d and sign in (-1,1), 'ADD')
            weights.append(l1[d]+l1[s])
            state[d] = combine(state[d],state[s],sign)
            errors[d] = combine(errors[d],errors[s],sign)
            errors[d][len(weights)-1] = 1
        else:
            need(kind == 'NEG' and s is None and sign == 0, 'exact NEG')
            state[d] = {i:-v for i,v in state[d].items()}
            errors[d] = {i:-v for i,v in errors[d].items()}
        l1[d] = sum(abs(v) for v in state[d].values())
        gamma[d] = sum(abs(v) for v in errors[d].values())
        weighted[d] = sum(abs(v)*weights[i] for i,v in errors[d].items())
        amplitude = max(amplitude,l1[d])
        for value,peak in [(gamma[d],gpeak),(weighted[d],mpeak)]:
            if value > peak['value']:
                peak.update(value=value,cut=index+1,row=d,coefficients=sorted([i,v] for i,v in errors[d].items()))
    g,m = gpeak['value'],mpeak['value']
    q = (m+2*g-1).bit_length() if m+2*g else 0
    return {'records':len(word),'adds':len(weights),'negs':len(word)-len(weights),
            'prefix_input_row_l1':amplitude,'gamma_all_cuts':gpeak,
            'weighted_all_cuts':mpeak,'gamma_endpoint':max(gamma),
            'weighted_endpoint':max(weighted),'fractional_guard_bits':q,
            'threshold_denominator':m+2*g,
            'weights_sha256':hashlib.sha256(canonical(weights).encode()).hexdigest()}, weights


def reverse_witness(word,cut,row,n,weights):
    # Independent covector traversal of only the specified output coordinate.
    # If current v is a linear functional after a gate, v*A gives its value
    # before the gate; the post-ADD error coefficient is v[d].
    covector = [0]*n
    covector[row] = 1
    coefficients = {}
    add_index = sum(g[0] == 'ADD' for g in word[:cut])-1
    for kind,d,s,sign in reversed(word[:cut]):
        if kind == 'ADD':
            if covector[d]:
                coefficients[add_index] = covector[d]
            add_index -= 1
            covector[s] += sign*covector[d]
        else:
            covector[d] = -covector[d]
    return sorted([i,v] for i,v in coefficients.items())


def attain(word,cut,row,n,coefficients,weights,weighted):
    # Direct perturbed scalar execution attains the independent-error-box norm.
    state = [0]*n
    signs = dict(coefficients)
    j = 0
    for kind,d,s,sign in word[:cut]:
        if kind == 'ADD':
            state[d] += sign*state[s]
            coeff = signs.get(j,0)
            if coeff:
                state[d] += (1 if coeff>0 else -1)*(weights[j] if weighted else 1)
            j += 1
        else:
            state[d] = -state[d]
    return state[row]


def verify_analysis(word,n):
    result,weights = scan(word,n)
    for key,weighted in [('gamma_all_cuts',False),('weighted_all_cuts',True)]:
        peak = result[key]
        coeff = reverse_witness(word,peak['cut'],peak['row'],n,weights)
        need(coeff == peak['coefficients'], 'transposed impulse mismatch')
        need(attain(word,peak['cut'],peak['row'],n,coeff,weights,weighted) == peak['value'],
             'sharp independent-error witness')
    q=result['fractional_guard_bits']; g=result['gamma_all_cuts']['value']; m=result['weighted_all_cuts']['value']
    need((1 << q) >= m+2*g and (q == 0 or (1 << (q-1)) < m+2*g),'least uniform power-of-two guard')
    return result


def controls():
    # Canceling exact circuit still accumulates rounding errors.
    word=[('ADD',0,1,1),('ADD',0,1,-1)]
    r=verify_analysis(word,2)
    need(r['gamma_endpoint']==2 and r['weighted_endpoint']==5, 'cancellation positive control')
    rejected=[]
    def reject(name,condition):
        need(not condition,'control accepted: '+name)
        rejected.append(name)
    reject('endpoint_identity_implies_zero_error',r['gamma_endpoint']==0)
    reject('operation_count_is_weighted_error_bill',r['weighted_endpoint']==len(word))
    reject('one_bit_undercharge',(1 << (r['fractional_guard_bits']-1))>=r['threshold_denominator'])
    coeff=reverse_witness(word,2,0,2,[2,3])
    reject('omitted_roundoff_event',coeff[:-1]==r['gamma_all_cuts']['coefficients'])
    # Sign ordering matters for impulse witnesses, despite a possible same norm.
    negword=[('ADD',0,1,1),('NEG',0,None,0),('ADD',0,1,1)]
    signed=verify_analysis(negword,2)
    reject('discarded_NEG_sign',all(v>0 for _,v in signed['gamma_all_cuts']['coefficients']))
    return rejected


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    pins()
    result={'schema_version':1,'model':'ADD local additive error; exact NEG; arbitrary exact input; every chronological cut',
            'words':{name:verify_analysis(word,WIDTH) for name,word in words().items()},'controls':controls()}
    # Keep every exact event:coefficient pair without thousands of vertical
    # JSON formatting lines. This is serialization only, after witness checks.
    for report in result['words'].values():
        for key in ['gamma_all_cuts','weighted_all_cuts']:
            peak=report[key]
            peak['nonzero_impulses']=len(peak['coefficients'])
            peak['coefficients']=';'.join(str(i)+':'+str(v) for i,v in peak['coefficients'])
    need(result['words']['joint']['prefix_input_row_l1']==42 and result['words']['separate']['prefix_input_row_l1']==30,'prefix positive source control')
    path=HERE/'RESULT.json'
    if args.write:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    need(canonical(result)==canonical(json.loads(path.read_text(encoding='utf-8'))),'receipt mismatch')
    for name,r in result['words'].items():
        print(name,'Gamma',r['gamma_all_cuts']['value'],'M',r['weighted_all_cuts']['value'],'q',r['fractional_guard_bits'])
    print('PASS_Z4_PERSISTENT_ERROR_ENVELOPE words=4 controls=5 no_host_precision_admission')


if __name__=='__main__':main()
