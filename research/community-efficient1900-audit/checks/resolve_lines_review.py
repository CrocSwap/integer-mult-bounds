from pathlib import Path
import json,subprocess,hashlib,itertools,shutil
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'sources/2244';pkg=D/'research/line-system-saturation';head=json.loads((P/'2244.json').read_text())['headRefOid'];f=pkg/'README.md';original=f.read_bytes();text=original.decode()
a='**2k′+1 generic rational orthonormal frames of ℚ^T realise v = (2k′+1)T, x = 1** for every T.'
b='**2k′+1 generic rational orthonormal frames of ℚ^T realise v = (2k′+1)T, x = 1** for every T ≥ 2. The dimension-one space has only one distinct line, so it is excluded from this converse when F ≥ 2.'
assert text.count(a)==1;text=text.replace(a,b)
a='**Corollary D2.** A saturated system at level k′ yields saturated systems at levels k′−1, …, 1. Hence **saturation at any k′ ≥ 4 forces a saturated k′ = 4 system** (for general multiplicities the levels 1, 2, 3 are realised by D4, D6, E7 and their real blow-ups, §7.2).'
b='''**Corollary D2.** Proposition D1 gives a saturated quotient family, possibly on a zero-dimensional space if m_p = T. In positive dimension, **saturation at any k′ ≥ 4 forces a positive-dimensional saturated k′ = 4 system** (the Gram examples D4, D6 and E7 realise levels 1, 2 and 3).

*Positive-dimensional descent to level four.* For any k′ ≥ 3, some occupied label has 0 < m_p < T. Otherwise every nonzero idempotent equals Id_T. Orthogonality then makes the occupied labels a pairwise non-collinear set, while saturation requires exactly one occupied label on each generator, hence 2^{k′}+1 occupied labels by incidence counting. Their adjacency is J−I, whose F2 rank is at least their number minus one, so there are at most 2k′+1 occupied labels. This contradicts 2^{k′}+1 > 2k′+1 for k′ ≥ 3. Choosing a proper-rank label therefore keeps T−m_p positive; repeat while k′ > 4. A claim of positive-dimensional descent through *every* lower level is not needed here: at level two, rank-one scalar idempotents on a five-point ovoid give a saturated family in T=1 whose quotients have dimension zero.'''
assert text.count(a)==1;text=text.replace(a,b)
a='The derived system at p has class sizes c_L − m_p (L ∋ p, bijectively with generators of the quotient) in dimension T − m_p, so its saturation'
b='If m_p = T, the bound A_p ≤ sT + (1−s)m_p = T follows directly from c_L ≤ T; no quotient ratio is taken. For m_p < T, the derived system at p has class sizes c_L − m_p (L ∋ p, bijectively with generators of the quotient) in dimension T − m_p, so its saturation'
assert text.count(a)==1;text=text.replace(a,b)
f.write_text(text)
# Save the author originals and separately reviewed successors.
originals=R/'research/community-efficient1900-audit/originals/2244/research/line-system-saturation';originals.mkdir(parents=True,exist_ok=True);(originals/'README.md').write_bytes(original);(originals/'MANIFEST.sha256').write_bytes((pkg/'MANIFEST.sha256').read_bytes())
rows=(pkg/'MANIFEST.sha256').read_text().splitlines();new=[]
for row in rows:
 h,name=row.split('  ',1);new.append((hashlib.sha256(f.read_bytes()).hexdigest() if name=='README.md' else h)+'  '+name)
(pkg/'MANIFEST.sha256').write_text('\n'.join(new)+'\n')
def dot(x,y):return sum(((x>>(2*i))&1)*((y>>(2*i+1))&1)+((x>>(2*i+1))&1)*((y>>(2*i))&1) for i in range(2))%2
ovo=next(c for c in itertools.combinations(range(1,16),5) if all(dot(x,y)==1 for x,y in itertools.combinations(c,2)))
generators=sorted({tuple(sorted((x,y,x^y))) for x in range(1,16) for y in range(x+1,16) if dot(x,y)==0});assert len(generators)==15 and all(len(set(g)&set(ovo))==1 for g in generators)
# Authenticate the stated inherited library lineage against current main when present.
libs=[]
for name in ('exact.py','report.py','units.py'):
 rel='research/ideal-decoder-floors/lib/'+name;v=subprocess.run(['git','show','HEAD:'+rel],cwd=R,capture_output=True)
 assert v.returncode==0 and v.stdout==(pkg/'lib'/name).read_bytes(),name
 libs.append(dict(path='lib/'+name,retained_source=rel,sha256=hashlib.sha256(v.stdout).hexdigest()))
cmd=['/tmp/pr-efficient200-venv/bin/python','-B',str(pkg/'scripts/provenance.py')];a=subprocess.run(cmd,cwd=D,capture_output=True,text=True);(P/'check-2244-resolution.log').write_text(a.stdout+a.stderr);a.check_returncode();assert a.stdout.count('PASS')==2
plan=json.loads((P/'resolution-plan.json').read_text())
for name in ('README.md','MANIFEST.sha256'):
 rel='research/line-system-saturation/'+name;dst=P/'resolutions/2244'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(pkg/name,dst);assert not any(x['number']==2244 and x['path']==rel for x in plan);plan.append(dict(number=2244,path=rel,resolved_mode='100644',resolved_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),reason='Clarify T>=2 for distinct generic frames, preserve positive-dimensional descent to level four with its rank-clique proof, and avoid division by zero in quantitative descent. Scientific code/data unchanged; original README and manifest retained.'))
(P/'resolution-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
receipt=dict(number=2244,head=head,status='passed',scope='Two written boundary repairs and unchanged scientific source/data. Original full89 checks retained; updated manifest/provenance rerun only.',argv=cmd,exit_code=a.returncode,log_sha256=hashlib.sha256((P/'check-2244-resolution.log').read_bytes()).hexdigest(),degenerate_idempotent_witness=dict(k=2,T=1,occupied_labels=list(ovo),generators=generators,all_generator_sums_equal_identity=True,quotient_dimension=0),inherited_libraries=libs,source_resolution=[x for x in plan if x['number']==2244]);(P/'check-2244-resolution.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS written boundary repairs, 15-generator exact witness, 3 inherited libraries')
