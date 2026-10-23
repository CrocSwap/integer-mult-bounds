"""Acquire immutable source bytes, saving upstream programs as inert text."""
from pathlib import Path
import argparse, urllib.request
import support

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--from-dir',type=Path)
    args=parser.parse_args(); support.verify_dependencies()
    for row in support.pins()['files']:
        destination=support.INPUTS/row['local']
        if destination.exists(): raw=destination.read_bytes()
        elif args.from_dir: raw=(args.from_dir/row['local']).read_bytes()
        else:
            with urllib.request.urlopen(row['url'],timeout=60) as response: raw=response.read()
        support.check_bytes(raw,row)
        destination.parent.mkdir(parents=True,exist_ok=True); destination.write_bytes(raw)
    support.verify_inputs(); print('Verified all immutable source files. No upstream program was executed.')
if __name__=='__main__':main()
