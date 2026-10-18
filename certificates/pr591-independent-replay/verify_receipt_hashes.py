"""Verify PR591 replay receipt, log and artifact hashes from an extracted work directory."""
import argparse, hashlib, json
from pathlib import Path

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('work', type=Path)
    a=ap.parse_args()
    receipts=sorted(a.work.rglob('RECEIPT.json'))
    assert receipts, 'no RECEIPT.json found'
    checked=[]
    for path in receipts:
        rec=json.loads(path.read_text())
        for step in rec['steps']:
            assert step['exit_code']==0, step
            log=path.parent/(step['name']+'.log')
            assert sha(log)==step['log_sha256'], (path, step['name'])
        for rel,digest in rec['artifacts'].items():
            assert sha(path.parent/rel)==digest, (path, rel)
        checked.append({'receipt':str(path.relative_to(a.work)), 'steps':len(rec['steps']), 'artifacts':len(rec['artifacts']), 'status':rec['status']})
    print(json.dumps({'status':'PASS_RECEIPT_LOG_ARTIFACT_HASHES','receipts':checked}, indent=2))

if __name__=='__main__':
    main()
