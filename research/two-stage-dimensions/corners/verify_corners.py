#!/usr/bin/env python3
"""PR29 two-stage at dims (47,45) + PR31 contiguous data-corner blocks, exact certificate.
Composes: Zhihao Chen PR29 (construction/assembly), Rohan Arun PR31 (data-corner identities,
generator/auditor/moment/cutoffs, parametrized here only in (a,b)), and the (47,45) producers."""
import sys,json
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
HERE=Path(__file__).resolve().parent;PARENT=HERE.parent
sys.path[:0]=[str(HERE),str(PARENT)]
import verify_candidate as base
from independent_param import run as audit
from moment import moment_search
from assembly_parameterized import assembly
from cutoffs import cutoffs,js
A,B_=47,45;EXPECTED_RUNS=[1,43,1,1,1,1,1,1,37,1,1,1,1]
BIT=Q(1638156876,10**14);KAPPA=Q(1638103206,10**14);BETA=Q(1,20);HEADROOM=Q(1,10**12)

def run():
    manifest=json.loads((HERE/'SOURCE.json').read_text())
    for name,digest in manifest['local_sha256'].items():
        assert sha256((HERE/name).read_bytes()).hexdigest()==digest,name
    old=base.run();b=old['bit'];N=b['N'];m=b['m'];d=A+B_-1
    assert old['dims']==[A,B_]
    c=json.loads((HERE/f'corner-{A}-{B_}.json').read_text())
    idn=audit(c,EXPECTED_RUNS)
    big=idn['profile']['blocks'][:-1];assert idn['profile']['singletons']+sum(big)==d
    rows=Counter({int(t):n for t,n in b['rows'].items()})
    assert rows[m-2*d]>=2*N
    rows[1]-=2*N*sum(big)
    for w in big:rows[w]+=2*N
    assert rows[1]>=N and sum(t*n for t,n in rows.items())==b['s'] and max(rows)==max(int(t) for t in b['rows'])
    bit=moment_search(m,b['W'],rows,denominator=10**14)
    assert bit['saving']==BIT and bit['strict_gap']>0 and bit['next_moment_upper']>=1
    f=old['finite_bridge'];assert f['rows']['degree']==47000
    a=assembly(f,BIT,KAPPA,beta=BETA,h=HEADROOM);assert len(a['constraints'])==47 and len(a['margins'])==7 and a['absorption_gap']>0
    eventual=cutoffs(f,a)
    rejected=[]
    for name,kw in [('old_guard',dict(old_guard=True)),('old_exposures',dict(old_exposures=True))]:
        try:assembly(f,BIT,KAPPA,beta=BETA,h=HEADROOM,**kw)
        except AssertionError:rejected.append(name)
        else:raise AssertionError(name)
    try:assembly(f,BIT,KAPPA+Q(1,10**14),beta=BETA,h=HEADROOM)
    except AssertionError:rejected.append('next_kappa_grid')
    else:raise AssertionError('next kappa passes')
    try:assembly(f,BIT,KAPPA,beta=Q(1,10),h=HEADROOM)
    except AssertionError:rejected.append('pr29_beta_one_tenth_leaf_too_slow')
    else:raise AssertionError('beta 1/10 unexpectedly passes')
    bad=json.loads(json.dumps(c));bad['zero_minor_certificates'][0]['partition']^=1
    try:audit(bad,EXPECTED_RUNS)
    except (AssertionError,KeyError):rejected.append('corrupted_identity_certificate')
    else:raise AssertionError('corrupted certificate accepted')
    assert moment_search(m,b['W'],Counter({int(t):n for t,n in b['rows'].items()}))['saving']<BIT
    rejected.append('omit_data_blocks_lowers_saving')
    proof=base.ROOT/'notes/two-stage-corners-47-45-note.tex'
    source_paths=[Path(__file__),HERE/'SOURCE.json',proof,HERE/'README.md']
    return dict(source_sha256={str(p.relative_to(base.ROOT)):sha256(p.read_bytes()).hexdigest() for p in source_paths},
        status=f'CONDITIONAL kappa={KAPPA} at PR29 dims ({A},{B_}) with PR31-type data blocks; not formal verification',
        data_profile=dict(copies=2*N,**idn['profile']),identity_audit=idn,counts={k:b[k] for k in ('a','b','m','N','W','L','s','deficit')},
        rows=dict(sorted(rows.items())),bit=bit,finite_bridge=f,assembly=a,eventual_bounds=eventual,negative_controls=rejected,
        corner_certificate_sha256=sha256((HERE/f'corner-{A}-{B_}.json').read_bytes()).hexdigest(),
        references=dict(PR29='9d963275075fa98f1da821e27757b238dafd6b3c',PR31='02f68f95369c39955c5ffcfddbd75cd83e26b305'))

if __name__=='__main__':
    r=run();(HERE/f'certificate-corners-{A}-{B_}.json').write_text(json.dumps(js(r),indent=2,sort_keys=True)+'\n')
    from difflib import unified_diff
    original=(base.ROOT/'notes/two-stage-16-note.tex').read_text()
    updated=(base.ROOT/'notes/two-stage-corners-47-45-note.tex').read_text()
    patch=''.join(unified_diff(original.splitlines(keepends=True),updated.splitlines(keepends=True),fromfile='a/notes/two-stage-16-note.tex',tofile='b/notes/two-stage-16-note.tex'))
    (base.ROOT/'patches/two-stage-corners-47.patch').write_text(patch)
    print('PASS kappa',r['assembly']['parameters']['kappa'],'bit',r['bit']['saving'],'gap',float(r['bit']['strict_gap']),'final gap',float(r['assembly']['absorption_gap']))
    print('profile',r['data_profile'],'zero certs',r['identity_audit']['zero_certificates'],'neg',r['negative_controls'])
