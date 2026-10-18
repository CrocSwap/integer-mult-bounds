"""Independent read-only exact local admission of a concrete borrowing variant."""
import argparse
import copy
import gzip
import hashlib
import json
import sys
from pathlib import Path
from fractions import Fraction

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import native as C
from check_trace import run as replay
from precision import calculate

def need(condition,label):
    if not condition:raise ValueError(label)

def rejected(function,label):
    try:function()
    except (ValueError,KeyError,AssertionError,StopIteration):return label
    raise ValueError('mutation was accepted: '+label)

def check_native(trace,native):
    jobs,events,residuals=C.make_jobs(trace,literal_bound=True)
    need(set(native['records'])==set(jobs),'complete native operation coverage')
    need(native['event_recipe_refs']==events,'actual chronological native occurrence binding')
    need(native['helper_residual_refs']==residuals,'actual relative helper binding')
    for key,job in jobs.items():
        record=native['records'][key]
        need(record['kind']==job['kind'],'native instruction kind')
        need(json.loads(json.dumps(job['metadata']))==record['metadata'],'native frame/symbol metadata')
        need(json.loads(json.dumps(job['actual'].circuit))==record['literal_expected'],'actual physical expected circuit')
        need(record['recipe']['rank']==job['rank'],'actual paid Fourier rank')
        C.N.equal(C.N.recipe(record['recipe']),tuple(job['actual'].circuit),'fresh independent native replay')
    return jobs

