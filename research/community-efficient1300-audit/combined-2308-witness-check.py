"""Maintainer check of the exact named pair, independent of optimized assertions."""
import importlib.util,json,pathlib,sys,hashlib
root=pathlib.Path(sys.argv[1]).resolve()
path=root/'research/cycle47-shared-frame-correction/verify.py'
spec=importlib.util.spec_from_file_location('shared_correction_review',path)
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
m=v.load_module('frame_geometry_review',root/'research/complex-frame-pair-decoders/verify.py')
images,beta=v.e8_binary_images(m.LINES,m.IP,m.ip)
selected=sorted(int(x['line']) for x in v.CERT['q_to_line'])
frames=v.enumerate_frames(selected,m.IP)
rp=tuple(v.CERT['witness']['r_bits']);S1,S2=map(tuple,v.CERT['witness']['frames'])
assert S1!=S2 and S1 in frames and S2 in frames
assert all(beta(rp,images[a])==1 for S in (S1,S2) for a in S)
family=[S for S in frames if all(beta(rp,images[a])==1 for a in S)]
M0,_=v.correction_block(family[0],rp,selected,m.IP,images,beta)
piv=v.row_pivots(M0);assert len(piv)==8
inv=v.inverse([[M0[i][j] for j in piv]for i in range(8)])
Cs=[];Ms=[];den=1
for S in (S1,S2):
 M,_=v.correction_block(S,rp,selected,m.IP,images,beta)
 C=v.matmul([[M[i][j] for j in piv]for i in range(8)],inv)
 assert v.matmul(C,M0)==M and v.qrank(M)==8
 for row in C:
  for x in row:den=den*x.denominator//v.gcd(den,x.denominator)
 Cs.append(C);Ms.append(M)
Ds=[[[int(x*den)for x in row]for row in C]for C in Cs]
assert all(v.matmul(D,M0)==[[den*x for x in row]for row in M] for D,M in zip(Ds,Ms))
r=v.f2rank(Ds[0]+Ds[1]);assert r==1
print(json.dumps({'status':'PASS','source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'frames_in_exhaustive_domain':True,'both_rational_ranks':8,'pair_denominator':den,'pair_coefficient_F2_rank':r,'scope':'Exact named same-direction witness, not a physical support-rank invoice.'},indent=2))
