"""Exact finite evidence for the written complex-coefficient decoder extension.

The universal argument is PROOF.md, with PR968's stated flat-classification
premise retained. No finite Q(i) sample is presented as that proof.
Prepared for @woklerx with substantial OpenAI Codex assistance, Apache-2.0.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE='2921874911956718fcaaaf9396fe8267b3cfa9f0'
SOURCES={'research/complex-frame-pair-decoders/'+name for name in ('PROOF.md','README.md','verify.py')}
spec=importlib.util.spec_from_file_location('gaussian_exact',HERE/'exact.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
G=ex.G


def need(value,reason):
    if not value:raise ValueError(reason)


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
def read(path):return json.loads(path.read_text(encoding='utf-8'))


def check_pins(pins):
    need(pins['base_commit']==BASE and set(pins['files'])==SOURCES,'exact source inventory')
    for name,digest in pins['files'].items():
        raw=(ROOT/name).read_bytes().replace(b'\r\n',b'\n')
        need(hashlib.sha256(raw).hexdigest()==digest,'source digest')


def normal_pattern(rs,normal):
    zeros=[r for r in rs if not sum(G(r[j])*normal[j] for j in range(8))]
    real=[x.r for x in normal];imag=[x.i for x in normal]
    real_imag_rank=ex.rankq([real,imag])
    dim=ex.rankq(zeros)
    need(dim<=8-real_imag_rank,'zero-flat codimension')
    need(dim<7 or real_imag_rank==1,'dimension-seven forces real-proportionality')
    support=sum((r not in zeros)<<i for i,r in enumerate(rs))
    representative=None
    for t in range(122):
        w=[x+t*y for x,y in zip(real,imag)]
        candidate=sum((sum(x*y for x,y in zip(r,w))!=0)<<i for i,r in enumerate(rs))
        if candidate==support:
            representative=t;break
    need(representative is not None,'finite generic real representative')
    return {'real_imag_rank':real_imag_rank,'root_zero_dimension':dim,'root_zero_count':len(zeros),'realifier_parameter':representative}


def run():
    pins=read(HERE/'SOURCES.json');check_pins(pins)
    result=subprocess.run([sys.executable,'-I','-B',str(HERE/'replay_source.py')],capture_output=True,text=True)
    need(result.returncode==0,'source fact replay: '+result.stderr)
    inherited=json.loads(result.stdout)
    need(inherited['d7_orbit']==1080 and len(inherited['census'])==8 and len(inherited['chain'])==25,'required predecessor coverage')
    rs=ex.roots()
    source_map={max(tuple(r),tuple(-x for x in r)):i for i,r in enumerate(inherited['root_lines'])}
    need(set(source_map)==set(rs) and len(rs)==120,'independent E8 enumeration')
    order=[source_map[r] for r in rs]
    pairing=[sum(((sum(x*y for x,y in zip(r,s))//4+1)%2)<<j for j,s in enumerate(rs)) for r in rs]
    need(ex.rank2(pairing)==9 and all((row>>j&1)==(inherited['pairing_rows'][order[i]]>>order[j]&1)
         for i,row in enumerate(pairing) for j in range(120)),'all pairing entries and rank')
    phase=[[G(1,1)*x for x in row] for row in ex.eye()]
    isotropic=ex.eye()
    isotropic[0][0]=isotropic[0][1]=G(1)
    isotropic[1][0]=G(0,1);isotropic[1][1]=G(0,-1)
    seeded=ex.eye();rng=random.Random(44)
    for _ in range(12):
        d,s=rng.sample(range(8),2)
        coefficient=G(rng.choice((-2,-1,1,2)),rng.choice((-1,1)))
        seeded[d]=[x+coefficient*y for x,y in zip(seeded[d],seeded[s])]
    examples=[]
    for name,a in (('support-preserving phase',phase),('isotropic cross-term coincidence',isotropic),('seed44 twelve complex shears',seeded)):
        b=ex.dual(a)
        need(ex.full_identity(rs,a,b),'all-entry ordinary-transpose identity')
        patterns=[normal_pattern(rs,col) for col in ex.transpose(a)+ex.transpose(b)]
        sa,sb=ex.supports(rs,a),ex.supports(rs,b)
        profiles=[]
        for p in range(25):
            live=((1<<120)-1)^((1<<p)-1)
            costs=[ex.rank2([pairing[i]&right&live for i in range(120) if (left&live)>>i&1]) for left,right in zip(sa,sb)]
            # Explicit live intersection avoids any use of complex coefficient magnitude.
            need(sum(costs)>=max(72-p,56),'complex example violates claimed floor')
            profiles.append({'p':p,'costs':costs,'total':sum(costs)})
        examples.append({'name':name,'A':ex.encoded(a),'B':ex.encoded(b),'patterns':patterns,'profiles':profiles,'identity_entries':14400})
    # Independently verify the inherited real attaining decoders in Q(i), after phase scaling.
    srcroots=inherited['root_lines'];f0=inherited['frame0'];pairs=inherited['example']['pairs']
    attainments=[]
    for p in range(25):
        item=inherited['chain'][str(p)]
        if p<=8:
            cols=[[G(x)/2 for x in srcroots[k]] for k in f0]
        else:
            cols=[[G(x)/2 for x in srcroots[a]] for a,b in pairs]
        a=ex.transpose(cols)
        # Independent nonzero phase for each column preserves its support.
        for k in range(8):
            phase_k=G(1,1+(k+44)%3)
            for i in range(8):a[i][k]=a[i][k]*phase_k
        b=ex.dual(a)
        removed={max(tuple(srcroots[k]),tuple(-x for x in srcroots[k])) for k in item['punctured']}
        live=sum((r not in removed)<<i for i,r in enumerate(rs))
        sa,sb=ex.supports(rs,a),ex.supports(rs,b)
        costs=[ex.rank2([pairing[i]&right&live for i in range(120) if (left&live)>>i&1]) for left,right in zip(sa,sb)]
        need(sum(costs)==max(72-p,56)==item['cost'],'phase-scaled attaining chain')
        if p in (0,8,16,24):need(ex.full_identity(rs,a,b),'phase-scaled chain identity')
        attainments.append({'p':p,'total':sum(costs),'costs':costs})
    controls=[]
    def reject(label,fn):
        try:fn()
        except ValueError:controls.append(label)
        else:raise ValueError('accepted false claim: '+label)
    a,b=isotropic,ex.dual(isotropic)
    acol,bcol=ex.transpose(a),ex.transpose(b)
    need(acol[0]==bcol[1] and sum(x*x for x in acol[0])==0,'isotropic cross-term equality witness')
    reject('unrestricted cross-term nonparallel assertion',lambda:need(acol[0]!=bcol[1],'complex isotropy'))
    real_a=[[G(x.r) for x in row] for row in phase];real_b=[[G(x.r) for x in row] for row in ex.dual(phase)]
    need(ex.supports(rs,real_a)==ex.supports(rs,phase) and ex.supports(rs,real_b)==ex.supports(rs,ex.dual(phase)),'projection retains exact support')
    reject('support-preserving real projection preserves duality',lambda:need(ex.full_identity(rs,real_a,real_b),'projection identity'))
    reject('Hermitian transpose substitution',lambda:need(ex.full_identity(rs,a,[[x.conjugate() for x in row] for row in b]),'ordinary transpose required'))
    reject('assign dimension seven to isotropic witness',lambda:need(normal_pattern(rs,acol[0])['root_zero_dimension']==7,'dimension-six witness'))
    changed=copy.deepcopy(b);changed[0][0]=changed[0][0]+1
    reject('mutated dual coefficient',lambda:need(ex.full_identity(rs,a,changed),'all-entry matrix identity'))
    mutated=copy.deepcopy(pins);mutated['files'].pop(next(iter(SOURCES)))
    reject('removed source pin',lambda:check_pins(mutated))
    mutated=copy.deepcopy(pins);mutated['files'][next(iter(SOURCES))]='0'*64
    reject('changed source digest',lambda:check_pins(mutated))
    return {'status':'PASS_COMPLEX_DECODER_FIELD_EXTENSION_S44','seed':44,'base_commit':BASE,
            'sources':pins,'inherited':inherited,'examples':examples,'attaining_chain':attainments,
            'negative_controls':controls,'root_pairing_entries':14400,
            'theorem':'For arbitrary complex D,T with exactly eight columns and D T^transpose = 2G on all live pairs, p<=24 implies cost>=max(72-p,56). Existing real attainments show sharpness over puncture sets of each size.',
            'premises':'PR968 finite facts replayed; its standard real E8 hyperplane-flat classification (F6) and written real geometric lemmas remain inherited. Quantified complex extension requires PROOF.md, not finite examples.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
    receipt=run();path=HERE/'CERTIFICATE.json'
    if args.write:path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    else:need(canonical(receipt)==canonical(read(path)),'complete certificate mismatch')
    print('PASS_COMPLEX_DECODER_FIELD_EXTENSION_S44 p=0..24 examples=3 attaining=25 pairing=14400 controls='+str(len(receipt['negative_controls'])))


if __name__=='__main__':main()
