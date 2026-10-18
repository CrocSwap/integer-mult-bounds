#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound finite premise replay plus explicit limits of the scalar checker."""
import copy,gzip,hashlib,importlib.util,json
from pathlib import Path
import argparse,sys
ap=argparse.ArgumentParser(description=__doc__)
for name in ('source','native-cache','native-receipt','predecessor','out'):ap.add_argument('--'+name,type=Path,required=True)
a=ap.parse_args();S=a.source.resolve();cache=a.native_cache.resolve();receipt_path=a.native_receipt.resolve();P=a.predecessor.resolve();OUT=a.out.resolve()
if OUT.exists() or OUT.is_symlink():raise RuntimeError('fresh output directory required')
if any(OUT.is_relative_to(p) or p.is_relative_to(OUT) for p in (S,cache,P)):raise RuntimeError('output must be disjoint from immutable inputs')
if any(p.is_symlink() for p in (a.source,a.native_cache,a.native_receipt,a.predecessor)):raise RuntimeError('input symlinks prohibited')
if sys.flags.optimize:raise RuntimeError('enabled assertions required by inherited checker')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def need(x,m):
 if not x:raise RuntimeError(m)
manifest=rd(S/'MANIFEST.json'); need(len(manifest)==549,'549 source files')
need(sha(S/'MANIFEST.json')=='44ed6a457e1d1ba24726f35db86dc9e551072dd9331a8fed3ad3f0efa33ff0be','P53 source pin')
actual={p.relative_to(S).as_posix():sha(p) for p in S.rglob('*') if p.is_file() and p.name!='MANIFEST.json'}
# Nested manifests are scientific source files too.
actual={p.relative_to(S).as_posix():sha(p) for p in S.rglob('*') if p.is_file() and p!=S/'MANIFEST.json'}
need(actual==manifest,'complete unchanged source inventory')
receipt=rd(receipt_path)
need(receipt['status']=='PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE' and receipt['manifest_sha256']==sha(S/'MANIFEST.json') and receipt['source_commit']=='pr2853-dirtentry4','native receipt exact source binding')
need({p.relative_to(cache).as_posix():sha(p) for p in cache.rglob('*') if p.is_file()}==receipt['cache_files'],'complete authenticated native cache')
path=P/'vendor/pr2839/blocknorm_certificate.py'
need(sha(path)=='e5bfbad8e8e6cb4206f7ba92d333780f423918d8f217b474302346169e991f92','exact P39 blocknorm checker')
spec=importlib.util.spec_from_file_location('reviewed_blocknorm',path);bn=importlib.util.module_from_spec(spec);spec.loader.exec_module(bn)
registry={};dirs={};details={}
for tag,rec in receipt['providers'].items():
 d=cache/rec['word_sha256']/'local';dirs[tag]=d;w=rd(d/'CANONICAL-WORD.json.gz')
 registry[tag]={'v':w['v'],'R':w['R'],'h':w['h'],'canonical_word_sha256':sha(d/'CANONICAL-WORD.json.gz'),'local_programs_sha256':sha(d/'LOCAL-PROGRAMS.json.gz'),'local_programs':rd(d/'LOCAL-PROGRAMS.json.gz'),'local_program_checks':rd(d/'LOCAL-CHECKS.json'),'exact_local_clifford_recipe_sha256':sha(d/'CLIFFORD-RECIPES.json'),'residual_adapter_sha256':sha(d/'RESIDUAL-ADAPTERS.json')}
 native_word=S/('new/borrow/words/BORROW-WORD-43'+tag+'.json.gz')
 need(sha(native_word)==rec['word_sha256'] and rd(d/'FULL-WORD.json.gz')==rd(native_word),'native literal P53 word')
 phases=rd(d/'CLIFFORD-REVIEW.json');wrappers=rd(d/'WRAPPER-CHECKS.json');replay=rd(d/'INDEPENDENT-LOCAL-REPLAY.json')
 need(phases['canonical_word_sha256']==registry[tag]['canonical_word_sha256'] and phases['warp_recipes_rank_zero'] and phases['warp_recipes_equal_exact_512_column_product'] and phases['all_child_equalities_include_global_phase'],'complete native phases')
 need(wrappers['status']=='PASS_RESIDUAL_WRAPPERS_ARE_EXACT','tensor wrappers')
 details[tag]={'full_word_sha256':rec['word_sha256'],'canonical_word_sha256':registry[tag]['canonical_word_sha256'],'local_programs_sha256':registry[tag]['local_programs_sha256'],'phase_recipe_sha256':registry[tag]['exact_local_clifford_recipe_sha256'],'phase_review_sha256':sha(d/'CLIFFORD-REVIEW.json'),'wrapper_check_sha256':sha(d/'WRAPPER-CHECKS.json'),'local_prefix':{o:replay['local'][o] for o in ('forward','backward')},'native_scalar_rejections':len(replay['negative_controls_rejected']),'wrapper_rejections':len(wrappers['wrappers_reject']),'exact_warp_classes':phases['warp_recipes'],'phase_checked_directed_edges':phases['directed_edges']}
