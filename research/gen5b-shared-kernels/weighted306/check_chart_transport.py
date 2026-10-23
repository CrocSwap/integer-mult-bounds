"""Rebind inherited 281 candidate charts to unchanged first demands of PR306.
No upstream program is imported or executed. Interior baseline306 chart/frame
admission remains a separate obligation. Prepared with OpenAI assistance.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
import gzip,hashlib,json
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def data(p):return json.loads(gzip.decompress(p.read_bytes()))
def check_inputs(word,frames,sinks,witness,chart,selections):
    aliases={b:a for a,b in word['pairs']};recipient={a:b for a,b in word['pairs']}
    regs=sorted(set(range(17160))-set(aliases));pre={r:3520+i for i,r in enumerate(regs)}
    sunk={z['role'] for z in sinks};compact={r:3520+i for i,r in enumerate(x for x in regs if x not in sunk)}
    pivots={e['virtual_pivot'] for e in witness['entries']};donors={d for e in witness['entries'] for d in e['virtual_donors']};active=pivots|donors
    assert len(pivots)==156 and len(donors)==197 and not pivots&donors
    owners={r:r for r in active}
    for r in active:
        if r in recipient:owners[recipient[r]]=r
    phase=set(word['phase1']);order=word['phase1']+[i for i in range(len(word['ops'])) if i not in phase]
    first={}
    for index in order:
        for role in word['ops'][index][:2]:
            if role in owners:first.setdefault(owners[role],word['op_frame'][index])
    for role,frame in zip(word['rootroles'],word['root_frame']):
        if role in owners:first.setdefault(owners[role],frame)
    assert set(first)==active
    lines={}
    for e in witness['entries']:
        line=tuple(i for i,x in enumerate(e['basis'][0]) if x)
        for role in [e['virtual_pivot']]+e['virtual_donors']:
            assert role not in lines or lines[role]==line;lines[role]=line
    touched=[];compact_owner={compact[r]:r for r in active}
    for tag,number in [('reorder',237),('reorder2',2)]:
        selection=selections[tag];assert len(selection['moves'])==number
        for index,move in enumerate(selection['moves']):
            affected=set(move['incidence'][:2])&set(compact_owner)
            for stream in affected:
                role=compact_owner[stream]
                assert move['category']=='side_root' and stream==move['incidence'][1]
                first_dim=frames[str(first[role])]['dim'];assert first_dim in (3,5) and first_dim<move['old_frame_rank']==21 and move['frame_rank']==22
                touched.append(dict(round=tag,index=index,role=role,first_frame=first[role],first_dimension=first_dim))
    assert len(touched)==18
    programs=chart['factor_programs'];assert len(programs)==chart['charts']==281
    expected_uses=[]
    for role in sorted(active):
        dim=frames[str(first[role])]['dim']
        expected_uses.extend([('first_frame_quotient',role,pre[role],first[role],dim-1),
            ('pivot_residual' if role in pivots else 'donor_line_entrance',role,pre[role],None,23 if role in pivots else 1)])
    actual=[(u['kind'],u['role'],u['stream'],u.get('frame'),u['rank']) for u in chart['role_chart_uses']]
    assert actual==expected_uses and len(actual)==706
    for u in chart['role_chart_uses']:
        p=programs[u['program_id']]
        assert tuple(p['line'])==lines[u['role']] and p['residual_rank']==u['rank']
        if u['kind']=='first_frame_quotient':assert p['frame']==first[u['role']] and p['first_dimension']==frames[str(first[u['role']])]['dim']
    return touched

def replay_program(p):
    columns=[[Q(x) for x in c] for c in p['basis_columns']];wanted=list(map(list,zip(*columns)))
    matrix=[[Q(i==j) for j in range(24)] for i in range(24)]
    assert len(p['factors'])==p['count']<=508
    for kind,i,j,q in reversed(p['factors']):
        q=Q(q);assert abs(q.numerator)<=615 and q.denominator<=810
        if kind=='swap':matrix[i],matrix[j]=matrix[j],matrix[i]
        elif kind=='scale':matrix[i]=[x/q for x in matrix[i]]
        else:
            assert kind=='add';matrix[i]=[x-q*y for x,y in zip(matrix[i],matrix[j])]
    assert matrix==wanted

def replay_charts(chart):
    assert len(chart['factor_programs'])==281
    for p in chart['factor_programs']:replay_program(p)
    assert chart['max_changed_chart_factors']==508 and 576+119+120==chart['combined_normalizer_factor_bound']==815

def run(config):
    source=Path(config['old_source']);new=Path(config['new_source']);out=Path(config['output_dir'])
    prior=load(Path(config['prior_case']));cp=Path(config['prior_charts']);raw=cp.read_bytes();chart=json.loads(raw)
    assert sha(raw)==prior['changed_chart_receipt_sha256']
    wp=Path(config['witness']);witness=load(wp)
    assert sha(wp.read_bytes())==chart['candidate_sha256']==prior['candidate_sha256']
    manifest=load(new/'MANIFEST.json')['files']
    files=['gen5bit/selected/bit/word_p12.json.gz','gen5bit/selected/bit/frames_p12.json.gz','sink-selection.json']
    for name in files:assert sha((source/name).read_bytes())==manifest[name]
    word=data(source/files[0]); frames=data(source/files[1])['frames'];sinks=load(source/'sink-selection.json')['sinks']
    selections={}
    for tag in ['reorder','reorder2']:
        path=new/(tag+'-selection.json');assert sha(path.read_bytes())==manifest[tag+'-selection.json']
        selections[tag]=load(path)
    touched=check_inputs(word,frames,sinks,witness,chart,selections)
    replay_charts(chart)
    receipt=dict(status='PASS_CANDIDATE_CHART_INPUT_AND_FACTOR_TRANSPORT_CONDITIONAL_ON_REORDER_ADMISSION',
        source_head='0314371983b8837f01723f5af2c70217f75b01cc',candidate_sha256=chart['candidate_sha256'],
        inherited_chart_receipt_sha256=sha(raw),chart_programs=281,exact_factor_programs_replayed=281,role_uses=706,
        unchanged_first_quotient_demands=353,unchanged_pivot_residual_demands=156,unchanged_donor_line_demands=197,
        selected_roles_touched_by_reorder=18,overlap_categories={'side_root':18},touched=touched,
        maximum_changed_chart_factors=508,inherited_base_max_chart_factors=576,combined_normalizer_bound=815,
        baseline306_interior_chart_admission_replayed=False,
        scope='The candidate adds only first-frame quotient, pivot residual and donor entrance chart programs. Their inputs and all281 inverse programs are exactly unchanged. Eighteen later rank22 visits do not create additional candidate chart programs; those MOVE/ADD chart and source-span obligations belong to baseline306 and remain conditional on its changed-word bridge.')
    out.mkdir(parents=True,exist_ok=True)
    (out/'chart-transport-inputs.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['touched','scope']},indent=2))
    return receipt
if __name__=='__main__':
    import argparse
    if not __debug__:raise RuntimeError('Assertions required')
    parser=argparse.ArgumentParser();parser.add_argument('--config',type=Path,required=True)
    run(load(parser.parse_args().config))
