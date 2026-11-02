#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded two-engine moment plus modern outer arithmetic; no full admission."""
from pathlib import Path
import argparse,importlib.util,json
HERE=Path(__file__).resolve().parent

def load(name):
    spec=importlib.util.spec_from_file_location('retimed_'+name,HERE/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise ValueError('fresh bounded arithmetic output directory required')
    a.out.mkdir(parents=True)
    check=load('check');moment=check.check(json.loads(a.profile.read_bytes()))
    (a.out/'MOMENT.json').write_text(json.dumps(moment,indent=2)+'\n')
    transfer=load('outer').check_outer(moment,a.out/'outer')
    result={'status':'PASS_BOUNDED_RETIMED_T488_MOMENT_AND_MODERN_OUTER','kappa':transfer['kappa'],
            'root_interval':moment['root_interval'],'strict_outer_inequalities':transfer['strict_inequalities'],
            'outer_rejection_controls':transfer['rejected_controls'],
            'scope':'Bounded exact moment and modern outer transfer arithmetic both pass. Native, controller, complete release, all-size compiler, physical realization, precision/tape, exact recovery and inherited analytic/BIT hypotheses remain separate and conditional.'}
    (a.out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])

if __name__=='__main__':main()
