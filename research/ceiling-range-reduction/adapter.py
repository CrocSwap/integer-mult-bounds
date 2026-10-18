# SPDX-License-Identifier: Apache-2.0
"""Opt-in logarithm repair for the authenticated frozen ceiling engine.

Douglas Colkitt's retained interval/ceiling engine keeps its original credit.
Prepared for ywz65 with OpenAI Codex assistance. No source file is modified.
"""
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import types

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ENGINE='research/complex-local-word-ceiling/ceiling.py'


def authenticated():
    sources=json.loads((HERE/'SOURCES.json').read_bytes())
    blobs={}
    for row in sources['files']:
        if row['usage']=='input':
            data=(ROOT/row['path']).read_bytes()
            if hashlib.sha256(data).hexdigest()!=row['sha256']:
                raise ValueError('source pin: '+row['path'])
            blobs[row['path']]=data
    return blobs


def load(*, original=False, log_only=False):
    blobs=authenticated()
    engine=types.ModuleType('ceiling')
    engine.__file__=str(ROOT/ENGINE)
    exec(compile(blobs[ENGINE],engine.__file__,'exec'),engine.__dict__)
    if not original:
        @lru_cache(None)
        def binary_ln(k):
            engine.require(isinstance(k,int) and k>=1,'ln domain')
            if k==1:
                return Q(0),Q(0)
            exponent=k.bit_length()-1
            power=1<<exponent
            low2,high2=engine.atanh(Q(1,3))
            lo,hi=2*exponent*low2,2*exponent*high2
            if k!=power:
                low,high=engine.atanh(Q(k-power,k+power))
                lo+=2*low;hi+=2*high
            return engine.down(lo),engine.up(hi)
        engine.ln=binary_ln
        if not log_only:
            original_exp=engine.exp
            def reduced_exp(lo,hi):
                lo,hi=Q(lo),Q(hi)
                engine.require(0<=lo<=hi,'exp nonnegative interval')
                if hi<=Q(1,2):
                    return original_exp(lo,hi)
                squarings=0
                while hi>Q(1,2):
                    lo/=2;hi/=2;squarings+=1
                lower,upper=original_exp(lo,hi)
                for _ in range(squarings):
                    lower=engine.down(lower*lower)
                    upper=engine.up(upper*upper)
                return lower,upper
            engine.exp=reduced_exp
    return engine,blobs
