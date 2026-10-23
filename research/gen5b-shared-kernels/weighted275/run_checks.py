"""Portable full replay, with generated banks/charts outside frozen receipts.

All executed modules are this contribution's authored code. Upstream files are
read-only data, including Python source parsed as syntax for the cap audit.
"""
from pathlib import Path
import argparse,contextlib,io,json,os,sys,time

def run(case_names=('70','166'),screen=True,check=False):
    import source_data as src
    import reproduce_pr275 as base,reproduce_complex
    import check_shared_banks as banks
    import integrate_bounded_candidate as integration
    from cases import CASES
    src.OUTPUT.mkdir(parents=True,exist_ok=True)
    started=time.monotonic();count=src.verify()
    def stable(x):
        if isinstance(x,dict):return {k:stable(v)for k,v in x.items()if k not in ('seconds','receipt_sha256')}
        if isinstance(x,list):return [stable(v)for v in x]
        return x
    def save(name,result):
        serial=base.ae.serial(result)
        (src.OUTPUT/(name+'.json')).write_text(json.dumps(serial,indent=2)+'\n')
        expected=src.ROOT/'certificates'/(name+'.json')
        if check and expected.exists() and (name!='aggregate' or (tuple(case_names)==('70','166') and screen)):
            assert stable(json.loads(json.dumps(serial)))==json.loads(expected.read_text()),('Frozen certificate differs',name)

    baseline=base.run();complex_result=reproduce_complex.run()
    save('baseline',baseline);save('complex',complex_result)
    results={}
    for name in case_names:
        case=CASES[name];candidate=src.ROOT/case['file'];bank_dir=src.OUTPUT/('banks'+name)
        bank=banks.run(candidate,bank_dir);bank_path=src.OUTPUT/('banks'+name+'.json');save('banks'+name,bank)
        result=integration.run('case'+name,candidate,src.ROOT,bank_path,bank_dir/'bank-address-table.json')
        assert result['literal_stock']==case['stock'] and result['calls']==case['calls'] and result['rank_mass']==case['rank']
        assert result['assembly']['kappa']==base.F(case['kappa'])
        assert result['norm_review']['forward']==case['F'] and result['norm_review']['inverse']==case['B']
        assert result['changed_charts']['charts']==case['chart_programs']
        assert result['finite_arithmetic']['displayed_finite_coefficient']==case['finite_coefficient']
        assert result['role_bank_binding']['assignment_sha256']==case['assignment_sha256']
        save('case'+name,result);results[name]=dict(kappa=case['kappa'],stock=case['stock'],calls=case['calls'],rank=case['rank'],chart_programs=case['chart_programs'],payload_bits=result['norm_review']['payload_bits'],original104=result['norm_review']['original_cap_satisfied'],explicit_cap_bits=result['norm_review']['explicit_candidate_cap_bits'],finite_coefficient=case['finite_coefficient'])
    search_summary=None
    if screen:
        import map_roles,build_response_cache
        with contextlib.redirect_stdout(io.StringIO()):mapping=map_roles.run();cache=build_response_cache.run()
        assert len(mapping['final12_new_recipient_helpers'])==12
        import search_expanded_lines,resolve_group_overlaps
        search=search_expanded_lines.run()
        assert search['lines_tested']==276 and search['eligible_unused_helpers']==8085 and search['eligible_reused_donors']==1591
        expected={(16,17):(136,170),(6,7):(36,46),(2,3):(12,16)}
        assert {tuple(z['line']):(z['selected_pivots'],z['used_donors'])for z in search['best_candidates']}==expected
        for row in search['best_candidates']:
            file=src.ROOT/('candidate-line%d-%d.json'%tuple(row['line']));candidate=json.loads(file.read_text())
            assert [(e['virtual_pivot'],e['virtual_donors'])for e in candidate['entries']]==[(e['pivot'],e['donors'])for e in row['relations']]
            from compose_screened_groups import ledger
            assert ledger(candidate['entries'])[0]==row['local_histogram_delta']
        overlap=resolve_group_overlaps.run();save('overlap',overlap)
        search_summary={k:v for k,v in search.items()if k not in('best_candidates','all_line_receipts')}
        save('line-screen',search)
    result=dict(status='PASS_WEIGHTED275_PORTABLE_AGGREGATE',source_files=count,cases=results,screen=search_summary,seconds=time.monotonic()-started,scope='Changed obligations under inherited physical-decoder and compiler interfaces. Exact candidate112 ceiling is separate from the failing legacy104 assertion. Rounded closure is a bounded discovery procedure, not a global optimality proof.')
    save('aggregate',result);return result

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    parser=argparse.ArgumentParser();parser.add_argument('--inputs',type=Path);parser.add_argument('--output',type=Path);parser.add_argument('--case',choices=('70','166','both'),default='both');parser.add_argument('--skip-screen',action='store_true');parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if args.inputs:os.environ['PR275_INPUTS']=str(args.inputs.resolve())
    if args.output:os.environ['PR275_OUTPUTS']=str(args.output.resolve())
    print(json.dumps(run(('70','166')if args.case=='both'else(args.case,),not args.skip_screen,args.check),indent=2))
