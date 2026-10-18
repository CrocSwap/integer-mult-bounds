# SPDX-License-Identifier: Apache-2.0
"""Exact fixed-family owner-packing bound; outputs are outside the checkout."""
import argparse
import copy
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def require(ok,message):
    if not ok:raise ValueError(message)
def read(path):return json.loads(path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args();out=args.out.resolve()
require(not sys.flags.optimize,'Outer engine assertions must remain enabled')
require(not out.exists()and not out.is_relative_to(ROOT),'New output directory outside checkout required')
manifest=read(HERE/'MANIFEST.json')
actual={str(p.relative_to(HERE)):sha(p)for p in HERE.rglob('*')if p.is_file()and p.name!='MANIFEST.json'and '__pycache__'not in p.parts}
require(actual==manifest,'Package manifest')
for relative,expected in read(HERE/'DEPENDENCY-PINS.json').items():require(sha(ROOT/relative)==expected,'Source dependency '+relative)
out.mkdir(parents=True)
for script,arguments in [('search.py',['--out',out/'SEARCH.json']),('independent_bound.py',['--input',out/'SEARCH.json','--out',out/'INDEPENDENT.json'])]:
    with(out/(script+'.log')).open('w')as log:
        subprocess.run([sys.executable,'-B',str(HERE/script),*map(str,arguments)],stdout=log,stderr=subprocess.STDOUT,check=True)
rejected=[]
producer=read(out/'SEARCH.json')
for name,mutate in [
    ('incorrect_dual_price',lambda x:x['upper'].__setitem__('44',x['upper']['44']+1)),
    ('infeasible_rank6_incumbent',lambda x:x['candidates'][20].__setitem__('non48',[6])),
    ('omitted_replica_count',lambda x:x['candidates'].pop()),
]:
    bad=copy.deepcopy(producer);mutate(bad)
    path=out/(name+'.json');path.write_text(json.dumps(bad)+'\n')
    process=subprocess.run([sys.executable,'-B',str(HERE/'independent_bound.py'),'--input',str(path),'--out',str(out/(name+'-accepted.json'))],text=True,capture_output=True)
    require(process.returncode!=0,'Accepted negative control '+name)
    (out/(name+'.log')).write_text(process.stdout+process.stderr)
    rejected.append(dict(name=name,reason=process.stderr.splitlines()[-1]))
claim=read(ROOT/'research/complex-t21-owners/data/CLAIM.json');bound=read(out/'INDEPENDENT.json')
z=Fraction(claim['complex_lower'])+Fraction(1,10**24)
require(Fraction(bound['endpoint'])==z and bound['winner']==21,'Successor endpoint and winning replica count')
helper_path=ROOT/'research/complex-t21-owners/vendor/pr870/independent/price_profile_t16.py'
helpers=load(helper_path,'unchanged_outer_price')
engine=helpers.load(ROOT/'research/complex-k492-owner-repair/vendor/multicold/engines','outer')
upper=helpers.outer47(Fraction(claim['bit_lower']),z,engine)
require(Fraction(upper['kappa'])==Fraction(claim['kappa']),'Same maximum 1e-18 kappa grid at relaxed upper endpoint')
result=dict(status='PASS_FIXED_U8_WHOLE_OWNER_GRID_BOUND',complex_upper=str(z),kappa_grid_upper=upper['kappa'],
            kappa_decimal=upper['kappa_decimal'],best_replicas=21,best_idle=bound['best_idle'],
            bin_count_vectors=bound['bin_vectors'],remainder_count_vectors=bound['complete_states'],
            best_profile_moment=bound['best_profile_moment'],upper_outer=upper,
            controls_rejected=rejected,
            input_sha256={'manifest':sha(HERE/'MANIFEST.json'),'dependencies':sha(HERE/'DEPENDENCY-PINS.json')},
            artifact_sha256={p.name:sha(p)for p in out.iterdir()if p.is_file()},
            scope='Fixed U8 local profile, full helper widths, cap8/16/32/48 stock and retained prefix rule T<=22. No packing in this family yields a higher 1e-24 complex endpoint or a higher 1e-18 kappa under the same seven-step outer recipe. Attainability is checked separately by complex-t21-owners. Other words, capacities, helper splitting and prefix rules are outside scope.')
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],result['kappa_decimal'])
