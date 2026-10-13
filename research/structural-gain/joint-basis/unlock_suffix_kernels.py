#!/usr/bin/env python3
"""Remove inserted suffix kernels by exact scalar subsequence alignment.

The original scalar B word is a pinned input; all existing frame promotions
and every fixed field are preserved. Prepared with OpenAI Codex, Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--word',type=Path,required=True)
    ap.add_argument('--original',type=Path,required=True)
    ap.add_argument('--gk-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();assert __debug__ and not a.out.exists()
    sys.path.insert(0,str(a.gk_dir.resolve()));import gk_word as g,gk_common as co
    g.V=co.V=112;g.DATA=co.DATA=7168
    source=json.loads(gzip.decompress(a.word.read_bytes()))
    original=json.loads(gzip.decompress(a.original.read_bytes()))
    word=copy.deepcopy(source);retained=[];removed=[];index=0
    for event in word['B']:
        if index<len(original['B'])and event[:-1]==original['B'][index][:-1]:
            retained.append(event);index+=1
        else:removed.append(event)
    assert index==len(original['B'])
    unlocked=set(word['start_extra'])-set(original['start_extra'])
    assert removed and all(e[0]=='add'and str(e[2])in unlocked for e in removed)
    assert set(str(e[2])for e in removed)==unlocked
    word['B']=retained
    word['start_extra']={r:E for r,E in word['start_extra'].items()if r not in unlocked}
    word['cleanup']=[g.inverse(e,g.FULL)for e in reversed(word['A']+word['B'])if not 112<=e[1]<224]
    profile=g.profile(word);C=g.responses(word)
    assert all(not C[int(r)-224]for r in word['start_extra'])
    a.out.mkdir(parents=True);(a.out/'FULL-WORD.json.gz').write_bytes(g.dump(word))
    report=dict(status='PASS_EXACT_SUFFIX_UNLOCK',source_sha256=hashlib.sha256(a.word.read_bytes()).hexdigest(),
                original_sha256=hashlib.sha256(a.original.read_bytes()).hexdigest(),
                removed_gates=removed,unlocked_pivots=sorted(map(int,unlocked)),profile=dict(profile),
                scalar_B_subsequence_exact=True,remaining_entering_columns_zero=True)
    (a.out/'UNLOCK.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k!='removed_gates'},indent=2))


if __name__=='__main__':main()