endpoint,localbits=bn.certify_providers(registry,dirs);need(localbits==70,'actual max prefix70')
controls=[]
for tag,p in registry.items():
 for orientation in ('forward','backward'):
  events=p['local_programs'][orientation]
  mutations={
   'helper_to_data_leak':events+[['scalar',['add',['L',112],['L',224],1,1],1]],
   'uncleared_private_centre':events+[['scalar',['add',['C',0],['L',0],1,1],1]],
   'extra_formal_helper_warp':events+[['warp',['L',224],999,1,1]],
  }
  for name,changed in mutations.items():
   try:bn.replay_endpoint(changed,112,408,orientation=='backward')
   except AssertionError as e:controls.append({'provider':tag,'orientation':orientation,'mutation':name,'rejection':str(e)})
   else:raise RuntimeError('mutant accepted '+name)
# Deliberate scope discriminator: scalar checker ignores phase semantics; full native phases remain mandatory.
events=registry['base']['local_programs']['forward']
need(bn.replay_endpoint(events+[['phase','invalid_unchecked_phase_marker']],112,408,False)==endpoint['base']['forward'],'scope discriminator unexpectedly changed')
G=2**1296
for j in range(1,37):G*=2**(2*j)-1
Tmax=(2**20-490)//896;need(Tmax==1169,'exact admitted T cap')
geometry={}
for T in (1,248,Tmax,Tmax+1):
 physical=896*T+490;stockbits=(G*physical).bit_length();l2=(stockbits+1)//2
 actual=localbits+37+18+l2+1+4;reserve=128+37+18+l2+1+4;row=2*stockbits+9909+252+2*2048
 geometry[str(T)]={'physical':physical,'full_stock_bits':stockbits,'stock_l2_bits':l2,'actual_prefix':actual,'conservative_prefix':reserve,'payload':2048,'row':row,'physical_guard':physical<=2**20,'row_guard':row<20161,'reserve_guard':reserve<2048}
try:bn.full_stock_l2(896*(Tmax+1)+490)
except AssertionError as e:physical_reject=str(e)
else:raise RuntimeError('T1170 physical cap accepted')
result={'status':'PASS_SOURCE_BOUND_FINITE_BLOCKNORM_PREMISE_REVIEW','upstream_head':'d01045dfb67428679618027dff552f1d032fa999','blocknorm_contract_head':'c50d12e4720cd1fef2b5a65e337e37de9731879a','source_file_count':549,'blocknorm_checker_sha256':sha(path),'source_manifest_sha256':sha(S/'MANIFEST.json'),'native_receipt_sha256':sha(receipt_path),'reviewer_sha256':sha(Path(__file__)),'native_replay_scope':'Explicit authenticated native-cache reuse; independently re-executed exact free-warp endpoint checker here. This command does not run the native chains or a complete candidate admission.','endpoint_replay':endpoint,'providers':details,'rejected_controls':controls,'scalar_only_scope_discriminator':'Appending an invalid phase marker preserves replay_endpoint output: this checker alone is intentionally insufficient for unitary/phase correctness. Unchanged full native phases/wrappers and emitted owner/controller audits remain mandatory.','largest_T_under_unmodified_contract':Tmax,'geometry':geometry,'T1170_rejection':physical_reject,'proof_obligation':'Per completed owner block, donor helper factors are C_[w] tensor identity conjugated by exact monomial/within-family bijective charts. No helper-to-data or cross-owner output remains; local data shears and nine bridges are the only norm-growing steps. The separately retained generic hstep lemma then yields depth18.','conditional_limits':['Normalized recursive child/whole-call hosting and arbitrary-size compilation remain inherited assumptions.','Scalar endpoint replay does not establish normalization or unitarity by itself.','No fresh Lean kernel replay or new theorem beyond the inherited sufficient lemma is claimed.','T≤1169 is a cap for this fixed checker, not a constructive allocation existence theorem or a maximum over other contracts.']}
OUT.mkdir(parents=True)
(OUT/'BLOCKNORM-REVIEW.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({'status':result['status'],'max_T':Tmax,'geometry':geometry,'rejected_controls':len(controls),'scalar_only_discriminator':True},indent=2))
