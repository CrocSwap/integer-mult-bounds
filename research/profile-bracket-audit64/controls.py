"""Semantic and source-inventory rejection controls. Apache-2.0."""
import copy,json,sys
from fractions import Fraction as F
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
from repair import need,bracket,classify
from verify import sources
from independent import audit

def main():
    c=json.loads((P/'EXPECTED.json').read_bytes());names=[]
    def reject(name,fn):
        try:fn()
        except (ValueError,KeyError):names.append(name)
        else:raise ValueError('accepted control: '+name)
    for name,mut in [
      ('legacy_bracket_mislabeled_safe',lambda x:x['fixtures'][0].__setitem__('legacy_bracket_excludes_root',False)),
      ('wrong_root_side_bracket',lambda x:x['fixtures'][0]['repair'].__setitem__('certified_bracket',x['fixtures'][0]['legacy_bracket'])),
      ('surcharge_omitted',lambda x:x['fixtures'][2].__setitem__('factor','1')),
      ('off_by_one_algebraic_floor',lambda x:x['fixtures'][0]['n'].__setitem__('1',x['fixtures'][0]['n']['1']+1)),
      ('missing_case',lambda x:x['fixtures'].pop()),
      ('capped_ambiguity_called_certified',lambda x:x['capped_control'].__setitem__('status','CERTIFIED'))]:
        x=copy.deepcopy(c);mut(x);reject(name,lambda x=x:audit(x))
    m=json.loads((P/'SOURCES.json').read_bytes())
    for name,field in [('repository_source_omitted','repository_files'),('vendor_source_omitted','package_files')]:
        x=copy.deepcopy(m);del x[field][next(iter(x[field]))];reject(name,lambda x=x:sources(x))
    x=copy.deepcopy(m);x['package_files']['vendor/bitprof.py']='0'*64
    reject('original_source_corrupted',lambda:sources(x))
    reject('invalid_interval',lambda:classify(F(1),F(-1)))
    # An exact root at the first midpoint is not strictly sign decidable.
    exact=lambda x,t:(x-F(1,20),x-F(1,20))
    result=bracket(exact,digits=8,initial_terms=1,max_terms=4)
    need(result['status']=='UNRESOLVED_INTERIOR_SIGN' and result['certified_bracket']==['0','1/10'],'exact-midpoint equality control')
    # A broad oracle cannot certify even its initial endpoints.
    wide=bracket(lambda x,t:(F(-1),F(1)),digits=8,initial_terms=1,max_terms=2)
    need(wide['status']=='UNRESOLVED_INITIAL_ENDPOINTS' and wide['certified_bracket'] is None,'initial unknown control')
    print(json.dumps(dict(status='PASS_REJECTION_CONTROLS',rejected=names,equality_and_initial_unknown_controls=2),sort_keys=True))
if __name__=='__main__':main()
