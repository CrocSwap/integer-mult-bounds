import glob,re,collections
for f in sorted(glob.glob('run_*.log')):
    rows=[l.split() for l in open(f) if l.startswith('it ')]
    if not rows: continue
    C=[int(r[5]) for r in rows]; C1=[int(r[9]) for r in rows]; S=[int(r[11]) for r in rows]
    unsat=sum(1 for r in rows if 'cls []' in ' '.join(r))
    # S1 histogram
    h=collections.Counter(S)
    print(f[4:-4],'n',len(rows),'minC',min(C),'minC1',min(C1),'minS1',min(S),'S1 q10/50',sorted(S)[len(S)//10],sorted(S)[len(S)//2],'(C,S1) at minS1',[(c,s) for c,s in zip(C,S) if s==min(S)][:2], 'min C-S1 slack',min(c1-s for c1,s in zip(C1,S)))
