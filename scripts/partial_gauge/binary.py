# Copyright 2026 icekylinx. Apache-2.0.
# Prepared with OpenAI GPT-6 Astra and Codex assistance; see NOTICE.
"""Read the selected scalar DAG and frame-label binary formats."""
from pathlib import Path
from collections import defaultdict,Counter
import struct,array,json,argparse

def load(path):
    blob=Path(path).read_bytes();h,v,n,q=struct.unpack_from('<4I',blob);at=16
    def take(code,num):
        nonlocal at
        a=array.array(code);nb=a.itemsize*num;a.frombytes(blob[at:at+nb]);at+=nb;return a
    args=take('I',2*n);core=take('Q',n);cover=take('Q',n);roots=take('I',q);kind=take('I',q);active=take('B',n)
    lab=Path(str(path).replace('.bin','.labels')).read_bytes();rank=array.array('I');rank.frombytes(lab[:4*n]);types=lab[4*n:]
    assert at==len(blob) and len(types)==n
    return h,v,n,q,args,core,cover,roots,kind,active,rank,types
