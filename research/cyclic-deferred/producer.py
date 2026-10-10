"""Reproducible first22 restriction of the pinned original PR117 scalar DAG.

Original searched DAG: eumemic with Anthropic Claude assistance.
Restriction/replay integration with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from replayed_producer import build as replayed_build
from restrict_dag import checked_record

def build(h,prefix,central_disjoint,base=2):
    assert (h,central_disjoint,base)==(22,22,2)
    record,stats=checked_record()
    result=replayed_build(Path(__file__).resolve().parent/'inputs/restricted-dag.json.gz',prefix)
    assert (result['h'],result['v'],result['c'],result['q'])==(22,1540,64140,6182)
    result['restriction']=stats
    return result
