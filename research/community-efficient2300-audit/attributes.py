from pathlib import Path
import json,subprocess,hashlib,re
P=Path('/tmp/pr-efficient2300');R=Path('/tmp/integer-mult-efficient1100-20261015')
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
intake=json.loads((P/'INTAKE.json').read_text());chosen=[x for x in intake['pull_requests'] if x['status']=='archive_ready'];diffs={x['number']:x for x in json.loads((P/'ATTRIBUTE-DIFFS.json').read_text())};base=git('show','HEAD:.gitattributes');new=base;rules=[];originals={}
all_research={f['path'] for x in chosen for f in json.loads((P/'packets'/f'{x['number']}.json').read_text())['files'] if f['path'].startswith('research/')}
all_research.update(git('ls-tree','-r','--name-only','HEAD','--','research').decode().splitlines())
for x in chosen:
 n=x['number'];pk=json.loads((P/'packets'/f'{n}.json').read_text());f=next((f for f in pk['files'] if f['path']=='.gitattributes'),None)
 if not f:continue
 d=diffs[n];assert not d['drops'];raw=git('cat-file','blob',f['source']['oid']);originals[str(n)]=dict(blob=f['source']['oid'],sha256=hashlib.sha256(raw).hexdigest(),added_rules=d['adds'])
 out=P/'original-attributes'/f'{n}.gitattributes';out.parent.mkdir(exist_ok=True);out.write_bytes(raw)
 research=[f['path'] for f in pk['files'] if f['path'].startswith('research/')]
 for line in d['adds']:
  if not line.strip() or line.startswith('#'):continue
  fields=line.split();pattern=fields[0];assert re.fullmatch(r'research/[A-Za-z0-9_.-]+/(?:[A-Za-z0-9_.-]+/)*\*\*',pattern),pattern
  prefix=pattern[:-2];assert any(name.startswith(prefix) for name in all_research),(n,pattern)
  assert fields[1:] in (['-text','-whitespace'],['-text'],['whitespace=cr-at-eol']),(n,line)
  if line not in new.decode().splitlines():
   if not new.endswith(b'\n'):new+=b'\n'
   new+=line.encode()+b'\n';rules.append(line)
(P/'resolved.gitattributes').write_bytes(new)
receipt=dict(scope='Explicit integration resolution: preserve current attributes and append only reviewed additive research-package rules. Original author root attribute files retained separately; no scientific source bytes changed.',baseline_sha256=hashlib.sha256(base).hexdigest(),resolved_sha256=hashlib.sha256(new).hexdigest(),added_rules=rules,originals=originals)
(P/'ATTRIBUTE-RESOLUTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Validated',len(originals),'author attribute deltas;',len(rules),'new narrow rules.')
