#!/usr/bin/env python3
"""Independent exact differential audit: no construction/audit modules imported."""
import sys,json,gzip,hashlib,collections,copy,argparse
if not __debug__:
 raise SystemExit("Refusing Python -O/-OO: this independent checker requires active assertions.")
from pathlib import Path
from fractions import Fraction as Q
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-word',type=Path,required=True)
parser.add_argument('--candidate-word',type=Path,required=True)
parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args();BASE=args.source_word;CAND=args.candidate_word
source_bytes=BASE.read_bytes();candidate_bytes=CAND.read_bytes()
source_sha=hashlib.sha256(source_bytes).hexdigest();candidate_sha=hashlib.sha256(candidate_bytes).hexdigest()
PINNED={
 'dda9878455b3a3bec64ca16b1ac7789bbf5ffb603d5713b8df8644485e85b1b7':'base',
 'bbe6bcba59e45e827a8e932ee4b23650d56ed4a0b8e0875c14f23c36b9e47eac':'extra',
}
if source_sha not in PINNED:raise SystemExit('Source word is not one of the two pinned PR2833 words.')
VARIANT=PINNED[source_sha]
w=json.loads(gzip.decompress(source_bytes));x=json.loads(gzip.decompress(candidate_bytes))
V=112;N=704;H=9;FULL=(256,128,64,32,16,8,4,2,1)
live=sorted(set(range(N))-set(w['removed']));restored=set(map(int,w['helper_final']));checks=[]
def ok(v,name):
 if not v:raise AssertionError(name)
 checks.append(name)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def basis(v):
 rows=[a for a in v if a];out=[]
 for bit in range(H-1,-1,-1):
  choices=[a for a in rows if a>>bit&1]
  if not choices:continue
  p=choices[0];rows.remove(p);rows=[a^p if a>>bit&1 else a for a in rows];out=[a^p if a>>bit&1 else a for a in out];out.append(p)
 return tuple(out)
def sub(U,F):return basis(U+F)==F
def regs(e):return e[1:3] if e[0]=='add' else e[1:2]
def coeff(e):return Q(e[3],e[4]) if e[0]=='add' else Q(e[2],e[3])
def plus(dst,src,c):
 for k,a in src.items():
  z=dst.get(k,Q(0))+c*a
  if z:dst[k]=z
  else:dst.pop(k,None)
def left(row,op):
 out={}
 for (r,word),a in row.items():
  seq=word[1:] if word and word[0]==-op else (op,)+word
  out[r,seq]=a
 return out
def apply(rows,e,dual=False):
 kind=e[0]
 if kind=='warp':
  op=e[2];op=op+(1000000 if op>0 else -1000000) if dual else op
  rows[e[1]]=left(rows[e[1]],op)
 elif kind=='corr':
  _,t,s,word,c=e
  if dual:
   tmp=rows[t]
   for op in word:tmp=left(tmp,-op-(1000000 if op>0 else -1000000))
   plus(rows[s],tmp,-c)
  else:
   tmp=rows[s]
   for op in reversed(word):tmp=left(tmp,op)
   plus(rows[t],tmp,c)
 elif kind=='add':
  t,s=e[1:3];c=coeff(e)
  if dual:t,s,c=s,t,-c
  plus(rows[t],rows[s],c)
 elif kind=='scale':
  c=coeff(e);c=1/c if dual else c
  rows[e[1]]={k:a*c for k,a in rows[e[1]].items()}
 else:raise AssertionError(kind)
def eye():return {r:{(r,()):Q(1)} for r in range(N)}
def b_events(z):
 byp=collections.defaultdict(list)
 for op,rec in enumerate(z['warps'],1):byp[rec[0]].append(['warp',rec[1],op])
 out=[]
 for i in range(len(z['B'])+1):
  out.extend(byp[i])
  if i<len(z['B']):out.append(z['B'][i])
 return out
