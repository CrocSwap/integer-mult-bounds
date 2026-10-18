# SPDX-License-Identifier: Apache-2.0
"""Check the unchanged coverage-law envelope for the changed local word.

Yiyang (@Lyy-iiis), with substantial OpenAI Codex assistance. The envelope
engine and its scope are retained from complex-local-word-ceiling.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from fractions import Fraction as Q
import argparse,gzip,hashlib,json,types

def need(ok,why):
    if not ok: raise ValueError(why)
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,default=Path(__file__).resolve().parent);a=ap.parse_args();p=a.package
    tool=p/'vendor/ceiling.py'
    need(hashlib.sha256(tool.read_bytes()).hexdigest()=='86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc','exact retained envelope engine')
    c=types.ModuleType('retained_coverage_ceiling');exec(compile(tool.read_bytes(),str(tool),'exec'),c.__dict__)
    pins={'base':'001b14314d8db873d4d80826d4af9c40a3e5a1fecde743e5a26391bdf673f458','extra':'bc5bfe51178f0c3312d28318412ec490463c896ceed0660b9c443fcb76496546'}
    local={1:2394,2:642,3:266,4:128,5:26,8:8}
    for tag,h in pins.items():
        f=p/('words/WORD-'+tag+'.json.gz');need(hashlib.sha256(f.read_bytes()).hexdigest()==h,'exact candidate word')
        need({int(k):v for k,v in read(f)['report']['local_profile'].items()}==local,'both actual local profiles')
    evidence=read(p/'evidence/relaxation/LOCAL-CEILING.json');model=c.model(local,73,896,9,64)
    need({k:str(v) for k,v in model.items()}==evidence['model'],'coverage law and idle mass')
    lo=Q(evidence['complex_cap_lower']);hi=Q(evidence['complex_cap_upper'])
    need(c.relax(local,73,896,9,64,lo)[1]<1<c.relax(local,73,896,9,64,hi)[0],'strict exact ceiling bracket')
    claim=read(p/'CLAIM.json');kappa=Q(claim['kappa'])
    need(kappa<lo,'headline below local coverage ceiling')
    print(json.dumps(dict(status='PASS_ACTUAL_LOCAL_WORD_COVERAGE_CEILING',local_profile=local,lower=str(lo),upper=str(hi),candidate_fraction_of_upper=str(kappa/hi),scope='Rank-51 fractional idle relaxation under the inherited coverage law; not an attainable allocation. Modern headline compared directly, without the historical a/(1+a) conversion.'),sort_keys=True))
if __name__=='__main__':main()
