"""Source-bound geometry/profile/copied-center composition for changed RaD DAGs.
Default rechecks archived complete geometry and local receipts, not a fresh DAG
or multi-million-pair run. Those portable full replays are separate make gates.
"""
from pathlib import Path
from math import comb
from hashlib import sha256
import argparse,importlib.util,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]

def read(path):return json.loads(Path(path).read_text())
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()

def validate_axis(doc,prof,label,schedule,pin):
    row=doc['original'];h=row['h'];v=comb(h,3)
    assert h in (23,25) and row['v']==v and row['q']==3*v+h
    assert doc['configuration']['point_policy']=='alternating-reverse'
    assert doc['scalar']['all_additions_disjoint'] and doc['scalar']['all_partial_outputs_exact'] and doc['scalar']['every_node_has_common_point']
    assert doc['dag_sha256']==label['dag_sha256']==schedule['dag_sha256']==pin['dag_sha256']
    assert label['source_triples']==v and label['center_terminal_count']==h
    for field in ('JLV_identity','all_additions_disjoint','all_output_supports_exact','no_center_middle_consumers'):assert label[field]
    assert set(label['original_core_classes'])=={'1','2','3'} and label['original_core_classes']['3']==v
    assert schedule['roles']==pin['roles']==row['R']==row['c']+row['q']-row['matched']
    assert schedule['matches']==pin['matches']==row['matched']
    assert schedule['selected_edges_sha256']==pin['selected_edges_sha256']
    assert schedule['exact_all_source_coefficients'] and schedule['complete_dirty_basis'] and schedule['dirty_wrapper_regression']
    assert schedule['complete_dirty_basis_vectors']==row['R']+v
    assert schedule['copied_center_outputs']==h and schedule['copied_rank_saving']==h*(h-1)==row['loss']
    assert schedule['matched_center_uses']==schedule['matched_output_uses']==0
    assert schedule['exact_terminal_slots']==row['q']
    assert all(prof[k]==row[k] for k in ('h','v','R','loss','rank_sum'))
    assert prof['crt_matrices']==prof['distinct_matrices']>0
    assert sum(t*n for t,n in enumerate(row['histogram']))==row['rank_sum']==h*row['R']+2*row['loss']
    assert sum(t*n for t,n in enumerate(prof['blocks']))==row['rank_sum']
    assert row['histogram'][h]==h and prof['blocks'][h]>=h
    copied=list(prof['blocks']);copied[h]-=h;copied[1]+=h
    assert min(copied)>=0 and sum(t*n for t,n in enumerate(copied))==h*row['R']+row['loss']
    return dict(h=h,v=v,R=row['R'],loss=row['loss'],copied_blocks=copied,copied_mass=h*row['R']+row['loss'],dag_sha256=doc['dag_sha256'],original_matching_sha256=pin['selected_edges_sha256'],distinct_profile_matrices=prof['distinct_matrices'])

def run(refresh=False):
    paths=[HERE/'compatibility.py',HERE/'proof.txt',HERE/'full_profiles.cpp',HERE/'review/input-pins.json',HERE/'review/original-labels.json']
    for h in (23,25):paths.extend([HERE/f'input-{h}.json',HERE/f'profile-{h}.json',HERE/f'review/original-schedule{h}.json',HERE/f'review/original-matching{h}.json'])
    paths.extend(HERE/'review'/name for name in ('original_label_audit.py','schedule_audit.py','audit.py','matching-proof.txt'))
    geometry_path=ROOT/'research/copied-both-reversed/geometry.py';paths.extend([geometry_path,geometry_path.with_name('geometry-source.json'),geometry_path.with_name('geometry-certificate.json')])
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}
    if not refresh:assert hashes==read(HERE/'compatibility.json')['source_sha256'],'Changed compatibility input; requires explicit evidence regeneration'
    spec=importlib.util.spec_from_file_location('rad_fixed_PR40_geometry',geometry_path);geom=importlib.util.module_from_spec(spec);spec.loader.exec_module(geom)
    g=geom.run();assert g['data_profile']==[1]*9+[21,17,481] and g['line_counts']=={'23':1771,'25':2300}
    assert g['modular']['pairs']==4073300 and len(g['center_complements'])==48
    labels=read(HERE/'review/original-labels.json');labels={r['h']:r for r in labels}
    pins=read(HERE/'review/input-pins.json');axes=[]
    for h in (23,25):
        pin=pins[str(h)];assert digest(HERE/f'review/original-matching{h}.json')==pin['matching_file_sha256']
        axes.append(validate_axis(read(HERE/f'input-{h}.json'),read(HERE/f'profile-{h}.json'),labels[h],read(HERE/f'review/original-schedule{h}.json'),pin))
    N=axes[0]['v']*axes[1]['v'];copies=[N//r['v'] for r in axes];banks=[c*r['R'] for c,r in zip(copies,axes)];W=2*N+sum(banks);L=sum(c*r['loss'] for c,r in zip(copies,axes));m=axes[0]['h']*axes[1]['h']
    local=sum(c*r['copied_mass'] for c,r in zip(copies,axes));exterior=sum(B*(m-r['h']) for B,r in zip(banks,axes));growth=sum(2*N*(r['h']-1) for r in axes);data=2*N*sum(g['data_profile']);paid=N
    rank=local+exterior+growth+data+paid
    assert rank==m*W-N+L
    assert (N,W,L,rank)==(4073300,178378409,2226400,102565738275)
    return dict(status='SOURCE-BOUND FIXED GEOMETRY, ORIGINAL PROFILE AND COPIED-CENTER COMPOSITION PASS',axes=axes,dimensions=[r['h'] for r in axes],m=m,N=N,copies=copies,banks=banks,W=W,L=L,rank_mass=rank,rank_classes=dict(local=local,exterior=exterior,growth=growth,data=data,paid_endpoint=paid),data_profile=g['data_profile'],data_occurrences=2*N,geometry_pairs=g['modular']['pairs'],source_sha256=hashes,scope='Default verifies pinned saved complete geometry, exact local/fallback controls and source-bound fresh producer/profile receipts. Full producer, schedule and five-prime profiler replays remain separate verification targets. No generic-profile substitution or duplicate local contribution.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args();result=run(refresh=bool(a.output))
    if a.output:a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:assert result==read(HERE/'compatibility.json')
    print(result['status'])
