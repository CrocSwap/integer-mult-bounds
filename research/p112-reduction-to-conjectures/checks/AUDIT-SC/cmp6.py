import sys,json,pickle
sys.path.insert(0,'../SC-B2')
import allrows6 as A6   # prints its Counter
res=pickle.load(open('../SPANCOVER/opts.pkl','rb'))
theirs={(d,tuple(sorted(ws,reverse=True))) for d,s,ws,e,o in res if s==6 and A6.robust6(sorted(ws,reverse=True),d)}
mine=json.load(open('../AUDIT-SC/rrc_results.json'))
M={(o[1],tuple(o[3])):o for o in mine if o[2]==6}
mk={k for k,o in M.items() if o[4]==True}
print('theirs',len(theirs),'mine',len(mk),'theirs-mine',sorted(theirs-mk),'mine-theirs',sorted(mk-theirs))
for k in sorted(theirs-mk):
    print(k,[(t,c is not None) for t,c in M[k][5]])
