from pathlib import Path
import json
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015')
f=R/'AGENTS.md';s=f.read_text();needle='Before reviewing an existing PR' # place before frozen-evidence rule
anchor='Keep `upstream/`, frozen source archives and pinned evidence unchanged.'
assert anchor in s
s=s.replace(anchor,'For maintainer PR intake, consult [research archive status](docs/research/research-archive-intake.md).\nA merged research package can remain **partially reviewed**: archival acceptance\ndoes not endorse its mathematical claims, stored PASS receipts or proposed κ.\nCheck the central ledger and exact-head review scope before building on it.\n\n'+anchor,1);f.write_text(s)
f=R/'CONTRIBUTING.md';s=f.read_text();anchor='This is a research draft.';assert anchor in s
s=s.replace(anchor,'Maintainers distinguish **archival intake** from **validated incorporation**.\nNew isolated research packages may be merged after source/integrity intake while\nremaining `partially_reviewed` in the ledger, with the unverified obligations\npreserved. Such a merge retains the contribution; it does not verify a theorem,\ncertify a new κ, or change the selected result. Shared-code changes and known\ncorrectness objections remain in substantive review. See the\n[archive policy and exact-head index](docs/research/research-archive-intake.md).\n\n'+anchor,1);f.write_text(s)
f=P/'build_report.py';s=f.read_text();s=s.replace("holds=json.loads", "archives=json.loads((P/'archive-intake.json').read_text()) if (P/'archive-intake.json').exists() else {}\nholds=json.loads",1)
anchor='for row in rows:\n c=closed.get'
assert anchor in s
s=s.replace(anchor,"""for row in rows:
 archive=archives.get(str(row['number']))
 if archive:
  published=row['github_state']=='MERGED'
  row.update(disposition='partially_reviewed',scope=archive['scope'],unresolved_question=archive['remaining'],review_completion=dict(changed_file_coverage=True,scoped_mechanism_review=False,required_execution_complete=False,published=published))
  if published:row['closure']['kind']='merged_for_archive_only'
  row['verification_evidence']=list(dict.fromkeys(row['verification_evidence']+['research/community-efficient1900-audit/checks/check-archive-intake.json']))
for row in rows:
 c=closed.get""",1)
s=s.replace("merged=sum(x['disposition']=='incorporated' for x in rows);", "archived=sum(x['github_state']=='MERGED' and str(x['number']) in archives for x in rows);merged=sum(x['github_state']=='MERGED' for x in rows);")
s=s.replace('ready=len(ready),merged=merged,', 'ready=len(ready),merged=merged,archived_partially_reviewed=archived,')
s=s.replace("'## Reviewed contributions'", "'## Integrated contributions and archive admissions'")
s=s.replace("The selected conditional κ is unchanged. Attribution", "Of the merged submissions, {archived} are archival admissions only and remain partially reviewed, with mathematical and replay obligations open. The selected conditional κ is unchanged. Attribution")
# This paragraph is a plain string in the legacy generator; make the inserted count literal via concatenation.
s=s.replace("'Of the merged submissions, {archived}", "f'Of the merged submissions, {archived}")
s=s.replace("'run_lines_review.py','resolve_lines_review.py','register_lines_review.py']", "'run_lines_review.py','resolve_lines_review.py','register_lines_review.py','archive_intake.py','configure_archive_intake.py','register_archive_intake.py','archive-intake.json','live-open-eighth-refresh.json']")
anchor="(A/'METRICS.json').write_text(json.dumps(metrics,indent=2)+'\\n')"
assert anchor in s
s=s.replace(anchor,anchor+"\nif archives:\n (A/'ARCHIVE-INTAKE.json').write_text(json.dumps(archives,indent=2)+'\\n')")
f.write_text(s);compile(s,str(f),'exec')
f=P/'integrate_plain.py';s=f.read_text();anchor='# These author-original whitespace bytes are preserved;';assert anchor in s
s=s.replace(anchor,"""archives=json.load(open(P/'archive-intake.json')) if (P/'archive-intake.json').exists() else {}
for n in ns:
 if str(n) in archives:
  whitespace_excludes.extend(':(exclude)'+p+'/**' for p in archives[str(n)]['paths'])
"""+anchor,1)
s=s.replace("'Integrate reviewed research PRs '","'Integrate research contributions '")
s=s.replace('Exact-head finite checks and claim limits are recorded','Exact-head review tiers, source-only archival admissions, finite checks where performed, and open obligations are recorded')
f.write_text(s);compile(s,str(f),'exec')
print('Configured archive-aware reporting; scientific acceptance flags stay false.')
