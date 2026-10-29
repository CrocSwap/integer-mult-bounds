import json,csv,ast
from collections import Counter
mine=json.load(open('rrc_results.json'))
M={(o[1],tuple(o[3])):o for o in mine}
A=json.load(open('../SC-B2/allrows_rrc.json'))
print(len(A), Counter(type(x[3]).__name__ if not isinstance(x[3],list) else 'list' for x in A))
print(A[0], [x for x in A if x[1]==6][:2])
theirs7=[(x[0],tuple(sorted(x[2],reverse=True))) for x in A if x[1]==7 and x[3] is not None and x[3]!=False]
print('theirs s7 entries',len(theirs7))
miss=[k for k in theirs7 if not M[k][4]]
print('their s7 kills not killed by me:',len(miss),miss[:5])
# class B rows
B=list(csv.DictReader(open('../SC-B2/killed.csv')))
kb=[(int(r['d']),tuple(sorted(ast.literal_eval(r['weights']),reverse=True))) for r in B]
print('class B',len(kb),'mine dead',sum(1 for k in kb if M[k][4]==True), [ (k,M[k][2]) for k in kb if M[k][4]!=True])
S7B=list(csv.DictReader(open('../SC-S7B/killed.csv')))
k7=[(int(r['d']),tuple(sorted(ast.literal_eval(r['weights']),reverse=True))) for r in S7B]
print('S7B',len(k7),'mine dead',sum(1 for k in k7 if M[k][4]==True))
L=list(csv.DictReader(open('../SPANCOVER/ledger.csv')))
s7a=[(int(r['d']),tuple(sorted(ast.literal_eval(r['weights']),reverse=True))) for r in L if r['status'].startswith('CIRCUIT-proven')]
print('S7a',len(s7a),'mine dead',sum(1 for k in s7a if M[k][4]==True), 'IMM',sum(1 for k in s7a if M[k][5][0][1][0]=='IMM'))
