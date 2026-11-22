"""Replay fixed-template balanced-fusion second-slot exclusions offline."""
from hashlib import sha256
from pathlib import Path
import gzip,json,subprocess,sys,random

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from gf2 import Echelon

# Check the marked-history reduction against direct exhaustive spans on
# independent four-bit toy examples, including zero and duplicate records.
rng=random.Random(98407)
for _ in range(200):
    tagged=[(rng.randrange(16),rng.randrange(2)) for _ in range(rng.randrange(1,7))]
    marked=[x for x,a in tagged if a];plain=[x for x,a in tagged if not a]
    pivot=marked[0] if marked else None
    E=Echelon(plain+([x^pivot for x in marked[1:]] if marked else []))
    for q in range(16):
        actual=Echelon(x^(q if a else 0) for x,a in tagged)
        for target in range(16):
            predicted=not E.residue(target) or (bool(marked) and not E.residue(target^pivot^q))
            assert bool(predicted)==(not actual.residue(target))

data=(HERE/'pinned'/'ONE-RESIDUAL.json.gz').read_bytes()
assert sha256(data).hexdigest()=='7fa5589301124788237a569c3c0bbc0783f70efd840b15238300b8a2d5ab1cd7'
raw=gzip.decompress(data)
assert sha256(raw).hexdigest()=='3cd1dd12039550bc0deecadcdb3074123598cd41cd41e94e0fb43451411ecb96'
G=json.loads(raw);n=G['public'];assert n==630
ch=dict(enumerate(G['start']));v={i:1<<i for i in ch};clears=0
for op,d,*a in G['program']:
    if op=='INIT':assert d not in ch;ch[d],v[d]=a[0],0
    elif op=='ADD':s,c=a;assert ch[d]==ch[s]==c;v[d]^=v[s]
    elif op=='MOVE':assert ch[d]==a[0];ch[d]=a[1]
    elif op=='SWAP':s,=a;ch[d],ch[s]=ch[s],ch[d];v[d],v[s]=v[s],v[d]
    elif op=='CLEAR':assert ch.pop(d)==a[0];v.pop(d);clears+=1
    else:raise ValueError(op)
assert ch==dict(enumerate(G['final'])) and clears==3433
expected=[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(n)]
assert [i for i in range(n) if v[i]!=expected[i]]==[130]
assert v[130]^expected[130]==1<<38

sites={2472:(8635,380,544),2475:(8647,381,544),2477:(8655,382,544),
       3318:(21258,91,544),3317:(21254,0,91)}
receipts=[]
for field,(index,src,dst) in sites.items():
    result=subprocess.run([sys.executable,'-I','-B',str(HERE/'slot_solver.py'),str(field),'--historical'],
                          check=True,text=True,capture_output=True).stdout
    first=result.splitlines()[0]
    assert first.startswith(f'SITE ({index}, {field}, {src}, {dst}) ')
    assert 'CONFLICTS 1' in first and 'CORE [' in result
    receipts.append({'field':field,'index':index,'source':src,'destination':dst,
                     'solver':first,'core':next(line for line in result.splitlines() if line.startswith('CORE '))})

result=subprocess.run([sys.executable,'-I','-B',str(HERE/'sponsor_solver.py')],
                      check=True,text=True,capture_output=True).stdout
assert "FIRST_MIN_CONFLICT [('chart0_x38', 0), (525, 111, 0)]" in result
assert "CONFLICT_EQUATION ('chart0_x38', 0) [3149, 3150, 'history-12'] = 1" in result
assert "CONFLICT_EQUATION (525, 111, 0) [3149, 3150, 'history-12'] = 0" in result
out={'source_compressed_sha256':sha256(data).hexdigest(),
     'source_expanded_sha256':sha256(raw).hexdigest(),
     'native_rows':629,'single_incorrect_owner':130,'error_support':[38],
     'retained_private_clears':clears,'single_slot_screens':receipts,
     'feedback_site':[11012,3150,509,0],
     'feedback_conflicting_forms':[[3149,3150,'history-12'],[3149,3150,'history-12']],
     'feedback_required_bits':[1,0],
     'scope':'frozen subsequent tape; one linear sender recoding and arbitrary linear terminal decoding with free histories'}
print(json.dumps(out,indent=2,sort_keys=True))
print('PASS_FROZEN_BALANCED_FUSION_SECOND_SLOT_SCREENS')
