"""Reject material false release claims using full semantic receipt checks."""
import copy,json
from pathlib import Path
import evidence_check as e
P=Path(__file__).resolve().parent/'evidence'
original=[e.read(P/name)for name in ['RESULT.json','RELEASE-RECEIPT.json','NATIVE-RECEIPT.json','PREFIX-AND-INVOICE.json','INDEPENDENT-OWNERS.json']]
e.semantic_check(*original);controls=[]
def reject(name,change):
 records=copy.deepcopy(original);change(records)
 try:e.semantic_check(*records)
 except ValueError:controls.append(name)
 else:raise ValueError('accepted '+name)
reject('release stage omitted',lambda d:d[0]['stages'].pop())
reject('nonzero stage exit',lambda d:d[0]['stages'][0].__setitem__('exit_code',1))
reject('wrong kappa endpoint',lambda d:d[0].__setitem__('kappa','1/1000'))
reject('one unpaid child',lambda d:d[0]['profile'].__setitem__('1',d[0]['profile']['1']-1))
reject('native word source substituted',lambda d:d[2]['providers']['base'].__setitem__('word_sha256','0'*64))
reject('private buffers omitted',lambda d:d[3].__setitem__('physical',d[3]['physical']-91))
reject('strict invoice check omitted',lambda d:d[3]['strict_checks'].pop('router'))
reject('precision undercharged',lambda d:d[3].__setitem__('charged_prefix_bits',1477))
reject('dirty endpoint column omitted',lambda d:d[3]['blocknorm']['endpoint_replay']['gauge44']['backward'].__setitem__('all_arbitrary_columns',631))
reject('one literal role omitted',lambda d:d[4].__setitem__('roles',d[4]['roles']-1))
print(json.dumps({'status':'PASS_STORED_EVIDENCE_SEMANTIC_CONTROLS','controls':controls}))
