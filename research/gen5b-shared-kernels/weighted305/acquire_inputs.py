"""Reuse the authored immutable-data downloader with the PR305 input contract."""
import argparse,json
from pathlib import Path
import source_data
from fetch_inputs import run
if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=source_data.ROOT/'inputs')
    print(json.dumps(run(p.parse_args().output),indent=2))
