import functools
s=open('partMain.lean').read()
s=s.replace("EVCOMB",functools.reduce(lambda e,i:"all_app4 (%s) %s"%(e,("BlockLaw2Ev%d.ev%d"%(i//8,i))), range(1,48),"BlockLaw2Ev0.ev0"))
s=s.replace("end BlockLaw2\n","")
planecomb=functools.reduce(lambda e,i:"all_appP (%s) BlockLaw2Pl%d.pl%d"%(e,i//8,i), range(1,48),"BlockLaw2Pl0.pl0")
s+="\ntheorem certs_plane : certs.all planeChk = true :=\n  "+planecomb+"\n"+open('part6.lean').read()
try: s+=open('part8.lean').read()
except FileNotFoundError: pass
s+="""
#print axioms certs_even_ind
#print axioms Fperp_cap_exact
#print axioms blocking_one_Lam
#print axioms sem_one_Lam
#print axioms branch2_forced
#print axioms no_blocking_le6
#print axioms blocking_dim_ge7
#print axioms BlockLaw2D8.blocking8_iff
end BlockLaw2
"""
open('<research-tree>/lean/decoder-duality/Nov15/BlockLaw2.lean','w').write(s)
