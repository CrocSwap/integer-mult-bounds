"""Explicit GL-cover variant and sharp-fallback premises, OpenAI Codex.
No orthogonal-cover counting estimate is transferred to GL. Original PR473
source templates are emitted unchanged first, then this declared variant
changes the cover only. Actual instruction streams and ranks stay fixed.
"""
import gzip,hashlib,io,json,sys
from fractions import Fraction as Q
from pathlib import Path
import sympy as S
SOURCE,OUT=map(Path,sys.argv[1:3]);H=OUT/'hosted';m=78;physical=9609;depth=3
read=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
fs=read(OUT/'native/records/frames.json')['frames'];maxdet=1;primes=set();denoms=set();witnesses=[]
for k,z in fs.items():
 B=S.Matrix(z['B']) if z['B'] else S.zeros(0,8)
 G=B*B.T;det=int(G.det()) if B.rows else 1;assert det>0
 primes.update(map(int,S.factorint(det)));maxdet=max(maxdet,det)
 P=B.T*G.inv()*B if B.rows else S.zeros(8)
 assert P*P==P and P.trace()==z['dim']
 denoms.update(int(x.q) for x in P)
 witnesses.append([int(k),z['dim'],det])
assert primes<={2} and all(d&(d-1)==0 for d in denoms)
assert maxdet<2**128 and m<2**128 and physical<2**128
# Actual route coefficients are dyadic and their inverse is explicitly orthogonal.
geo=read(H/'GEOMETRY.json');assert geo['bad_prime_factors']==[2] and geo['route_denominators']==[1,2,4]
iso=read(SOURCE/'data/residual-isometries.json');assert all(z['denominator']==2 for z in iso)
# Every reduced idempotent has rank=trace r: q>m makes integer0..m traces distinct.
# For each k<=r the cleared leading minor has degree<=m*k. Its polynomial is
# nonzero on GL by similarity of a rank-r idempotent to diag(I_r,0).
degree=m*m*(m+1)//2;assert degree<=m**3
q0=2**128;fallback=6*(2*m)*(2*m-1)+3*(2*m)+6*(2*m-1);assert fallback==146478
fraction=Q(2*m**3,q0);assert fallback*fraction<Q(32*m*m,10**16)
row=depth*(m*m+1)+9909+252;assert row==28416
orthogonal_row=depth*(m*(m+1)//2+9)+9909+252
assert orthogonal_row<20161<row and Q(10**6)-Q(51*row,25)>0
# Compile the new declared cover into fresh output. Preserve the old receipt hash.
t=read(H/'GLOBAL-TEMPLATE.json.gz');g=read(H/'GLOBAL.json');old=g['template_sha256']
assert t['cover']=='O(I_78/2,F_q) for admitted odd address primes q'
assert g['live']==9600 and g['physical']==physical and g['maxchild']==56
assert g['emitted_events']==1722776 and g['hosted_residuals']==62920
assert m**depth>2*g['maxchild']**depth
raw=gzip.decompress((H/'GLOBAL-TEMPLATE.json.gz').read_bytes());assert hashlib.sha256(raw).hexdigest()==old
(H/'ORTHOGONAL-SOURCE-TEMPLATE.json.gz').write_bytes((H/'GLOBAL-TEMPLATE.json.gz').read_bytes())
t['cover']='GL_78(Z/q^w Z), every fixed odd prime q>2^128 and every atom width w>=1'
t['cover_variant']='Common split-idempotent conjugation; exact whole-owner right multiplication; rank-minor fallback counted on GL; full m^2 high-digit row stock.'
raw=json.dumps(t,separators=(',',':'),sort_keys=True).encode()
encoded=io.BytesIO()
with gzip.GzipFile(filename='',mode='wb',fileobj=encoded,mtime=0) as gz:gz.write(raw)
(H/'GLOBAL-TEMPLATE.json.gz').write_bytes(encoded.getvalue())
g['template_sha256']=hashlib.sha256(raw).hexdigest();g['source_orthogonal_template_sha256']=old;g['cover']=t['cover'];g['complete_gl_row_coefficient']=row
(H/'GLOBAL.json').write_text(json.dumps(g,indent=2)+'\n')
r=dict(status='PASS_EXPLICIT_GL_COVER_AND_SHARP_FALLBACK_PREMISES',m=m,source_template_sha256=old,template_sha256=g['template_sha256'],
 frame_count=len(fs),fixed_gram_determinant_prime_factors=sorted(primes),maximum_fixed_gram_determinant=maxdet,projector_denominators=sorted(denoms),
 fixed_frame_gram_witnesses=witnesses,route_denominators=[1,2,4],prime_rule='Choose any fixed prime q>2^128; every fixed denominator is a power of2, every fixed projector rank is preserved by idempotence and trace, and no numeric unproved primality assertion is needed.',
 maximum_sum_minor_degrees=degree,charged_degree=m**3,bad_class_fraction=str(fraction),fallback_children=fallback,
 proof='Clear det(g)^k from each leading k-minor of gPg^-1. Degree<=m*k; rank-r similarity supplies a nonzero witness over Fq. Sum<=m^3. Polynomial zero bound gives m^3/q on all matrices; conditioning on GL costs<2. Whole-owner and data maps multiply g on the right, preserving uniformity. Average edge costs separately; no union over edge types.',
 row=dict(cover='GL',high_digit_dimension=m*m,low_cover_bound='|GL_m(F_q)|<q^(m^2)',physical_exponent=1,physical_families=physical,halving_depth=depth,complete_row_coefficient=row,orthogonal_cap20161_rejected=True),
 unchanged_invoice_factors='Routing-time high-digit dimension already m^2; every helper selector has residual isometry, slot permutation, and idle basis charges. Scalar program/paid profile/physical prefix are unchanged. New outer assembly must charge row28416.',
 scope='Exact finite premises for applying the inherited weighted GL-cover compiler/fallback theorem. No transfer of an orthogonal counting bound, no split-family residual admission, and no new unconditional all-size theorem.')
(OUT/'GL-COVER-PREMISES.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='fixed_frame_gram_witnesses'},indent=2))
