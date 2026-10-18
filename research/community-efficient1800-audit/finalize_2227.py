from pathlib import Path
import json,hashlib,subprocess,shutil,importlib.util,sys
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'sources/2227';H=D/'research/complex-compensation-network';A=R/'research/community-efficient1800-audit';sha=lambda b:hashlib.sha256(b).hexdigest()
pk=json.loads((P/'packets/2227.json').read_text());c=json.loads((P/'check-2227.json').read_text());b=json.loads((P/'check-2227-benchmark.json').read_text());fresh=json.loads((P/'benchmark-2227-fresh.json').read_text());old=json.loads((H/'BENCHMARKS.json').read_text());assert c['status']==b['status']=='passed' and not c['changed_files_after'] and not b['changed_files_after'] and len(c['commands'])==4
assert fresh['benchmark_source_sha256']==sha((H/'benchmark.py').read_bytes())!=old['benchmark_source_sha256'];assert fresh['candidate_word_payload_sha256']==old['candidate_word_payload_sha256'];assert all(c['input_sha256'][x['path']]==sha((D/x['path']).read_bytes()) for x in pk['files'])
for key in ['rounds','repetitions','bits']:assert fresh[key]==old[key]
sys.path.insert(0,str(R/'scripts'));spec=importlib.util.spec_from_file_location('metadata',R/'scripts/research_package.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.validate(D,'research/complex-compensation-network')
readme=H/'README.md';original=readme.read_bytes();text=original.decode();needle='## Sources, novelty and limits';assert needle in text
note='''## Maintainer timing provenance and independent replay

The maintainer replayed all four declared verification commands, including
complete native emission/frame checks, the 22 integer-dyadic programs,
relocation/corruption controls and all seventeen published-routine trials.
All declared upstream inputs match their pinned Git blobs and current main.
This validates the scoped finite construction, not a new supplier or κ.

The original `BENCHMARKS.json` is preserved verbatim. Its recorded benchmark
source hash (`32dad02a…`) does **not** match the submitted `benchmark.py`
(`a46bd2cd…`), and the exact older script was not located in the published
PR history. Its timing provenance is therefore not authenticated against the
submitted script. The maintainer did not rewrite that historical source hash.

[MAINTAINER-BENCHMARK.json](MAINTAINER-BENCHMARK.json) records a fresh run of
that exact submitted script with the same 1,024-bit workload, eleven alternating
rounds and five repetitions. Every endpoint was checked on every run. Median
ratios were 2.36–2.39 under Horner and 2.68–2.69 under copy/unit lowering.
These are environment-specific scalar interpreter measurements; they exclude
recursive children, frame operators, compiler work and integer multiplication.
Optional search-nomination timings and optimality were not independently checked.

Maintainer review and provenance clarification: Douglas Colkitt with OpenAI
Codex assistance. Original construction and predecessor credit remain above
and below; this is not an independent human or proof-assistant review.

'''
readme.write_text(text.replace(needle,note+needle));(H/'MAINTAINER-BENCHMARK.json').write_bytes((P/'benchmark-2227-fresh.json').read_bytes());m.validate(D,'research/complex-compensation-network')
# Keep complete primary execution receipt, add a separate reviewed composition receipt.
for suffix in ['json','log']:(P/f'check-2227.{suffix}').rename(P/f'check-2227-full.{suffix}')
finding=dict(status='passed',head=pk['head'],changed_author_files=len(pk['files']),registered_metadata='Current research_package.validate passed, including pinned task-card identity and all Git-source/current-input hashes.',mathematical_review=['Restored PCH^-1 compensation charges preparation and inverse restoration and exactly recovers arbitrary-input compensation.','Two-sided LMR=S cleanup is checked on the complete rational operator, including inverse-transpose chronology.','Native emission matches the independently spliced full stream; unchanged native auditor verifies frames/wrappers and paid profile.','Separate integer-dyadic engine checks 22 programs on all 713 columns, restores 480 helpers, erases nine private inputs and matches exact counts/prefix bounds.','Forest comparator is an author reimplementation, not a method optimum. Authentic published PR1119 routines reproduce all 17 trials and selected literal operator.'],limitations=['Unchanged 3494-child recursive profile and selected kappa.','No full physical Clifford/phase compilation, global invoice or supplier admission.','Optional discovery search timings not rerun; no optimality claimed.','Original benchmark receipt source mismatch documented, unchanged historical data retained, fresh full benchmark separately bound.'],credit='conorholds with substantial OpenAI Codex assistance; all extensive predecessor attribution retained.',receipts=['check-2227-full.json','check-2227-benchmark.json'],source_provenance='provenance-2227-current-inputs.json')
(P/'finding-2227-review.json').write_text(json.dumps(finding,indent=2)+'\n')
inputs={x['path']:sha((D/x['path']).read_bytes()) for x in pk['files']};inputs['research/complex-compensation-network/MAINTAINER-BENCHMARK.json']=sha((H/'MAINTAINER-BENCHMARK.json').read_bytes());log=(json.dumps(finding,indent=2)+'\n').encode();(P/'check-2227.log').write_bytes(log);(P/'check-2227.json').write_text(json.dumps(dict(number=2227,head=pk['head'],status='passed',seconds=0,commands=[],commands_expected=0,input_sha256=inputs,changed_files_after={},log_sha256=sha(log),scope='Composition receipt: full original source-bound verification retained in check-2227-full; only README provenance clarification and independently generated timing receipt added. Scientific code and original mathematical receipts unchanged.'),indent=2)+'\n')
plan=json.loads((P/'resolution-plan.json').read_text());assert not any(x['number']==2227 for x in plan)
for rel,prior in [('research/complex-compensation-network/README.md',original),('research/complex-compensation-network/MAINTAINER-BENCHMARK.json',b'')]:
 f=P/'resolutions/2227'/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes((D/rel).read_bytes());plan.append(dict(number=2227,path=rel,original_sha256=sha(prior),resolved_sha256=sha(f.read_bytes()),resolved_mode='100644',reason='Preserve original author timing receipt while explicitly documenting its source-hash mismatch and retaining a fresh full same-parameter benchmark bound to submitted source. No scientific code, recipe, count or kappa changed.'))
f=P/'prior-revisions/2227-original/research/complex-compensation-network/README.md';f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(original);(P/'resolution-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
holds=json.loads((P/'extra-holds.json').read_text());holds.pop('2227',None);(P/'extra-holds.json').write_text(json.dumps(holds,indent=2)+'\n');f=P/'scopes.txt';lines=[l for l in f.read_text().splitlines() if not l.startswith('2227|')];lines.append("2227|conorholds' fully restored nonforest R480 compensation and two-sided cleanup: all four declared native/arithmetic/relocation/17-trial comparison commands pass. All 713 columns in 22 scalar programs checked, full paid recursive profile unchanged. Panel saves 4858 Horner primitives versus author's same-input forest implementation; original method/predecessor credit retained. Historical timing source mismatch explicitly disclosed; fresh same-parameter matched scalar benchmark separately bound. No new kappa, method optimum, complete supplier or multiplication-speed claim.");f.write_text('\n'.join(lines)+'\n')
for name in ['prepare_2227.py','run_2227.py','run_2227_benchmark.py','finalize_2227.py']:shutil.copy2(P/name,A/name)
print('Complete review registered with two explicit provenance/timing resolutions')
