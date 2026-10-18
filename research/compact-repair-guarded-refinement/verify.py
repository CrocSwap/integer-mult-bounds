import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from replay import run,need
from kernel import receipt_check

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    dest=Path(__file__).resolve().parent/'RESULT.json'
    if a.write:need(not dest.exists(),'refuse receipt overwrite')
    receipt_check()  # Structural provenance check only; this command does not run Lean.
    actual=run()
    if a.write:
        with dest.open('x',encoding='utf-8',newline='\n') as f:json.dump(actual,f,indent=2,sort_keys=True);f.write('\n')
    else:need(json.dumps(actual,sort_keys=True)==json.dumps(json.loads(dest.read_text(encoding='utf-8')),sort_keys=True),'receipt mismatch')
    print('PASS_COMPACT_GUARDED_REPAIR records='+str(sum(x['records'] for x in actual['fixtures']))+' controls='+str(len(actual['controls'])))

if __name__=='__main__':main()
