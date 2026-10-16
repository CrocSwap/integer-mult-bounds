"""Exact local checks for a new involutive rank-eight source reflection.

This is an experiment, not native admission or a new kappa certificate.
The identity-target interface and retained core correction are credited to PR1862 at
bb29ea73ad9be9a0c3d53cdcb1d22b2ee9ffe42f. Current supplier is PR1800 at
46d865ab92e58098538b8c5348b6a131c99abf45. Original sources are unchanged.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import gzip, hashlib, json, os, sys, tempfile, time

HERE = Path(__file__).resolve().parent
ROOT = HERE
# Assert-based checks must never silently disappear under optimized Python.
if not __debug__:
    raise RuntimeError("Run without -O: assertions are required for this verifier")
import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--interface', choices=['unit-transfer','reflection-shear'], default='unit-transfer')
parser.add_argument('--out', type=Path, help='Optional fresh report directory; default is read-only')
args = parser.parse_args()
if args.out is not None and args.out.exists():
    raise ValueError("Output directory already exists")
manifest=json.loads((HERE/'SOURCES.json').read_text())
for relative, record in manifest['files'].items():
    path=HERE/relative
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=record['sha256']:
        raise ValueError('Source pin differs: '+relative)
    if 'payload_sha256' in record and hashlib.sha256(gzip.decompress(raw)).hexdigest()!=record['payload_sha256']:
        raise ValueError('Payload pin differs: '+relative)
sys.path.insert(0, str(HERE/'vendor/pr1862'))
sys.path.insert(0, str(HERE))
import source_data as base
import reflection_unit as producer
if args.interface == 'reflection-shear':
    import restored_reflection as producer
import input_logger as algebra
import native_verify as native
import verify_unit_transfer as transfer_check
import verify_input_logger as scalar_check

pins = {}
def read(path):
    raw = path.read_bytes()
    pins[str(path.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)

reports = []
for provider in ('base', 'extra'):
    start = time.monotonic()
    local = HERE/'inputs'/provider
    word = read(local/'CANONICAL-WORD.json.gz')
    programs = read(local/'LOCAL-PROGRAMS.json.gz')
    v, n = word['v'], 2*word['v']+word['R']
    boundary = base.replay(programs['forward'], n,
                           programs['forward'].index(['phase','centers']))
    R = [{j:x for j,x in boundary[c].items() if j<v} for c in word['centers']]
    H = [{j:x for j,x in boundary[c].items() if j>=2*v} for c in word['centers']]
    assert all(boundary[c] == R[k] | H[k] for k,c in enumerate(word['centers']))
    K = [{k:row[j]/4 for k,row in enumerate(R) if j in row} for j in range(v)]
    RT = algebra.transpose(R,v)
    assert base.product(R,RT)==[{i:Q(56)} for i in range(len(R))]
    def dot(a,b): return sum(x*b.get(i,0) for i,x in a.items())
    adj=[{j for j in range(v) if i!=j and dot(RT[i],RT[j])==0} for i in range(v)]
    def clique(candidates, chosen=()):
        if len(chosen)==len(R): return list(chosen)
        if len(candidates)<len(R)-len(chosen): return None
        for i in sorted(candidates):
            found=clique({j for j in candidates&adj[i] if j>i},chosen+(i,))
            if found is not None: return found
        return None
    A=clique(set(range(v)))
    assert A
    certificate=dict(compensation_ports=A)
    J = base.difference([{i:Q(1)} for i in range(v)], base.product(K,R))
    D = [{} for _ in range(v)]
    for e in word['cut']:
        base.add(D[e[1]-v], {word['centers'].index(e[2]):Q(e[3],e[4])}, Q(1))
    clean = {}
    for direction,program in programs.items():
        fixed,prefix = base.corrected_program(program,H,D,direction=='backward')
        base.check_frame_access(fixed,word)
        rows = base.replay(fixed,n)
        for i,row in enumerate(rows):
            expected = {i:Q(1)} if i<n else {}
            if direction=='forward' and v<=i<2*v:
                base.add(expected,J[i-v],Q(1))
            if direction=='backward' and i<v:
                base.add(expected,{v+j:x for j,x in J[i].items()},Q(-1))
            assert row==expected,(provider,direction,i,'clean-J')
        clean[direction] = fixed
    data = dict(word=word,R=R,J=J,clean_programs=clean)
    # The reflection uses only the compensation minor; no fixed query logger.
    out = producer.produce(data,certificate,algebra)
    vals = producer.matrices(data,certificate,algebra)
    identity=[{i:Q(1)} for i in range(v)]
    assert base.product(vals['G'],vals['G_inverse'])==identity
    assert base.product(vals['G_inverse'],vals['G'])==identity
    # Check physical boundary access separately from canonical scalar content.
    assert transfer_check.boundary_frames(
        out['blocks']['backward_input']+out['blocks']['source_G'],
        word,A,False,scalar_check)==A
    assert transfer_check.boundary_frames(
        out['blocks']['forward_source']+out['blocks']['forward_output'],
        word,A,True,scalar_check)==A
    recipe_records=[]; gaussian_columns=0
    for port in A:
        label=word['ports'][port]
        chart=native.transpose(native.extend((label,),word['h']))
        def mono(matrix,offset=0):
            return dict(matrix_rows=list(matrix),quadratic_rows=[0]*word['h'],
                        linear_Z4=[0]*word['h'],offset=offset,phase=0)
        positive=dict(rank=1,left=mono(chart),right=mono(native.inverse(chart)))
        negative=dict(rank=1,left=mono(chart,label),right=mono(native.inverse(chart)))
        for sign,record in ((1,positive),(-1,negative)):
            actual=native.recipe(record);expected=(('C',label,sign),)
            native.equal(actual,expected,'current intrinsic line')
            for col in range(1<<word['h']):
                assert native.state(actual,col)==native.state(expected,col)
                gaussian_columns+=1
            phase_mutant=actual+(('phase',1),)
            assert native.tableau(phase_mutant)==native.tableau(expected)
            assert native.state(phase_mutant)!=native.state(expected)
        assert native.state(native.recipe(positive))!=native.state(native.recipe(negative))
        native.equal(native.fourier(word['h'])+native.recipe(negative),
                     (('C',label,-1),)+native.fourier(word['h']),
                     'current FULL-to-hole')
        recipe_records.append(dict(port=port,label=label,positive=positive,inverse=negative))
    orientation = {}
    for direction,program in out['programs'].items():
        rows = base.replay(program,n)
        assert scalar_check.transpose(scalar_check.adjoint(program), n+8)==rows
        for i,row in enumerate(rows):
            expected = {i:Q(1)} if i<n else {}
            if direction=='backward':
                if args.interface == 'reflection-shear':
                    if i<v: base.add(expected,{v+j:x for j,x in vals['G'][i].items()},Q(-1))
                else:
                    if i<v: base.add(expected,{v+i:Q(1)},Q(-1))
                    elif i<2*v: expected={v+j:x for j,x in vals['G'][i-v].items()}
            else:
                if args.interface == 'reflection-shear':
                    if v<=i<2*v: base.add(expected,vals['G'][i-v],Q(1))
                else:
                    if i<v: expected=vals['G_inverse'][i]
                    elif i<2*v: base.add(expected,vals['G_inverse'][i-v],Q(1))
            assert row==expected,(provider,direction,i,'unit-transfer')
        profile=Counter(e[5] for e in program if e[0]=='climb')
        added=[e for e in program if e[0] in ('unit_transfer_input_line','unit_transfer_exit_line')]
        profile.update(e[-1] for e in added)
        original=Counter(e[5] for e in programs[direction] if e[0]=='climb')
        original.update(e[4] for e in programs[direction] if e[0]=='center')
        assert not any(e[0]=='center' for e in program)
        assert len(added)==len(R)
        native_tags=('climb','adapter','residual_adapter')
        assert [e for e in program if e[0] in native_tags]==[e for e in programs[direction] if e[0] in native_tags]
        # An omitted correction must change an actual data output.
        block=out['blocks']['backward_input' if direction=='backward' else 'forward_output']
        bad=program[len(block):] if direction=='backward' else program[:-len(block)]
        assert base.replay(bad,n)[:2*v] != rows[:2*v]
        # Source mutation is nontrivial, so it cannot be treated as restored.
        source=range(v,2*v) if direction=='backward' else range(v)
        changed=sum(rows[i]!={i:Q(1)} for i in source)
        assert changed==0 if args.interface=='reflection-shear' else changed>0
        orientation[direction]=dict(
            independent_input_columns=n+8, arbitrary_helpers_restored=word['R'],
            private_outputs_zero=len(R), source_rows_changed=changed,
            original_profile=dict(sorted(original.items())),
            candidate_profile=dict(sorted(profile.items())),
            original_rank_mass=sum(r*c for r,c in original.items()),
            candidate_rank_mass=sum(r*c for r,c in profile.items()),
            scalar_allowance_real=2*sum(base.primitive_bound(e[1]) for e in program if e[0]=='scalar'),
            omitted_target_correction='REJECT',
            native_status='Retained events identical; added intrinsic recipes and physical boundary access checked. Full physical composition NOT replayed')
    reports.append(dict(provider=provider,minors=certificate,orientations=orientation,
                        added_native_gaussian_columns=gaussian_columns,
                        added_native_recipes=recipe_records,seconds=time.monotonic()-start))
    print(provider+': exact scalar, adjoint, boundary and native-line checks PASS',flush=True)

for module in (base,producer,algebra,native,transfer_check,scalar_check):
    path=Path(module.__file__)
    pins[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
result=dict(interface=args.interface,status='PASS_CURRENT_LOCAL_REFLECTION_WITH_BOUNDARY_CHECKS',providers=reports,
            source_pins=pins,
            scope='Exact scalar identities on all input columns, inherited core frame access, and added native recipes and physical boundary access. Depending on interface, source remains encoded or the transferred operator is F rather than identity. Full operator composition, changed-chart routing, source decoding, hosting and full precision invoice are open. No new kappa certified.')
if args.out is not None:
    args.out.mkdir(parents=True,exist_ok=False)
    (args.out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'])
print(result['scope'])
