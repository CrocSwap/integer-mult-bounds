"""Apply Josie Elliston's owner audit and Sagar Thakrar's pricing to PR1094.
Maintainer composition by Douglas Colkitt with OpenAI Codex assistance.
Apache-2.0. Does not extend either auditor's inherited-interface scope.
"""
from pathlib import Path
import hashlib,importlib.util,json,sys,gzip
ROOT=Path(__file__).resolve().parents[2]
def load_module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def require(ok):
 if not ok:raise ValueError('Independent PR1094 check failed')

def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())

a=load_module('owners',ROOT/'research/t16-owner-audit-seed67/verify.py')
pins=read(ROOT/'research/t16-owner-audit-seed67/SOURCES.json')['inputs']
require(hashlib.sha256((ROOT/a.TEMPLATE).read_bytes()).hexdigest()==pins['template_sha256'])
require(hashlib.sha256((ROOT/a.PHASES).read_bytes()).hexdigest()==pins['data_phases_sha256'])
require(hashlib.sha256(gzip.decompress(a.WORD.read_bytes())).hexdigest()==pins['word_content_sha256'])
w=read(a.WORD);geo=a.geometry(read(ROOT/a.TEMPLATE),read(ROOT/a.PHASES));widths=a.word_widths(w);local=a.as_profile(w['report']['local_profile'])
p=ROOT/'research/complex-t16-rare-pattern-exchanges';spec=read(p/'data/SPEC.json');plan=read(p/'data/PLAN.json');roles=read(p/'data/OWNERS.json.gz')
require(a.as_profile(spec['providers']['gauge44']['expected_profile'])==local)
require(a.Counter(widths)==a.as_profile(spec['providers']['gauge44']['inventory']))
owned=a.audit(geo,widths,local,roles,plan,a.as_profile(spec['expected']['idle_remainder_profile']),16)
require(owned['profile']==a.as_profile(read(p/'PROFILE.json'))==a.as_profile(plan['profile']))
controls=a.controls(geo,widths,local,roles,plan,a.as_profile(spec['expected']['idle_remainder_profile']),16)
require(len(controls)==11)
sys.path.insert(0,str(ROOT/'research/pending-claims-independent-pricing'))
sweep=load_module('pricing',ROOT/'research/pending-claims-independent-pricing/sweep.py')
assembly=read(Path(sys.argv[1]));head=read(Path(__file__).with_name('PLAN.json'))['heads']['1094']
c=dict(pr=1094,head=head,profile=owned['profile'],live=14336,calls=144,complex_lower=assembly['complex_lower'],record_kappa=assembly['kappa'],claimed_kappa_decimal='0.001672660197076918',bit_lower=assembly['bit_lower'])
priced=sweep.price(c)
for k in ['endpoint_certified','deficit_equals_W_minus_64N','halving','record_bit_is_pr589','kappa_equals_record','kappa_equals_title']:require(priced[k])
out=dict(status='PASS_INDEPENDENT_PR1094_OWNERS_AND_PRICE',owner=owned,controls=controls,price=priced)
Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n')
print(out['status'],priced['kappa_exact_decimal'])
