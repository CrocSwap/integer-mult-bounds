"""LEANFRAME gen.py (own code): exact F2 certificates for H_frame; writes FrameData.lean-style data.
usage: gen.py N out.lean   (N = number of Lams, 0 = all)"""
import sys; sys.set_int_max_str_digits(0)
D='<research-tree>/cards/WILD/LUNCH/exchange/d56dir/mod4/'
lab=list(map(int,open(D+'labels.txt').read().split()))
fr=[list(map(int,l.split())) for l in open(D+'frames.txt').read().strip().split('\n')[1:]]
assert len(lab)==104 and len(fr)==759 and all(len(f)==8 for f in fr)
fmask=[sum(1<<t for t in f) for f in fr]
dot=lambda a,b: bin(a&b).count('1')&1
def members(S):
    m={0}
    for v in S: m|={x^v for x in m}
    return m
blocks=[]
for line in open(D+'block.out'):
    p=line.split()
    if int(p[2])!=7: continue
    blocks.append([int(x) for x in p[4:4+7]])
N=int(sys.argv[1]) or len(blocks)
cases=[]
for S in blocks[:N]:
    mem=members(S)
    nz=[u for u in range(1,512) if all(dot(u,s)==0 for s in S)]
    assert len(nz)==3
    u1,u2=nz[0],nz[1]
    lam=[t for t in range(104) if dot(lab[t],u1)==0 and dot(lab[t],u2)==0]
    assert set(lam)=={t for t in range(104) if lab[t] in mem}
    lm=sum(1<<t for t in lam)
    # elimination
    piv={}  # high bit -> (row, combo)
    sel=[]
    for i,fm in enumerate(fmask):
        r=fm&lm; c=0
        while r:
            h=r.bit_length()-1
            if h in piv: r^=piv[h][0]; c^=piv[h][1]
            else:
                sel.append(i); c^=1<<(len(sel)-1); piv[h]=(r,c); break
    assert len(sel)==len(lam)-1,(len(sel),len(lam))
    p0=lam[0]; ent=[]
    for p in lam[1:]:
        r=(1<<p)|(1<<p0); c=0
        while r:
            h=r.bit_length()-1
            r^=piv[h][0]; c^=piv[h][1]
        ent.append((p,c))
    cases.append((u1,u2,p0,sel,ent))
out=open(sys.argv[2],'w')
out.write('/-- labels packed 9 bits each -/\ndef labelsP : Nat := %d\n\n'%sum(v<<(9*i) for i,v in enumerate(lab)))
out.write('/-- the 759 frames as 104-bit masks, packed 104 bits each -/\ndef framesP : Nat := %d\n\n'%sum(v<<(104*i) for i,v in enumerate(fmask)))
def pack(vals,k): return sum(v<<(k*j) for j,v in enumerate(vals))
def fmt(c):
    u1,u2,p0,sel,ent=c
    es=[]
    for p,cc in ent:
        idx=[sel[b] for b in range(len(sel)) if cc>>b&1]
        assert len(idx)<32 and max(idx)<1024
        es.append(p+128*(len(idx)+32*pack(idx,10)))
    return '[%d,%d,%d,%s]'%(u1,u2,p0,','.join(map(str,es)))
CH=int(sys.argv[3]) if len(sys.argv)>3 else 24; names=[]; thms=[]
for k in range(0,len(cases),CH):
    out.write('def certs%d : List (List Nat) := [\n'%(k//CH)+',\n'.join(fmt(c) for c in cases[k:k+CH])+']\n\n'); names.append('certs%d'%(k//CH)); thms.append('theorem certs%d_ok : certs%d.all certOK = true := by decide +kernel\n'%(k//CH,k//CH))
out.write('/-- certificates [u1,u2,p0, entries...], entry = p + 128*(cnt + 32*packed frame indices (10b each)); 7-dim blockings -/\ndef certs : List (List Nat) := '+' ++ '.join(names)+'\n')
print(len(cases),max(len(c[3]) for c in cases))

th=open(sys.argv[2]+'.thms','w')
th.write(''.join(thms))
th.write('/-- number of certified 7-dim blocking sets -/\ntheorem certs_length : certs.length = %d := by decide +kernel\n'%len(cases))
acc=names[0]+'_ok'
for n in names[1:]: acc='all_app (%s) %s_ok'%(acc,n)
th.write('\ntheorem certs_ok : certs.all certOK = true :=\n  '+acc+'\n')
