#!/usr/bin/env python3
"""Materialize exact frozen numerical reproduction inputs; does not execute them.

Use a NEW output directory. Prepared with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import argparse,importlib.util,shutil
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('packed_evidence_verify',P/'verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('output',type=Path);args=ap.parse_args()
sources=v.source_members();args.output.mkdir(parents=True,exist_ok=False)
for name,data in sources.items():
    target=args.output/'staged-source'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
a=P/'evidence/real-packed-outer-consumer-20261023'
for name in ['packed_sandwich_DRAFT.py','run_full_packed_attempt2_DRAFT.py','PUBLIC-TEXT-MANIFEST.json']:
    shutil.copyfile(a/name,args.output/name)
print('MATERIALIZED_ONLY',args.output.resolve(),'no numerical execution; p48 reduced diagnostic only')
