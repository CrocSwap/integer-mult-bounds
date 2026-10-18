"""One target transvection after PR967 helper mixing; fully paid finite search.

Prepared for @woklerx with substantial OpenAI Codex assistance. Apache-2.0.
PR915/926 bitplane and PR967 theon199 supply the credited frozen circuits.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT='research/r439-helper-stars-seed19/candidate.json.gz'


def need(value,reason):
    if not value: raise ValueError(reason)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def load(path):
    path=Path(path)
    raw=path.read_bytes()
    if path.suffix=='.gz': raw=gzip.decompress(raw)
    return json.loads(raw)


def rows(parent):
    need((parent['v'],parent['R'])==(111,439),'source dimensions')
    gates=parent['D'][527:638]
    need(len(gates)==111 and all(f==0 and d==111+i and all(222<=s<661 for s in src) and len(src)==len(set(src))
         for i,(f,d,src) in enumerate(gates)),'source middle shape')
    return [sum(1<<(s-222) for s in src) for _,_,src in gates]


def assemble(parent,a,b):
    middle=copy.deepcopy(parent['D'][527:638])
    changed=rows(parent)[a]^rows(parent)[b]
    middle[a][2]=[222+j for j in range(439) if changed>>j&1]
    gate=[0,111+a,[111+b]]
    word=dict(parent)
    word['D']=parent['D'][:527]+[gate]+middle+[gate]+parent['D'][638:]
    return word


def positive(word,reverse=False):
    values=[1]*661
    maximum=1
    sections=('C','B','scatter','A','D') if reverse else ('D','A','scatter','B','C')
    for section in sections:
        if section=='scatter':
            for j in (reversed(range(9)) if reverse else range(9)):
                value=values[word['ret'][j]]
                for i,sources in enumerate(word['scatter']):
                    if j in sources:
                        values[111+i]+=value
                        maximum=max(maximum,values[111+i])
        else:
            for _,d,sources in reversed(word[section]) if reverse else word[section]:
                values[d]+=sum(values[s] for s in sources)
                maximum=max(maximum,values[d])
    return maximum


def bill(word):
    f,b=positive(word),positive(word,True)
    return {'ADDs':sum(len(g[2]) for sec in ('D','A','B','C') for g in word[sec])+sum(map(len,word['scatter'])),
            'D_ADDs':sum(len(g[2]) for g in word['D']), 'F':f,'B':b,
            'local':str(64*f**3*b**2),'nine_stage':str((1<<18)*f**5*b**4)}


def admitted(receipt):
    return int(receipt['local'])<1<<104 and int(receipt['nine_stage'])<1<<192


def run(parent):
    matrix=rows(parent)
    baseline=bill(parent)
    need(baseline['ADDs']==11783 and baseline['F']==72847 and baseline['B']==10394084,'PR967 baseline bill')
    census=[]
    nominees=[]
    for a in range(111):
        for b in range(111):
            if a==b:continue
            gain=matrix[a].bit_count()-(matrix[a]^matrix[b]).bit_count()-2
            tie=hashlib.sha256(f'14:{a}:{b}'.encode()).hexdigest()
            census.append([a,b,gain,tie])
            if gain>0:
                receipt=bill(assemble(parent,a,b))
                need(receipt['ADDs']==baseline['ADDs']-gain,'paid gain')
                nominees.append({'a':a,'b':b,'gain':gain,'tie':tie,'bill':receipt,'admitted':admitted(receipt)})
    nominees.sort(key=lambda x:(-x['gain'],x['tie']))
    accepted=[x for x in nominees if x['admitted']]
    best=accepted[0] if accepted else None
    result={'format':'r439-target-retune/1','seed':14,'base_commit':'2921874911956718fcaaaf9396fe8267b3cfa9f0',
            'domain':'one directed target transvection after the fixed PR915 target basis in the fixed PR967 helper-star circuit, with literal inverse restoration',
            'ordered_pairs':len(census),'census_sha256':hashlib.sha256(canonical(census)).hexdigest(),
            'positive_gain_pairs':len(nominees),'admitted_positive_pairs':len(accepted),
            'baseline':baseline,'nominees':nominees,'selected':best,
            'stopping_rule':'All 12210 directed scores; exact full-word pricing of every strictly improving nominee; no iteration or restart.'}
    return result,assemble(parent,best['a'],best['b']) if best else parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    certificate,word=run(load(ROOT/PARENT))
    if args.write:
        (HERE/'CERTIFICATE.json').write_text(json.dumps(certificate,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        (HERE/'candidate.json.gz').write_bytes(gzip.compress(canonical(word),mtime=0))
    else:
        need(canonical(certificate)==canonical(load(HERE/'CERTIFICATE.json')),'certificate mismatch')
        need(canonical(word)==canonical(load(HERE/'candidate.json.gz')),'candidate payload mismatch')
    print(json.dumps({k:certificate[k] for k in ('ordered_pairs','positive_gain_pairs','admitted_positive_pairs','selected')},sort_keys=True),flush=True)


if __name__=='__main__':main()
