"""Necessary coordinate screen for unchanged retired-bank readout.
Read-only, stdlib; new code prepared for Yiyang with substantial Codex assistance.
"""
import sys,json,gzip,types
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
BASE=Path(__file__).resolve().parents[1]
# Compile the current checker source directly; it authenticates its vendored bytes
# before execution, and no import-cache or stale pyc can substitute another engine.
verify=types.ModuleType('staged_boundary_verify');verify.__file__=str(BASE/'verify.py')
exec(compile((BASE/'verify.py').read_bytes(),str(BASE/'verify.py'),'exec'),verify.__dict__)
Model,join,FULL,regs=(getattr(verify.ENGINE,n) for n in ('Model','join','FULL','regs'))
require=verify.require

def add(dst,src,a):
 for word,c in src.items():
  dst[word]=dst.get(word,F(0))+a*c
  if not dst[word]:del dst[word]
def warp(row,op):return {(word[1:] if word and word[0]==-op else (op,)+word):c for word,c in row.items()}
def apply(g,rows):
 if g[0]=='add':add(rows[g[1]],rows[g[2]],F(g[3],g[4]))
 elif g[0]=='scale':rows[g[1]]={word:a*F(g[2],g[3]) for word,a in rows[g[1]].items()}
 elif g[0]=='warp':rows[g[1]]=warp(rows[g[1]],g[2])
 else:require(False,'unknown scalar opcode')
def check(w):
 m=Model(w);n=2*w['report']['v']+w['report']['R'];live=set(range(n))-set(w['removed']);rows={q:{} for q in live};rows[100]={():F(1)}
 for c in w['initial_corrections']:
  row=rows[c['source']]
  for op in reversed(c['operator_word']):row=warp(row,op)
  add(rows[c['target']],row,F(c['coefficient']))
 for g in w['precondition']+w['compensation']+w['A']+w['cut']:apply(g,rows)
 bypos=defaultdict(list)
 for op,rec in enumerate(w['warps'],1):bypos[rec[0]].append(['warp',rec[1],op])
 need=None
 for i in range(len(w['B'])+1):
  if i==1202:
   need={}
   for q,a in [(100,-1),(226,-1),(54,1)]:add(need,rows[q],F(a))
  for g in bypos[i]:apply(g,rows)
  if i<len(w['B']):apply(w['B'][i],rows)
 for g in w['restore']:apply(g,rows)
 require(need=={():F(-1)},'required original-input100 coefficient changed')
 H=m.floor(277,m.positions['B',1201]);banks=[]
 for q in sorted(live):
  if q<2*m.v or q==277 or m.start[q] or m.end[q]!=FULL:continue
  if len(join(H,m.floor(q,len(m.events))))<=8:banks.append(q)
 expected=[226,231,236,238,244,246,260,262,287,299,303,383,395,399,404,406,420,422,434,439,444,446]
 require(banks==expected,'eligible-bank set changed')
 require(all(rows[q]=={} for q in banks),'a naturally accumulated bank can carry input100')
 return dict(status='PASS_NATURAL_RETIRED_BANK_COORDINATE_OBSTRUCTION',eligible_banks=banks,bank_count=len(banks),required_input100_coefficient='-1',all_eligible_bank_input100_coefficients='0',scope='Read unchanged cold FULL-ended banks only after their final inherited use; require join with host floor rank<=8; allow any rational linear combination plus initial cold-input preloads. No new writes, bank warp, or consumer change. This is a necessary-coordinate screen, not a supplier replay.')
def main():
 out=[]
 for label in 'be':
  w=json.loads(gzip.decompress(verify.AUTHENTICATED[f'inputs/hosted-{label}-473-277.json.gz']));r=check(w);r['provider']=label;out.append(r)
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
