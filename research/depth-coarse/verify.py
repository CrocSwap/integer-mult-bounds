"""Independent literal-word/profile/exact certificate acceptance boundary.

Explicit scatter binding follows the verification correction in rfu08 PR64.
Substantial OpenAI Codex assistance. Retained all-size hypotheses remain.
"""
import sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,gzip,hashlib,itertools,json,os,shlex,shutil,subprocess,tempfile
from fractions import Fraction as Q
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts/experiments'))
from binary_frame_replay import replay
from binary_frame_profile_prepare import prepare
import binary_frame_math as arithmetic
from bindings import refine,audit
from construction import activate,compile_axis,compose

def source_check():
    source=json.loads((HERE/'SOURCE.json').read_text())
    for name,digest in source['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'Source/artifact changed: '+name

def literal_binding(word):
    """Exact ports, terminals and every literal J; no cancelling gate exemption."""
    d=json.loads(gzip.decompress(word.read_bytes()))
    h,v,R=d['h'],d['v'],d['R']
    assert type(h) is int and h in (23,25)
    triples=list(itertools.combinations(range(h),3));assert type(v) is int and v==len(triples)
    assert type(R) is int and R>0
    valid=lambda n,limit:type(n) is int and 0<=n<limit
    sources=d['sources'];assert type(sources) is dict and set(sources)=={str(i) for i in range(v)}
    assert all(valid(s,R) for s in sources.values()) and len(set(sources.values()))==v
    frames=d['frames'];assert len(frames)==len({tuple(f) for f in frames})
    for a,b,g in d['ops']:
        assert valid(a,R) and valid(b,R) and a!=b and valid(g,len(frames))
    for s,a,b in d['events']:
        assert valid(s,R) and type(a) is int and -1<=a<len(frames) and valid(b,len(frames))
    expected=[];terminals=set();inventory=set();centers=set()
    index={t:i for i,t in enumerate(triples)}
    for s,g,common,triple in d['outputs']:
        assert valid(s,R) and valid(g,len(frames)) and valid(common,h)
        assert s not in terminals;terminals.add(s)
        assert type(triple) is list and all(valid(x,h) for x in triple)
        t=tuple(triple);assert t==tuple(sorted(set(t))) and common in t
        if len(t)==1:
            assert t==(common,) and common not in centers;centers.add(common)
            targets=[i for i,t3 in enumerate(triples) if common in t3]
        else:
            assert len(t)==3 and t in index
            targets=[index[t]]
        assert (common,t) not in inventory;inventory.add((common,t))
        expected.extend([[v+i,2*v+s] for i in targets])
    assert centers==set(range(h)) and len(terminals)==h+3*v
    complete={(c,(c,)) for c in range(h)}|{(c,t) for t in triples for c in t}
    assert inventory==complete
    assert d['scatter']==expected,'Literal scatter must equal complete ordered output incidence list'
    return d

def arithmetic_check(work):
    for h in (23,25):shutil.copy2(HERE/f'axis-{h}.json',work/f'axis-{h}.json')
    result=compose(work)
    accepted=json.loads((work/'certificate.json').read_text())
    expected=json.loads((HERE/'certificate.json').read_text())
    assert accepted==expected,'Exact certificate changed'
    selection=json.loads((HERE/'selection.json').read_text())
    ledger=json.loads((HERE/'menu-ledger.json').read_text())
    assert selection==ledger['selected']
    import menu
    assert menu.check()==ledger
    for h in (23,25):
        receipt=json.loads((HERE/f'axis-{h}.json').read_text())
        assert receipt['source']['choices']==selection[str(h)]
        assert receipt==json.loads((HERE/f"menu/{selection[str(h)]}-{h}.json").read_text())
    p=accepted
    for name in ('pr71','pr75'):
        old=json.loads((HERE/f'comparisons/{name}.json').read_text())
        oldrows={int(t):n for t,n in old['bit']['child_multiplicities'].items()}
        lower=refine.exact_moment(old['bit']['m'],old['bit']['W'],oldrows,Q(p['bit_saving']))['lower']
        assert lower>1 and Q(p['kappa'])>Q(old['kappa']),name+' complete profile not excluded'
    return p

def verify_menu_choice(choice):
    source_check()
    with tempfile.TemporaryDirectory(prefix='depth-coarse-menu-') as directory:
        work=Path(directory);profiler=work/'profiles'
        subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),str(ROOT/'scripts/experiments/binary_frame_profiles.cpp'),'-o',str(profiler)],check=True)
        for h in (23,25):
            selected=json.loads((HERE/f'menu/{choice}-{h}.json').read_text())
            activate(choice);_,generated=compile_axis(h)
            raw=(json.dumps(generated,separators=(',',':'))+'\n').encode()
            assert hashlib.sha256(raw).hexdigest()==selected['word_sha256'],'Menu word differs'
            word=work/f'word-{h}.json.gz';word.write_bytes(gzip.compress(raw,mtime=0))
            literal_binding(word)
            assert json.loads(json.dumps(replay(word)))==selected['replay']
            transitions=work/f'axis-{h}.bin'
            assert json.loads(json.dumps(prepare(word,transitions)))==selected['transitions']
            subprocess.run([str(profiler),str(transitions)],check=True)
            assert json.loads(Path(str(transitions)+'.profiles.json').read_text())==selected['profile']
            print('PASS regenerated full menu axis',choice,h,flush=True)

def verify(regenerate=False,arithmetic_only=False):
    source_check()
    with tempfile.TemporaryDirectory(prefix='balanced-split-verify-') as directory:
        work=Path(directory)
        if not arithmetic_only:
            profiler=work/'profiles'
            subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),str(ROOT/'scripts/experiments/binary_frame_profiles.cpp'),'-o',str(profiler)],check=True)
            for h in (23,25):
                word=HERE/f'word-{h}.json.gz';literal_binding(word)
                selected=json.loads((HERE/f'axis-{h}.json').read_text())
                raw=gzip.decompress(word.read_bytes())
                assert hashlib.sha256(raw).hexdigest()==selected['word_sha256']
                assert json.loads(json.dumps(replay(word)))==selected['replay']
                transitions=work/f'axis-{h}.bin'
                assert json.loads(json.dumps(prepare(word,transitions)))==selected['transitions']
                subprocess.run([str(profiler),str(transitions)],check=True)
                assert json.loads(Path(str(transitions)+'.profiles.json').read_text())==selected['profile']
                if regenerate:
                    selection=json.loads((HERE/'selection.json').read_text())
                    activate(selection[str(h)])
                    _,generated=compile_axis(h)
                    generated_raw=(json.dumps(generated,separators=(',',':'))+'\n').encode()
                    assert generated_raw==raw,'Regenerated word differs'
                print('PASS literal scatter, all dirty/source/target basis, frames and CRT profiles h='+str(h),flush=True)
        result=arithmetic_check(work)
        print('PASS exact characteristic, complete PR71/75 exclusion, 47 strict constraints, 7 margins, next grids',flush=True)
        return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--regenerate',action='store_true');p.add_argument('--arithmetic-only',action='store_true');p.add_argument('--menu-choice',choices=[''.join(x) for x in itertools.product('cr',repeat=3)]);a=p.parse_args()
    if a.regenerate and a.arithmetic_only:p.error('Choose one mode')
    if a.menu_choice:
        if a.regenerate or a.arithmetic_only:p.error('Choose one mode')
        verify_menu_choice(a.menu_choice)
    else:verify(a.regenerate,a.arithmetic_only)
