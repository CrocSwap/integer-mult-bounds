from pathlib import Path
import json, hashlib, shutil
P=Path('/tmp/pr-efficient1900'); R=Path('/tmp/integer-mult-efficient1100-20261015'); A=R/'research/community-efficient1900-audit'
scopes={
2874:'Ross Richardson: exact identity-aware retained backing at packet prefix-return cuts, including erased arrays and cross-pass aliases. Written source proof, 130 native/interface cuts and 5,184 independent fixture cuts; not whole-loop or physical memory.',
2877:'Arham Tahir: exact logical traffic for the PR2753 linear sign, including countdown setup/disposal. Written canonical-input bound below 2048V, 387 countdowns and 150 signs; not physical compilation or a supplier admission.',
2882:'Hiroki KUMAZAKI/kumagi: full named-array packet-loop backing envelope and phase-aware private-action composition. Source proof, 99 runtime fixtures and independent arithmetic census; borrowed backing must remain fixed throughout the action.',
2888:'James Reed/jwr404: lcm row stock fits the existing wrapper and fourteen selected numerical guards. Exact arithmetic and predecessor contracts checked; integration clarifies zero depth and the required atom width/cutoff. Callee, root and physical obligations remain open.',
2902:'Nick Petalas: exact native ADD/swap/sign private payload backing, with pending results and cleared arrays retained. 60 source fixtures, 22 origin planes and defect controls; restricted payload composition only, not total private storage.',
2905:'Nick Petalas: exact native ADD Counter backing, constructor overlap and conditional callback phase composition. 63 source fixtures and 162 independent write-observed cases; cleared but captured callback tapes falsify the release premise.',
2912:'Nick Petalas: exact operand-order-sensitive Count.product backing and an extent-preparation upper bound. 4,099 products, 58 preparations and six complete ADD fixtures; encoded index width matters. No complete private-storage or allocator claim.',
2916:'Nick Petalas: joins extent/countdown backing at actual ADD phase boundaries with released-callback allowance. 70 complete fixtures, wrong-result/underbudget controls and module-restoration checks; other storage owners and physical reuse remain unpriced.'}
notes={
2874:['Return-cut maximum is K+(2N+1)F+4+D+3Q for native distinct results and at least two passes. First-pass source/current alias is counted once.', 'Reviewed literal packet engine, retained local/changed bindings and Consumer preflight. Independent interface fixtures are not selected GL64 execution.'],
2877:['Countdown invoice is 15n+14d-5 popcount(n)+36 for n>0 and 14d+40 for n=0. Source loop multiplicities and the conservative uniform bound were reviewed.', 'Padded countdown mutation changes total traffic while preserving source movement and endpoints. This is logical operation accounting, not a physical tape price.'],
2882:['Whole-loop maximum is K+(2N+1)F+4+D+2Q+max(Q,F); the copy and prefix peaks occur at different phases.', 'Private-array composition requires borrowed identities and lengths fixed throughout. The growing-then-restored borrowed-array counterexample correctly defeats an endpoint-only premise. Independent arithmetic census is not an additional runtime replay.'],
2888:['The all-width stock inequality is valid. Its strict intermediate chain requires D>=1; handle D=0 separately with log_q S=0.', 'The conclusion k<e/2 additionally requires the fit lemma atom choice w=ceil(e^s), e>=2^L and its exponent-gap hypotheses. Integration states these explicitly rather than treating w,e as independent at this step.', 'Checked predecessor selected-bit-ceiling-free-stock fit argument and selected-bootstrap-reserve-composition stage contracts. Fourteen selected guards were replayed; no predecessor executable or physical implementation is thereby admitted.'],
2902:['Reviewed source lifetimes for incoming/final translate arrays, bucket arrays and pending returned results. Weak observers do not retain dead payloads.', 'A_payload is only a subset of total A. Counter, numerical, program and callback owners remain separate; scoped composition does not combine maxima from incompatible phases.'],
2905:['Exact intrinsic peak p+r+m+max(m,r+2s*[S>1]) follows source loop and old/new constructor overlap.', 'The max(C,H) composition is conditional on callback release and no captured native frames. Successful cleared-but-retained counterexample invalidates composition without release.'],
2912:['Exact product peak A+B+C+6+max(0,A+2-v2(b)) was reviewed against product/add source; operand order matters.', 'Layout.extents bound S+max(I+2,3W+9) is an upper bound, returned cohort is exact. Padding the index gives a real preparation peak of 267 versus 21 despite identical returned marginals.', 'Unchanged AST definitions are used for the relevant geometry and ADD path; unrelated compiler branches are not covered. No claim of strict typed JSON receipt checking is made here.'],
2916:['The joined bound K+max(E,R+max(C,H)) follows actual two-bank Layout/action chronology; E is an upper bound rather than necessarily attained.', 'Exact execution witnesses distinguish phase max from additive maxima and show captured erased callback tapes remain live. Complete source permutations and all nine origin planes of the smallest fibre were checked.']}
for n,scope in scopes.items():
 meta=json.loads((P/f'{n}.json').read_text()); check=json.loads((P/f'check-{n}.json').read_text()); assert check['status']=='passed' and check['head']==meta['headRefOid']
 evidence=[f.name for f in sorted(P.glob(f'provenance-{n}-*.json'))]
 finding={'number':n,'reviewed_head':meta['headRefOid'],'status':'ready_with_documented_scope','scope':scope,'review':notes[n], 'source_authentication':evidence,'execution':f'check-{n}.json','limits':'No new selected kappa, full supplier replay, formal theorem audit, Python heap/physical tape memory bound or physical allocation proof. Declared finite tests and written scoped arguments are distinct evidence.'}
 (P/f'finding-{n}.json').write_text(json.dumps(finding,indent=2)+'\n')
