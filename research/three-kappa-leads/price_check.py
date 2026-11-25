"""Exact rational root enclosure and normalized paid-profile comparison."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,hashlib
from chronology_check import DEP,check,common,P
from dependency import load
price=load('retained_rational_price',DEP/'price.py')
def main():
 actual=check(common.read(P/'CHRONOLOGY-CANDIDATE.json'));expected=common.read(P/'PRICE-EXPECTED.json');H=actual['profile'];T=actual['replicas'];price.need(expected['profile']=={str(r):n for r,n in H.items()},'actual profile matches root input')
 retained=common.read(DEP/'EXPECTED.json')
 price.need(expected['comparator_profile']==retained['profile'] and expected['comparator_root_interval']==retained['root_interval'] and expected['comparator_replicas']==retained['replicas'],'retained PR3624 comparator binding')
 old={int(r):n for r,n in retained['profile'].items()};delta={r:450*H.get(r,0)-T*old.get(r,0)for r in set(H)|set(old)};price.need(sum(r*n for r,n in delta.items())==0,'normalized mass')
 difference=price.interval(delta,Q(expected['comparator_root_interval'][1]));price.need(difference[1]<0,'strict normalized cost decrease')
 signed=H.copy();signed[73]=-896*T;lo,hi=map(Q,expected['root_interval']);lower=price.interval(signed,lo);upper=price.interval(signed,hi);price.need(lower[1]<0<upper[0],'rational root bracket')
 result={'status':'PASS_EXACT_PROFILE_NOT_FULL_RELEASE','profile':H,'replicas':T,'normalized_delta_vs_PR3624':delta,'difference':price.compact(difference),'root_interval':expected['root_interval'],'lower_check':price.compact(lower),'upper_check':price.compact(upper),'endpoint':str(lo-Q(1,10**46)-Q(1,10**70))}
 directory=P/'comparators';provenance=common.read(directory/'SOURCES.json')
 for row in provenance['files']:
  price.need(hashlib.sha256((directory/row['retained']).read_bytes()).hexdigest()==row['sha256'],'latest comparator source '+row['retained'])
 latest=common.read(directory/'PR3626-EXPECTED.json');previous={int(r):n for r,n in latest['profile'].items()}
 latest_delta={r:latest['replicas']*H.get(r,0)-T*previous.get(r,0)for r in set(H)|set(previous)}
 price.need(sum(r*n for r,n in latest_delta.items())==0,'latest normalized mass')
 latest_difference=price.interval(latest_delta,Q(latest['root_interval'][1]));price.need(latest_difference[1]<0,'strict cost decrease over PR3626')
 price.need(lo>Q(latest['root_interval'][1]),'strict endpoint improvement over PR3626')
 result.update(latest_comparator_pr=3626,latest_comparator_head=provenance['head'],normalized_delta_vs_PR3626=latest_delta,latest_difference=price.compact(latest_difference),gain_root_lower_vs_PR3626_upper=str(lo-Q(latest['root_interval'][1])))
 print(json.dumps(result,indent=2));return result
if __name__=='__main__':main()
