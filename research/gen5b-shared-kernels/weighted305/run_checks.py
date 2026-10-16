"""Portable fresh PR305 replay, with explicit inherited interfaces."""
from pathlib import Path
import argparse,contextlib,hashlib,io,json,os,time

def run(labels=('154','156'),check=False):
    import source_data as src
    import reproduce_pr305 as base,reproduce_complex,witness
    import check_bridge as bridge,check_scalar_bounds as norms,check_shared_banks as banks
    import bind_candidate
    src.OUTPUT.mkdir(parents=True,exist_ok=True);started=time.monotonic();source_count=src.verify()
    def stable(x):
        if isinstance(x,dict):return {k:stable(v)for k,v in x.items()if k not in('seconds','receipt_sha256','bridge_receipt_sha256','norm_receipt_sha256')}
        if isinstance(x,list):return [stable(v)for v in x]
        return x
    def save(name,result):
        serial=json.loads(json.dumps(base.ae.serial(result)));path=src.OUTPUT/(name+'.json')
        path.write_text(json.dumps(serial,indent=2)+'\n');expected=src.ROOT/'certificates'/(name+'.json')
        if check and expected.exists()and(name!='aggregate'or tuple(labels)==('154','156')):
            assert stable(serial)==json.loads(expected.read_text()),('Frozen receipt differs',name)
        return path
    save('baseline',base.run());save('complex',reproduce_complex.run())
    results={}
    for label in labels:
        path=witness.write_case(label);bridge.configure(label)
        b=bridge.run();n=norms.run(path)
        bp=save('bridge'+label,b);np=save('norm'+label,n)
        folder=src.OUTPUT/('banks'+label);bank=banks.run(path,folder);br=save('banks'+label,bank)
        result=bind_candidate.run('case'+label,path,bp,np,br,folder/'bank-address-table.json')
        expected={'154':('0.000751160050810041',1229280,483000,2454160,2541),'156':('0.000751160060489770',1229275,483015,2454150,2545)}[label]
        assert(result['assembly']['kappa'],result['literal_stock'],result['calls'],result['rank_mass'],result['witness_counts']['setup_pairs'])==(base.F(expected[0]),*expected[1:])
        assert(result['norm_review']['forward'],result['norm_review']['inverse'])==(438151,14104135)
        assert result['norm_review']['fresh_norm_receipt']['actual_sink_redirects']==16
        assert result['role_bank_binding']['assignments_per_stage']==925440
        save('case'+label,result)
        results[label]=dict(kappa=expected[0],stock=expected[1],calls=expected[2],rank=expected[3],pairs=expected[4],charts=result['changed_charts']['charts'],finite_coefficient=result['finite_arithmetic']['displayed_finite_coefficient'],payload=result['norm_review']['payload'],legacy104=False,explicit112=True)
    import build_response_cache,port_and_reclose
    with contextlib.redirect_stdout(io.StringIO()):cache=build_response_cache.run()
    port=port_and_reclose.run();save('bounded-port',port)
    for label in labels:
        row=witness.case(label)
        assert hashlib.sha256((src.OUTPUT/row['file']).read_bytes()).hexdigest()==row['sha256']
    result=dict(status='PASS_PR305_BOUNDED_PORTABLE_AGGREGATE',source_files=source_count,cases=results,
        bounded_search=dict(complete_group_pivots=154,third_line_reclosures=1,surviving_relations=5,selected_before_parity=3,selected_after_parity=2,parity_omitted_pivot=9355),
        seconds=time.monotonic()-started,scope='Two fixed candidates only, under inherited full decoder/compiler/all-size interfaces. Actual eight sinks and16 redirects are freshly checked. Legacy104 fails; explicit112 passes. No current-best or optimality claim.')
    save('aggregate',result);return result
if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path);p.add_argument('--output',type=Path);p.add_argument('--case',choices=('154','156','both'),default='both');p.add_argument('--check',action='store_true')
    a=p.parse_args()
    if a.inputs:os.environ['PR305_INPUTS']=str(a.inputs.resolve())
    if a.output:os.environ['PR305_OUTPUTS']=str(a.output.resolve())
    print(json.dumps(run(('154','156')if a.case=='both'else(a.case,),a.check),indent=2))
