"""Fresh explicit role/replica bank-address replay for the fixed p10 candidate."""
from pathlib import Path
import sys
CODE=Path(__file__).resolve().parent
sys.path.insert(0,str(CODE.parent))
import support
CLOSURE=support.OUTPUT/'closure'
sys.path.insert(0,str(CODE.parent/'closure'))
from collections import Counter,defaultdict
from fractions import Fraction
import gzip,hashlib,json,struct
from source_contract import SOURCE,HEAD,verify_inputs
ROOT=support.out('certificates','placeholder').parent
BRIDGE=support.OUTPUT/'weighted'
WORD=support.OUTPUT/'matching/word_weighted892.json'
WORD_SHA='25a0edc8c5f399fcf536b28c4e3575aa52177bb78b6078a631acb748954f0739'

def read(name):
 raw=(SOURCE/name).read_bytes();return json.loads(gzip.decompress(raw)if name.endswith('.gz')else raw)
def run(case="weighted19"):
 assert case in("weighted19","15")
 verify_inputs();cp=BRIDGE/'rebound-candidate19.json'if case=='weighted19'else support.HERE/'witnesses/candidate15.json';c=json.loads(cp.read_text());price_path=support.OUTPUT/'arithmetic'/('provisional892-candidate19-pricing.json'if case=='weighted19'else'candidate15-pricing.json');price=json.loads(price_path.read_text())
 assert case=='15'or(hashlib.sha256(WORD.read_bytes()).hexdigest()==WORD_SHA and c['overlay_sha256']==WORD_SHA)
 w=json.loads(WORD.read_text())if case=='weighted19'else read('bitword/selected/bit/word_p10.json.gz');profile=read('bitword/selected/bit/profile_p10.json');R=profile['R'];v=profile['v'];h=profile['h'];assert(R,v,h)==(9120,960,20)
 removed={b for a,b in w['pairs']};regs=sorted(set(range(R))-removed);physical={r:2*v+i for i,r in enumerate(regs)};inverse={s:r for r,s in physical.items()}
 sinks=read('sink-selection.json')['sinks'];sunk={r['role']for r in sinks};roles=sorted(set(regs)-sunk)
 entrance={r:0 for r in roles};endpoint={r:h for r in roles}
 for row in w['gauges']:
  if row['role']in entrance:entrance[row['role']]=row['dim']
 kernel=read('kernel-selection.json')
 for row in kernel['pairs']+kernel['families']:
  r=inverse[row.get('pivot',row.get('a'))];assert entrance[r]==0;entrance[r]=row['rank']
 for row in read('restore-selection.json')['entries']:
  r=inverse[row['helper']];assert entrance[r]==row['dims'][0]and endpoint[r]==h;endpoint[r]=row['rank']
 for row in c['entries']:
  r=row['virtual_pivot'];assert physical[r]==row['pivot']and entrance[r]==0 and endpoint[r]==h;entrance[r]=1
 widths={r:endpoint[r]-entrance[r]for r in roles};assert len(widths)==(8221 if case=="weighted19"else 8223) and min(widths.values())>0
 census=Counter(widths.values());assert dict(census)=={int(k):v for k,v in price['residual_census'].items()}
 bywidth=defaultdict(list)
 for r in roles:bywidth[widths[r]].append(r)
 queues={width:iter((role,replica)for role in rs for replica in range(60))for width,rs in bywidth.items()}
 seen=bytearray(R*60);records=[];bank=0;digest=hashlib.sha256()
 for pattern in price['packing_patterns']:
  assert sum(pattern['widths'])==100
  for _ in range(pattern['count']):
   offset=0
   for width in pattern['widths']:
    role,replica=next(queues[width]);key=60*role+replica;assert not seen[key];seen[key]=1
    assert widths[role]==width and 0<=offset<offset+width<=100
    row=(role,replica,bank,offset,width);records.append(row);digest.update(struct.pack('>IIIII',*row));offset+=width
   assert offset==100;bank+=1
 assert bank==price['banks_per_stage']==(85701 if case=="weighted19"else 85707)
 assert len(records)==sum(seen)==len(roles)*60==(493260 if case=="weighted19"else 493380)
 for width,q in queues.items():assert next(q,None)is None
 assert all(seen[60*r+i]for r in roles for i in range(60))
 assert 60*4*v+5*bank==price['literal_stock']==(658905 if case=="weighted19"else 658935)
 assert Fraction(price['literal_stock'],60)==Fraction(price['unreplicated_stock'])
 label='weighted892-candidate19'if case=='weighted19'else'candidate15'
 output=ROOT/(label+'-bank-addresses.bin.gz')
 with gzip.GzipFile(filename=str(output),mode='wb',mtime=0)as stream:
  for row in records:stream.write(struct.pack('>IIIII',*row))
 allstages=hashlib.sha256()
 for stage in range(5):
  lo,hi=stage*bank,(stage+1)*bank
  for role,replica,b,offset,width in records:
   address=lo+b;assert lo<=address<hi;allstages.update(struct.pack('>IIIIII',stage,role,replica,address,offset,width))
 report=dict(status='PASS_EXPLICIT_P10_ROLE_BANK_ASSIGNMENT',source_head=HEAD,candidate_sha256=hashlib.sha256(cp.read_bytes()).hexdigest(),pricing_sha256=hashlib.sha256(price_path.read_bytes()).hexdigest(),
  candidate_word_sha256=WORD_SHA if case=='weighted19'else None,physical_R=len(roles),replicas=60,stages=5,assignments_per_stage=len(records),total_assignments=5*len(records),banks_per_stage=bank,total_banks=5*bank,literal_stock=price['literal_stock'],unreplicated_stock=price['unreplicated_stock'],residual_census=dict(sorted(census.items())),
  all_blocks_full=True,all_role_replica_pairs_exactly_once=True,stage_bank_ranges_disjoint=True,
  one_stage_table_format='Big-endian uint32 rows:role,replica,bank,coordinate_start,width. Stages translate bank by stage*banks_per_stage.',
  one_stage_table_uncompressed_sha256=digest.hexdigest(),five_stage_assignment_sha256=allstages.hexdigest(),compressed_table_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
  scope='Complete integer inventory/address binding. Reuse of these bank coordinates throughout the physical word remains under the separately checked source/frame and inherited bank/compiler interfaces.')
 (ROOT/(label+'-bank-receipt.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return report
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 run()
