"""Construct a source-pinned exact interval shear; no optimizer or network access."""
from pathlib import Path
from fractions import Fraction as Q
import argparse,copy,gzip,hashlib,json,sys
def canon(w):return json.dumps(w,sort_keys=True,separators=(',',':')).encode()
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--input',required=True);ap.add_argument('--gk-dir',required=True)
 ap.add_argument('--out',required=True)
 ap.add_argument('--selection',default=str(Path(__file__).with_name('EPOCH-SELECTION.json')))
 a=ap.parse_args();out=Path(a.out)
 if out.exists() and any(out.iterdir()):raise SystemExit('Output must be absent or empty.')
 out.mkdir(parents=True,exist_ok=True)
 sys.path.insert(0,a.gk_dir)
 import gk_word as g,gk_common as gc
 g.V=gc.V=112;g.DATA=gc.DATA=7168
 w=json.loads(gzip.decompress(Path(a.input).read_bytes()))
 sel=json.loads(Path(a.selection).read_text())
 assert hashlib.sha256(canon(w)).hexdigest()==sel['source_semantic_sha256'],'source pin mismatch'
 sec=sel['section'];lo=sel['first'];hi=sel['last'];r=sel['destination'];s=sel['source']
 q=Q(sel['numerator'],sel['denominator']);L=sel['lower'];U=sel['upper']
 assert sec=='A'and lo==0 and hi==len(w['A'])-1
 assert r!=s and r not in w['centers']and s not in w['centers']
 assert g.basis(w['start_extra'][str(r)])==g.basis(L)
 assert g.basis(w['start_extra'][str(s)])==g.basis(L)
 assert not any(e[1]in(r,s)for e in w[sec][lo:hi+1]),'epoch is not read-only'
 def add(t,src,v,F):return['add',t,src,v.numerator,v.denominator,list(F)]
 def simplify(seq):
  result=[]
  for e in seq:
   merged=False
   if e[0]=='add':
    assert e[1]!=e[2]
    for j in range(len(result)-1,max(-1,len(result)-sel['commutation_window']),-1):
     old=result[j]
     if old[0]!='add':
      if old[1]in(e[1],e[2]):break
      continue
     if e[1:3]==old[1:3]and e[-1]==old[-1]:
      v=Q(e[3],e[4])+Q(old[3],old[4])
      if v:result[j]=add(e[1],e[2],v,e[-1])
      else:result.pop(j)
      merged=True;break
     if e[1]==old[2]or e[2]==old[1]:break
   if not merged:result.append(e)
  return result
 body=[]
 for e in w[sec][lo:hi+1]:
  body.append(e)
  if e[0]=='add'and e[2]==r:body.append(add(e[1],s,-q*Q(e[3],e[4]),e[-1]))
 body=simplify(body)
 z=copy.deepcopy(w)
 z[sec]=w[sec][:lo]+[add(r,s,q,L)]+body+[add(r,s,-q,U)]+w[sec][hi+1:]
 z['cleanup']=[g.inverse(e,g.FULL)for e in reversed(z['A']+z['B'])if not 112<=e[1]<224]
 assert len(z['A'])-len(w['A'])==sel['expected_A_delta']
 assert len(z['cleanup'])-len(w['cleanup'])==sel['expected_cleanup_delta']
 assert g.profile(z)==g.profile(w),'paid profile changed'
 assert z['start_extra']==w['start_extra'],'entrances changed'
 for e in z['A']+z['B']+z['cleanup']:
  den=(Q(e[3],e[4])if e[0]=='add'else Q(e[2],e[3])).denominator
  assert den>0 and den&(den-1)==0,'nondyadic gate'
 raw=g.dump(z)
 assert hashlib.sha256(canon(z)).hexdigest()==sel['expected_word_semantic_sha256'],'semantic output pin mismatch'
 (out/'FULL-WORD.json.gz').write_bytes(raw)
 # A single retained reader inside the changed basis is a concrete mutation.
 reader=next(i for i,e in enumerate(z['A'])if 0<i<len(z['A'])-1 and e[0]=='add'and e[2]==r)
 controls=[]
 c=copy.deepcopy(z);del c['A'][-1];controls.append(c)
 c=copy.deepcopy(z);del c['A'][reader];controls.append(c)
 def enc(e):
  if e[0]=='add':return f"0 {e[1]} {e[2]} {e[3]} {e[4]}"
  return f"1 {e[1]} -1 {e[2]} {e[3]}"
 with(out/'AUDIT-INPUT.txt').open('w',newline='\n')as f:
  f.write('728 112 4\n')
  for word in[w,z,*controls]:
   seq=word['A']+word['cut']+word['B']
   f.write(str(len(seq))+'\n'+'\n'.join(map(enc,seq))+'\n')
 receipt=dict(status='constructed; run audit_epoch for exact all-column evidence',
  source_semantic_sha256=sel['source_semantic_sha256'],word_sha256=hashlib.sha256(raw).hexdigest(),
  word_semantic_sha256=hashlib.sha256(canon(z)).hexdigest(),local_profile=dict(sorted(g.profile(z).items())),
  A_delta=-14,cleanup_delta=-14,total_scalar_delta=-28,helper_count=504,
  controls=['omit terminal inverse','omit transformed reader'],reader_control_index=reader,
  widths_unchanged=True,paid_profile_unchanged=True)
 (out/'CONSTRUCTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt))
if __name__=='__main__':main()


