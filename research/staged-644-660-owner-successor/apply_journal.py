"""Apply the complete five-owner, 24-row journal to regenerated PR3605 owners.

Every proof-relevant payload byte is checked. Gzip headers and deflate streams
are permitted to vary. Source: this run's replay_A.py, with container equality
removed from admission, explicit journal predicates and targeted controls added.
"""
from pathlib import Path
import argparse,gzip,hashlib,json,re
ROWS=2717280
OLD_PAYLOAD='653085641ff2e9470e25aedfc92861ec34e5cf594d52123e8b28b6f0ec20b9f8'
NEW_PAYLOAD='d1ab78aaf268303bab0baca9a0aa3b607fbc9d49cba3e45d0634eca734ddd57c'
DELTA={'1':-4,'4':-1,'5':1,'6':-3,'7':3}
PROFILE={'1':16417892,'2':4835160,'3':1540174,'4':679320,'5':143993,'7':3,'8':53280,'48':283185}
MOVES={16544:[22,6,111],16545:[25,6,111],16546:[135,6,26],130613:[703,12,0],1355192:[18,15,111]}
def need(v,message):
 if not v:raise ValueError(message)
def sha(b):return hashlib.sha256(b).hexdigest()
def encode(row):return json.dumps(row,separators=(',',':')).encode('ascii')
def validate(j):
 entries=j['all_changed_rows'];need(len(entries)==24,'all24 changed rows required')
 edits={}
 for e in entries:
  i=e['index'];need(type(i)is int and 0<=i<ROWS,'valid literal row index');need(i not in edits,'duplicate literal row edit')
  need(all(len(e[k])==6 and all(type(v)is int and v>=0 for v in e[k]) for k in ('old','new')),'six nonnegative integer columns')
  need(e['old'][:2]==e['new'][:2]==[i//408,i%408],'call/helper identities unchanged')
  need(e['old']!=e['new'],'only actual changes journaled');edits[i]=e
 changed={i:e['new'][2:5] for i,e in edits.items() if e['old'][2:5]!=e['new'][2:5]}
 need(changed==MOVES,'exact five whole-owner destinations')
 need(sum(e['old'][5]!=e['new'][5] for e in entries)==21,'all21 offset changes')
 need(len(j['moves'])==5 and {e['index'] for e in j['moves']}==set(MOVES),'complete five-move explanation')
 for e in j['moves']:
  need(e['old']==edits[e['index']]['old'] and e['new'][:5]==edits[e['index']]['new'][:5],'move and full journal agree')
 need(j['delta']==DELTA and j['profile']==PROFILE,'complete declared delta and profile')
 need(sum(int(r)*n for r,n in DELTA.items())==0,'rank mass preserved')
 return edits

def apply_payload(payload,j):
 need(sha(payload)==OLD_PAYLOAD,'complete predecessor literal payload')
 edits=validate(j);prefix,body=payload.split(b',"rows":[',1)
 need(json.loads(prefix+b'}')==dict(columns=['time','helper','owner_replica','child','port','offset'],dispatch_overrides=[]),'literal predecessor schema')
 start=len(prefix)+len(b',"rows":[');parts=[];previous=0;found=set();count=0
 for i,match in enumerate(re.finditer(rb'\[\d+,\d+,\d+,\d+,\d+,\d+\]',body)):
  count+=1
  if i in edits:
   e=edits[i];need(match.group()==encode(e['old']),'exact changed-row preimage')
   absolute=start+match.start();parts.extend((payload[previous:absolute],encode(e['new'])));previous=start+match.end();found.add(i)
 need(count==ROWS and found==set(edits),'complete literal row and patch coverage');parts.append(payload[previous:]);result=b''.join(parts)
 need(sha(result)==NEW_PAYLOAD,'complete successor literal payload')
 return result

def controls(j):
 results=[]
 def reject(name,mutate,reason):
  changed=json.loads(json.dumps(j));mutate(changed)
  try:validate(changed)
  except ValueError as e:need(str(e)==reason,'wrong rejection '+name);results.append(name)
  else:raise ValueError('accepted defect '+name)
 reject('omitted offset edit',lambda x:x['all_changed_rows'].pop(),'all24 changed rows required')
 reject('duplicate edited identity',lambda x:x['all_changed_rows'].__setitem__(1,x['all_changed_rows'][0]),'duplicate literal row edit')
 reject('changed helper identity',lambda x:x['all_changed_rows'][0]['new'].__setitem__(1,407),'call/helper identities unchanged')
 reject('changed owner destination',lambda x:x['all_changed_rows'][0]['new'].__setitem__(2,739),'exact five whole-owner destinations')
 reject('omitted relay explanation',lambda x:x['moves'].pop(),'complete five-move explanation')
 reject('unpaid rank-one child',lambda x:x['profile'].__setitem__('1',x['profile']['1']+1),'complete declared delta and profile')
 return results

def replay(source,journal,out):
 need(not out.exists(),'fresh output required');j=json.loads(journal.read_bytes());payload=gzip.decompress(source.read_bytes());result=apply_payload(payload,j);checks=controls(j)
 # Equivalent container representation is a positive semantic control.
 alternate=gzip.compress(payload,compresslevel=1,mtime=12345)
 need(alternate!=source.read_bytes() and gzip.decompress(alternate)==payload,'alternate gzip has identical complete payload')
 out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('xb') as f,gzip.GzipFile(filename='',fileobj=f,mode='wb',compresslevel=1,mtime=0) as z:z.write(result)
 need(gzip.decompress(out.read_bytes())==result,'written complete successor payload')
 return dict(status='PASS_COMPLETE_SEMANTIC_SUCCESSOR_JOURNAL',rows=ROWS,changed_rows=24,moves=5,payload_sha256=sha(result),container_sha256=sha(out.read_bytes()),source_payload_sha256=sha(payload),controls=checks,equivalent_gzip_positive_control=True,scope='Exact complete literal transformation only; independent chronology/family/prefix/full invoice and complete release are separate obligations.')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--journal',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();print(json.dumps(replay(a.source,a.journal,a.out),sort_keys=True,indent=2))
if __name__=='__main__':main()
