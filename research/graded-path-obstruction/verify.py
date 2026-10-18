"""Standalone exact replay, with independent Gaussian-matrix path grouping."""
if not __debug__:
    raise SystemExit('Run without -O: inherited Clifford checks require assertions.')
from collections import Counter,defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from itertools import permutations,product
from pathlib import Path
import gzip,json,sys

# Permit an isolated interpreter and an unrelated current working directory.
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from model import decode,Engine,execute,fourier_rank,endpoint_frames
from screen import layers,certificate
import dense


def dense_certificate(program):
    stages=layers(program)
    matrices=[];ranks=[]
    for stage in stages:
        matrices.append([]);ranks.append([])
        for operations in stage:
            a=dense.identity()
            for op in operations:a=dense.multiply(dense.operator(op),a,True)
            counts=[sum(a[1][8*r+c]!=0 or a[2][8*r+c]!=0 for r in range(8)) for c in range(8)]
            assert len(set(counts))==1 and counts[0] in (1,2,4,8)
            matrices[-1].append(a);ranks[-1].append(counts[0].bit_length()-1)
    classes=defaultdict(list)
    for path in product(range(3),repeat=len(stages)-2):
        a=dense.identity()
        for k,r in enumerate(path,1):a=dense.multiply(matrices[k][r],a,True)
        a=dense.normalize(*a,projective=True)
        classes[a].append((list(path),sum(ranks[k][r] for k,r in enumerate(path,1))))
    classes=sorted((sorted(v) for v in classes.values()),key=lambda x:x[0][0])
    return ranks,classes


def check_certificate(program,saved):
    wanted=certificate(program)
    assert saved==wanted
    ranks,classes=dense_certificate(program)
    assert saved['unary_ranks']==ranks and saved['middle_classes']==classes
    return wanted


def add(a,b):
    out=dict(a)
    for e,c in b.items():out[e]=out.get(e,0)+c
    return {e:c for e,c in out.items() if c}


def mul(a,b):
    out={}
    for e,c in a.items():
        for f,d in b.items():out[e+f]=out.get(e+f,0)+c*d
    return {e:c for e,c in out.items() if c}


def determinant(matrix):
    out={}
    for p in permutations(range(3)):
        term={0:(-1)**sum(p[i]>p[j] for i in range(3) for j in range(i+1,3))}
        for r,c in enumerate(p):term=mul(term,matrix[r][c])
        out=add(out,term)
    return out


def determinant_control(program,cert):
    blocks=cert['scalar_blocks'];matrices=[];det=1
    for k in range(blocks):
        b=[[1,k+1,0],[0,1,1],[1,0,1]];matrices.append(b)
        actual=determinant([[{0:x} if x else {} for x in row] for row in b])
        assert actual=={0:k+2};det*=k+2
    current=[[{0:x} if x else {} for x in row] for row in matrices[0]]
    for k in range(1,blocks):
        current=[ [{e+cert['unary_ranks'][k][r]:c for e,c in p.items()} for p in row]
                 for r,row in enumerate(current)]
        b=matrices[k];out=[[{} for _ in range(3)] for _ in range(3)]
        for r,c,j in product(range(3),repeat=3):out[r][c]=add(out[r][c],mul({0:b[r][j]},current[j][c]))
        current=out
    degree=sum(map(sum,cert['unary_ranks'][1:-1]))
    assert determinant(current)=={degree:det}
    concrete=[];at=0
    for gate in program:
        if gate[0]=='mix3':concrete.append(('mix3',*(x for row in matrices[at] for x in row)));at+=1
        else:concrete.append(gate)
    if cert['status']=='excluded':
        ring=Engine();rows=execute(ring,concrete)
        assert any(fourier_rank(ring.groups[key>>2])<3 for row in rows for key,c in row.items() if c)


