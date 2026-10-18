"""Reject understated T74 prefix, stock and invocation charges using strict assembly."""
import argparse,copy,hashlib,json,os,sys
from pathlib import Path
assert __debug__
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--strict',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
sys.path.insert(0,str(P/'code'));os.environ['GAIN_PR564_SOURCE']=str(a.source.resolve());os.environ['WITNESS_SPEC']=str(a.strict/'runtime/data/SPEC.json')
from assemble import assemble
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
digest=lambda v:hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
op=a.strict/'global/audit/OWNERS-AND-PROFILE.json';ip=a.strict/'global/audit/PREFIX-AND-INVOICE.json';owner=json.loads(op.read_text());invoice=json.loads(ip.read_text());assemble(owner,invoice,sha(op),sha(ip))
def old_prefix(o,i):
 i['charged_prefix_bits']=1024;i['row_prefix_extra']=2048;i['finite']['physical_row_coefficient']-=2048

def old_call_count(o,i):
 i['complete_invocation_sweeps']-=1;i['bridge_sweeps']-=1

def old_parent_idle(o,i):o['source_idle_children_charged']//=2

def old_stock(o,i):i['physical_stock_identity']['data_and_owner_families']//=2

def missing_call(o,i):i['selected_calls'].pop()

def low_row(o,i):i['finite']['physical_row_coefficient']-=1
rejected=[]
for fn in [old_prefix,old_call_count,old_parent_idle,old_stock,missing_call,low_row]:
 o,i=copy.deepcopy(owner),copy.deepcopy(invoice);fn(o,i);assert (o,i)!=(owner,invoice), 'geometry mutant must change actual receipts';oh=digest(o);i['owner_audit_sha256']=oh
 try:assemble(o,i,oh,digest(i))
 except AssertionError as e:rejected.append(dict(name=fn.__name__,reason=str(e) or 'strict arithmetic invariant'))
 else:raise AssertionError('accepted '+fn.__name__)
a.out.write_text(json.dumps(dict(status='PASS_T74_GEOMETRY_AND_CHARGE_CONTROLS',rejected=rejected),indent=2)+'\n');print('PASS_GEOMETRY_CONTROLS',len(rejected))
