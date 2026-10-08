#!/usr/bin/env python3
"""Stage pinned native data and execute the byte-identical scientific checker.
No predecessor implementation is executed. --prepare-only does no science.
"""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
CHECKER='876b03f9cb57de4e940a1bab623ad73dfcbfbfff05d79d03e869031fe756ec5a'
MANIFEST='739c5206cf10247097d575baa58fb088f7e18c5989204ca961888bd2dc8003be'
COMPLEX='399f102e9bab4d098604971c22d1ec39a787ca39dce84c455791d857e97739f0'
def digest(b):return hashlib.sha256(b).hexdigest()
def prepare(root,dest):
 checker=(HERE/'check_composition.py').read_bytes();manifest=(HERE/'VERIFIED_INPUT_MANIFEST.json').read_bytes()
 assert digest(checker)==CHECKER and digest(manifest)==MANIFEST
 pack=dest/'two_stage_composition';pack.mkdir(parents=True)
 (pack/'check_composition.py').write_bytes(checker);(pack/'VERIFIED_INPUT_MANIFEST.json').write_bytes(manifest)
 entries=json.loads(manifest)
 for e in entries:
  rel=Path(e['path']);assert not rel.is_absolute() and '..' not in rel.parts
  raw=(root/rel).read_bytes();assert len(raw)==e['bytes'] and digest(raw)==e['sha256']
  assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==e['git_blob']
  target=pack/'verified_inputs'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 rel=Path('research/translated-partial/complex-certificate.json');raw=(root/rel).read_bytes();assert digest(raw)==COMPLEX
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()=='fb6726518e25d601f34edae289822f393abe94db'
 target=dest/'semantic_pr28/inputs'/rel;target.parent.mkdir(parents=True);target.write_bytes(raw)
 return pack

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source-root',type=Path,default=HERE.parents[1]);ap.add_argument('--output',type=Path,default=HERE/'REPRODUCED_ASSEMBLY.json');ap.add_argument('--prepare-only',type=Path,help='New empty staging directory; verify/copy inputs without executing science.');args=ap.parse_args()
 if args.prepare_only:
  assert not args.prepare_only.exists() or not any(args.prepare_only.iterdir())
  prepare(args.source_root.resolve(),args.prepare_only.resolve());print('PASS: exact checker and ten pinned inputs staged; no scientific code executed.');return
 with tempfile.TemporaryDirectory(prefix='two-stage-reproduction-') as tmp:
  pack=prepare(args.source_root.resolve(),Path(tmp));subprocess.run([sys.executable,str(pack/'check_composition.py'),'--output',str(args.output.resolve())],cwd=pack,check=True)
if __name__=='__main__':main()
