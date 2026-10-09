"""Cover every emitted frame by retained exact witnesses or new exact Gram factors."""
if not __debug__:raise RuntimeError('Prime verification requires assertions')
from pathlib import Path
import argparse,gzip,hashlib,importlib.util,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/paired-cube-bit'))
from check_paired_cube_bit import kernel
parent_script=ROOT/'research/paired-cube-local-bit-168/bit/prime_witnesses.py'
spec=importlib.util.spec_from_file_location('retained_prime_arithmetic',parent_script);P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
parent_path=parent_script.with_name('prime-witnesses.json.gz')
frame_path=ROOT/'references/paired-cube/bit-physical/frames_p12.json.gz'
parent=json.loads(gzip.decompress(parent_path.read_bytes()));primes=tuple(parent['stripped_primes']);assert primes==P.PRIMES
# Preserve the precise inherited q>2^80 guard. Every stripped prime is below it.
limit=2**80;assert all(type(p) is int and 1<p<limit and all(p%d for d in range(2,int(p**0.5)+1)) for p in primes)

def coverage(word):
 fr=json.loads(gzip.decompress(frame_path.read_bytes()))['frames'];h=word['h'];assert h==parent['h']==24
 used={o[3] for o in word['ops']}|set(word['rootframes'])|{z['frame'] for z in word['gauges']}|{word['full_frame']}
 for e in word['k']['entries']:used.update(e['carrier_chain']);used.update(e['passive_chain'])
 inherited={r['basis_sha256']:r for r in parent['frame_witnesses']};assert len(inherited)==len(parent['frame_witnesses'])
 own={};covered={};records=[]
 for f in sorted(used):
  rec=fr[str(f)];B=kernel([tuple(a) for a in rec['a']],h)[0] if 'a' in rec else rec['b']
  key=json.dumps(B,separators=(',',':'));sha=hashlib.sha256(key.encode()).hexdigest()
  if sha in inherited:
   r=inherited[sha];P.validate_factor(r['cleared_gram_determinant'],r['small_prime_powers'],r['remaining_factor']);assert r['dimension']==len(B)
   covered.setdefault(sha,[]).append(f)
  else:
   if sha not in own:
    sums=list(map(sum,B));G=[[9*sum(x*y for x,y in zip(a,b))-sums[i]*sums[j] for j,b in enumerate(B)] for i,a in enumerate(B)]
    d=P.det(G);powers,residual=P.factor_witness(d)
    own[sha]=dict(basis_sha256=sha,frame_ids=[],dimension=len(B),cleared_gram_determinant=d,small_prime_powers=powers,remaining_factor=residual,gram_denominator_power_of_9=len(B))
   own[sha]['frame_ids'].append(f)
  records.append([f,sha])
 assert sum(map(len,covered.values()))+sum(len(r['frame_ids']) for r in own.values())==len(used)
 # Missing supplement coverage and factor corruption must be rejected.
 controls=[];zeros={str(p):0 for p in primes}
 for name,args in [('zero_determinant',(0,zeros,1)),('incorrect_factor_identity',(15,zeros,1)),('factor_at_or_above_inherited_prime_floor',(limit+7,zeros,limit+7))]:
  try:P.validate_factor(*args)
  except AssertionError:controls.append(name)
  else:raise AssertionError('Invalid witness accepted: '+name)
 assert own,'This recorded supplement must be nonempty'
 missing=next(iter(own));available=set(inherited)|set(own);available.remove(missing)
 try:assert all(sha in available for f,sha in records)
 except AssertionError:controls.append('missing_supplemental_basis')
 else:raise AssertionError('Missing supplemental basis accepted')
 return dict(status='PASS',h=h,used_frames=len(used),parent_covered_frames=sum(map(len,covered.values())),parent_covered_bases=len(covered),supplemental_frames=sum(len(r['frame_ids']) for r in own.values()),supplemental_bases=len(own),parent_witness_sha256=hashlib.sha256(parent_path.read_bytes()).hexdigest(),parent_arithmetic_sha256=hashlib.sha256(parent_script.read_bytes()).hexdigest(),frame_source_sha256=hashlib.sha256(frame_path.read_bytes()).hexdigest(),used_frame_basis_manifest_sha256=hashlib.sha256(json.dumps(records,separators=(',',':')).encode()).hexdigest(),stripped_primes=list(primes),prime_lower_bound=limit,prime_guard_unchanged=True,maximum_supplemental_determinant_bits=max(abs(r['cleared_gram_determinant']).bit_length() for r in own.values()),maximum_supplemental_remaining_factor=max(r['remaining_factor'] for r in own.values()),frame_witnesses=[own[k] for k in sorted(own)],adverse_controls=controls,scope='Canonical basis hashes bind all emitted frames to pinned retained exact Gram witnesses or explicitly recomputed supplemental Bareiss witnesses. Retained determinant values rely on the independently verified immutable parent witness; factor identities are rechecked here. Every q>2^80 remains valid. Complement formula denominators 3 and5 are already excluded.')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--word',type=Path,required=True);ap.add_argument('--write',action='store_true');ap.add_argument('--output',type=Path);a=ap.parse_args()
 record=coverage(json.loads(a.word.read_text()));frozen=HERE/'prime-coverage.json'
 if a.write:frozen.write_text(json.dumps(record,indent=2)+'\n')
 else:assert record==json.loads(frozen.read_text()),'Supplemental prime witness drift'
 if a.output:a.output.write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps({k:v for k,v in record.items() if k!='frame_witnesses'},indent=2))
if __name__=='__main__':main()
