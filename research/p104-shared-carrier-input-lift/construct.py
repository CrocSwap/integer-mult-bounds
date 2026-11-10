"""Deterministic construction of the shared-carrier input-lift word; no search at replay.

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
Step one rebuilds the pending #6805 word from the #6702 word (retimed_construct.py,
by @CubeJerry with OpenAI assistance, helper basis adapted from Ali Romman); step two
applies the exact edit list LIFT.json (lift.py).
"""
import json
from pathlib import Path
import native as N
import retimed_construct
import lift

HERE=Path(__file__).resolve().parent

def base(source,witness):
    return retimed_construct.construct(source,witness)

def construct(source,witness,edit=None):
    return lift.apply(base(source,witness),edit if edit is not None else json.loads((HERE/'LIFT.json').read_bytes()))

if __name__=='__main__':
    import argparse,gzip
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--base-only',action='store_true',help='write the #6805 word instead')
    args=parser.parse_args()
    src=N.read(HERE/'retained/native/PR6702-WORD.json.gz');wit=N.read(HERE/'WITNESS.json')
    word=base(src,wit) if args.base_only else construct(src,wit)
    raw=json.dumps(word,sort_keys=True,separators=(',',':')).encode()
    args.output.write_bytes(gzip.compress(raw,mtime=0)if args.output.suffix=='.gz'else raw+b'\n')
