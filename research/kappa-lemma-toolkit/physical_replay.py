"""Independent audit of every improved physical-family factor and native ABI."""
import argparse,importlib.util,json,sys,gzip,hashlib
from pathlib import Path
from types import SimpleNamespace
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'selective-borrowing-kappa'
def normalize_result(result,archive,expected_payload):
    if hashlib.sha256(archive).hexdigest()!=result['actual_factors_sha256']:raise ValueError('fresh archive does not match its own receipt')
    payload=hashlib.sha256(gzip.decompress(archive)).hexdigest()
    if payload!=expected_payload:raise ValueError('exact decompressed factor payload differs')
    normalized=dict(result);normalized['actual_factors_payload_sha256']=payload
    normalized.pop('actual_factors_sha256');normalized.pop('seconds',None);return normalized
def replay(out):
    sp=importlib.util.spec_from_file_location('retained_independent_factor_audit',BASE/'independent/audit.py');a=importlib.util.module_from_spec(sp);sys.modules[sp.name]=a;sp.loader.exec_module(a)
    args=SimpleNamespace(parent=BASE/'independent/inputs/T8-PARENT.json.gz',parent_sha256='025448abdf2012d327e50a009084e1501690d05e650300d2982836aa0350ae00',phases=BASE/'owners/inputs/DATA-PHASES.json',plan=BASE/'owners/inputs/PLAN.json',owners=HERE/'OWNERS.json.gz',forward_trace=BASE/'local/data/forward.json',backward_trace=BASE/'local/data/backward.json',forward_native=BASE/'local/data/native-forward.json.gz',backward_native=BASE/'local/data/native-backward.json.gz',forward_wrapper=BASE/'local/data/wrappers-forward.json',backward_wrapper=BASE/'local/data/wrappers-backward.json',engine=BASE/'local/vendor/native_verify.py',out=out)
    a.audit(args)
    result=json.loads((out/'RESULT.json').read_text());archive=(out/'ACTUAL-FAMILY-FACTORS.json.gz').read_bytes()
    expected=json.loads((HERE/'PHYSICAL-EXPECTED.json').read_bytes())
    return normalize_result(result,archive,expected['actual_factors_payload_sha256'])
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    if args.out.resolve().is_relative_to(HERE.parent):raise ValueError('write receipts outside both source packages')
    args.out.parent.mkdir(parents=True,exist_ok=True);r=replay(args.out);(args.out/'MATHEMATICAL-RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
