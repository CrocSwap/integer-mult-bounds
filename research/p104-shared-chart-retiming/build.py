"""Explicit construction in a new caller-owned output directory."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import model as M
def construct():
    M.authenticate();source=M.read(M.HERE/'source/PR2662-WORD.json')
    word,edges=M.construct(source)
    native=M.native_payload(edges,M.load_interpreter())
    return word,native
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=Path,required=True);args=ap.parse_args()
    word,native=construct();args.out_dir.mkdir(parents=True,exist_ok=True)
    for name,value in (('WORD.json',word),('NATIVE.json',native)):
        with (args.out_dir/name).open('x',encoding='utf-8') as file:file.write(json.dumps(value,indent=2)+'\n')
    print('BUILT_SHARED_CHART_RETIMING')
if __name__=='__main__':main()
