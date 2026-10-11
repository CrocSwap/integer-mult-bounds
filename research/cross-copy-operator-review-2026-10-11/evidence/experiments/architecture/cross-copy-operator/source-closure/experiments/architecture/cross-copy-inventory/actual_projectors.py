from pathlib import Path
import json
import sympy as S
O=Path(__file__).resolve().parent;ROOT=O.parents[2];F=json.load(open(ROOT/'experiments/architecture/collective-common-frame-bit/composed/records/frames.json'))['frames'];chain=[0,2,459,493,919,1]
def projector(i):
 B=S.Matrix(F[str(i)]['B'])
 return B.T*(B*B.T).inv()*B if B.rows else S.zeros(8)
Ps=[projector(i)for i in chain];I=S.eye(8);A=Ps[-2];B=I-A
assert A.rank()==7 and B.rank()==1 and A*A==A and B*B==B and A*B==S.zeros(8)
for j,P in enumerate(Ps):
 assert P*P==P and P==P.T and A*P==P*A and B*P==P*B
 if j:assert Ps[j-1]*P==Ps[j-1]
assert B*Ps[1]==S.zeros(8)
r={'status':'EXACT_ACTUAL_NONCOORDINATE_7_PLUS_1_REDUCING_SPLIT','helper':240,'frame_chain':chain,'dimensions':[P.rank()for P in Ps],'projectors':{str(i):[[str(x)for x in row]for row in P.tolist()]for i,P in zip(chain,Ps)},'piece7':[[str(x)for x in row]for row in A.tolist()],'piece1':[[str(x)for x in row]for row in B.tolist()],'scope':'ExactQ projector split commuteswithallactualMOVEframes and containsfirstlineinpiece7. This provesa geometricreducing decomposition, notadmissibleorthogonalrationalchart/ADDRESSsigma/virtualVALUEencoding. Even this favorablealignedgeometry is subjecttoFIRST-LAST-GATE. AllADDR operationsanddirtinversecostseparate.'};(O/'ACTUAL-PROJECTORS.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'])
