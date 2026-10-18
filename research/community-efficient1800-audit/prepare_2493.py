from pathlib import Path
import json,subprocess,shutil,hashlib
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'combined-2493';S=P/'sources/2493';assert not D.exists()
shutil.copytree(P/'combined-2505',D,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc'))
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
names=set(subprocess.check_output(['git','ls-tree','-r','--name-only',head],cwd=R,text=True).splitlines())
paths=sorted(({f.relative_to(D).as_posix() for f in D.rglob('*') if f.is_file()} & names) | {x for x in names if x.startswith(('scripts/','tests/')) or (x.startswith('research/') and x.endswith('/VERIFY.json'))} | {'README.md'})
p=subprocess.Popen(['git','cat-file','--batch'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
for rel in paths:
 p.stdin.write((head+':'+rel+'\n').encode());p.stdin.flush();h=p.stdout.readline().split();assert len(h)==3 and h[1]==b'blob';b=p.stdout.read(int(h[2]));assert p.stdout.read(1)==b'\n';f=D/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
p.stdin.close();assert p.wait()==0
for rel in ['research/overlap-discussion-batching','tests/test_research_discussion_batching.py']:
 if (S/rel).is_dir():shutil.copytree(S/rel,D/rel)
 else:shutil.copy2(S/rel,D/rel)
f=D/'tests/test_research_discussion_batching.py';t=f.read_text();t=t.replace('len(board.calls), 2, "small threads must share the two listing requests"','len(board.calls), 6, "51 small threads share six ten-thread listing requests"');f.write_text(t)
f=D/'research/overlap-discussion-batching/README.md';t=f.read_text();note='''## Maintainer integration, 2026-10-16

The original PR #2493 implemented 50/5/5 initial page sizes. Main already
incorporates the same batching mechanism from Nick Petalas's #2514 with
10/25/10 initial page sizes. Integration retains that current implementation,
including later PR-file pagination and query handling, and adds Arham Garg's
six independent pagination/cache controls. The 51-small-thread request test
therefore expects six listing requests; complete ordered records are unchanged.
The original tests and implementation are retained at PR head
`a459ee34fad0488691beba8441e0a31e103b91a5` and in the review archive.

All benchmark numbers and the original validation/integration narrative below
are historical author evidence for the original 50/5/5 implementation, not
fresh measurements of main's 10/25/10 implementation. The opt-in benchmark
records the code actually run and must write a new output; keep BENCHMARK.json
and its source/fixture pins unchanged. The integration does not modify the
shared overlap helper or onboarding test, so it introduces no further drift
in either older package named below. Their historical pin failures are not
reported as successful replays. Current maintainer execution is recorded in
`research/community-efficient1800-audit/checks/check-2493.json`.

''';t=t.replace('\n\n','\n\n'+note,1);f.write_text(t)
f=D/'README.md';t=f.read_text();anchor='## Historical audited checkpoint: 527 reused sources';assert anchor in t
addition='''### Overlap checks

The overlap helper searches open PRs, Discussions, and local research notes.
Discussion listings batch initial comments and replies, then exhaust every
continuation page. The [batching evidence and integration note](research/overlap-discussion-batching/README.md)
retain Arham Garg's independent coverage controls and historical benchmark,
alongside the current implementation from Nick Petalas's #2514.
Reports state coverage and freshness; no matches does not establish novelty.

```sh
python3 scripts/find_overlap.py --task joint-query-controller --refresh
```

''';f.write_text(t.replace(anchor,addition+anchor))
# Authenticated objects are available for metadata verification without copying repository history.
subprocess.run(['git','init','-q',str(D)],check=True)
objects=subprocess.check_output(['git','rev-parse','--git-path','objects'],cwd=R,text=True).strip();objects=str((R/objects).resolve())
(D/'.git/objects/info/alternates').write_text(objects+'\n');subprocess.run(['git','add','.'],cwd=D,check=True)
manifest=json.loads((S/'research/overlap-discussion-batching/SOURCES.json').read_text());pins=[]
for row in manifest['files']:
 raw=subprocess.check_output(['git','show',manifest['base_commit']+':'+row['path']],cwd=R);blob=subprocess.check_output(['git','rev-parse',manifest['base_commit']+':'+row['path']],cwd=R,text=True).strip();assert blob==row['git_blob'] and hashlib.sha256(raw).hexdigest()==row['sha256'];pins.append(row)
b=json.loads((S/'research/overlap-discussion-batching/BENCHMARK.json').read_text());assert b['after_sha256']==hashlib.sha256((S/'scripts/find_overlap.py').read_bytes()).hexdigest();assert b['fixture_sha256']==hashlib.sha256((S/'research/overlap-discussion-batching/FIXTURE.json').read_bytes()).hexdigest()
(P/'provenance-2493.json').write_text(json.dumps(dict(status='PASS',base=head,refreshed_files=len(paths),historical_source_pins=pins,benchmark_source_and_fixture_authenticated=True,scope='Historical benchmark provenance only; no fresh timing claim. Current helper and onboarding retained byte-for-byte; no additional historical-pin drift.'),indent=2)+'\n')
print('Prepared',D,len(paths))
