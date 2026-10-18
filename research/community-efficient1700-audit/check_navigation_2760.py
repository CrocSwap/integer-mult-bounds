from pathlib import Path
import json,re,subprocess,hashlib,time,math
P=Path('/tmp/pr-efficient1700');R=Path('/tmp/integer-mult-efficient1100-20261015');start=time.monotonic();n=2760
packet=json.loads((P/'packets/2760.json').read_text());tree=P/'sources/2760';inputs={};external=[];relative=[]
def blob(head,rel):return subprocess.check_output(['git','show',head+':'+rel],cwd=R)
for f in packet['files']:
 rel=f['path'];raw=(tree/rel).read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==f['source']['oid'];inputs[rel]=hashlib.sha256(raw).hexdigest();s=raw.decode()
 for head,path in re.findall(r'https://github.com/CrocSwap/integer-mult-bounds/blob/([0-9a-f]{40})/([^\s)#]+)',s):
  data=blob(head,path);external.append({'head':head,'path':path,'sha256':hashlib.sha256(data).hexdigest()})
 for link in re.findall(r'\]\(([^\s)]+)\)',s):
  if '://' in link or link.startswith('#'):continue
  path=str((Path(rel).parent/link.split('#')[0]));parts=[]
  for bit in Path(path).parts:
   if bit=='..':parts.pop()
   elif bit!='.':parts.append(bit)
  path='/'.join(parts)
  if path not in inputs and not (tree/path).is_file():blob('HEAD',path)
  relative.append({'source':rel,'target':path})
# Nine named component source heads, with declared standard-library replay manifests.
scientific=re.findall(r'https://github.com/CrocSwap/integer-mult-bounds/blob/([0-9a-f]{40})/([^\s)#]+)',(tree/'docs/research/selected-bit-caller-storage-map.md').read_text())
assert len(scientific)==9
manifests=[]
for head,rel in scientific:
 path=str(Path(rel).parent/'VERIFY.json');raw=blob(head,path);m=json.loads(raw);assert m['python']=='3.12' and not m.get('requirements');manifests.append({'head':head,'path':path,'sha256':hashlib.sha256(raw).hexdigest(),'commands':len(m['commands'])})
assert math.lcm(28416,28425)==269241600 and 269241600//28416==9475
q='query {repository(owner:"CrocSwap",name:"integer-mult-bounds") {'+' '.join('p'+str(i)+':pullRequest(number:'+str(i)+'){number author{login ... on User{name}}}' for i in [2688,2697,2708,2731,2743,2749,2753,2758,2759])+'}}'
authors=json.loads(subprocess.check_output(['gh','api','graphql','-f','query='+q],text=True))['data']['repository']
assert {i:authors['p'+str(i)]['author']['login'] for i in [2688,2697,2708,2731,2743,2749,2753,2758,2759]}=={2688:'ywz65',2697:'jmbarrancoml',2708:'petalas',2731:'starship-s',2743:'petalas',2749:'petalas',2753:'DavidAriasC',2758:'petalas',2759:'petalas'},authors
log=json.dumps({'immutable_links':external,'relative_links':relative,'replay_manifests':manifests,'authors':authors,'arithmetic':'lcm stock and quotient exact','scope':'Navigation/source identity and replay-route checks. Parametric claims compared to cited source statements; no new proof or historical replay claimed.'},indent=2)+'\n';(P/'check-2760.log').write_text(log)
d={'number':n,'head':packet['head'],'status':'passed','seconds':time.monotonic()-start,'commands':[{'argv':['python3','/tmp/pr-efficient1700/check_2760.py'],'exit_code':0,'checks':'All changed blobs, immutable source links, relative targets, nine declared replay routes, cited authors and stock arithmetic.'}],'input_sha256':inputs,'changed_files_after':{},'log_sha256':hashlib.sha256(log.encode()).hexdigest(),'scope':'Documentation navigation only; author replay reports remain historical evidence. No supplier admission.'};(P/'check-2760.json').write_text(json.dumps(d,indent=2)+'\n');print('PASS',len(external),'immutable links',len(relative),'relative links',len(manifests),'replay routes')
