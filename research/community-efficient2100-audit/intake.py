from pathlib import Path
import ast,json,hashlib,subprocess,collections,time
P=Path('/tmp/pr-efficient2100');R=Path('/tmp/integer-mult-efficient1100-20261015')
selection=json.loads((P/'selection.json').read_text());ledger=json.loads((R/'docs/research/pr-ledger.json').read_text());prior={x['number']:x for x in ledger['pull_requests']};candidates=set(json.loads((P/'candidates.json').read_text()));blocked={1876: 'Inherited broad-shift sign errors and disabled check need separate correction/admission.', 1930: 'Claimed scalar-XOR bill counts output rows rather than actual map evaluation; repair bill.', 2134: 'Omitted legal source-count profiles invalidate stated full census scope.', 2215: 'Only-hostable-gain claim exceeds time-capped receiver coverage; narrow scope.', 2216: 'Checked arbitrary-payload counterexamples to literal native invoice; repair typed adaptation.', 2249: 'Twelve-singleton witness contradicts W>=16 in enlarged readout model.', 2477: 'Exact LF/CRLF-only policy counterexample; repair line grammar.'}
reader=subprocess.Popen(['git','cat-file','--batch'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE);seen={};rows=[]
def blob(oid):
 reader.stdin.write((oid+'\n').encode());reader.stdin.flush();header=reader.stdout.readline().split();assert len(header)==3 and header[1]==b'blob';size=int(header[2]);assert size<256*1024*1024
 raw=reader.stdout.read(size);assert len(raw)==size and reader.stdout.read(1)==b'\n';assert hashlib.sha1(b'blob '+str(size).encode()+b'\0'+raw).hexdigest()==oid;return raw
for x in selection['prs']:
 n=x['number'];pk=json.loads((P/'packets'/f'{n}.json').read_text());remaining=prior.get(n,{}).get('unresolved_question') or 'Full substantive review remains open.';row=dict(number=n,head=pk['head'],remaining=remaining,status='held_shared_or_existing_paths',errors=[],paths=sorted({'/'.join(f['path'].split('/')[:2]) for f in pk['files']}))
 if n in blocked:row.update(status='held_known_correctness',reason=blocked[n])
 elif n in candidates:
  collisions=[f['path'] for f in pk['files'] if f['path'] in seen and seen[f['path']]!=f['source']['oid']]
  if collisions:row.update(status='held_conflicting_archive_versions',collisions=collisions)
  else:
   files={f['path']:blob(f['source']['oid']) for f in pk['files']};syntax=collections.Counter();pins=[]
   for name,raw in files.items():
    try:
     if name.endswith('.py'):ast.parse(raw,filename=name);syntax['python']+=1
     elif name.endswith('.json'):json.loads(raw,parse_int=str);syntax['json']+=1
    except (ValueError,SyntaxError,UnicodeDecodeError) as e:row['errors'].append(dict(path=name,check='syntax',error=str(e)))
   for root in row['paths']:
    name=root+'/MANIFEST.json'
    if name not in files:continue
    obj=json.loads(files[name]);checked=0;outside=0
    if isinstance(obj,dict):
     for rel,h in obj.items():
      if not isinstance(h,str) or len(h)!=64 or not all(c in '0123456789abcdef' for c in h):continue
      if Path(rel).is_absolute() or '..' in Path(rel).parts:row['errors'].append(dict(path=rel,check='unsafe_manifest_path'));continue
      key=root+'/'+rel
      if key not in files:outside+=1;continue
      checked+=1
      if hashlib.sha256(files[key]).hexdigest()!=h:row['errors'].append(dict(path=key,check='manifest_sha256'))
    pins.append(dict(path=name,local_pins_checked=checked,outside_changed_files=outside))
   row.update(status='archive_ready' if not row['errors'] else 'held_intake_errors',syntax=dict(syntax),manifests=pins,files={k:dict(sha256=hashlib.sha256(v).hexdigest(),bytes=len(v)) for k,v in files.items()})
   if not row['errors']:
    for f in pk['files']:seen[f['path']]=f['source']['oid']
 rows.append(row)
reader.stdin.close();assert reader.wait()==0
(P/'INTAKE.json').write_text(json.dumps(dict(baseline=selection['baseline'],scope='Source-only archival integrity intake; no submitted code executed or claims validated.',pull_requests=rows),indent=2)+'\n')
print(dict(collections.Counter(x['status'] for x in rows)))
for x in rows:
 if x['errors']:print(x['number'],x['errors'][:3])
print('READY',[x['number'] for x in rows if x['status']=='archive_ready'])
