exec(open((__import__('os').environ['HM_ROOT']+'/cards/B98c/work/gate.py')).read().split("good=[")[0])
import collections
A=[list(e) for e in d['A']]; st=d['start']; cur=list(d['start'])
for e in A:
    f=e[-1]
    for q in regs(e):f=F.join(f,cur[q])
    for q in regs(e):cur[q]=f
def spanset(basis):
    s={0}
    for b in basis: s|={x^b for x in s}
    return s
blk=['(0, 1, 2, 3)','(0, 1, 4, 5)','(0, 1, 6, 7)']
allcols=sorted({j for bn in blk for r in blocks[bn] for j in rows0[r]})
print('union cols',len(allcols))
vec={l:F.fr[st[l]][0] for l in allcols}
spc={}
def B_of(r):
    if r not in spc:
        s=spanset(F.fr[cur[r]]); spc[r]=frozenset(l for l in allcols if vec[l] in s)
    return spc[r]
def H_of(S):
    s=spanset([vec[p] for p in S]); return frozenset(l for l in allcols if vec[l] in s)
# col registers: bounds and start frames
cb=collections.Counter(len(B_of(l)) for l in allcols); print('col reg |B| dist',sorted(cb.items()))
cs=collections.Counter(len(F.fr[st[l]]) for l in allcols); print('col start dim',cs)
print('cols appear in blocks:',collections.Counter(sum(1 for bn in blk if l in {j for r in blocks[bn] for j in rows0[r]}) for l in allcols))
stoppers=[];regsall=[]
for bn in blk:
    for r in blocks[bn]:
        S=rows0[r]; regsall.append(r)
        if not S: continue
        H=H_of(S);B=B_of(r)
        if len(S)>=3 and len(H)==4 and B==H and len(S)==4: stoppers.append((bn,r,H))
print('stoppers',len(stoppers),'distinct planes',len({h for _,_,h in stoppers}))
# candidates: any register (scratch of any block or col) other than z with B>=H
pool=regsall+allcols
cand={}
for bn,z,H in stoppers: cand[z]=[u for u in pool if u!=z and H<=B_of(u)]
for z in cand: print(z,len(cand[z]),cand[z][:12])
match={}
def aug(z,seen):
    for u in cand[z]:
        if u in seen: continue
        seen.add(u)
        if u not in match or aug(match[u],seen): match[u]=z; return True
    return False
print('matching',sum(aug(z,set()) for z in cand))
scr_set=set(regsall)
for name,filt in (('scratch-only partners',lambda u:u in scr_set),('col-only partners',lambda u:u not in scr_set)):
    match={}
    c2={z:[u for u in cand[z] if filt(u)] for z in cand}
    cand_bak=cand;cand=c2
    print(name,'matching',sum(aug(z,set()) for z in cand),'of',len(cand))
    cand=cand_bak
# per block scratch-only
for bn in blk:
    zs=[z for b,z,H in stoppers if b==bn]
    match={};c2={z:[u for u in cand[z] if u in set(blocks[bn])] for z in zs};cand_bak=cand;cand=c2
    print(bn,'stoppers',len(zs),'scratch-only matching',sum(aug(z,set()) for z in zs));cand=cand_bak
