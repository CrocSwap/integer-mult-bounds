from pathlib import Path
import json,hashlib,shutil
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015');A=R/'research/community-efficient1900-audit'
data={
2876:('Arham Tahir: common signed block-scale scan, finite-format admissibility and exact Boolean gate invoice.', ['Reviewed unsigned absolute-value handling including the most-negative input, OR leading-bit reduction and literal all-width invoice. Sharing one scale across all pairs/factors follows the pinned line contract; per-pair scaling is invalid.', 'All declared normal/optimized and artifact checks passed:309494 signed cases,313 wide fixtures,258 full small-line comparisons and rejection controls. Three exports Git-authenticated. Physical movement, fan-out, exponent lifetime, workspace and recursive admission remain unpriced.']),
2893:('Arham Tahir: complete integral optimal face of the fixed T185 packing relaxation.', ['Reviewed elimination of nine inventory equations on eleven exactly tight patterns. Attainment iff5 divides positive T; count(21T+1)^2 is of pattern multiplicity vectors, not physical owner schedules.', 'Independent positive-binomial directed intervals certify all1163 patterns and strict non-tight slack>1/250 over the pinned root interval. All11236 T5 vectors,200 rounded witnesses and controls replayed normally and optimized. Five exports authenticated; no new physical T5 construction or supplier admission.']),
2895:('Sagar Thakrar: conditional retained-array catch-up law and specified final-record route pricing.', ['Reviewed cut-rank lower bound and matching median-level construction for independent record/partner subspaces. Storage at a fixed frame is uncharged by this moment; physical storage remains outside the model.', 'Source-pinned timeline/hosting,34454 exact finite record-partner cases,4044 general cases, independent all16-replica height replay and2432 independent frame cases pass. Route rejection requires the explicit observation, unproved per-cut rank/uncompressed delivery, no-slack, timing and capture premises. Theorem B remains an unreviewed external conditional input; changing the contract can evade these conclusions.']),
2903:('Nick Petalas: source-bound QQ16 numerical-contract navigation, attribution and incomplete caller bill.', ['Reviewed numerical composition and unit distinctions: relative Hilbert error, finite component width, Boolean gates and physical costs. Both registered binding/control checks passed after hydrating six link-existence targets omitted from the isolated setup; original failed setup retained.', 'Five incorporated predecessor heads and two pending scan snapshots authenticated. The historical checkpoint labels PR2876 pending; current incorporation is in the maintainer ledger. Author-recorded predecessor primary replays are not fresh maintainer full-suite replays. No supplier admission.']),
2904:('digitalis-p: bounded dirty-entry and fixed-word frame-refit screens, with explicit enumeration limits.', ['All three declared source-bound parts passed on the pinned PR2833/2857/2894 words, including positive quartet calibration, exact bilinear relay test and defect controls. Ten original word/notice exports authenticated.', 'Additional direct-position enlargement checks98 nonzero-first-frame helpers on each PR2857 and PR2894 base word: identical exact response spans and no accepted target. It does not complete arbitrary-position relay or extra-word coverage. Integration explicitly narrows the README to enumerated positions and floating threshold refit screens; author cold replay/full relaxed census remain separately labelled historical evidence.']),
2918:('Ross Richardson: rank-seven helper408 boundary obstruction and fully charged optimistic comparison.', ['Reviewed scalar forbidden-input diagonal minor of determinant-1/4 and independent inverse restriction I11. Either excludes the required row/column pairing for arbitrary allowed rational basis changes at the fixed middle/entrance/terminal support.', 'Both exact operator implementations and the complete666-call hypothetical budget passed;16 exports authenticated. The rank-eight construction supplies positive compensation/cleanup controls. The favorable rank-seven bill is unrealizable in this boundary model, not a new primitive or general obstruction.'])}
ready=json.loads((P/'ready-scopes.json').read_text());assert not set(map(str,data))&set(ready)
for n,(scope,notes) in data.items():
 meta=json.loads((P/f'{n}.json').read_text());c=json.loads((P/f'check-{n}.json').read_text());assert c['head']==meta['headRefOid'] and c['status']=='passed' and len(c['commands'])==c['commands_expected'] and not c['changed_files_after'];assert all(x['exit_code']==0 and x['stop_reason'] is None for x in c['commands']);assert hashlib.sha256((P/f'check-{n}.log').read_bytes()).hexdigest()==c['log_sha256']
 finding=dict(number=n,reviewed_head=meta['headRefOid'],status='ready_with_documented_scope',scope=scope,review=notes,source_authentication=[f.name for f in sorted(P.glob(f'provenance-{n}-*.json'))],execution=f'check-{n}.json',limits='Scoped proof, finite replay or navigation only. No new selected kappa or full supplier/multiplication theorem verification.')
 (P/f'finding-{n}.json').write_text(json.dumps(finding,indent=2)+'\n');ready[str(n)]=scope
