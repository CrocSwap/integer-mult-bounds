# margins: A8 min over 6-flats of r*H-beta (398 needs >6); A7 classes with sigma0-refined relief bound.
exec(open('tight.py').read().split("done=set()")[0])
done=set()
for p in (8,9):
  for ch in chains(p):
    c=classify(ch)
    if (p,c) in done: continue
    done.add((p,c))
    g=[gvec(t,ch) for t in L]; need=[]; pat=[]; ex=[]
    for gv in g:
      cnt=Counter(gv).most_common(); m1=cnt[0][1]; m2=cnt[1][1] if len(cnt)>1 else 0
      need.append(p-m1)
      if m1>m2: pat.append({k for k in range(p) if gv[k]!=cnt[0][0]}); ex.append(m1-m2)
      else: pat.append(None); ex.append(0)
    TOT=sum(need); cap=36*p
    A=[sum(1<<i for i in range(120) if pat[i] is not None and a in pat[i]) for a in range(p)]
    m=[max(pc(A[a]&F) for F in fl7) for a in range(p)]
    r=min(ex[i]/need[i] for i in range(120) if pat[i] is not None and need[i]>0)
    res=[]
    for s0 in range(1,p):
      rel=[max(0,min(need[i],s0,2*need[i]-s0)) for i in range(120)]
      mn=None
      for L0 in fl6:
        beta=cap-TOT+sum(rel[i] for i in range(120) if L0>>i&1)
        H=sum(max(0,pc(A[a]&~L0)-m[a]) for a in range(p))
        mg=r*H-beta
        if mn is None or mg<mn: mn=mg
      res.append((s0,mn))
    print(f"p={p} perp={c}: min margin r*H-beta by sigma0: {res}")