ok(set(x)==set(w),'top_level_key_set_unchanged')
ok((w['report']['v'],w['report']['h'],w['report']['R'])==(112,9,480),'pinned_source_geometry')
allowed={'A','compensation','start_extra','report','cleanup'}
ok({k for k in w if w[k]!=x[k]}==allowed,'only_declared_top_level_fields_change')
ok(x['A'][:84]==w['A'][:84] and x['prelude_events']==84,'prelude_unchanged')
GROUPS=[(478,479,490,491),(460,461,468,469),(462,463,470,471),(480,481,492,493)]
ENTRIES={478:[25],460:[7],462:[7],480:[25]}
ok(x['start_extra']==dict(w['start_extra'],**{str(k):v for k,v in ENTRIES.items()}),'sole_four_declared_start_changes')
ok(x['report'].keys()==w['report'].keys() and all(x['report'][k]==v for k,v in w['report'].items() if k not in ['local_profile','width_inventory']),'only_profile_and_width_report_change')
# Reconstruct expected twenty inserted primitives from pinned original first-touch rows.
# Their identity is separately checked by symbolic A replay; this is a structural boundary check.
insert=collections.defaultdict(list);C=copy.deepcopy(w['compensation']);T={};group_records=[];supports=[];target_supports=[]
for q0,q1,q2,q3 in GROUPS:
 info={}
 for q in (q0,q1,q2,q3):
  touches=[(i,e) for i,e in enumerate(w['A']) if q in regs(e)]
  ok(len(touches)==1 and touches[0][1][0]=='add' and touches[0][1][1]==q,f'group{q0}_helper{q}_unique_original_A_write')
  i,e=touches[0];info[q]=(i,e[2],coeff(e),basis(e[-1]))
  ok(not any(g[1]==e[2] for g in w['A']),f'group{q0}_partner{e[2]}_not_written_in_A')
 i0,s0,c0,E=info[q0];i1,s1,c1,E1=info[q1];i2,s2,c2,G=info[q2];i3,s3,c3,G1=info[q3]
 L=basis(ENTRIES[q0]);ok(E==E1 and G==G1 and sub(L,E) and sub(L,G) and len(E)==len(G)==2,f'group{q0}_literal_paired_frames')
 def emit(i,t,src,c,U):insert[i].append(['add',t,src,c.numerator,c.denominator,list(U)])
 emit(min(i0,i2),q2,q0,Q(-1),L)
 emit(max(i0,i1)+1,q1,q0,Q(1),E);emit(max(i0,i1)+1,q1,s0,-c0,E)
 emit(max(i2,i3)+1,q3,q2,Q(1),G);emit(max(i2,i3)+1,q3,s2,-c2,G)
 C=[e for e in C if not(e[0]=='add' and e[2]==q0)]+[e[:2]+[q2]+e[3:] for e in w['compensation'] if e[0]=='add' and e[2]==q3]
 T.update({q0:{q0:1},q1:{q1:1,q0:1},q2:{q2:1,q0:-1},q3:{q3:1,q2:1,q0:-1}})
 helpers=[q0,q1,q2,q3];targets=sorted({e[1] for e in w['compensation'] if e[0]=='add' and e[2] in helpers})
 M=[[sum((coeff(e) for e in w['compensation'] if e[0]=='add' and e[1]==t and e[2]==h),Q(0)) for h in helpers] for t in targets]
 def rank_of(M):
  R=[row[:] for row in M];rank=0
  for c in range(len(R[0])):
   piv=next((i for i in range(rank,len(R)) if R[i][c]),None)
   if piv is None:continue
   R[rank],R[piv]=R[piv],R[rank];a=R[rank][c];R[rank]=[v/a for v in R[rank]]
   for i in range(len(R)):
    if i!=rank:
     a=R[i][c];R[i]=[v-a*u for v,u in zip(R[i],R[rank])]
   rank+=1
  return rank
 rank=rank_of(M);ok(rank==3 and all(sum(row[k]*[1,1,-1,-1][k] for k in range(4))==0 for row in M),f'group{q0}_exact_rank3_kernel')
 group_records.append(dict(helpers=helpers,targets=targets,matrix=[[str(v) for v in row] for row in M],rank=rank))
 supports.append(set(helpers)|{s0,s1,s2,s3});target_supports.append(set(targets))
A=[]
for i in range(len(w['A'])+1):
 A.extend(insert[i])
 if i<len(w['A']):A.append(w['A'][i])
