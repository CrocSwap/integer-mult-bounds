#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Nominate candidate SPEC inputs; discovery must freeze derived contracts."""
import argparse
from collections import Counter
import copy,gzip,hashlib,json
from pathlib import Path
from check_endpoints import CASE,RESEARCH,NATIVE,CONSERVATIVE
from check_bootstrap import OPTIONS

HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())

def main():
 assert __debug__
 ap=argparse.ArgumentParser();ap.add_argument('--native',type=Path,default=Path('/home/zoe/MP/maths/mult/seed39-four-native-cold-20261015T0734Z'));a=ap.parse_args()
 parent=RESEARCH/'anticipatory-stage-evidence/parent';owners=HERE.parent/'owners'
 old=rd(parent/'new/SPEC.json');s=copy.deepcopy(old);plan=rd(owners/'PLAN.json')
 s['name']='seed39-four428-complete-cost-candidate'
 s['call_order']=plan['order'];s['dispatch']=rd(owners/'DISPATCH.json')
 # The legacy EXPECTED outcomes depend on changed words/owners. Preserve the
 # inherited theorem geometry and baseline; erase only derived result pins,
 # then let unchanged strict recomputation freeze and check the new values.
 s['expected']={'gain_baseline_kappa':old['expected']['gain_baseline_kappa'],
                'complex_lower':str(NATIVE),'conservative_complex_lower':str(CONSERVATIVE)}
 s['data']={'plan_sha256':sha(owners/'PLAN.json'),'owners_sha256':sha(owners/'OWNERS.json.gz')}
 s['outer_refinement']=OPTIONS
 s['providers']={}
 native_pins={}
 for pid,tag,edges in [('gauge44','base',2900),('extra','extra',2899)]:
  path=a.native/tag;word=rd(path/'CANONICAL-WORD.json.gz');ph=rd(path/'CLIFFORD-REVIEW.json');rec=rd(path/'INDEPENDENT-LOCAL-REPLAY.json')
  widths=[len(word['frames'][word['final'][r]])-len(word['frames'][word['start'][r]]) for r in range(224,224+word['R'])]
  assert word['R']==428 and tuple(widths[h] for h in s['width_spot_helpers'])==(9,9,8,8)
  assert len(rec['negative_controls_rejected'])==46 and ph['directed_edges']==edges and ph['endpoint_adapters']==224
  assert widths==plan['provider_registry'][pid]['widths']
  s['providers'][pid]={'native_negative_controls':46,'phase_edges':edges,
   'inventory':dict(sorted(Counter(widths).items())),
   'expected_profile':word['local_profile'],
   'artifacts':{n:sha(path/n) for n in ('LOCAL-CHECKS.json','CLIFFORD-RECIPES.json','RESIDUAL-ADAPTERS.json')},
   'artifact_semantic_sha256':plan['provider_registry'][pid]['artifact_semantic_sha256']}
  native_pins[pid]={n:sha(path/n) for n in ('CANONICAL-WORD.json.gz','CLIFFORD-REVIEW.json','INDEPENDENT-LOCAL-REPLAY.json')}
 assert s['dispatch']==old['dispatch'] and s['call_order']==old['call_order']
 assert s['geometry']==old['geometry'] and s['pivot_swap']==old['pivot_swap']
 (owners/'SPEC.json').write_text(json.dumps(s,indent=2)+'\n')
 report={'status':'PREPARED_CANDIDATE_SPEC_REQUIRES_DISCOVERY_AND_STRICT_REPLAY',
 'parent_spec_sha256':sha(parent/'new/SPEC.json'),'new_spec_sha256':sha(owners/'SPEC.json'),
 'removed_expected_generated_keys':sorted(set(old['expected'])-{'gain_baseline_kappa','complex_lower','conservative_complex_lower'}),
 'removed_provider_generated_keys':{p:sorted(set(old['providers'][p])-set(s['providers'][p])) for p in s['providers']},
 'retained_static_fields':['geometry','pivot_swap','width_spot_helpers','call_order','dispatch','schema'],
 'native_receipt_bindings':native_pins,'changed_inputs':['name','data hashes','new exact endpoints','D24 refinement','new native46 controls/phase edges/profiles/inventories/artifacts'],
 'policy':'Old output pins cannot describe changed words. Discovery recomputes them; freeze_spec refuses conflicting values and strict replay then requires every frozen pin. No proof obligation or assertion is removed.'}
 (HERE/'SPEC-PREPARATION.json').write_text(json.dumps(report,indent=2)+'\n')
 print(report['status'])

if __name__=='__main__':main()
