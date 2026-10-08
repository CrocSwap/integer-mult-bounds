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
from width_bridge import bridge_for_width
from fractions import Fraction as Q
from collections import Counter
from itertools import combinations
from math import comb
from hashlib import sha256
import gzip,json,subprocess,tempfile

def required():
    from pin_balanced_split_sources import required_paths as balanced_paths
    names=balanced_paths()|{'research/balanced-split/SOURCE.json','certificates/balanced-split-kappa.json','.github/workflows/combined-flags.yml'}
    archive=ROOT/'references/frame-compiler/pr76'
    names.update(str(f.relative_to(ROOT)) for f in archive.rglob('*') if f.is_file())
    names.update(str(f.relative_to(ROOT)) for f in HERE.iterdir() if f.is_file() and f.name not in ('SOURCE.json','validation.json'))
    return names

def original_path(h):
    return ROOT/'references/frame-compiler/pr76/research/round7-scheduling/selected-both/word-23.json.gz' if h==23 else ROOT/'certificates/balanced-split-word-25.json.gz'

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
    cert=json.loads((HERE/'certificate.json').read_text())
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
    bridge=bridge_for_width(json.loads((ROOT/'references/frame-compiler/pr48/research/copied-fixed/certificate.json').read_text())['finite_bridge'],W)
    assert arithmetic.js(bridge)==cert['finite_bridge']
    result=refine.assemble(bridge,saving,Q(1,10**12),10**18)
    assert arithmetic.js(result)==cert['assembly'] and str(result['kappa'])==cert['kappa']
    for path in (ROOT/'references/frame-compiler/pr76/research/round7-scheduling/selected-both/arithmetic.json',ROOT/'certificates/balanced-split-kappa.json'):
        old=json.loads(path.read_text());prior=old.get('profile',old.get('bit'))
        oldrows={int(t):n for t,n in prior['child_multiplicities'].items()}
        assert refine.exact_moment(prior['m'],prior['W'],oldrows,saving)['lower']>1
        assert Q(cert['kappa'])>Q(old['kappa'])
    print('PASS exact conditional kappa',result['kappa'],'47 constraints, seven margins, independent bounds and next-grid controls')

def verify():
    sources();profiles=[]
    with tempfile.TemporaryDirectory(prefix='coordinate-flags-') as directory:
        work=Path(directory);exe=work/'profiles'
        subprocess.run(['c++','-O3','-std=c++17','-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),str(ROOT/'scripts/experiments/binary_frame_profiles.cpp'),'-o',str(exe)],check=True)
        for h in (23,25):
            original=json.loads(gzip.decompress((original_path(h)).read_bytes()))
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
