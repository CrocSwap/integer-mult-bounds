"""Rank-eight involutive source preparation for the current E8 interface.

Derived from PR1862's identity-target interface, dropping its selected full
query logger condition. Here RK=14I, RP=I, U=K-12P, F=I-UR. Then RU=2I,
F^2=I, RF=-R and (I-KR)F-I=12PR. Eight repair rows suffice as before.
No routed-controller closure or improved kappa is asserted by this producer.
"""
from fractions import Fraction as Q

def matrices(data,certificate,base):
 R=data['R'];n=len(data['J']);rank=len(R)
 K=[{k:row[p]/4 for k,row in enumerate(R)if p in row}for p in range(n)]
 A=certificate['compensation_ports']
 P=[row.copy()if p in A else{}for p,row in enumerate(K)]
 small=[{k:Q(1)}for k in range(rank)]
 assert base.product(R,P)==small
 assert base.product(R,K)==[{k:Q(14)}for k in range(rank)]
 U=[row.copy()for row in K]
 for row,part in zip(U,P):base.add(row,part,-12)
 assert base.product(R,U)==[{k:Q(2)}for k in range(rank)]
 F=[{p:Q(1)}for p in range(n)]
 for row,part in zip(F,base.product(U,R)):base.add(row,part,-1)
 correction=[{j:12*x for j,x in row.items()}for row in base.product(P,R)]
 assert base.product(F,F)==[{p:Q(1)}for p in range(n)]
 assert base.product(R,F)==[{j:-x for j,x in row.items()}for row in R]
 actual=base.product(data['J'],F)
 for p,row in enumerate(actual):base.add(row,{p:Q(1)},-1)
 assert actual==correction
 assert {p for p,row in enumerate(correction)if row}==set(A)
 return dict(R=R,K=K,P=P,U=U,G=F,G_inverse=F,JG_minus_I=correction)

def source_word(values,bank,frame,base):
 events=[]
 for k,row in enumerate(values['R']):
  events.append(['scalar',['clear',['C',0]],frame])
  events += [base.scalar_add(['C',0],['L',bank+j],x,frame)for j,x in sorted(row.items())]
  events += [base.scalar_add(['L',bank+p],['C',0],-row[k],frame)for p,row in enumerate(values['U'])if k in row]
  events.append(['scalar',['clear',['C',0]],frame])
 return events

def produce(data,certificate,base):
 w=data['word'];v=w['v'];full=w['final'][0];vals=matrices(data,certificate,base)
 before=[['phase','reflection_input_correction']]
 after=[['phase','reflection_output_correction']]
 for p in certificate['compensation_ports']:
  row=vals['JG_minus_I'][p]
  before.append(['scalar',['clear',['C',0]],0])
  before += [base.scalar_add(['C',0],['L',v+j],x,0)for j,x in sorted(row.items())]
  before.append(['unit_transfer_input_line',p,w['ports'][p],0,w['start'][p],1])
  before.append(base.scalar_add(['L',p],['C',0],1,w['start'][p]))
  before.append(['scalar',['clear',['C',0]],0])
  after.append(['scalar',['clear',['C',0]],full])
  after += [base.scalar_add(['C',0],['L',j],-x,full)for j,x in sorted(row.items())]
  after.append(['unit_transfer_exit_line',p,w['ports'][p],-1,full,w['final'][v+p],1])
  after.append(base.scalar_add(['L',v+p],['C',0],1,w['final'][v+p]))
  after.append(['scalar',['clear',['C',0]],0])
 source=source_word(vals,v,0,base);exit_source=source_word(vals,0,full,base)
 return dict(matrices={k:base.serial(v)for k,v in vals.items()},
  blocks=dict(backward_input=before,source_G=source,forward_source=exit_source,forward_output=after),
  programs=dict(backward=before+source+data['clean_programs']['backward'],
                forward=data['clean_programs']['forward']+exit_source+after))