def check_wrappers(trace,native,wrappers):
    helpers=wrappers['helpers']
    need(set(helpers)==set(native['helper_residual_refs']),'complete relative helper wrapper coverage')
    for register,w in helpers.items():
        key=native['helper_residual_refs'][register];record=native['records'][key]
        recipe=record['recipe'];endpoint=trace['endpoints'][register]
        need(w['relative_native_ref']==key and w['width']==recipe['rank'],'actual helper wrapper binding')
        need(w['initial']==endpoint['initial'] and w['final']==endpoint['final'],'actual nonzero helper entry/exit frames')
        pre=C.N.adjoint(C.N.monomial(recipe['right']));post=C.N.adjoint(C.N.monomial(recipe['left']))
        need(json.loads(json.dumps(pre))==w['prewrapper'] and json.loads(json.dumps(post))==w['postwrapper'],'literal inverse monomial wrapper factors')
        operation=C.chart(C.canonical(endpoint['initial'])).adjoint().then(C.chart(C.canonical(endpoint['final'])))
        C.N.equal(pre+tuple(operation.circuit)+post,C.N.fourier(recipe['rank']),'normalized complete helper spectators and phase')
    data=wrappers['data'];need(len(data)==224 and {e['register'] for e in data}==set(range(224)),'complete intrinsic data adapter coverage')
    for e in data:
        endpoint=trace['endpoints'][str(e['register'])]
        source=(e['register']<112) if trace.get('orientation')!='backward' else (112<=e['register']<224)
        if source:
            old=C.canonical(endpoint['initial']);need(len(old)==1,'source singleton')
            p=old[0];operation=C.CE.cgate(9,p).adjoint().then(C.chart(old))
            need(e['role']=='source' and e['position']=='entry','source adapter placement')
        else:
            new=C.canonical(endpoint['final']);normal=C.canonical(C.CE.nullspace(new,9));need(len(normal)==1,'target hyperplane')
            p=normal[0];intrinsic=C.CE.cgate(9,p,-1).then(C.CE.fourier(9))
            operation=C.chart(new).adjoint().then(intrinsic)
            need(e['role']=='target' and e['position']=='exit','target adapter placement')
        need(e['normal']==p and e['recipe']['rank']==0,'actual intrinsic point and monomial rank')
        C.N.equal(C.N.recipe(e['recipe']),tuple(operation.circuit),'intrinsic data adapter exact phase')
    return dict(helper_wrappers=len(helpers),intrinsic_data_adapters=len(data))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data',dest='variant',type=Path,default=HERE/'data');parser.add_argument('--out',type=Path)
    args=parser.parse_args();reports={};hashes={};controls=[];postlude_reports={}
    package=HERE.parent.resolve()
    if args.out:
        target=args.out.resolve()
        need(target!=package and package not in target.parents,'receipt output must be outside the read-only package')
    for pin in json.loads((HERE/'SOURCE-PINS.json').read_bytes())['files']:
        need(hashlib.sha256((HERE/pin['path']).read_bytes()).hexdigest()==pin['sha256'],'portable source drift: '+pin['path'])
    postludes=json.loads((args.variant/'postludes.json').read_bytes())
    for orientation in ('forward','backward'):
        trace_path=args.variant/(orientation+'.json')
        native_path=args.variant/('native-'+orientation+'.json.gz')
        trace=json.loads(trace_path.read_bytes());native=json.loads(gzip.decompress(native_path.read_bytes()))
        report=replay(trace);jobs=check_native(trace,native)
        wrapper_path=args.variant/('wrappers-'+orientation+'.json')
        wrappers=json.loads(wrapper_path.read_bytes())
        need(wrappers['trace_sha256']==hashlib.sha256(trace_path.read_bytes()).hexdigest(),'wrapper exact trace source binding')
        need(wrappers['native_payload_sha256']==hashlib.sha256(gzip.decompress(native_path.read_bytes())).hexdigest(),'wrapper exact native payload binding')
        report['wrappers']=check_wrappers(trace,native,wrappers)
        report['native_jobs']=len(jobs);report['precision']=calculate(trace)
        reports[orientation]=report
        postlude=postludes[orientation]
        private={e[1] for e in trace['events'] if e[0] in ('copy','zero_buffer')}
        need(len(postlude)==len(private)==76 and {e[1] for e in postlude}==private,'exact complete owned-array CLEAR postlude')
        need(all(e[0]=='clear' for e in postlude),'postlude has only actual exact CLEAR instructions')
        composed=copy.deepcopy(trace);composed['events'].extend(postlude)
        composed_report=replay(composed)
        need(composed_report['paid_profile']==report['paid_profile'],'CLEAR postlude adds no recursive child')
        need(composed_report['private_fields']==76,'postlude preserves actual private stock')
        postlude_reports[orientation]=dict(exact_clear_instructions=len(postlude),
            complete_public_columns=composed_report['independent_input_columns'],
            every_owned_private_array_returns_zero=True,extra_paid_children=0,
            actual_composed_word_sha256=hashlib.sha256(json.dumps(composed['events'],separators=(',',':')).encode()).hexdigest())
        hashes[orientation+'_trace']=hashlib.sha256(trace_path.read_bytes()).hexdigest()
        hashes[orientation+'_native_payload']=hashlib.sha256(gzip.decompress(native_path.read_bytes())).hexdigest()
        for kind in ('transport','helper_residual'):
            key=next(k for k,v in jobs.items() if v['kind']==kind)
            bad=copy.deepcopy(native['records'][key]['recipe'])
            bad['left']['phase']=(bad['left']['phase']+1)%4
            controls.append(rejected(lambda:C.N.equal(C.N.recipe(bad),tuple(jobs[key]['actual'].circuit),'mutated phase'),orientation+'_'+kind+'_phase'))
        if orientation=='forward':
            bad=copy.deepcopy(trace)
            event=next(e for e in reversed(bad['events']) if e[0]=='add' and 112<=e[1]<224)
            event[3]=str(-Fraction(event[3]))
            controls.append(rejected(lambda:replay(bad),'wrong_last_target_coefficient'))
            bad=copy.deepcopy(trace)
            index=next(i for i,e in enumerate(bad['events']) if e[0]=='handoff')
            del bad['events'][index]
            controls.append(rejected(lambda:replay(bad),'missing_actual_reference_change'))
            bad=copy.deepcopy(native)
            index=next(i for i,r in enumerate(bad['event_recipe_refs']) if r)
            bad['event_recipe_refs'][index]=None
            controls.append(rejected(lambda:need(bad['event_recipe_refs']==C.make_jobs(trace,literal_bound=True)[1],'binding changed'),'missing_native_occurrence_binding'))
        print('PASS_INDEPENDENT_'+orientation.upper()+'_LOCAL_WORD',len(jobs),'native jobs',flush=True)
    result=dict(status='PASS_COMPLETE_TWO_ORIENTATION_LOCAL_NATIVE_VARIANT',
                reports=reports,source_hashes=hashes,negative_controls=controls,
                exact_owned_clear_postludes=postlude_reports,
                source_compiler_sha256=hashlib.sha256((C.VENDOR/'clifford_exact.py').read_bytes()).hexdigest(),
                independent_native_interpreter_sha256=hashlib.sha256((C.VENDOR/'native_verify.py').read_bytes()).hexdigest(),
                scope='Exact finite local words, arbitrary dirty logical restoration, owned-zero scratch and all actual native phase bindings. Whole-call owners, physical finite invoice, exact completed-child depth/precision admission, tape and all-size transfer remain separate.')
    expected=json.loads((args.variant/'expected-local.json').read_bytes())
    for key in ('reports','source_hashes','negative_controls','source_compiler_sha256','independent_native_interpreter_sha256'):
        need(json.loads(json.dumps(result[key]))==expected[key],'canonical exact local receipt mismatch: '+key)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('PASS_PORTABLE_LOCAL_NATIVE_AND_EXACT_PRIVATE_POSTLUDE',len(controls),'fault controls',flush=True)

if __name__=='__main__':main()
