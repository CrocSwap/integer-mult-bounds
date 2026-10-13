"""Reproduce the bounded CK two-sided construction and its finite evidence.

Ross Richardson, substantial OpenAI Codex assistance. Apache-2.0.
Run from any directory with Python 3.10+ and the standard library.
"""
import argparse
import copy
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import experiment as e
import independent as independent


def summary_integer(result):
    peak=result['positive_prefix']
    return {'real_primitives':2*result['primitive_count'],
            'prefix_l1':str(Q(peak['numerator'], 2**peak['denominator_power'])),
            'prefix_bits':peak['strict_power_of_two_bits'],
            'maximum_denominator_power':result['maximum_denominator_power']}


def native(w, programs):
    """Unchanged inherited emitter, common-frame/wrapper audit and 25 controls."""
    with tempfile.TemporaryDirectory(prefix='ck-two-sided-') as directory:
        out=Path(directory)
        (out/'CANONICAL-WORD.json.gz').write_bytes(gzip.compress(e.canonical(w),mtime=0))
        logs={}
        for script in ('hpe_emit_local.py','hpe_audit_local.py'):
            path=e.ROOT/'research/complex-571-cold14-k492c/code'/script
            # -I ignores PYTHONOPTIMIZE; parent -O must not disable inherited asserts.
            run=subprocess.run([sys.executable,'-I','-B',str(path),str(out)],capture_output=True,text=True)
            e.require(run.returncode==0, 'native '+script+' failed:\n'+run.stdout+run.stderr)
            logs[script]=run.stdout.strip().splitlines()
        rebuilt=e.read(out/'LOCAL-PROGRAMS.json.gz')
        e.require(e.canonical(rebuilt)==e.canonical(programs),'native emitter program disagreement')
        checks=e.read(out/'LOCAL-CHECKS.json')
        audit=e.read(out/'INDEPENDENT-LOCAL-REPLAY.json')
        e.require(len(audit['negative_controls_rejected'])==25,'native control coverage')
        return {'checks':checks, 'local':audit['local'], 'paid_profiles':audit['paid_profiles'],
                'negative_controls_rejected':audit['negative_controls_rejected'], 'logs':logs}


def controls(w, panel, recipe):
    """Actual faulty circuits, checked against every arbitrary input column."""
    base_events=[e.scalar(x,False) for x in w['compensation']]
    reference,_=e.fraction_replay(base_events)
    nt=len(recipe['target_forest']); nh=len(recipe['helper_pairs']); nr=recipe['residual_additions']
    mutants={
        'omitted_target_preparation':panel[1:],
        'omitted_helper_preparation':panel[:nt]+panel[nt+1:],
        'omitted_helper_restoration':panel[:nt+nh+nr]+panel[nt+nh+nr+1:],
        'omitted_target_restoration':panel[:-1],
        'reversed_target_preparation':list(reversed(panel[:nt]))+panel[nt:],
        'reversed_target_restoration':panel[:-nt]+list(reversed(panel[-nt:])),
    }
    wrong=copy.deepcopy(panel);wrong[nt][3]*=-1;mutants['wrong_helper_preparation_sign']=wrong
    wrong=copy.deepcopy(panel);wrong[nt+nh][3]*=-1;mutants['wrong_residual_sign']=wrong
    rejected=[]; helper_only_control=False
    for label,mutant in mutants.items():
        state,_=e.fraction_replay([e.scalar(x,False) for x in mutant])
        e.require(state!=reference,'mutation accepted: '+label)
        if label=='omitted_target_preparation':
            project=lambda st: {r:{k:v for k,v in row.items() if 224<=k<716}
                                for r,row in st.items()}
            e.require(project(state)==project(reference),'helper-only blind spot was not reproduced')
            helper_only_control=True
        rejected.append(label)
    # A source-ineligible cold helper is forbidden before its paid pre-wrapper.
    cold=next(r for r in range(224,716) if w['start'][r]==0 and w['final'][r]!=1)
    bad=copy.deepcopy(w);replaced=bad['compensation'][0][2]
    for operation in bad['compensation']:
        if operation[2]==replaced: operation[2]=cold
    try: e.matrix(bad)
    except ValueError as error:
        e.require(str(error)=='helpers must be unwrapped at entry','cold control rejected for wrong reason')
        rejected.append('cold_wrapped_helper_access')
    else: raise ValueError('cold helper mutation accepted')
    # An initial clear is mathematically needed for arbitrary coefficient work.
    p=e.lower(['add',['L',1],['L',0],1,1])
    good=independent.replay(p,n=2,centers=0)
    independent.check_endpoint(good,'forward',v=1)
    try: independent.check_endpoint(independent.replay(p[1:],n=2,centers=0),'forward',v=1)
    except independent.ReplayError: rejected.append('omitted_initial_work_clear')
    else: raise ValueError('dirty work mutation accepted')
    return {'rejected':rejected,'omitted_target_preparation_passes_helper_only':helper_only_control}


