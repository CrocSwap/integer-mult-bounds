"""Check strict payload boundaries, then mutate the completed T37 admission.

Use --arithmetic-only before the strict global replay exists. This mode does
not claim that altered payloads have a complete controller/invoice admission.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import traceback

if not __debug__:
    raise RuntimeError('Assertions must remain enabled; do not use Python -O')
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
digest=lambda obj:hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arithmetic-only',action='store_true')
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--geometry',type=Path,help='Defaults to WORK/INDEPENDENT-OWNERS.json')
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    WORK=args.work.resolve()
    args.out=args.out.resolve()
    assert not args.out.exists() and not args.out.is_relative_to(ROOT),'New output outside checkout required'
    geometry_path=(args.geometry or WORK/'INDEPENDENT-OWNERS.json').resolve()
    geometry=json.loads(geometry_path.read_text())
    assert geometry['status']=='PASS_INDEPENDENT_VARIABLE_T_LITERAL_WINDOWS_CHARTS_PREFIX_ROW'
    assert geometry['prefix_bits']==779 and geometry['physical_stock_bits']==2643
    boundary=[]
    for payload,expected in [(512,False),(778,False),(779,False),(780,True),(1024,True),(2356,True),(2357,False)]:
        prefix=geometry['local_prefix_bits']+37+geometry['calls']+geometry['bridge_events']+4
        row=2*geometry['physical_stock_bits']+9909+252+2*payload
        okay=prefix<payload and row<20161
        assert okay==expected
        boundary.append(dict(payload=payload,prefix=prefix,row=row,accepted_by_reserve_arithmetic=okay,
          rejection=None if okay else 'strict prefix'if prefix>=payload else 'strict row'))
    result=dict(status='PASS_STRICT_PAYLOAD_RESERVE_BOUNDARIES',boundary=boundary,
      geometry_sha256=sha(geometry_path),geometry_path=str(geometry_path),
      scope='Strict finite prefix and row parameter arithmetic. Boundary alternatives are not complete alternative supplier admissions.')
    if not args.arithmetic_only:
        source=ROOT/'research/complex-k492-owner-repair/vendor/multicold'
        code=WORK/'runtime/code'
        os.environ['GAIN_PR564_SOURCE']=str(source)
        os.environ['MULTICOLD_SOURCE']=str(source)
        os.environ['WITNESS_SPEC']=str(WORK/'runtime/data/SPEC.json')
        for key in ('WITNESS_DISCOVER','WITNESS_RECORD','PYTHONOPTIMIZE'):
            os.environ.pop(key,None)
        sys.path.insert(0,str(code))
        spec=importlib.util.spec_from_file_location('payload_assembly',code/'assemble.py')
        A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
        owner_path=WORK/'strict/global/audit/OWNERS-AND-PROFILE.json'
        invoice_path=WORK/'strict/global/audit/PREFIX-AND-INVOICE.json'
        owner=json.loads(owner_path.read_text());invoice=json.loads(invoice_path.read_text())
        baseline=A.assemble(owner,invoice,sha(owner_path),sha(invoice_path))
        assert baseline['kappa_decimal']=='0.001662039077758742'
        cases=[]
        for payload in (512,779,780,1023,1025):
            bad=copy.deepcopy(invoice)
            bad['charged_prefix_bits']=payload
            bad['row_prefix_extra']=2*payload
            bad['finite']['physical_row_coefficient']=15447+2*payload
            cases.append(('different_payload_'+str(payload)+'_and_consistent_row',bad))
        for prefix in (491,778,780,1024,1025):
            bad=copy.deepcopy(invoice);bad['global_prefix_bits']=prefix
            cases.append(('incorrect_prefix_'+str(prefix),bad))
        bad=copy.deepcopy(invoice)
        bad['row_prefix_extra']=1024
        bad['finite']['physical_row_coefficient']=16471
        cases.append(('new_payload_but_old_512_row_charge',bad))
        rejected=[]
        for name,bad in cases:
            try:A.assemble(owner,bad,sha(owner_path),digest(bad))
            except AssertionError:
                frame=traceback.extract_tb(sys.exc_info()[2])[-1]
                rejected.append(dict(name=name,source_line=frame.lineno,predicate=frame.line))
            else:raise AssertionError('Accepted payload mutation '+name)
        result.update(status='PASS_T37_PAYLOAD_BOUNDARIES_AND_STRICT_ADMISSION_MUTATIONS',
          baseline_kappa=baseline['kappa_decimal'],rejected_controls=rejected,
          inputs={str(p.resolve()):sha(p)for p in [geometry_path,owner_path,invoice_path,code/'assemble.py',WORK/'runtime/data/SPEC.json']},
          scope='Strict reserve parameter boundaries plus actual frozen T37 assembly rejects eleven changed/understated payload-prefix-row receipts. Existing geometric and supplier audits remain prerequisites. Supplier ancestry admission is checked separately by the driver.')
    out=args.out
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],len(boundary),'boundaries;',len(result.get('rejected_controls',[])),'actual assembly mutations')

if __name__=='__main__':main()
