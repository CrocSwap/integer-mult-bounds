#!/usr/bin/env python3
"""Actual same-chart cache coefficient mutant through frozen native interpreter.

This is an additional semantic control. It intentionally bypasses the literal
source zipper to test native row content after preserving frame/ownership rules.
"""
import argparse,copy,gzip,hashlib,json,time
from pathlib import Path
from prior_dyadic_engine import require
from provider_rows import interpret

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]/'repository'
FROZEN={'check_provider.py':'3774c5742b565ea9007af90d10e43d38a3e675c2074583c8c365799fc256baaf',
'phase_exact.py':'15e90b63c5659090f02902cb38951ec4ab252352fb0b967b411ed547c501e2ba',
'provider_rows.py':'c7e579939d89709d72457d5fa213173b3b492c3cc3de7546afc3ed6a6fb32f0c',
'prior_dyadic_engine.py':'3ee4ae79a55188d5abf2306f678179f4aafb799602ffb970fc1bc8f76cb061d9'}

def main(out):
    started=time.monotonic()
    for name,digest in FROZEN.items():require(hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest,'frozen engine changed')
    source=ROOT/'research/native-center-free-code/SOURCE-WORD.json.gz'
    candidate=ROOT/'research/native-rank8-helper-provider/WORD.json.gz'
    sraw=source.read_bytes();raw=candidate.read_bytes()
    c=json.loads(gzip.decompress(sraw))['canonical']
    original=json.loads(gzip.decompress(raw))['word'];mutated=copy.deepcopy(original)
    i=next(i for i,e in enumerate(mutated) if e[0]=='scalar' and e[1][0]=='copy' and e[1][1]==['C',1])
    frame=mutated[i][2]
    require(mutated[i-1]==['scalar',['clear',['C',1]],frame],'actual cache COPY already preceded by same-chart owned CLEAR')
    event=['scalar',['scale',['C',1],-1,1],frame]
    mutated.insert(i+1,event)
    require(mutated[:i+1]==original[:i+1] and mutated[i+2:]==original[i+1:],'exactly one legal scalar event inserted')
    # SCALE -1 is a legal ordinary signed power-of-two on the same current
    # physical chart. It neither reads another owner nor erases any owner.
    rejection=None
    try:interpret(c,mutated,{('C',j) for j in range(9)},require_owned_return=False)
    except ValueError as e:rejection=str(e)
    require(rejection=='zero retag requires complete exact zero row','mutant must reject for nonzero algebraic content, not frames or ownership')
    require(source.read_bytes()==sraw and candidate.read_bytes()==raw,'source changed')
    result={'status':'PASS_SAME_CHART_CACHE_CONTENT_MUTANT_REJECTED','mutation_source_event':i,'inserted_event':event,'preserved':'same chart, all owned CLEAR/COPY rules, no borrowed erasure; one legal SCALE -1 on retained C1 only','rejection':rejection,'runtime_seconds':round(time.monotonic()-started,6),'source_raw_sha256':hashlib.sha256(sraw).hexdigest(),'candidate_raw_sha256':hashlib.sha256(raw).hexdigest(),'frozen_engine_sha256':FROZEN,'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=HERE/'SAME-CHART-CACHE-MUTANT.json');main(ap.parse_args().out)