ok(x['A']==A,'exact_twenty_insertions_no_hidden_scalar_changes')
ok(C==x['compensation'],'exact_compensation_column_replacements')
ok(all(a.isdisjoint(b) for i,a in enumerate(supports) for b in supports[i+1:]),'four_operand_supports_pairwise_disjoint')
ok(all(a.isdisjoint(b) for i,a in enumerate(target_supports) for b in target_supports[i+1:]),'four_compensation_target_supports_pairwise_disjoint')
ok(all(q not in regs(e) for q in ENTRIES for e in x['precondition']+x['compensation']) and all(c['source'] not in ENTRIES for c in x['initial_corrections']),'new_entrances_have_no_wrapper_or_correction_reads')
oldA,newA=eye(),eye()
for e in w['A']:apply(oldA,e)
for e in x['A']:apply(newA,e)
def shear(row):
 out={}
 for (r,word),a in row.items():
  for src,c in T.get(r,{r:1}).items():
   key=src,word;out[key]=out.get(key,Q(0))+a*c
 return {k:a for k,a in out.items() if a}
ok(all(newA[r]==shear(oldA[r]) for r in range(N)),'all_704_A_outputs_equal_old_A_composed_with_four_raw_dirt_shears')
# Check C'=C*S as complete target response matrices, not only the displayed kernel blocks.
helpers=sorted(T);targets=list(range(V,2*V))
def cmat(z):return [[sum((coeff(e) for e in z['compensation'] if e[0]=='add' and e[1]==t and e[2]==h),Q(0)) for h in helpers] for t in targets]
M=cmat(w);Mp=cmat(x);MT=[[sum(M[i][k]*T[helpers[k]].get(h,0) for k in range(len(helpers))) for h in helpers] for i in range(len(targets))]
ok(Mp==MT,'complete_new_compensation_is_old_compensation_times_shear')
rank=rank_of(M);ok(rank==12,'combined_compensation_rank12_nullity4')
# Regenerate cleanup independently from the changed recorded non-target word.
forward=x['A'][84:]+b_events(x)+x['restore'];expected=[]
buf=lambda r:r+N if r in restored else r
for e in reversed(forward):
 if e[0]!='warp' and V<=e[1]<2*V:continue
 if e[0]=='warp':g=['warp',buf(e[1]),-e[2],list(FULL)]
 elif e[0]=='add':g=['add',buf(e[1]),buf(e[2]),-e[3],e[4],list(FULL)]
 else:g=['scale',buf(e[1]),e[3],e[2],list(FULL)]
 expected.append(g)
ok(expected==x['cleanup'],'exact_inverse_reverse_cleanup_excludes_prelude_targets_and_uses_private_buffers')
ok({r-N for e in x['cleanup'] for r in regs(e) if r>=N}==restored,'private_buffer_inventory_unchanged_72')
# Fresh exact endpoint replay, both orientations and all independent dirty columns.
corr=[['corr',c['target'],c['source'],tuple(c['operator_word']),Q(c['coefficient'])] for c in x['initial_corrections']]
program=corr+x['precondition']+x['compensation']+x['A']+x['cut']+b_events(x)+x['restore']
for dual in [False,True]:
 rows=eye();rows.update({r+N:{} for r in restored})
 for e in program:apply(rows,e,dual)
 if not dual:
  ok(all(rows[V+t]=={(V+t,()):Q(1),(t,()):Q(1)} for t in range(V)),'precleanup_forward_target_map')
  ok(all(rows[r]=={(r,()):Q(1)} for r in restored),'precleanup_restored_inputs_exact')
 for e in x['cleanup']:apply(rows,e,dual)
 exp=eye()
 for t in range(V):
  if dual:exp[t][V+t,()]=Q(-1)
  else:exp[V+t][t,()]=Q(1)
 ok(all(rows[r]==exp[r] for r in range(N)),'independent_'+('dual' if dual else 'forward')+'_all_column_endpoint')
 ok(all(not rows[r+N] for r in restored),'independent_'+('dual' if dual else 'forward')+'_zero_buffers')
