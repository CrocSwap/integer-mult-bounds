"""Exact dual certificate for a fixed whole-owner inventory and finite word menu.
This bounds that enlarged allocation model only, not general algorithms.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import argparse,json,importlib.util,hashlib
ap=argparse.ArgumentParser();ap.add_argument('inputs',type=Path);ap.add_argument('engine',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--base-two',action='store_true');a=ap.parse_args();assert not a.out.exists()
D=json.loads(a.inputs.read_text());spec=importlib.util.spec_from_file_location('exact_engine',a.engine);M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M);m=D['ambient'];live=D['live'];b=Q(D['rejected_endpoint']);nr={int(k):v for k,v in D['families_by_rank'].items()};menu=D['word_menu'];widths=sorted({int(w)for x in menu for w in x['widths']});calls=D['calls'];cost={0:(Q(0),Q(0))}
for r in range(1,max(nr)+1):
 if a.base_two:
  main=M.moment(m,1,[(r,1)],b);fallback=M.moment(m,1,[(1,32*m*m)],b)
  cost[r]=tuple(m*(main[i]+fallback[i]/10**16)for i in range(2))
 else:cost[r]=tuple(m*z for z in M.moment({r:1},m,1,b,True))
cl=lambda r:cost[r][0]
beta={9:(cl(3)-cl(48))/5,7:-cl(7),5:-cl(5)};alpha={16:cl(7)-beta[9],32:cl(5)-3*beta[9],48:cl(48)};beta[8]=-alpha[16]/2;alpha[8]=-beta[8]
def patterns(cap,k=0,p=()):
 yield p
 for j in range(k,len(widths)):
  if widths[j]<=cap:yield from patterns(cap-widths[j],j,p+(widths[j],))
ps={r:list(patterns(r))for r in nr};corrections={}
# Exact outward correction gives genuinely feasible rational duals, even on
# zero-slack support columns whose interval midpoint would not suffice.
for r in nr:
 corrections[r]=max([Q(0)]+[alpha[r]+sum(beta[w]for w in p)-cl(r-sum(p))for p in ps[r]])
 alpha[r]-=corrections[r]
assert all(alpha[r]+sum(beta[w]for w in p)<=cl(r-sum(p))for r in nr for p in ps[r])
word_scores=[]
for word in menu:
 h={int(k):v for k,v in word['profile'].items()};wc={int(k):v for k,v in word['widths'].items()};assert sum(wc.values())==D['helpers_per_call'];score=sum(n*cl(r)for r,n in h.items())+sum(n*beta[w]for w,n in wc.items());word_scores.append(score)
minimum=min(word_scores);best=[i for i,x in enumerate(word_scores)if x==minimum];bound=(sum(n*alpha[r]for r,n in nr.items())+calls*minimum)/(m*live);assert bound>1,('wall not certified',float(bound-1),best)
# A proposed feasible allocation must pay at least this bound at b. The
# monotonic moment therefore cannot certify b or any larger saving here.
mutations=[]
for name,aa,bb in [('increase rank48 dual',dict(alpha)|{48:alpha[48]+1},beta),('raise width9 dual',alpha,dict(beta)|{9:beta[9]+1})]:
 assert any(aa[r]+sum(bb[w]for w in p)>cl(r-sum(p))for r in nr for p in ps[r]);mutations.append(name)
res=dict(status='PASS_EXACT_FIXED_INVENTORY_FINITE_MENU_DUAL_WALL',engine_method='base-two'if a.base_two else'mercator',ambient=m,live=live,calls=calls,word_menu_size=len(menu),patterns_checked=sum(map(len,ps.values())),rejected_endpoint=str(b),moment_lower_bound=str(bound),strict_margin=str(bound-1),strict_margin_float=float(bound-1),minimizing_menu_indices=best,minimizing_labels=[menu[i]['label']for i in best],alpha={str(r):str(x)for r,x in alpha.items()},beta={str(w):str(x)for w,x in beta.items()},outward_corrections={str(r):str(x)for r,x in corrections.items()},word_reduced_costs=[str(s-minimum)for s in word_scores],mutations_rejected=mutations,inputs_sha256=hashlib.sha256(a.inputs.read_bytes()).hexdigest(),engine_sha256=hashlib.sha256(a.engine.read_bytes()).hexdigest(),scope='Exact necessary-condition obstruction within the fixed m/live/call/inventory model and this finite profile-width menu, under the inherited fallback law. Windows, physical injectivity and integer word choices are relaxed. No limit on different words, geometry, stock, stages, fallback laws or algorithms is claimed. This is not a universal integer-multiplication bound.')
if 'outer' in D:
 cfg=D['outer'];eta=Q(cfg['eta']);be=Q(cfg['beta']);s=(1-be)*b;chain=Q(cfg['initial']);assert 0<s<Q(1,2)
 for _ in range(cfg['steps']):
  assert 1-2*s+chain>0
  chain=(1-s)*s+s*chain
 q=(1-2*eta)*chain;margin=(1-eta)*q/(1+q);base=Q(cfg['baseline_kappa']);grid=Q(cfg['grid']);assert base<margin<base+grid
 res['fixed_outer_grid_obstruction']=dict(upper_margin=str(margin),next_kappa=str(base+grid),next_kappa_rejected=True,scope=cfg['scope'])
a.out.write_text(json.dumps(res,indent=2)+'\n');print(res['status'],'margin',res['strict_margin_float'],'menu',len(menu),'minimizers',res['minimizing_labels'],flush=True)
