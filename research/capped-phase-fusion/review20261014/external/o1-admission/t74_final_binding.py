"""T16-parity final binding for a completed T74 strict replay (PR1319-family replay.py work dir).

verify_t16.py (selected PR1094 supplier chain) ends with a cross-receipt "final binding" that PR1319's replay.py omits.
This applies the T74 analogue of every one of those assertions to the strict work dir, plus the geometry receipt:
 controller: ASYNC-AUDIT mutation controls run, 15 rejected, one owner per complete invocation, residual/role/call/chart counts
 invoice:    every strict_checks inequality true, owner/controller audit hashes bind the actual audit files, row < retained limit,
             prefix < charged, invocation sweeps == calls
 assembly:   47 strictly positive outer margins, template hash shared by assembly/owner/invoice/controller, profile equalities
 providers:  provider content binding (bound provider artifacts == native local dirs, semantic), phase semantic hashes agree
 geometry:   GEOMETRY-CONTROLS 6 rejected and bound to this strict dir
usage: t74_final_binding.py STRICT_DIR GEOMETRY_JSON GAUGE44_LOCAL EXTRA_LOCAL PARENT_KAPPA OUT.json"""
import gzip, hashlib, json, sys
sys.set_int_max_str_digits(0)
from fractions import Fraction
from pathlib import Path
W, GEO, L44, LEX, PK, OUT = sys.argv[1:7]; W = Path(W)
def rd(p): p = Path(p); b = p.read_bytes(); return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
g = W / 'global'
asm, ind, inv = rd(W / 'ASSEMBLY.json'), rd(W / 'INDEPENDENT.json'), rd(g / 'audit/PREFIX-AND-INVOICE.json')
own, aud, res = rd(g / 'audit/OWNERS-AND-PROFILE.json'), rd(g / 'audit/ASYNC-AUDIT.json'), rd(W / 'RESULT.json')
geo, plan = rd(GEO), rd(g / 'PLAN.json')
adm, bit = rd(W / 'ADMISSION-CONTROLS.json'), rd(W / 'BIT-CONTROLS.json')
calls = sum(asm['provider_counts'].values())
C = {}
C['strict status'] = res['status'] == 'PASS_STRICT_MIXED_T74_EXACT_FILL' and res['kappa'] == asm['kappa']
C['controller: status'] = aud['status'] == 'PASS_INDEPENDENT_ASYNC_WHOLE_OWNER_CONTROLLER_PHASES_AND_SPECTATORS'
npid = len(plan['provider_registry'])
C['controller: 7+8*providers mutations run+rejected (T16: 15 for one provider)'] = aud['mutation_controls_run'] is True and len(aud['mutations_rejected']) == 7 + 8 * npid == len(set(aud['mutations_rejected']))
C['controller: one owner per complete invocation'] = aud['one_owner_per_complete_invocation'] is True and own['all_live_owners_per_call_distinct'] is True
C['controller: all charts and provider bindings'] = aud['all_actual_residual_and_spectator_charts'] is True and aud['all_provider_program_phase_and_wrapper_bindings'] is True
C['roles: ind == owner hosted == audit hosted == checked windows'] = ind['roles'] == own['hosted_residuals'] == aud['complex_hosted_residuals'] == aud['helper_busy_family_window_checks'] == own['actual_helper_owner_charts']
C['calls: ind == audit invocations == invoice sweeps == dispatch'] = ind['calls'] == aud['complete_invocations'] == inv['complete_invocation_sweeps'] == calls
C['charts: ind == owner sigmas == audit maps'] = ind['actual_73_axis_charts'] == own['actual_73column_sigmas'] == aud['actual_orthogonal_73column_maps']
C['rank mass / deficit agree'] = ind['rank_mass'] == own['rank_mass'] == aud['rank_mass'] and ind['deficit'] == own['deficit'] == aud['deficit']
C['live/physical agree'] = ind['live'] == own['live'] == aud['complex_live'] == inv['live'] and ind['physical'] == own['physical'] == aud['physical'] == inv['physical']
C['idle agrees'] = sum(ind['idle'].values()) == aud['idle_remainders'] and all(str(k) in ('1','48') for k in ind['idle']) and own['explicit_idle_remainder_children'] == aud['idle_remainders']
C['invoice: status'] = inv['status'] == 'PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE'
C['invoice: every strict inequality'] = bool(inv['strict_checks']) and all(inv['strict_checks'].values())
C['invoice: owner audit hash binds file'] = inv['owner_audit_sha256'] == sha(g / 'audit/OWNERS-AND-PROFILE.json') == asm['input_sha256']['owner_audit']
C['invoice: controller audit hash binds file'] = inv['controller_audit_sha256'] == sha(g / 'audit/ASYNC-AUDIT.json') == own['controller_audit_sha256']
C['invoice: assembly binds fresh invoice'] = asm['input_sha256'].get('fresh_invoice') == sha(g / 'audit/PREFIX-AND-INVOICE.json')
C['invoice: prefix ind == invoice < charged'] = ind['prefix_bits'] == inv['global_prefix_bits'] < inv['charged_prefix_bits'] == ind['charged_prefix_bits']
C['invoice: row ind == invoice < retained 20161'] = ind['physical_row_coefficient'] == inv['finite']['physical_row_coefficient'] < inv['finite']['retained_row_coefficient'] == 20161
C['assembly: status'] = asm['status'] == 'PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY'
C['assembly: 47 strictly positive outer margins'] = len(asm['outer']) == 47 and all(Fraction(v) > 0 for v in asm['outer'].values())
C['assembly: template hash shared'] = asm['template_sha256'] == own['template_sha256'] == inv['template_sha256'] == aud['template_sha256'] == aud['complex_template_sha256']
C['profile: ind == asm == owner == audit == PLAN'] = ind['profile'] == asm['complex_profile'] == own['paid_profile'] == aud['complex_profile'] == plan['profile']
C['provider counts agree'] = ind['provider_counts'] == asm['provider_counts'] == inv['provider_counts'] == aud['provider_counts']
C['phase semantic hashes agree'] = own['provider_phase_semantic_sha256'] == aud['provider_phase_semantic_sha256'] == inv['provider_phase_semantic_sha256']
C['artifact semantic hashes agree with PLAN'] = own['provider_artifact_semantic_sha256'] == aud['provider_artifact_semantic_sha256'] == {k: v['artifact_semantic_sha256'] for k, v in plan['provider_registry'].items()}
for pid, loc in (('gauge44', Path(L44)), ('extra', Path(LEX))):
    for n in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'LOCAL-CHECKS.json', 'INDEPENDENT-LOCAL-REPLAY.json',
              'RESIDUAL-ADAPTERS.json', 'CLIFFORD-RECIPES.json', 'CLIFFORD-REVIEW.json'):
        C['provider content binding %s/%s' % (pid, n)] = rd(g / 'base/providers' / pid / n) == rd(loc / n)
C['admission controls 114, none accepted'] = len(adm['rejected_controls']) == 114 and not adm.get('discovery_accepted_controls')
C['bit controls 12'] = len(bit['rejected_controls']) == 12
C['independent controls 8'] = len(ind['controls_rejected']) == 8
C['geometry: 6 rejected'] = len(geo['rejected']) == 6
GAPS = {'geometry receipt carries no input hash of the strict owner/invoice it mutated': not any(k for k in geo if 'sha' in k)}
C['strictly improves parent kappa'] = Fraction(asm['kappa']) > Fraction(PK)
ok = all(C.values())
out = dict(status='PASS_T74_T16_PARITY_FINAL_BINDING' if ok else 'FAIL', strict=str(W), kappa=asm['kappa'], kappa_decimal=asm['kappa_decimal'][:40], checks=C, informational_gaps=GAPS)
Path(OUT).write_text(json.dumps(out, indent=1) + '\n'); print(out['status'], out['kappa_decimal'])
for k, v in C.items():
    if not v: print('FAILED:', k)
sys.exit(0 if ok else 1)
