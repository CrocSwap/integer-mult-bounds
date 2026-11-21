from qzdrive import *
masks=[{0,1},{0,1},{0,1,2},{0,1,2}]
d=make_design(4,3,masks,[{0,1},{0,1}],(2,0,1),{0:2,1:2})
S=Sys(d)
for t in range(4):
    z=np.random.default_rng(t).normal(size=d.nv); z,nr=lm(S,z,it=1500)
    V,W,ab=d.unpack(z)
    print('%.2e'%nr,'ab',[round(a*b,5) for a,b in ab],'max|v|,|w| %.1e %.1e'%(np.abs(V).max(),np.abs(W).max()))
