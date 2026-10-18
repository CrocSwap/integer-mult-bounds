"""Rebuild doublecold OWNERS from immutable PR564 owners and literal edits.

This verifies the exact serialized owner construction, not phase, scalar,
physical-chart or complete finite-invoice admission.
"""
import argparse,gzip,hashlib,json
from pathlib import Path
if not __debug__:raise SystemExit('Assertions must remain enabled.')
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-owners',type=Path,required=True)
parser.add_argument('--construction',type=Path,required=True)
parser.add_argument('--expected-owners',type=Path,default=Path(__file__).resolve().parents[1]/'data/OWNERS.json.gz',help='Selected owner file to compare, default package data/OWNERS.json.gz')
parser.add_argument('--output',type=Path)
args=parser.parse_args()
record=json.loads(args.construction.read_bytes());raw=args.source_owners.read_bytes()
assert hashlib.sha256(raw).hexdigest()==record['source_inputs']['data/OWNERS.json.gz']
plain=gzip.decompress(raw)
assert hashlib.sha256(plain).hexdigest()==record['source_owner_content_sha256']
owners=json.loads(plain);last=-1;changes=record['literal_changes']
assert len(changes)==record['changed_records']
for change in changes:
 index=change['index'];assert type(index)is int and last<index<len(owners)
 assert owners[index]==change['before']
 assert [owners[index][f]for f in('time','stage','replica','helper')]==change['key']
 assert [change['after'][f]for f in('time','stage','replica','helper')]==change['key']
 owners[index]=change['after'];last=index
assert len(owners)==record['owner_count']
payload=json.dumps(owners,sort_keys=True,separators=(',',':')).encode('utf-8')
assert hashlib.sha256(payload).hexdigest()==record['owner_output_content_sha256']
expected=args.expected_owners.read_bytes()
assert hashlib.sha256(expected).hexdigest()==record['owner_output_sha256']
assert gzip.decompress(expected)==payload, 'Rebuilt owners differ from the selected owner file.'
if args.output is not None:
 assert not args.output.exists(), 'Choose a fresh output file.'
 compressed=gzip.compress(payload,mtime=0)
 compressed=compressed[:9]+b'\xff'+compressed[10:]
 assert gzip.decompress(compressed)==payload
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(compressed)
print(json.dumps(dict(status='PASS_LITERAL_OWNER_REBUILD_AND_SELECTED_FILE_COMPARISON',source_head=record['source_head'],owner_count=len(owners),changed_records=len(changes),content_sha256=hashlib.sha256(payload).hexdigest(),selected_file_sha256=hashlib.sha256(expected).hexdigest(),selected_file_content_equal=True,scope=__doc__.split('\n\n')[1].strip()),indent=2))