def verify(record=False):
    w,original,checks=e.load()
    panel,recipe=e.construct(w)
    candidate=e.replace_programs(w,original,panel)
    expected_recipe=e.HERE/'RECIPE.json'
    if not record:
        e.require(e.canonical(e.read(expected_recipe))==e.canonical(recipe),'RECIPE.json does not reproduce')
    result={'status':'FINITE_CK_TWO_SIDED_COMPENSATION_NO_NEW_KAPPA',
            'base_commit':e.BASE,'seed':e.SEED,'source_pins_sha256':e.digest(e.read(e.HERE/'SOURCES.json')),
            'recipe_sha256':e.digest(recipe),'columns':{'logical':716,'private':9},
            'search':{'target_edges':recipe['forest_search']['edges'],
                      'helper_cases':recipe['helper_search']['cases'],
                      'profitable_helper_cases':recipe['helper_search']['profitable'],
                      'target_basis_edges':len(recipe['target_forest']),
                      'helper_pairs':len(recipe['helper_pairs'])},
            'panel_component_prices':{'baseline':recipe['baseline_panel_price'],
                                      'target_only':recipe['forest_search']['price'],
                                      'two_sided':recipe['two_sided_panel_price']},
            'programs':{}}
    result['independent_recipe']=independent.check_recipe(w,recipe)
    for name in ('forward','backward'):
        result['programs'][name]={}
        for label,events in (('baseline',original[name]),('candidate',candidate[name])):
            state,receipt=e.fraction_replay(events)
            e.endpoint(state,name=='backward')
            other=independent.replay(e.primitives(events))
            independent.check_endpoint(other,name)
            e.require(receipt==summary_integer(other),'integer/Fraction replay disagreement')
            e.require(receipt['prefix_bits']<=192,'inherited 192-bit allowance exceeded')
            if label=='baseline':
                e.require(receipt['real_primitives']==checks[name]['real_component_primitive_bound'],'baseline invoice mismatch')
            result['programs'][name][label]={**receipt,'program_sha256':e.digest(events),
                'primitive_word_sha256':e.digest(list(e.primitives(events))),
                'scalar_macros':sum(x[0]=='scalar' for x in events),
                'primitive_counts':other['primitive_counts']}
        r=result['programs'][name]
        saved=r['baseline']['real_primitives']-r['candidate']['real_primitives']
        e.require(saved==2*(recipe['baseline_panel_price']-recipe['two_sided_panel_price']),'complete price mismatch')
        r['real_saved']=saved
        r['additional_real_saved_vs_target_forest']=2*recipe['helper_search']['gain']
    nw=copy.deepcopy(w);nw['compensation']=panel
    result['native']=native(nw,candidate)
    for name in ('forward','backward'):
        r=result['programs'][name]['candidate']; nc=result['native']['checks'][name]; na=result['native']['local'][name]
        e.require(nc['real_component_primitive_bound']==r['real_primitives'],'native price mismatch')
        e.require(na['prefix_l1_upper']==r['prefix_l1'],'native prefix mismatch')
        e.require(nc['paid_profile']==checks[name]['paid_profile'],'paid profile changed')
    result['controls']=controls(w,panel,recipe)
    if record:
        expected_recipe.write_text(json.dumps(recipe,indent=2)+'\n')
        (e.HERE/'EXPECTED.json').write_text(json.dumps(result,indent=2)+'\n')
    else:
        e.require(e.canonical(e.read(e.HERE/'EXPECTED.json'))==e.canonical(result),'EXPECTED.json does not reproduce')
    print('PASS_CK_TWO_SIDED target_edges=106 helper_pairs=112 cases=128524 saved_real=75318 additional_vs_target=8798 columns=716+9 orientations=2 controls=10+25 no_new_kappa')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record',action='store_true',help='replace this package receipts after all checks pass')
    args=parser.parse_args()
    verify(args.record)