# Independent GF2 frame accounting with no inherited audit functions.
def frame_ledger(z):
 starts=[(p,) for p in z['ports']]+[()]*(N-V)
 ends=[FULL]*V+[basis([a for a in range(1,512) if (a&p).bit_count()%2==0]) for p in z['ports']]+[FULL]*(N-2*V)
 for r,U in z['start_extra'].items():starts[int(r)]=basis(U)
 for r,U in z['helper_final'].items():ends[int(r)]=basis(U)
 current=starts[:];counts=collections.Counter();byreg=collections.defaultdict(collections.Counter)
 def climb(r,U):
  U=basis(U);assert sub(current[r],U),(r,current[r],U)
  d=len(U)-len(current[r])
  if d:counts[d]+=1;byreg[r][d]+=1
  current[r]=U
 for e in z['A']:
  if e[0]=='warp':assert current[e[1]]==basis(e[3]);current[e[1]]=basis(e[4])
  else:
   for r in regs(e):climb(r,e[-1])
 lev={int(t):basis(U) for t,U in z['target_levels'].items()}
 assert all(current[V+t]==lev.get(t,()) for t in range(V))
 for r,U in zip(z['centers'],z['center_frames']):
  U=basis(U);assert current[r]==U
  for end in sorted({lev.get(e[1]-V,()) for e in z['cut'] if e[2]==r},key=lambda t:-len(t)):
   assert sub(end,U)
   if end!=U:counts[len(U)-len(end)]+=1
   U=end
 for e in b_events(z)+z['restore']:
  if e[0]=='warp':rec=z['warps'][e[2]-1];assert current[e[1]]==basis(rec[3]);current[e[1]]=basis(rec[4])
  else:
   for r in regs(e):climb(r,e[-1])
 for r in live:climb(r,ends[r])
 widths={r:len(ends[r])-len(starts[r]) for r in live if r>=2*V}
 assert all(ends[r]==FULL for r in live if r<112 or r>=224 and r not in restored)
 return counts,byreg,widths
p0,c0,wi0=frame_ledger(w);p1,c1,wi1=frame_ledger(x)
ok(dict(p1)=={int(d):n for d,n in x['report']['local_profile'].items()},'independent_full_frame_profile')
ok(collections.Counter(wi1.values())==collections.Counter({int(d):n for d,n in x['report']['width_inventory'].items()}),'independent_width_inventory')
delta={d:p1[d]-p0[d] for d in sorted(set(p0)|set(p1)) if p1[d]!=p0[d]}
ok(delta=={1:12,2:-8},'profile_delta_plus12H1_minus8H2')
ok({r:(wi0[r],wi1[r]) for r in wi0 if wi0[r]!=wi1[r]}=={q:(9,8) for q in ENTRIES},'only_four_ordered_widths_shrink9to8')
changed_climbs={r:{d:c1[r][d]-c0[r][d] for d in set(c0[r])|set(c1[r]) if c0[r][d]!=c1[r][d]} for r in live if c0[r]!=c1[r]}
expected_climbs={}
for q0,q1,q2,q3 in GROUPS:expected_climbs.update({q0:{1:1,2:-1},q2:{1:2,2:-1}})
ok(changed_climbs==expected_climbs,'only_eight_declared_helpers_change_paid_climbs')
ok(sha(BASE)==source_sha and sha(CAND)==candidate_sha,'inputs_unchanged_during_audit')
result=dict(status='PASS_INDEPENDENT_FOUR_GROUP_LOCAL_DIFFERENTIAL_AUDIT',variant=VARIANT,groups=group_records,candidate_compressed_sha256=sha(CAND),candidate_content_sha256=hashlib.sha256(gzip.decompress(CAND.read_bytes())).hexdigest(),base_compressed_sha256=sha(BASE),checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_commit='e9307b48d7d1b690939935ecef0f8e524e6d92f4',checks=checks,compensation_targets=targets,compensation_matrix=[[str(v) for v in row] for row in M],compensation_rank=rank,dirty_shear=T,profile_delta=delta,changed_register_profiles=changed_climbs,ordered_width_change={str(q):[9,8] for q in ENTRIES},primitive_count_changes={'A':20,'cleanup':20,'compensation':0},remaining_admission=['fresh declared-stage producer/source bindings and negative controls','strict source release including no stale bytecode','native phase/Gaussian replay including all extra gates and cleanup','actual owner fill/order/dispatch with changed ordered width list; recompute actual idle profile','both exact outer checkers and selected-parent admission at claimed target','full inherited borrowed-word/owner/geometry/controller rejection controls'],limitations=['This checks candidate word bytes only; no owner/native/outer admission or whole-package source-release audit is performed.','The free-operator endpoint proof does not itself certify Clifford phase/Gaussian products.','No unrestricted optimality claim for rank-three kernel or frame schedule.'])
args.out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
