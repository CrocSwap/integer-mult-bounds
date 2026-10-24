from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from model import need,run
ROOT=HERE.parents[1]
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def main():
    sources=json.loads((HERE/'SOURCES.json').read_text())
    for item in sources['files']:
        if item['usage']=='input':
            need(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],'source mismatch: '+item['path'])
    actual=run(); frozen=json.loads((HERE/'RESULT.json').read_text())
    need(canonical(actual)==canonical(frozen),'typed complete receipt mismatch')
    print('PASS_UNEQUAL_CYCLE_FIT_RIGIDITY_BOUNDARY')
if __name__=='__main__':main()