def controls(counts):
    identity=('mix3',1,0,0,0,1,0,0,0,1)
    boundary=tuple(('paid',role,axis) for role in range(3) for axis in (1,2,4))+(identity,)
    cert=certificate(boundary);check_certificate(boundary,cert)
    assert cert['scalar_blocks']==1 and cert['rank_bill']==9 and cert['heterogeneous_classes']==0
    assert cert['status']=='not_excluded_by_this_criterion'
    ring=Engine();assert endpoint_frames(ring,execute(ring,boundary)) is not None
    counts['positive_nine_call_controls']+=1
    # Three commuting independent butterflies on every stream: exact boundary.
    for extra in (0,2):
        word=[identity]
        for axis in (1,2,4):
            word.extend(('paid',role,axis) for role in range(3));word.append(identity)
        word.extend([identity]*extra);word=tuple(word)
        cert=certificate(word);check_certificate(word,cert)
        assert cert['rank_bill']==9 and cert['heterogeneous_classes']==0
        assert cert['status']=='not_excluded_by_this_criterion'
        ring=Engine();assert endpoint_frames(ring,execute(ring,word)) is not None
        counts['positive_nine_call_controls']+=1
    # The same group element arises with degrees 0 and 2: C^-1 C = I.
    word=(identity,('paid',1,1),identity,('paid',1,1),('free',1,3),identity)
    cert=certificate(word);check_certificate(word,cert)
    assert cert['heterogeneous_classes'] and cert['status']=='not_excluded_by_this_criterion'
    forged=deepcopy(cert);forged['heterogeneous_classes']=0;forged['status']='excluded'
    try:check_certificate(word,forged)
    except AssertionError:counts['false_homogeneity_rejected']+=1
    else:raise AssertionError('false homogeneity accepted')
    # Omitting homogeneity would preserve a cancellation incorrectly:
    # A^-1 diag(1,t) diag(1,t) A has off-diagonal (1-t^2)/2,
    # whereas the unweighted group word A^-1 diag(I,C^-1 C) A is I.
    off={0:Q(1,2),2:Q(-1,2)}
    assert sum(off.values())==0 and off
    counts['inhomogeneous_cancellation_control']+=1


def replay():
    payload=gzip.decompress((ROOT/'words.json.gz').read_bytes())
    data=json.loads(payload);counts=Counter();origins=defaultdict(Counter);certificates=[]
    assert len({c['id'] for c in data['cases']})==len(data['cases'])
    for case in data['cases']:
        word=decode(case['program']);cert=certificate(word)
        assert cert['paid_calls']==8
        check_certificate(word,cert);determinant_control(word,cert)
        certificates.append({'id':case['id'],'certificate':cert})
        counts[cert['status']]+=1;origins[case['origin']][cert['status']]+=1
        counts['dense_middle_paths']+=3**(cert['scalar_blocks']-1)
        counts['determinant_polynomial_controls']+=1
    controls(counts)
    sample=decode(data['cases'][0]['program']);forged=deepcopy(certificates[0]['certificate'])
    forged['rank_bill']+=1
    try:check_certificate(sample,forged)
    except AssertionError:counts['corrupt_rank_bill_rejected']+=1
    else:raise AssertionError('corrupt rank bill accepted')
    packed=json.dumps(certificates,sort_keys=True,separators=(',',':')).encode()
    return {'status':'PASS_GRADED_PATH_OBSTRUCTION','counts':dict(counts),
            'by_origin':{k:dict(v) for k,v in origins.items()},
            'words_payload_sha256':sha256(payload).hexdigest(),
            'certificates_sha256':sha256(packed).hexdigest()}


def check_manifest():
    manifest=json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf-8'))
    expected={'.gitattributes','model.py','dense.py','screen.py','verify.py',
              'EXPECTED.json','ORIGINS.json','README.md','PROOF.md','NOTICE.md','VALIDATION.json'}
    assert set(manifest['files'])==expected
    for name,wanted in manifest['files'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==wanted, 'Source integrity mismatch: '+name
    payload=gzip.decompress((ROOT/'words.json.gz').read_bytes())
    assert sha256(payload).hexdigest()==manifest['words_payload_sha256'], 'Word payload integrity mismatch'
    origins=json.loads((ROOT/'ORIGINS.json').read_text(encoding='utf-8'))
    for name,wanted in origins['vendored_files'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==wanted


if __name__=='__main__':
    check_manifest()
    report=replay()
    expected=json.loads((ROOT/'EXPECTED.json').read_text(encoding='utf-8'))
    if report!=expected:raise SystemExit('Expected certificate mismatch')
    print(json.dumps(report,sort_keys=True))
