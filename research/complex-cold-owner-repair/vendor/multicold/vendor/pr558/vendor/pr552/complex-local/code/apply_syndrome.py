from pathlib import Path
from fractions import Fraction as Q
import json,gzip,sys,copy,hashlib,argparse
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--gk',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();sys.path.insert(0,str(args.gk))
import gk_word as g,gk_common as c
g.V=c.V=112;g.DATA=c.DATA=7168
p=Path(__file__).resolve().parent;w=json.load(gzip.open(args.input));old=copy.deepcopy(w)
N=728;V=112;protected=set(range(V))|set(map(int,w['start_extra']))
rows=[{i:Q(1)}for i in range(N)]
e=w['A'][33];assert e[1:3]==[513,523]
for op in w['A'][:33]:g.apply_op(op,rows)
a=Q(-1);err=rows[523].copy()
for j,x in rows[512].items():
 err[j]=err.get(j,Q(0))-a*x
 if not err[j]:err.pop(j)
assert err and not protected&set(err) and all(j>=224 for j in err)
e[2]=512;e[3]*=-1
w['cleanup']=[g.inverse(e,g.FULL)for e in reversed(w['A']+w['B'])if not V<=e[1]<2*V]
before=g.profile(old);after=g.profile(w);assert before==after
out=args.out;out.mkdir(exist_ok=False)
raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode();(out/'FULL-WORD.json.gz').write_bytes(gzip.compress(raw,mtime=0))
r=dict(status='PASS_EXACT_COLD_DIRT_QUOTIENT_SUBSTITUTION',section='A',index=33,old_operation=old['A'][33],new_operation=e,source_relation_multiplier=str(a),cold_initial_error={str(j):str(x)for j,x in err.items()},protected_columns=len(protected),source_rows_computed_by_finite_triangular_forward_elimination=True,local_profile=dict(after),profile_unchanged=True,requires_regenerated_frame_zero_compensation=True,source_content_sha256=hashlib.sha256(json.dumps(old,sort_keys=True,separators=(',',':')).encode()).hexdigest(),output_content_sha256=hashlib.sha256(raw).hexdigest())
(out/'SYNDROME-CERTIFICATE.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
