"""Independent PR493 pinned-source invoice and exact arithmetic audit, OpenAI Codex. Apache-2.0.
Usage: review_invoice.py PR493_PACKAGE FRESH_OUTPUT REPORT.json
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import gzip,hashlib,importlib.util,json,sys
if not __debug__:raise RuntimeError('assertions must remain enabled')
assert len(sys.argv)==4, 'usage: review_invoice.py PR493_PACKAGE FRESH_OUTPUT REPORT.json'
PKG,O,REPORT=map(lambda x:Path(x).resolve(),sys.argv[1:])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
manifest={}
for line in (PKG/'MANIFEST.sha256').read_text().splitlines():h,p=line.split('  ',1);manifest[p]=h
actual={str(p.relative_to(PKG)):sha(p) for p in PKG.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256' and '__pycache__' not in p.parts};assert actual==manifest
PINNED_BLOBS={'EXPECTED.json': '973aaf30f1ec6a4d58038acabb9361ee1f44787a', 'LICENSE': '261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64', 'MANIFEST.sha256': '1213654fbd423d66e785bf582ba8ee76a41cdd36', 'NOTICE.md': '5a0ecdcd2c7fad0488740a1da0f633b73b56a809', 'README.md': 'dd0d7c43611d6c527a17287bc550e763edca0294', 'SOURCE-pr370.json': '1b30f277afa20cb9db1e4495d655a32d64552317', 'SOURCE-pr381.json': 'fb0b0edd1375ffcbe9b2c9065bcca236a974660f', 'SOURCE-pr386.json': '3744861904f61f29b00e2dec9cb98639a0fb7dfe', 'SOURCE-pr436.json': 'f190527ae1c97a51fa9030518b59affeb0befcd3', 'SOURCE-pr445.json': 'ae29de391a7aa893bec6ab8c2b6e89688191b088', 'SOURCE-pr448.json': '3648ab36928a28564ce89d224cfb3f16c891ecf1', 'SOURCE-pr451.json': 'fbd9881e09d7219f264eb1ee67c40c2e43d0832e', 'SOURCE-pr458.json': 'c36c74cbeacf690473803b59a8d25008ec5a7710', 'SOURCE-pr471.json': '0dc019cfb1933e55d063fbd9e45bb316e4045857', 'SOURCE-pr472.json': '31acb027ecd0808f18e6f59c59662f6f94f5b9ac', 'SOURCE-pr473.json': '821caf8f073c615680ba5610e268eee2d23d2d03', 'SOURCE-pr478.json': '608323ccbe4150d5a6522ddb3b18aa9cb5dff4fa', 'SOURCE-pr483.json': '817396d9c89965a32979b943e638163d8261a205', 'SOURCE-pr484.json': '76292df8518ac72acb3754a7b4fb23c368725b13', 'code/bit/checkers/columns_h.cpp': '00c5a3a5d81d083582f60f33dd2e7bea5049c37f', 'code/bit/checkers/columns_k.cpp': '42bb232fbec4de703e70cc13dc2f39a3b43a3a01', 'code/bit/checkers/gram_frames.py': 'b740d47295c02692260d7cc01874a49fe48f78ab', 'code/bit/checkers/json.hpp': '82d69f7c5d044c9887c96b90c97f5639083ecd14', 'code/bit/checkers/legality_h.cpp': 'cb1233c7e96b1aa8bbf4d2e4165d75ab0dca64b9', 'code/bit/export_records.py': '3632d370486a02f5456f7643ced03f8c925b2350', 'code/bit/independent/checkword.py': 'da4e0fe05067184d4dab1e130ae1384c1fa983f5', 'code/bit/independent/interface.py': '8beb87c39a07e389c8f83f32ab9d17f8097ed9b1', 'code/bit/independent/mutate.py': 'eba592fd468e0d7e7e5100fe99da6eb548c5906b', 'code/bit/independent/mutate_mut.py': 'f4c6191b783094c4d241f179446085331feb052b', 'code/bit/independent/relax.py': 'a37e8b8176080d4a977bb48bd25f92f4a62b156b', 'code/bit/mutate_records.py': '6794516f665d36eac189894e350a5ad01113cb4c', 'code/bit/mutate_records_mut.py': 'ea26fcebf99312eb5d4f5440862959fa6a74ec52', 'code/bit/regression/stage_cohort.py': 'f6d7afe3e623208c4207b6a683a1e3e49249e31c', 'code/cited.py': 'e543cf2c9b2b1d43693bed6efbdba607ad9ac277', 'code/eleven/adapt.py': 'c13c91c245146670d4b454ff07b835f480171fc1', 'code/eleven/assemble.py': '87cc45bc831fa7003906e8b026ac1480a69da1de', 'code/eleven/audit.py': '10e47d32e3b4769ae5ce5bad9f76a7b3e5d797fc', 'code/eleven/emit.py': '640cdb4d1220950e198f2fd9994d76d69ecbf764', 'code/eleven/local_audit.py': '2233c5f35f2fcb58809f7a1d8f91e9b36ad74080', 'code/hub/e8-r715-whole-hosted/code/assemble.py': 'cd60b4bcfae515fccd7f21fd1ff5a7114a132eb9', 'code/hub/e8-r715-whole-hosted/code/audit.py': '155b61f2944116423a5be6ae666276e1c1827fe5', 'code/hub/e8-r715-whole-hosted/code/emit.py': 'df74ad698a98419e828b37d4dfd7c036fc49a890', 'code/hub/e8-r715-whole-hosted/code/local_audit.py': '931f884920125b334412f70cf30d9517b084dc7a', 'code/hub/e8-r715-whole-hosted/data/hosting.json': '381fb06ccbe055f4fbdc7544dcf8c0bae8f96701', 'code/hub/e8-r715-whole-hosted/data/residual-isometries.json': '5864e4d680035401d53d32adab0369046d80b171', 'code/hub/e8-r715-whole-hosted/data/word.json.gz': 'f7d55b8bd45d385011ced25e632a3d922bb77bba', 'code/hub/e8-r740-replica32/code/bank_routes.py': '9e43a876664a26899762f3b8e9a582e684a3650a', 'code/hub/e8-r740-replica32/code/e8core.py': '78983b368715e89fe8524a6dd2c13585d2b5394e', 'code/hub/e8-r740-replica32/code/engines/base_two_moment.py': '14a90fa0e788217856f070382c9e61bd7c603c61', 'code/hub/e8-r740-replica32/code/engines/moment.py': '7d697cb45203fe72d97037403d6da41f71f3b7fd', 'code/hub/e8-r740-replica32/code/engines/outer.py': '43007488ad2c43187c77cc6798beff8b1cd76ad2', 'code/hub/e8-r740-replica32/code/tile_m.py': 'cd5fd9b5399f5e7afe5d2a95bd3504bd543c0d60', 'code/hub/e8-r740-replica32/data/residual-isometries.json': '9b8b35cb1528a978e209e1098864cae48c57fd93', 'code/hub/e8-r740-replica32/data/word.json.gz': '85390b07e4747feddbf2e16f94b5e0a8a308c191', 'code/hub/idle-axis-hosting/hosting_core.py': '68b536daa9e6546c0aa046934bf840aaa3c3fde3', 'code/hub/r740-hosted-eleven/code/emit.py': '5ff0de0d6f088ac95e25a2a7aed8653e8cd0333e', 'code/hub/r740-hosted-eleven/code/geometry.py': 'b4ad5074014dc00a01143910eb1cd27fafe0e15c', 'code/hub/r740-hosted-eleven/code/row_bound.py': '11d3c0d48e4ea5a02ac3b6689f3c7d36f2972eb8', 'code/hub/r740-hosted-eleven/data/selection.json': '8e548e5a9204a909d539ba36b866804b256d4c2b', 'code/hub/r740-hosted-rank149/code/emit.py': '5ff0de0d6f088ac95e25a2a7aed8653e8cd0333e', 'code/hub/r740-hosted-rank149/data/residual-isometries.json': 'ec8b4131d203d7a288ca078ca559f922d38fe9d2', 'code/hub/r740-hosted-rank149/data/selection.json': 'c57069f7385c3b6aff4fe3c73c0a21bae727c76f', 'code/hub/r740-hosted-rank149/data/word.json.gz': '3c8489a29f0de2cad7dafaddc340a1ff197d5172', 'code/nine/geometry.py': '91594e0223e8fac49162b5aef834ffaa8e94a254', 'code/pricing/base_two_moment.py': '14a90fa0e788217856f070382c9e61bd7c603c61', 'code/pricing/moment.py': '7d697cb45203fe72d97037403d6da41f71f3b7fd', 'code/pricing/outer.py': '43007488ad2c43187c77cc6798beff8b1cd76ad2', 'code/pricing/prime_witnesses.py': '7f16d930302ae879c562dd58e085d9747fcac077', 'code/provenance.py': '9bfcb106230e454d9405ce5eb42dd2218d905ea6', 'code/skeleton/e8.py': '92e83a2e0c1f67551f583630a728b2a880b06f51', 'code/skeleton/gen.py': '9811c127d41521e906462a75322a29f0e193629c', 'code/skeleton/geom.py': '9e5fe3a781dc52e07b7c5de3a44c8be6f5024cd4', 'code/skeleton/wordkit.py': '7cc4e6d618d9d0166efe8be75a019b6aecee0582', 'data/bit/bitE8-r865.json.gz': '8bec1751f7e33c3a1e4673ef5dbc34d6f205321e', 'data/bit/bitE8mut-r489.json.gz': 'ef67bec220c96a1de7b87c9f1a6e7acb26cb3284', 'data/complex-b.json': '0df48f8e590fc9ad01ca4d6eaf97b9acc10aac7d', 'data/complex/pr448/EXPECTED.json': '1574e6488b6fc59191ae49fcc0c089e48b196fbd', 'data/complex/pr458/EXPECTED.json': 'e06a17c177eee0e0962c96ea61554239ef38ef4d', 'data/complex/pr471/EXPECTED.json': 'ed1e72239ebebdbfad847fb817e5546f980c1d8d', 'data/complex/pr473/EXPECTED.json': '45ee9fde7fdf6b19b6303372068977201b4ef61c', 'data/complex/pr478/EXPECTED.json': '77f5805cd8125602e8c50f4eaba1691440c611c2', 'data/complex/pr483/EXPECTED.json': 'f7ff643cd54a334bf46c82989ba155eb6e69adde', 'data/complex/pr484/EXPECTED.json': '7f93fcbb9f1c2799fd86dd308ec1e6f0ad2a3264', 'data/eleven/hosting.json': '72b63ff0866db6aec50ecd356d7d007b17bf6475', 'data/eleven/residual-isometries.json': '5c645b267861fd0994d2679885f8e0bbf99640b0', 'data/skeleton/d4part-pairs.json': '7ea439877369b6c2e94bb47980d08944d61454fb', 'data/skeleton/plan-skB.json': '52e341f4f0b441ff88897162cc9f25eb72f34405', 'discovery/README.md': '751a9e82df9c860b496affd423b938cb008e2d88', 'discovery/d4part.py': 'ed7418a0800321d7629e86b4946f77e8cf60a044', 'discovery/host_select.py': '5b50de453ddbd90d433f9ea8ed584308e7ab2d0f', 'discovery/plan.py': '050a3ca42bad8b3d34d149607a7c67de39a52356', 'portable-include/bits/stdc++.h': 'fc5664e929d9a81d9b4926bee049a93330be86ec', 'requirements.txt': '05bdf190fff0fda4cf958441aa15b9d7a9239ad4', 'verify.sh': 'dd7df2a4445f5a8b0d5e336a855a930ab5d34bee'}
blobs=0
for path,blob in PINNED_BLOBS.items():
 raw=(PKG/path).read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob;blobs+=1
res=read(O/'RESULT.json');exp=read(PKG/'EXPECTED.json');g=read(O/'bit/GLOBAL.json');a=read(O/'bit/AUDIT.json');geo=read(O/'bit/GEOMETRY.json');t=read(O/'bit/GLOBAL-TEMPLATE.json.gz')
assert hashlib.sha256(json.dumps(read(O/'word.json.gz'),sort_keys=True,separators=(',',':')).encode()).hexdigest()==exp['word']['content_sha256']
assert hashlib.sha256(gzip.decompress((O/'bit/GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest()==g['template_sha256']==a['template_sha256']==res['bit_template_sha256']
assert g['emitted_program_sha256']==a['emitted_program_sha256']==res['emitted_program_sha256']==exp['eleven']['emitted_program_sha256']
p=Counter()
for call in t['calls']:
 for ins in t['local_programs'][call['orientation']]:
  if ins[0]==0 and ins[4]:p[ins[4]]+=1
  elif ins[0]==2:p[ins[5]]+=1
for histogram in t['hosting']['remainders'].values():
 for rank,count in histogram.items():
  if int(rank):p[int(rank)]+=count
summarized={int(k) for k in t['hosting']['remainders']}
for e in t['schedule']:
 if e['kind']=='idle' and e['rank'] and e['idx'] not in summarized:p[e['rank']]+=1920
assert {str(k):v for k,v in p.items()}==a['profile']==res['bit_profile']==exp['eleven']['profile']
m,W,T,L,V,K,H=78,9600,8,11,120,5,489;E=sum(p.values());physical=W+9;J=8*T*L*(2*V+H)+8*(2*K*V*T)+2*L*T*H+2*g['copy_erase_episodes']
parts={'local_dispatch':L*T*g['local_additions']+g['bridge_additions'],'high_routes':J*16*(m*m+1)**2,'route_stock':J*physical,'children':E*(8*m*m+8+128*(2*m)**3),'fixed':16*m**3+g['copy_erase_episodes'],'selectors':2*L*T*((W-1)+H*m*(geo['max_route_factors']+144+2+(m-1)+m)),'prefix':int(g['global_prefix_bound']),'one':1}
coefficient=sum(parts.values());level3=(coefficient+1)**3*(E+1)**3
assert coefficient.bit_length()==parts['prefix'].bit_length()==res['bit']['coefficient_bits']==2119
assert level3.bit_length()==res['bit']['three_level_coefficient_bits']==6411
assert 64*((6411+63)//64)==res['bit']['charged_three_level_coefficient_bits']==6464
physical_exp=0
while 3**physical_exp<=physical:physical_exp+=1
row=3*(m*(m+1)//2+physical_exp)+9909+252;assert row==res['bit']['row_coefficient']==19431<20161
eng=PKG/'code/hub/e8-r740-replica32/code/engines'
def load(name,path=None):
 s=importlib.util.spec_from_file_location('review_'+name,path or eng/(name+'.py'));x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
M,B,Outer=map(load,['moment','base_two_moment','outer'])
c=Q(res['bit_lower']);step=Q(1,10**24);fb=32*m*m*E;intervals={}
for endpoint in [c,c+step]:
 ml,mh=M.moment(p,m,W,endpoint,True);bl,bh=B.moment(m,W,list(p.items()),endpoint);fl,fh=B.moment(m,W,[(1,fb)],endpoint);bl+=fl/Q(10**16);bh+=fh/Q(10**16)
 assert (mh<1 and bh<1) if endpoint==c else (ml>1 and bl>1)
 intervals[str(endpoint)]={'mercator':[str(ml),str(mh)],'base_two':[str(bl),str(bh)]}
# Each outer result is arithmetic on its cited b; only471 has already been
# independently source-replayed in this session.
outer={}
def assembly(bit,b,allow,charge):
 eta=beta=grid=Q(1,10**18);s=min(bit,(1-beta)*b)-Q(1,10**24);chain=[Q(384599,10**10)];cutoffs=[]
 for _ in range(6):
  old=chain[-1];a=(1-s)*s+s*old;gap=min(s-a,1-a-s,1-a-s*(1-old),1-s);assert 0<gap and old<a<s;chain.append(a);cutoffs.append({'gap':str(gap),'cutoff_log2':str(max((36/gap**2).__ceil__(),(2*(4+charge)/gap).__ceil__()))})
 q=chain[-1]*(1-2*eta);margin=(1-eta)*q/(1+q);k=grid*(((margin/grid).numerator-1)//(margin/grid).denominator)
 bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},'rows':{'degree_gap':Q(10**6)-Q(51*allow,25)}}
 ar=Outer.assembly(chain[-1],b,bridge,k,eta=eta,beta=beta);assert len(ar['strict_constraints'])==47 and all(x>0 for x in ar['strict_constraints'].values())
 controls=[]
 for name,kk,ee,bb in [('next_grid',k+grid,eta,beta),('zero_eta',k,Q(0),beta),('zero_beta',k,eta,Q(0)),('unit_beta',k,eta,Q(1))]:
  try:Outer.assembly(chain[-1],b,bridge,kk,eta=ee,beta=bb)
  except AssertionError:controls.append(name)
  else:raise AssertionError(name)
 return {'kappa':str(k),'bootstrap':cutoffs,'outer_controls':controls,'slacks':{k:str(v) for k,v in ar['strict_constraints'].items()}}
for name,z in res['kappa'].items():
 b=Q(z['complex_lower']);result=assembly(c,b,20161,6464);assert result['kappa']==z['kappa'] and result['bootstrap']==z['bootstrap'] and result['outer_controls']==z['outer_controls'];outer[name]=result
report={'status':'PASS_INDEPENDENT_PR493_PINNED_SOURCE_INVOICE_AND_EXACT_ASSEMBLY','head':'c3a9a436b84fe44fdc223a5784d84736d1c2d3c7','manifest_sha256':sha(PKG/'MANIFEST.sha256'),'manifest_files':len(manifest),'git_blob_files':blobs,'result_sha256':sha(O/'RESULT.json'),'native_columns_sha256':sha(O/'cout/columns.json'),'native_eleven_columns_sha256':sha(O/'cout/columns_k5.json'),'bit_lower':str(c),'actual_bit_profile':dict(sorted(p.items())),'rank_mass':sum(k*v for k,v in p.items()),'paid_calls':E,'invoice_parts':{k:str(v) for k,v in parts.items()},'prefix_bits':2119,'charged_prefix_bits':2176,'three_level_coefficient_bits':6411,'charged_coefficient_bits':6464,'row_coefficient':row,'retained_row_allowance':20161,'exact_moment_intervals':intervals,'outer':outer,'scope':'This audit independently checks pinned sources and the supplied fresh bit output. Supplier verifier execution and native compiler provenance are bound by the enclosing root verifier. The complex b values here remain cited arithmetic; the enclosing composition must bind its chosen b to a fresh complex replay. PR448 remains information-only disputed split. Inherited all-size compiler, mutable-label, restored-row and analytic contracts remain conditional.'}
REPORT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['exact_moment_intervals','outer','invoice_parts','GL_sharp_screen']},indent=2))
