"""Independent one-response-at-a-time exact audit; no mathematical float use."""
from pathlib import Path
from fractions import Fraction as Q
import json,hashlib,ast,copy
P=Path(__file__).parent
SOURCE=P/'NATIVE-INPUT.json'
EXPECTED=P/'EXPECTED-RESPONSES.json'
SOURCE_SHA256='d9ce8efd0f51191cd67d206d1d933834b1df16a0ce77c22318596370de5e1814'
EXPECTED_SHA256='44a7295bad8b9102451b5f1d62886ea226b4edca2397eaeedad6ef8ae6af4da9'

def need(ok,msg):
 if not ok:raise ValueError(msg)

def columns(program):
 out=[];warp_checks=0
 for chosen in range(8):
  R={('L',r):Q(0)for r in range(632)};R['C',0]=Q(0);capture=0
  for ix,e in enumerate(program):
   if e[0]=='scalar':
    g=e[1];a=tuple(g[1])
    if g[0]=='clear':R[a]=Q(0)
    elif g[0]=='copy':
     b=tuple(g[2]);need(R[b]==0,'Later copy source depends on an earlier response')
     need(a==('C',0),'Owned source capture');R[a]=Q(capture==chosen);capture+=1
    elif g[0]=='add':R[a]+=Q(g[3],g[4])*R[tuple(g[2])]
    elif g[0]=='scale':R[a]*=Q(g[2],g[3])
    else:raise ValueError('Unknown scalar')
   elif e[0]=='warp':
    need(R[tuple(e[1])]==0,'A physical warp sees a response');warp_checks+=1
  need(capture==8,'Exactly eight captures');need(R['C',0]==0,'Final C erased')
  out.append([R['L',r]for r in range(632)])
 return out,warp_checks

def compare(program,expected):
 C,warps=columns(program)
 for j in range(8):
  for r in range(632):need(C[j][r]==Q(expected.get(('L',r),['0']*8)[j]),'Final response coefficient mismatch')
 need(all(sum(bool(v)for v in col)==56 for col in C),'56 final nonzero entries per response')
 need(all(not C[j][r]for j in range(8)for r in list(range(112))+list(range(224,632))),'Responses affect only Y data fields')
 return C,warps

def run():
 raw=SOURCE.read_bytes();eraw=EXPECTED.read_bytes()
 need(hashlib.sha256(raw).hexdigest()==SOURCE_SHA256,'Frozen native source bytes')
 need(hashlib.sha256(eraw).hexdigest()==EXPECTED_SHA256,'Frozen discovery response bytes')
 d=json.loads(raw);E=json.loads(eraw);need(E['copydependencies']==[]and E['warp_hits']==[],'Discovery premise list')
 expected={ast.literal_eval(k):v for k,v in E['responses'].items()};program=d['programs']['forward'];C,warps=compare(program,expected)
 bad=copy.deepcopy(program)
 first=next(e for e in bad if e[0]=='scalar'and e[1][0]=='add'and e[1][2]==['C',0]);first[1][3]+=first[1][4]
 try:compare(bad,expected)
 except ValueError:control=True
 else:raise ValueError('Altered response injection not rejected')
 result={'status':'PASS_EIGHT_RESPONSE_DEFERRAL_SUFFICIENT_PRECONDITIONS','responses':8,'independent_source_columns_checked':8*632,'warp_zero_tests':warps,'nonzero_outputs_per_response':[sum(bool(v)for v in col)for col in C],'only_Y_outputs':True,'altered_injection_rejected':control,'owned_fields_before':1,'owned_fields_after':8,'new_kappa':False,'source_sha256':SOURCE_SHA256,'expected_sha256':EXPECTED_SHA256}
 print(json.dumps(result,indent=2));P.joinpath('lazy-response-audit.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':run()
