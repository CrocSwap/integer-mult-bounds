"""Rebuild the coordinate-permuted PR71 words and their exact paid bound."""
import sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts/experiments'))
from binary_frame_replay import replay
from binary_frame_profile_prepare import prepare
from split_pair_arithmetic import refine,audit
import binary_frame_math as arithmetic
from pin_split_pair_sources import required_paths
from fractions import Fraction as Q
from collections import Counter
from itertools import combinations
from math import comb
from hashlib import sha256
import gzip,json,subprocess,tempfile

def required():
    names=required_paths()|{'research/split-pair/SOURCE.json','certificates/split-pair-kappa.json',
        '.github/workflows/verify.yml'}
    names.update(str(p.relative_to(ROOT)) for p in HERE.iterdir() if p.is_file() and p.name not in ('SOURCE.json','validation.json'))
    return names

def sources():
    manifest=json.loads((HERE/'SOURCE.json').read_text())
    assert required()<=set(manifest['files']),'Source closure incomplete'
    for name,digest in manifest['files'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name

def relabel(word,config):
    h=word['h'];order=config['order'];assert sorted(order)==list(range(h))
    perm={old:new for new,old in enumerate(order)}
    assert perm=={int(k):v for k,v in config['mapping'].items()}
    triples=list(combinations(range(h),3));lookup={t:i for i,t in enumerate(triples)}
    index={i:lookup[tuple(sorted(perm[x] for x in triple))] for i,triple in enumerate(triples)}
    def mask(m):return sum(1<<perm[i] for i in range(h) if m>>i&1)
    word['frames']=[[mask(c),mask(u)] for c,u in word['frames']]
    word['sources']={str(index[int(i)]):s for i,s in word['sources'].items()}
    v=word['v'];word['scatter']=[[v+index[a-v],b] for a,b in word['scatter']]
    word['outputs']=[[s,g,perm[c],sorted(perm[x] for x in triple)] for s,g,c,triple in word['outputs']]
    return word

def exact(profiles):
    cert=json.loads((HERE/'certificate.json').read_text());baseline=json.loads((HERE/'baseline-pr71.json').read_text())
    N=comb(23,3)*comb(25,3);m=575;W=2*N+sum(N//p['v']*p['R'] for p in profiles)
    L=sum(N//p['v']*p['loss'] for p in profiles)
    rows=Counter({1:19*N,21:2*N,17:2*N,481:2*N})
    for p in profiles:
        h=p['h'];rep=N//p['v'];bank=rep*p['R']
        assert p['crt_disagreements']==0 and p['v']==comb(h,3)
        assert sum(t*n for t,n in enumerate(p['blocks']))==h*p['R']+h*(h-1)==p['rank_sum']
        rows.update({t:n*rep for t,n in enumerate(p['blocks']) if t and n})
        rows[h]+=bank;rows[m-2*h]+=bank;rows[1]+=2*N;rows[h-2]+=2*N
    bit=dict(m=m,N=N,W=W,L=L,total_rank=sum(t*n for t,n in rows.items()),child_multiplicities=dict(sorted(rows.items())))
    assert bit['total_rank']==m*W-N+L
    assert arithmetic.js(bit)==cert['bit']
    saving=Q(cert['bit_saving']);moment=refine.exact_moment(m,W,rows,saving)
    rejected=refine.exact_moment(m,W,rows,saving+Q(1,10**18))
    assert moment['upper']<1<rejected['lower']
    assert arithmetic.js(moment)==cert['exact_moment']
    bounds=audit.independent_moment(arithmetic.js(bit),saving,arithmetic.js(moment['terms']))
    next_bounds=audit.independent_moment(arithmetic.js(bit),saving+Q(1,10**18),arithmetic.js(moment['terms']))
    assert bounds[1]<1<next_bounds[0]
    bridge=baseline['finite_bridge'];assert bridge['bit']['W']==W
    result=refine.assemble(bridge,saving,Q(1,10**12),10**18)
    assert arithmetic.js(result)==cert['assembly'] and str(result['kappa'])==cert['kappa']
    prior=baseline['bit'];oldrows={int(t):n for t,n in prior['child_multiplicities'].items()}
    assert refine.exact_moment(m,W,oldrows,saving)['lower']>1
    print('PASS exact conditional kappa',result['kappa'],'47 constraints, seven margins, independent bounds and next-grid controls')

def verify():
    sources();profiles=[]
    with tempfile.TemporaryDirectory(prefix='coordinate-flags-') as directory:
        work=Path(directory);exe=work/'profiles'
        subprocess.run(['c++','-O3','-std=c++17','-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),str(ROOT/'scripts/experiments/binary_frame_profiles.cpp'),'-o',str(exe)],check=True)
        for h in (23,25):
            original=json.loads(gzip.decompress((ROOT/f'certificates/split-pair-word-{h}.json.gz').read_bytes()))
            config=json.loads((HERE/f'order-{h}.json').read_text());word=relabel(original,config)
            raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
            assert raw==gzip.decompress((HERE/f'word-{h}.json.gz').read_bytes())
            path=work/f'word-{h}.json';path.write_bytes(raw);checked=replay(path)
            stored=json.loads((HERE/f'replay-{h}.json').read_text());assert arithmetic.js(checked)==stored['replay']
            trans=work/f'transitions-{h}.bin';receipt=prepare(path,trans);assert arithmetic.js(receipt)==stored['transitions']
            subprocess.run([str(exe),str(trans)],check=True)
            profile=json.loads(Path(str(trans)+'.profiles.json').read_text());assert profile==json.loads((HERE/f'profiles-{h}.json').read_text())
            profiles.append(profile);print('PASS complete relabelled physical word and profile',h,flush=True)
    exact(profiles)
if __name__=='__main__':verify()
