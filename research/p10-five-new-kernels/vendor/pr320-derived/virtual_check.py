"""Retained admissions of the p = 10 bit word: PR168-v4 package checker and PR200 physical-word proof.

1. eumemic's unmodified PR168-v4 check_paired_cube_bit.py on the virtual (node-frame, unaliased) word:
   exact frames, mod-2 decoder with stars and side parts, geometry (source lines, root caps, operand
   nesting, star spans), role and target chains, partner chronology, G-nondegeneracy, a literal F2
   dirty-scratch replay and the ledger recount, with its five mutation controls.
2. Chafik Boukhalfa's unmodified PR200 physical-word classes, run as PR200's bit/prove.py runs them:
   exact changed operation frames and handoffs, the physical row (phase one = centre closure, actual
   addition operands, gauge supports, partner chronology, nested physical role and target chains,
   telescoping deficit), the physical word on every formal column over F2 and the defining integer
   decoder, and its adverse controls (omitted compensation, missing partner delivery, stale recipient
   read, zero operation frame).
Gen4 integration by DreamingOfClouds with Anthropic Claude assistance; Apache-2.0.
p = 10 port: honest pP file names, PR168's p argument, constants from word_pins (shape or pins).
"""
from pathlib import Path
import gzip,hashlib,importlib.util,json,shutil,time
from word_pins import P,expect,shape
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def run(output_dir,progress=lambda text:None):
    begun=time.monotonic();S=shape();sfx='_p%d.json'%P;src=HERE/'bitword/selected/bit';d=Path(output_dir)/'virtual-bit';d.mkdir(parents=True)
    assert sorted(x.name for x in src.iterdir())==sorted([n+sfx for n in('graph','kchron','profile')]+[n+sfx+'.gz' for n in('frames','word')])
    for name in ('graph','kchron','profile'):shutil.copyfile(src/(name+sfx),d/(name+sfx))
    for name in ('word','frames'):(d/(name+sfx)).write_bytes(gzip.decompress((src/(name+sfx+'.gz')).read_bytes()))
    p=HERE/'bitword/references/pr168-v4/research/paired-cube-bit/check_paired_cube_bit.py'
    mod=load('p10_pr168_v4_checker',p)
    progress('Running the PR168-v4 package checker on the p = 10 virtual word')
    result=mod.Checker(d,P).run()
    assert result['m']==S['virtual_m'] and result['deficit']==S['virtual_deficit'] and result['roles']==expect('virtual_R',result['roles'])
    expect('pr168_result',result)
    controls={}
    for m in ('broken_mix','outside_cap','below_level','dropped_star','non_nested'):
        try:mod.Checker(d,P,mutate=m).run()
        except mod.Fail as error:controls[m]=str(error)
        else:raise AssertionError('PR168 mutation control accepted: '+m)
    assert len(controls)==5
    progress('Running the PR200 physical-word proof on the p = 10 physical word')
    word=load('p10_pr200_physical_word_admission',HERE/'bitword/bit/word.py').Candidate()
    word.exact_frames();row=word.row()
    reference=json.loads((src/('profile'+sfx)).read_text())
    assert row['h']==S['h'] and row['v']==S['v']
    assert row['reused_registers']==len(word.pairs)==expect('reuse_pairs',row['reused_registers']) and row['virtual_R']==reference['R']==expect('virtual_R',row['virtual_R'])
    assert row['R']==expect('physical_R',row['R']) and row['W_per_vertex']==2*S['v']+row['R'] and row['deficit_per_vertex']==reference['deficit_per_vertex']==S['virtual_deficit'] and row['loss']==reference['loss']==S['ell']
    expect('changed_operation_frames',row['changed_operation_frames']);expect('entrances',row['selected_roles']);expect('entrance_ranks',dict(row['selected_rank_histogram']))
    formal=[word.formal(r) for r in (2,0)]
    assert formal[0]['identity'] and all(f['defining_decoder'] and f['all_dirty_and_source_columns_restored'] and f['formal_variables']==2*S['v']+row['R'] for f in formal)
    physical_controls=[]
    for tamper in ('omit_compensation','missing_partner','stale'):
        try:word.formal(2,tamper)
        except ValueError:physical_controls.append(tamper)
        else:raise AssertionError('PR200 adverse word control accepted: '+tamper)
    i=word.changed_frames[0];old=word.opframe[i];word.opframe[i]=word.register([])
    try:word.exact_frames()
    except ValueError:physical_controls.append('zero_operation_frame')
    else:raise AssertionError('zero operation frame accepted')
    word.opframe[i]=old
    assert len(physical_controls)==4
    row={k:(dict(v) if isinstance(v,dict) else v) for k,v in row.items()}
    return dict(status='PASS_PR168_V4_VIRTUAL_AND_PR200_PHYSICAL_ADMISSION_OF_P10_WORD',virtual=result,virtual_controls_rejected=controls,
        physical_row=row,physical_formal=formal,physical_controls_rejected=physical_controls,
        checker_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
        pr200_classes_sha256={n:hashlib.sha256((HERE/'bitword/bit'/n).read_bytes()).hexdigest() for n in ('word.py','base_word.py')},
        seconds=time.monotonic()-begun,
        scope='The pinned word is admitted by both retained checkers exactly as PR200 admitted its own word (its terminal-sink and prime steps have no counterpart here; primes are rechecked by prime_check).')
