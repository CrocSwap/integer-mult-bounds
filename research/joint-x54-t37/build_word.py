"""Apply the X54 triangle-hybrid slot (NewBArch builder, vendored unchanged) to PR1148's joint-entrance k8 word."""
import argparse,gzip,hashlib,json,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
def main():
 assert __debug__
 ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert not a.out.exists()
 r=json.loads((P/'RECIPE-X54-joint.json').read_text())
 assert hashlib.sha256(gzip.decompress(a.base.read_bytes())).hexdigest()==r['base_sha256']
 subprocess.run([sys.executable,'-B',str(P/'vendor/barch/build_tri.py'),str(a.base),str(P/'RECIPE-X54-joint.json'),str(a.out)],check=True)
 assert hashlib.sha256(gzip.decompress(a.out.read_bytes())).hexdigest()==r['expect_sha256'];print('PASS_X54_ON_JOINT_ENTRANCES')
if __name__=='__main__':main()