# Preserve the original README separately; no source archive or executable is changed.
rel='research/selected-lcm-stock-wrapper-fit/README.md'; src=P/'sources/2888'/rel
orig=A/'originals/2888'/rel; orig.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,orig)
s=src.read_text(); old='numeric hypotheses of Josie Elliston\'s repair-(b) fit lemma at this `ell`, so\nthat lemma gives `k<e/2`.'
new='numeric hypotheses of Josie Elliston\'s repair-(b) fit lemma at this `ell`.\nFor each branch/stage, this application uses its recorded exponent `s`,\natom width `w=ceil(e^s)`, and coarse width `e>=2^L` at the recorded cutoff.\nUnder these hypotheses, that lemma gives `k<e/2`; this fit conclusion is not\na statement for independently chosen arbitrary `w` and `e`.'
assert old in s; s=s.replace(old,new)
old='`m * 2^(17/28) < e`. Combined with the strict packet logarithm, '
assert old.rstrip() in s
s=s.replace('`m * 2^(17/28) < e`. Combined with the strict packet logarithm,','`m * 2^(17/28) < e`. If `D(e)=0`, then `S=1` and `log_q S=0`,\nwhich is strictly below `6748 w (1+log2 e)` for every admitted `w,e`.\nFor `D(e)>=1`, combine the depth estimate with the strict packet logarithm:')
old='the numeric hypotheses of the cited fit lemma. The lemma itself,'
new='the numeric hypotheses of the cited fit lemma, applied with the atom-width\nand cutoff conditions above. See the predecessor\n[ceiling-free stock fit argument](../selected-bit-ceiling-free-stock/README.md).\nThe lemma itself,'
assert old in s; s=s.replace(old,new)
dst=P/'resolutions/2888'/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(s)
plan=json.loads((P/'resolution-plan.json').read_text()); assert not any(x['number']==2888 for x in plan)
plan.append({'number':2888,'path':rel,'resolved_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'resolved_mode':'100644','reason':'Clarify the separate D=0 proof case and the required w=ceil(e^s), e>=2^L hypotheses for borrowing fit. Original README retained in originals/2888 and author history; executable checks and numerical results unchanged.'})
(P/'resolution-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
ready=json.loads((P/'ready-scopes.json').read_text());ready.update({str(n):s for n,s in scopes.items()});(P/'ready-scopes.json').write_text(json.dumps(ready,indent=2)+'\n');(P/'ready.json').write_text(json.dumps(sorted(map(int,ready)),indent=2)+'\n')
f=R/'CONTRIBUTORS.md';s=f.read_text(); needle='- Maintainer integration by Douglas Colkitt with OpenAI Codex assistance adds native macOS process-observer replays, preserves current historical routes and authenticates the exact runner successor.'
insert='''- **Ross Richardson / RossRichardson** — [#2874](https://github.com/CrocSwap/integer-mult-bounds/pull/2874), retained packet backing at common prefix-return cuts.
- **Hiroki KUMAZAKI / kumagi** — [#2882](https://github.com/CrocSwap/integer-mult-bounds/pull/2882), whole-loop packet backing and conditional private-action composition, extending Ross Richardson's return-cut result.
- **Arham Tahir / Arham-Tahir64** — [#2877](https://github.com/CrocSwap/integer-mult-bounds/pull/2877), complete logical traffic for David Arias's linear sign, including counter setup and disposal.
- **James Reed / jwr404** — [#2888](https://github.com/CrocSwap/integer-mult-bounds/pull/2888), lcm stock, wrapper padding and fourteen fit guards; builds on David Arias, Nick Petalas, Adam Gall, Josie Elliston, Aakash, DreamingOfClouds, eumemic, Rohan Arun and Jeremy Kothe.
- **Nick Petalas / petalas** — [#2902](https://github.com/CrocSwap/integer-mult-bounds/pull/2902), native private payload backing; [#2905](https://github.com/CrocSwap/integer-mult-bounds/pull/2905), ADD countdown backing; [#2912](https://github.com/CrocSwap/integer-mult-bounds/pull/2912), extent/count preparation; [#2916](https://github.com/CrocSwap/integer-mult-bounds/pull/2916), joined ADD count phases.
- The storage and traffic contributions retain Jose Manuel/jmbarrancoml's PR2697 runtime lineage, David Arias's PR2753 caller/sign, starship-s's nonblank accounting, ywz65's primitive audit, and the preceding Ross Richardson, kumagi and Nick Petalas interfaces. Full source-specific credit remains in each package.
'''
assert needle in s;s=s.replace(needle,insert+needle+' Maintainer review also clarifies the zero-depth and atom-width premises in #2888; the original text remains archived.');f.write_text(s)
# Retain replay drivers; evidence remains the exact runs already completed.
f=P/'build_report.py';s=f.read_text();needle="'hydrate_2906.py']";assert needle in s;s=s.replace(needle,"'hydrate_2906.py','extract_native_group.py','prepare_native_inputs.py','run_native_group.py','run_native_traffic_stock.py','authenticate_native_exports.py','register_native_group.py']");f.write_text(s)
print('Registered eight reviewed contributions and two stock-proof clarifications; no checks rerun.')