# Retain the original documentation and clarify the actual executable scope without changing the scientific code or receipts.
rel='research/t185-dirty-entry-frame-screens/README.md';src=P/'sources/2904'/rel;original=A/'originals/2904'/rel;original.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,original)
s=src.read_text();needle='## Scope and limits\n\n';assert needle in s
note='''**Maintainer scope clarification (round 1900).** The direct screen enumerates
insertion indices from the receiver timeline and q0 event indices. The relay
screen enumerates its second insertion from the receiver timeline. The words
"any program position" above describe the intended search domain; completeness
of those reduced candidate sets for arbitrary literal insertion times is not
proved here. The retained negative result is for the executable candidate sets.
A maintainer enlargement to all relevant receiver/q0/partner transition
boundaries found identical exact direct-response spans for all 98 eligible
nonzero-first-frame helpers on each PR2857 and PR2894 **base** word. This does
not establish arbitrary-position relay completeness or repeat that enlargement
on the extra providers. Single-gate refits use the listed endpoint/neighbour
frames; cascades stop when more than 400 gate overrides are required. Refit
cost decisions use floating arithmetic and the `-1e-12` reporting threshold;
they are screens, not exact global frame-optimality certificates. The complete
registered three-part replay passed; the separately recorded predecessor cold
replay and full frame-relaxed census are author evidence, not newly repeated
maintainer executions. These qualifications do not change the pinned source
words, executed code or original numerical receipts.

'''
s=s.replace(needle,needle+note);dst=P/'resolutions/2904'/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(s)
plan=json.loads((P/'resolution-plan.json').read_text());assert not any(x['number']==2904 for x in plan);plan.append(dict(number=2904,path=rel,resolved_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),resolved_mode='100644',reason='Clarify enumerated chronological positions, scope of the maintainer direct-position supplement, float/threshold/cascade limits and author-only historical replays. Original README retained; scientific code and receipts unchanged.'));(P/'resolution-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
(P/'ready-scopes.json').write_text(json.dumps(ready,indent=2)+'\n');(P/'ready.json').write_text(json.dumps(sorted(map(int,ready)),indent=2)+'\n')
holds={'2883':{'scope':'Metadata and source/model review completed; full census not run after observing CPU-wide multiprocessing and large table materialization.','question':'Supply or review a bounded-memory/concurrency replay plan. model.py materializes736281 length-seven even-subset tables then starts Pool(os.cpu_count()); the queued full run was held before execution. No census failure or mathematical rejection is inferred.'}}
(P/'review-holds.json').write_text(json.dumps(holds,indent=2)+'\n')
(P/'finding-2883.json').write_text(json.dumps(dict(number=2883,reviewed_head=json.loads((P/'2883.json').read_text())['headRefOid'],status='runtime_plan_required',**holds['2883']),indent=2)+'\n')
f=R/'CONTRIBUTORS.md';s=f.read_text();needle='- Maintainer integration by Douglas Colkitt with OpenAI Codex assistance adds native macOS process-observer replays';assert needle in s
lines='''- **Arham Tahir / Arham-Tahir64** — [#2876](https://github.com/CrocSwap/integer-mult-bounds/pull/2876), common QQ16 block-scale scan and Boolean invoice; [#2893](https://github.com/CrocSwap/integer-mult-bounds/pull/2893), all-replica integral optimal-face classification for Dugongue's T185 packing model.
- **Sagar Thakrar / thakrarsagar** — [#2895](https://github.com/CrocSwap/integer-mult-bounds/pull/2895), conditional retained-array catch-up and final-record route pricing, retaining Andrey Mas's transport model, ctoth's coverage, Philippe Van Velzen's contracts and the QQ16 lineage.
- **Nick Petalas / petalas** — [#2903](https://github.com/CrocSwap/integer-mult-bounds/pull/2903), source-bound numerical-contract map connecting the QQ16 error, line, finite-format, pair-circuit and block-scan results.
- **digitalis-p** — [#2904](https://github.com/CrocSwap/integer-mult-bounds/pull/2904), bounded dirty-entry and frame-refit screens, with the enumerated-position and numerical-screen limits recorded in the integration review.
- **Ross Richardson / RossRichardson** — [#2918](https://github.com/CrocSwap/integer-mult-bounds/pull/2918), rank-seven helper408 boundary obstruction, independent exact replay and the fully charged optimistic budget; builds on Jeremy Diviney's paired extraction and Jeremy Kothe's source words.
- These numerical and packing contributions retain Nick Petalas, ywz65, Ali Romman, Dugongue, Yiyang/Lyy-iiis, Jeremy Kothe, Jeremy Diviney, Marius-Paul Dumitrean, Philippe Van Velzen, Tekalign and the package-specific native, owner and compiler lineage. Full attribution remains in the source notices.
'''
f.write_text(s.replace(needle,lines+needle))
f=P/'build_report.py';s=f.read_text();s=s.replace("'register_structural_group.py']","'register_structural_group.py','prepare_numerical_inputs.py','run_numerical_group.py','authenticate_numerical_exports.py','run_navigation_followup.py','diagnose_2904_positions.py','run_position_diagnostic.py','position-audit-2904-*.json','register_numerical_group.py','review-holds.json']")
s=s.replace("rows=[]","holds=json.loads((P/'review-holds.json').read_text()) if (P/'review-holds.json').exists() else {}\nrows=[]")
s=s.replace(" rows.append(dict(number=n", " if str(n) in holds and not accepted:question=holds[str(n)]['question'];scope=holds[str(n)]['scope']\n rows.append(dict(number=n")
f.write_text(s)
f=P/'integrate_plain.py';s=f.read_text();s=s.replace("or (n==2760", "or (n==2903 and all(f['path'].startswith('research/qq16-numerical-contract-navigation/') or f['path'] in ['docs/research/bottleneck-brief.md','docs/research/qq16-controller-scope-map.md','docs/research/qq16-numerical-contract-map.md'] for f in pk['files'])) or (n==2760");f.write_text(s)
f=P/'finish_checkpoint.py';s=f.read_text().replace('Record twenty-six merged PRs and remaining round nineteen obligations','Record thirty-two merged PRs and remaining round nineteen obligations');s=s.replace("'premerge-2878-2920.json']:","'premerge-2878-2920.json','premerge-2876-2918.json']:");f.write_text(s)
print('Registered six; one resource hold; retained exact scope clarification.')
