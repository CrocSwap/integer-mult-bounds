"""Acquire immutable PR325 data and inert source text without executing it."""
from pathlib import Path
import argparse,urllib.request
import packet325 as packet

def main():
 packet.require_assertions();p=argparse.ArgumentParser();p.add_argument('--from-dir',type=Path);a=p.parse_args()
 for z in packet.source_manifest()['files']:
  dest=packet.INPUTS/z['local']
  if dest.exists():raw=dest.read_bytes()
  elif a.from_dir:raw=(a.from_dir/z['local']).read_bytes()
  else:
   with urllib.request.urlopen(z['url'],timeout=60)as reply:raw=reply.read()
  packet.check_input(raw,z);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
 packet.verify_inputs();print('All immutable PR325 input hashes and source-manifest entries verified. No upstream program was executed.')
if __name__=='__main__':main()
