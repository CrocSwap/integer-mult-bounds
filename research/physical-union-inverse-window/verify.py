"""Registered actual-source/physical-window integration replay."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import itertools
import json
import sys
PACKAGE=Path(__file__).resolve().parent
sys.path.insert(0,str(PACKAGE))
_spec=importlib.util.spec_from_file_location('union_fixture_sources',PACKAGE/'sources.py')
sources=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=sources;_spec.loader.exec_module(sources)
import reference_source
import source_window
import source_checks
import independent_oracle
from schedule_hook import prepared_schedule


def need(ok,message):
    if not ok:raise ValueError(message)


def stable(value):
    if isinstance(value,dict):return {k:stable(v) for k,v in value.items() if k!='seconds'}
    if isinstance(value,(tuple,list)):return [stable(x) for x in value]
    return value


def run(extended=False):
    for row in json.loads((PACKAGE/'DEPENDENCIES.json').read_text())['files']:
        need(hashlib.sha256((PACKAGE/row['retained']).read_bytes()).hexdigest()==row['sha256'],
             'exact retained predecessor bytes: '+row['retained'])
    raw=reference_source.authenticated_inputs(PACKAGE)
    reference=reference_source.make_reference(raw,(61,3,2,1,3,32))
    window=source_window.make_window(reference) if extended else source_window.make_window(
        reference,length=4,interior_blocks=((1,2),),cap=2)
    source_review=independent_oracle.check_source(reference,window)
    controls=independent_oracle.source_controls(reference,window)
    checked_source=source_checks.run(source_window,reference)
    print('SOURCE_VALIDATED',file=sys.stderr,flush=True)
    with sources.physical_runtime():
        from records import Tape
        from words import BLANK
        from physical_fixture import Fixture,body
        import independent_transport
        import support_control,partial_control
        all_tapes=[];old=Tape.__init__
        def tracked(t):old(t);all_tapes.append(t)
        Tape.__init__=tracked
        fixture=None
        try:
            fixture=Fixture(window,all_tapes)
            print('PHYSICAL_PAGES_PREPARED',file=sys.stderr,flush=True)
            for bank,pair in zip(fixture.pages,((window.shear_lower,window.shear_upper),
                                                (window.f_lower,window.f_upper))):
                expected=independent_oracle.page_words(*pair,window.block,window.P)
                from physical_fixture import word
                for page,values in zip(bank,expected):
                    data=body(page)
                    need([word(data[i:i+window.w]) for i in range(0,len(data),window.w)]==list(values),
                         'independent original-reference physical page bytes')
            g=2;L=window.length
            points=list(itertools.product(range(L),repeat=g))
            initial={x:(((37*i+11)%41-20)*(1<<(window.P-8)),
                        ((53*i+7)%47-23)*(1<<(window.P-8))) for i,x in enumerate(points)}
            expected,grid_review=independent_oracle.full_grid(L,(window,)*g,initial)
            def callback(tape,start,count,axis,round_index,boundaries):
                tape.goto(start);records=[tape.read() for _ in range(count)]
                out=fixture.call(records,axis,round_index,g)
                tape.goto(start)
                for record in out:tape.write(record)
                return count//len(boundaries[axis])
            fixture.shape_for(g)
            schedule=prepared_schedule(PACKAGE/'retained/pr4100-union-head-travel__verify.py',
                (window.E,)*g,initial,expected,callback,fixture.header_codec.width+2*window.w)
            result=schedule.run(g,L,[len(window.E)]*g,0)
            need(result['ok'] and result.pop('result')==expected,'complete retained schedule and source oracle')
            need(result['streamed']==result['sumF']==grid_review['visited_records'],
                 'exact source incidence across physical callbacks')
            need(grid_review['later_lines_with_changed_inputs']>0,'later rounds consume actual updated values')
            layout_checks=independent_transport.run(fixture.owner)
            support_checks=support_control.run(fixture.owner,independent_oracle)
            partial_checks=partial_control.run(fixture.owner,independent_oracle)
            table=sorted((list(point),list(pair)) for point,pair in expected.items())
            receipt=dict(marker='PASS_PHYSICAL_UNION_INVERSE_WINDOW',source=window.receipt(),
                source_review=source_review,source_controls=controls,source_checks=checked_source,
                preparation=fixture.preparation,transactions=fixture.receipts,
                schedule=result,grid_review=grid_review,transport=layout_checks,
                off_block_control=support_checks,partial_failure_control=partial_checks,
                scalar_products=sum(x['scalar_products'] for x in fixture.receipts),
                owned_roles=len(fixture.owner.forbidden()),
                final_output_sha256=hashlib.sha256(json.dumps(table,separators=(',',':')).encode()).hexdigest(),
                inherited_assumptions='prepared same-context headers; host union outside literal step5; no broad forward/outer theorem',
                no_new_kappa=True)
            return receipt
        finally:
            if fixture is not None:fixture.close()
            Tape.__init__=old


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--extended',action='store_true')
    parser.add_argument('--write-result',action='store_true');parser.add_argument('--emit',action='store_true')
    args=parser.parse_args();result=run(args.extended)
    target=PACKAGE/('EXTENDED.json' if args.extended else 'RESULT.json')
    if args.write_result:target.write_text(json.dumps(stable(result),indent=2,sort_keys=True)+'\n')
    elif not args.emit:need(stable(result)==json.loads(target.read_text()),'exact stable union receipt')
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()
