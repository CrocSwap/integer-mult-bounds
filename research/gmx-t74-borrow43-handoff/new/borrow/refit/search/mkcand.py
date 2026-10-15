"""mkcand.py NAME 'h:L,...'  -> cand/NAME-{b,e}.json.gz (refit + aliases on both #2526 words)"""
import os as _os,sys as _sys;_H=_os.path.dirname(_os.path.abspath(__file__));_sys.path[:0]=[_H,_os.path.join(_H,'..','..'),_os.path.join(_H,'..','..','prelife','search')]   # this dir, new/borrow, prelife/search (wordmodel)
import sys,json,gzip,os
from eval1 import apply_stack
D=_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'..','..','words')+'/'   # NB: the shipped words already carry the stack; run on the PR2526 words
os.makedirs('cand',exist_ok=True)
stack=[tuple(map(int,x.split(':'))) for x in sys.argv[2].split(',')]
for k,wt in (('b','base'),('e','extra')):
    w,log=apply_stack(D+f'BORROW-WORD-43{wt}.json.gz',stack)
    assert w is not None,log
    print(wt,w['report']['local_profile'],w['report']['width_inventory'])
    open(f'cand/{sys.argv[1]}-{k}.json.gz','wb').write(gzip.compress(json.dumps(w,separators=(',',':')).encode()))
