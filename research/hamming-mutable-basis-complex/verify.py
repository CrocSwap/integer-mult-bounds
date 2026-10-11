"""Replay the immutable local package in a fresh output directory."""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--work',required=True);args=p.parse_args()
root=Path(__file__).resolve().parent;out=Path(args.work).resolve();assert not out.exists(),'Use a fresh nonexistent output directory'
manifest=json.loads((root/'MANIFEST.json').read_text())
for name,want in manifest.items():
 src=root/name;assert hashlib.sha256(src.read_bytes()).hexdigest()==want,name
 dst=out/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
shutil.copyfile(root/'MANIFEST.json',out/'MANIFEST.json')
subprocess.run([sys.executable,'-B',str(out/'reproduce.py')],cwd=out,check=True)
print('Verified output:',out)
