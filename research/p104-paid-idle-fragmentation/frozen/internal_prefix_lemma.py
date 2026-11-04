"""Check the prefix matrix used by the internal-idle obstruction proof.

The algebraic proof in RESEARCH-NOTES.md treats arbitrary ordinary u.
These exact fixtures bind its signs, central normalization and chronology
to the literal binary macro, with all input coefficients tested.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
PACKAGE=HERE if (HERE/'two-fragment/independent.py').exists() else HERE/'release'
engine=PACKAGE/'two-fragment/independent.py'
spec=importlib.util.spec_from_file_location('prefix_laurent',engine)
I=importlib.util.module_from_spec(spec)
spec.loader.exec_module(I)
one={(0,0,0):I.ONE}
S=I.normalized_central(one)
L=I.shift(one,stages=[1])
LR=I.shift(one,stages=[1,2])
SL=I.shift(S,stages=[1])
minusSL=I.scale(SL,-1)
rows=[]
for kind,u in [('rank1',Q(0)),('rank1',Q(1)),('rank1',Q(2)),('rank1',Q(-1,2)),('rank2',Q(0))]:
    # x,y,a,b are 0,1,2,3. The first QUERY is normalized to S.
    events=[['SWAP',0,3],['SWAP',1,2],['SWAP',2,3],
            ['ADD',0,2,'1'],['ADD',3,1,'-1'],
            ['LAMBDA',2,-1],['QUERY',2,3,-1],['LAMBDA',2,1],
            ['ADD',3,1,'1'],['ADD',0,2,'-1']]
    if kind=='rank1':
        if u:events.append(['ADD',2,3,str(u)])
        events.extend([['IDLE_ONE',2,[1]],['IDLE_ONE',3,[1,2]]])
        if u:events.append(['ADD',2,3,str(-u)])
    else:events.append(['IDLE',2,3,[1]])
    # Complete the left child, with its actual negative orientation.
    events.extend([['SCALE',1,'-1'],['LAMBDA',1,-1],
                   ['LOCAL',1,0,1],['LAMBDA',1,1],['SCALE',1,'-1']])
    aY=I.plus(SL,I.plus(I.scale(L,u),I.scale(LR,-u))) if kind=='rank1' else SL
    expected=[[{},minusSL,SL,L],
              [{},L,{},minusSL],
              [L,aY,minusSL,{}],
              [{},LR if kind=='rank1' else L,{},{}]]
    for j in range(4):
        column=[dict(one) if j==k else {} for k in range(4)]
        for event in events:I.forward(column,event)
        I.need(column==[row[j] for row in expected],'Literal prefix column '+str(j))
    for j in range(4):
        row=[dict(one) if j==k else {} for k in range(4)]
        for event in reversed(events):I.right_action(row,event)
        I.need(row==expected[j],'Literal prefix row '+str(j))
    rows.append({'projector':kind,'u':str(u),'events':len(events),
                 'forward_coefficients':16,'reverse_coefficients':16})
result={'status':'PASS_INTERNAL_IDLE_PREFIX_MATRIX',
        'fixtures':rows,'central_relation':'S=lambda*q^-1, S^2=1, q^4=1',
        'engine_sha256':sha256(engine.read_bytes()).hexdigest(),
        'caller_sha256':sha256((PACKAGE/'two-fragment/caller.py').read_bytes()).hexdigest(),
        'scope':'Literal prefix matrix and phase fixtures. The arbitrary-u no-unit-pair conclusion is proved algebraically in RESEARCH-NOTES.md; no new paying construction is asserted.'}
raw=json.dumps(result,indent=2)+'\n'
if sys.argv[1:]==['--write']:(HERE/'INTERNAL-PREFIX-LEMMA.json').write_text(raw)
else:
    I.need(sys.argv[1:]==[],'Arguments')
    I.need((HERE/'INTERNAL-PREFIX-LEMMA.json').read_text()==raw,'Frozen prefix lemma')
print(result['status'])
