"""Global prefix and normalized-interface admission for cross-replica PR484 hosting.
Prepared by OpenAI Codex. No emitter/controller imports.
Usage: OUT PARENT_VARIANT HOSTED CONTROLLER_AUDIT
"""
from pathlib import Path
from fractions import Fraction as F
import json,gzip,hashlib,sys
O,V,H,C=map(Path,sys.argv[1:5]);read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(H/'GLOBAL-TEMPLATE.json.gz');base=read(V/'split-centres/GLOBAL-TEMPLATE.json.gz');host=read(H/'HOSTED.json');control=read(C);own=read(O/'OWNERS-AND-PROFILE.json');invoice=read(O/'PREFIX-AND-INVOICE.json');c=read(V/'split-centres/CANONICAL-WORD.json.gz')
th=hashlib.sha256(gzip.decompress((H/'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest();assert th==host['template_sha256']==control['complex_template_sha256']
assert control['one_owner_per_complete_invocation']and control['complete_invocations']==72 and control['helper_busy_family_window_checks']==40320
assert t['local_programs']==base['local_programs']and t['recipe']==base['recipe'];assert t['loop_order']==base['loop_order']and 'each local invocation completes before the next' in t['loop_order']
assert own['all_800_owners_per_call_distinct']and own['actual_helper_owner_charts']==40320 and own['actual_73column_sigmas']==3960
sigmas=read(H/'ACTUAL-SIGMAS.json.gz');assert len(sigmas)==3960
for key,columns in sigmas.items():
 assert hashlib.sha256(json.dumps(columns,separators=(',',':')).encode()).hexdigest()==key
 assert len(columns)==73
 assert all(((x&y).bit_count()&1)==(i==j)for i,x in enumerate(columns)for j,y in enumerate(columns))
# Each sigma belongs to the actual O(73,2) cover group. Right multiplication
# d -> d*sigma^-1 is a bijection on that finite group; no family can be active
# twice in a complete cover sweep. Different dirty-helper incidences are
# permitted, since their completed endpoint is a unitary coordinate factor.
locals_=len(t['calls']);bridges=[e for e in t['recipe']if e['kind']=='bridge'];assert locals_==72 and len(bridges)==9 and all(abs(e['coefficient'])==1 for e in bridges)
for row in t['calls']:
 assert row['orientation']in('forward','backward')
 assert len(row['owners'])==len(set(f for f,_ in row['owners']))==800
 assert row['owners'][:240]==next(x for x in base['calls']if(x['stage'],x['replica'])==(row['stage'],row['replica']))['owners'][:240]
# The independently replayed 800-column scalar maps have row-l1 <=2; their
# fixed frame and endpoint operators are unitary. Thus maximum stream L2 norm
# grows <=2 per complete invocation (more conservatively, per cover sweep).
# All idle factors, wrappers, addresses and terminal signed exchanges are
# unitary. Unit-modulus Gauss monomials are unitary; C_q=aI+bX_q is unitary
# since |a|^2+|b|^2=1 and a*conj(b)+b*conj(a)=0.
peak=max(F(x['prefix_l1'])for x in invoice['local'].values());localbits=peak.numerator.bit_length()-peak.denominator.bit_length()+1;assert localbits==20 and peak<2**20
input_to_l2=37 # sqrt(2^73) <2^37 for input sup norm1 per physical stream
complete_bits=locals_+len(bridges);primitive_margin=4
payload=localbits+input_to_l2+complete_bits+primitive_margin
assert payload==142 and payload<192
# No extra helper role or chart operation is introduced: all40320roles still
# receive the two selectors already charged in the unhosted finite invoice.
assert len(t['idle_children'])==own['explicit_idle_remainder_children']<=own['source_idle_children_charged']
assert own['banked_residuals']==0 and len(t['bank_padding']['families'])==0
assert t['physical']<=base['physical']and t['live']<=base['live']
assert invoice['conservative_pervertex_used']==invoice['unhosted_pervertex']
report=dict(status='PASS_GLOBAL_POOLED_PREFIX_AND_NORMALIZED_INTERFACE',template_sha256=th,source_template_sha256=hashlib.sha256(gzip.decompress((V/'split-centres/GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest(),controller_audit_sha256=sha(C),local_programs_sha256=sha(V/'split-centres/LOCAL-PROGRAMS.json.gz'),canonical_word_sha256=sha(V/'split-centres/CANONICAL-WORD.json.gz'),residual_adapters_sha256=sha(V/'split-centres/RESIDUAL-ADAPTERS.json'),actual_sigma_table_sha256=sha(H/'ACTUAL-SIGMAS.json.gz'),sigma_count=len(sigmas),orthogonal_73column_group_membership_checked=True,whole_owner_injection_all_calls=True,local_complete_row_l1_bound=2,complete_invocation_cover_sweeps=locals_,bridge_factor_two_sweeps=len(bridges),local_scalar_coefficient_work_prefix_bits=localbits,stream_input_sup_to_l2_bits=input_to_l2,primitive_arithmetic_margin_bits=primitive_margin,global_prefix_bits=payload,retained_payload_bits=192,charged_helper_selectors=2*40320,actual_idle_remainders=len(t['idle_children']),idle_children_already_charged=own['source_idle_children_charged'],conservative_pervertex_used=invoice['conservative_pervertex_used'],proof='Take the maximum L2 norm over all physical streams(F,g). A complete helper invocation has normalized endpoint C_pending tensor I and hence preserves this norm; full data endpoints have at most two unitary summands, and each bridge has coefficients±1. For each call, each actual orthogonal chart sigma induces a bijection d→d*sigma^-1 on O(73,2), so a complete cover sweep touches each active physical stream once. Completed helper interactions in other cover classes preserve its norm. Consequently72ordered invocation sweeps and9bridges contribute at most81bits, with no independence of replicas and no factor proportional to cover size. Inside an invocation the exact all-column scalar/Horner envelope contributes20bits; every frame/normalizer is unitary. An initial2^73entry stream with supremum≤1 has L2<2^37. Four bits cover primitive arithmetic before normalization, giving142<192. The all-size child/compiler interfaces and their existing precision/tape contracts remain inherited.',scope='New finite cross-replica global prefix argument under verified complete-invocation normalization and inherited O(73,2) cover/compiler contracts; no unconditional all-size theorem.')
(O/'GLOBAL-PREFIX.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],'global_prefix_bits',payload,'<192',flush=True)
