exec(open('cat1.py').read().split("res=[]")[0])
best=Counter(); per=defaultdict(list)
for o,(kind,h) in sel.items():
    vals=sorted((len(S&o),phi) for phi,S in O.items())
    per[(kind,len(o))].append(vals[:3])
for k in per:
    print(k, Counter(tuple(x[0] for x in vs) for vs in per[k]).most_common(5))
# the n4/76 with 12: which phi; is O_phi ∩ Off(h) structure
for o,(kind,h) in sel.items():
    if len(o)==76:
        for phi,S in O.items():
            if len(S&o)==12:
                I=S&o; print('n4',h,'phi',phi,'|O|',len(S),'I labels rank', len(I)); break
        break
# global: min over ALL h in list of |O_phi∩Off(h)| for each phi type
