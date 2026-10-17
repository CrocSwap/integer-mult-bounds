import json,csv,ast
from collections import Counter
mine=json.load(open('rrc_results.json'))
M={(o[1],tuple(o[3])):o for o in mine}
L=list(csv.DictReader(open('../SPANCOVER/ledger.csv')))
st={(int(r['d']),tuple(sorted(ast.literal_eval(r['weights']),reverse=True))):r['status'] for r in L}
A=list(csv.DictReader(open('../SC-A2/killed2.csv')))
A1=list(csv.DictReader(open('../SC-A/killed.csv')))
print('SC-A killed.csv == SC-A2 killed2.csv:',sorted(map(str,A))==sorted(map(str,A1)))
c=Counter(); uniq=[]
for r in A:
    k=(int(r['d']),tuple(sorted(ast.literal_eval(r['weights']),reverse=True)))
    rr=M[k][4]==True; sp=st[k].startswith('KILLED')
    c[(int(r['slack']),rr,sp)]+=1
    if not rr and not sp: uniq.append((k,r['slack'],r['lemma'],r['S_contracted'],r['s'],r['e_prime'],r['m'],r['sigma_omega']))
print(c)
print(len(uniq))
for u in uniq: print(u)
