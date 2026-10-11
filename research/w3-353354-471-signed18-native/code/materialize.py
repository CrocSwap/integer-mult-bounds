#!/usr/bin/env python3
"""Compact only the source admitted by the separately pinned PR353/354 replay."""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,json,hashlib,shutil,subprocess,os
from source_binding import check_source
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(out):
    out=Path(out).resolve();names=check_source(out);source=out/'source353354'
    with(out/'logs/compact-dormant-helpers.log').open('w')as f:
        subprocess.run([sys.executable,'-B',str(ROOT/'code/compact.py'),'--base',str(source/'base'),'--final',str(source/'candidate'),'--sinks',str(source/'pkg/sink-selection.json'),'--output',str(out/'materialized')],check=True,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    shutil.copyfile(out/'materialized/COMPACTION.json',out/'COMPACTION.json')
    comp=read(out/'COMPACTION.json');sink=read(source/'pkg/sink-selection.json')
    removed=sorted(x['stream']for x in sink['sinks'])
    roles=read(source/'newbase-source-admission/original-helper-roles.json');assert roles==list(range(8100))
    assert removed==comp['sink_roles_original'] and len(removed)==10
    survivors=[i for i in range(1920,10020)if i not in removed]
    assert sorted(map(int,comp['original_to_staged']))==list(range(1920))+survivors+[10020]
    assert comp['compacted_word_sha256']==read(ROOT/'SOURCE.json')['source_compacted_word_sha256']
    mapping=dict(status='PASS_CHANGED_BASE_SORTED_SOURCE_SINK_AND_DORMANT_MAP',removed_original_positions=removed,surviving_original_helper_positions=survivors,source_helper_roles_sha256=sha(source/'newbase-source-admission/original-helper-roles.json'),sink_selection_sha256=sha(source/'pkg/sink-selection.json'),copy_slots=comp['copy_slots'])
    (out/'SOURCE-ROLE-MAP.json').write_text(json.dumps(mapping,sort_keys=True,indent=2)+'\n')
    binding=dict(status='PASS_CHANGED_BASE_SOURCE_BOUND_TO_FRESH_NATIVE_MATERIALIZATION',source_receipts={n:sha(out/n)for n in names},source_manifest_sha256=sha(ROOT/'vendor/source353354/MANIFEST.json'),source_word_sha256=comp['source_word_sha256'],compacted_word_sha256=comp['compacted_word_sha256'],role_map_sha256=sha(out/'SOURCE-ROLE-MAP.json'),compaction_sha256=sha(out/'COMPACTION.json'))
    (out/'SOURCE-COMPOSITION.json').write_text(json.dumps(binding,sort_keys=True,indent=2)+'\n')
    print(binding['status'],flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output');a=p.parse_args();run(a.output)
