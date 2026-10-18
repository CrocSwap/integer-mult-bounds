#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Uses Douglas Colkitt's exact ceiling engine (Claude-assisted), pinned unchanged.
# Adapter by Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Fixed-word coverage-law ceiling; separate from physical and outer admission."""
import argparse, hashlib, importlib.util, json, sys
from fractions import Fraction as Q
from decimal import Decimal, localcontext
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
ENGINE_SHA = "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"
IDLE = {1:17316,3:6594,5:5216,32:1,48:26558}
CANDIDATE = {1:1593072,2:430236,3:204396,4:79920,5:22532,8:5328,32:1,48:26558}
ENDPOINT = Q('0.001717141586348426338109')

def need(ok, message):
    if not ok:
        raise ValueError(message)

def calculate(profile_path=None):
    path = HERE / 'vendor/ceiling.py'
    need(hashlib.sha256(path.read_bytes()).hexdigest() == ENGINE_SHA, 'ceiling source pin')
    spec = importlib.util.spec_from_file_location('packing_ceiling', path)
    engine = importlib.util.module_from_spec(spec); spec.loader.exec_module(engine)
    h = {int(r): n for r,n in json.loads((profile_path or HERE/'PROFILE.json').read_text()).items()}
    need(h == CANDIDATE and sum(r*n for r,n in h.items()) == 4816512,
         'complete candidate histogram and rank mass')
    local = {r: Q(h[r]-IDLE.get(r,0),666) for r in h if h[r] != IDLE.get(r,0)}
    need(local == {1:2366,2:646,3:297,4:120,5:26,8:8}, 'complete local profile')
    model = engine.model(local,73,896,9,64)
    need(model['total_mass']*666 == 4816512 and model['local_mass'] == 5223, 'coverage identity')
    lo,hi = engine.ceiling(local,73,896,9,64)
    need(engine.relax(local,73,896,9,64,hi)[0] > 1, 'upper cap rejection')
    c = Q(json.loads((HERE/'CLAIM.json').read_text())['complex_lower'])
    need(c == ENDPOINT, 'certified candidate endpoint')
    with localcontext() as ctx:
        ctx.prec = 50
        dec = lambda x: str(Decimal(x.numerator)/Decimal(x.denominator))
        return dict(status='PASS_FIXED_WORD_PACKING_CEILING',source_sha256=ENGINE_SHA,
                    local_per_call={str(r):str(n) for r,n in local.items()},
                    dimension=73,families=896,stages=9,centre_rank_per_call=64,max_idle_rank=model['R'],
                    complex_cap_bracket=[str(lo),str(hi)],complex_cap_upper_decimal=dec(hi),
                    realized_fraction_lower=str(c/hi),realized_fraction_decimal=dec(c/hi),
                    scope='Fixed joint-twelve local word and hosted nine-stage coverage law; all remaining mass is relaxed to fractional rank51 children. This generic coverage-law ceiling is weaker than a window-aware packing or lattice bound. It does not certify or import the predecessor advertised lattice ceiling. It bounds this complex model, not different words or coverage laws. Modern outer admission is separate; no historical a/(1+a) conversion is used.')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path)
    ap.add_argument('--profile',type=Path,default=HERE/'PROFILE.json');a=ap.parse_args()
    text=json.dumps(calculate(a.profile),indent=2)+'\n'
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text)
    print(text,end='')
if __name__=='__main__': main()
