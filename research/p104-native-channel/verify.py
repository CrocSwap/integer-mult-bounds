"""Read-only exact native channel replay; no network, Git or producer imports.

--regenerate also runs the compiler in temporary storage and compares the
complete decompressed certificate. Ordinary replay uses only the independent
native interpreter and framed scalar induction.
"""
from pathlib import Path
import argparse,gzip,hashlib,importlib.util,json,subprocess,sys,tempfile
P=Path(__file__).resolve().parent

def need(ok,why):
    if not ok:raise ValueError(why)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);ap.add_argument('--regenerate',action='store_true');args=ap.parse_args()
    sources=json.loads((P/'SOURCES.json').read_text())
    for item in sources['vendored_inputs']:
        need(hashlib.sha256((P/item['path']).read_bytes()).hexdigest()==item['sha256'],'pinned source changed: '+item['path'])
    spec=importlib.util.spec_from_file_location('p104_independent_channel',P/'check_native.py');checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    result=json.loads(json.dumps(checker.replay(True)))
    need(result==json.loads((P/'EXPECTED.json').read_text()),'independent replay differs from expected exact receipt')
    if args.regenerate:
        with tempfile.TemporaryDirectory(prefix='p104-native-')as directory:
            subprocess.run([sys.executable,'-I','-O','-B',str(P/'compile.py'),'--out-dir',directory],check=True,timeout=300)
            for filename in ['NATIVE-RECIPES.json.gz','SUMMARY.json']:
                a=(P/filename).read_bytes();b=(Path(directory)/filename).read_bytes()
                if filename.endswith('.gz'):a,b=gzip.decompress(a),gzip.decompress(b)
                need(a==b,'regenerated complete payload differs: '+filename)
    out=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.out:
        with args.out.open('x')as handle:handle.write(out)
    print(out,end='')

if __name__=='__main__':main()
