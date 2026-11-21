"""LEANBLOCK gen_block.py (own code): completeness data for the 7-dim blocking list.
For every 2-dim normal subspace {a,b,a^b} of F2^9 (canonical a<b<a^b, 43435 of them): witness frame index
(frame disjoint from Lam) or 1000+i (i = index in FrameCert.certs).  usage: gen_block.py out_prefix chunk"""
import sys
import sys; sys.set_int_max_str_digits(0)
D='<research-tree>/cards/WILD/LUNCH/exchange/d56dir/mod4/'
lab=list(map(int,open(D+'labels.txt').read().split()))
fr=[list(map(int,l.split())) for l in open(D+'frames.txt').read().strip().split('\n')[1:]]
fmask=[sum(1<<t for t in f) for f in fr]
dot=lambda a,b: bin(a&b).count('1')&1
# certs order = block.out dim-7 order (as in leanframe/gen.py)
def members(S):
    m={0}
    for v in S: m|={x^v for x in m}
    return m
certkey=[]
for line in open(D+'block.out'):
    p=line.split()
    if int(p[2])!=7: continue
    S=[int(x) for x in p[4:4+7]]
    nz=[u for u in range(1,512) if all(dot(u,s)==0 for s in S)]
    certkey.append((nz[0],nz[1]))
assert len(certkey)==1152
idx={k:i for i,k in enumerate(certkey)}
data=[]; nb=0
for a in range(1,512):
    for b in range(a+1,512):
        if not (b < a^b): continue
        lm=sum(1<<t for t in range(104) if dot(lab[t],a)==0 and dot(lab[t],b)==0)
        w=next((i for i,fm in enumerate(fmask) if fm&lm==0),None)
        if w is None:
            assert (a,b) in idx; w=1000+idx[(a,b)]; nb+=1
        else: assert (a,b) not in idx
        data.append(a+512*(b+512*w))
assert len(data)==43435 and nb==1152
# row table: W_a = sum_b w(a,b) << (12*b); w<759 frame witness, w=759 means listed
rows=[0]*512
for e in data:
    a=e%512; b=e//512%512; w=e//262144
    if w>=1000: w=759
    rows[a]|=w<<(12*b)
pre=sys.argv[1]; CH=int(sys.argv[2]); names=[]
out=open(pre,'w')
out.write('/-- bitmap over keys a+512*b of the 1152 certified normal pairs -/\ndef listedBM : Nat := %d\n\n'%sum(1<<(a+512*b) for (a,b) in certkey))
for k in range(0,512,CH):
    out.write('def wt%d : List Nat := [\n%s]\n\n'%(k//CH,',\n'.join(map(str,rows[k:k+CH])))); names.append('wt%d'%(k//CH))
out.write('def wts : List (List Nat) := [%s]\n'%','.join(names))
th=open(pre+'.thms','w')
for j,n in enumerate(names): th.write('theorem %s_ok : (List.range %d).all (fun j => rowOK (%d * %d + j) ((%s).getD j 0)) = true := by decide +kernel\n'%(n,CH,CH,j,n))
nk=len(names)
th.write('''
def tabW (a : Nat) : Nat := (wts.getD (a / %d) []).getD (a %% %d) 0

theorem table_ok : ∀ a, a < 512 → rowOK a (tabW a) = true := by
  intro a ha
  obtain ⟨k, hk⟩ : ∃ k, k = a / %d := ⟨_, rfl⟩
  obtain ⟨j, hj⟩ : ∃ j, j = a %% %d := ⟨_, rfl⟩
  have hkj : a = %d * k + j := by omega
  have hk8 : k < %d := by omega
  have hj64 : j < %d := by omega
  have ht : tabW a = (wts.getD k []).getD j 0 := by simp [tabW, ← hk, ← hj]
  rw [ht, hkj]
  interval_cases k
'''%(CH,CH,CH,CH,CH,nk,CH))
for n in names: th.write('  · exact List.all_eq_true.1 %s_ok j (List.mem_range.2 hj64)\n'%n)
print(len(names),'chunks')
