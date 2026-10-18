#!/usr/bin/env python3
"""Offline finite scalar certificate; no selected frontier mutation."""
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import experiment as e


def compute():
    word, programs, checks = e.load()
    recipe = json.loads((HERE / 'RECIPE.json').read_text())
    e.require(e.canonical(recipe) == e.canonical(e.synthesize(word)), 'recipe does not match complete census')
    new, prep, parents = e.forest(word, recipe)
    e.require(sum(e.cost(e.Q(op[3], op[4])) for op in new) == recipe['complex_primitive_floor'], 'attained forest floor')
    result = {'status':'PASS_X4_TARGET_FOREST', 'seed':34, 'base':'91a2094f2e022930069e8cfdc810a3ea1b81cd09',
              'compensation_original_additions':len(word['compensation']), 'compensation_new_additions':len(new),
              'preparation_additions':prep, 'restoration_additions':prep, 'middle_additions':len(new)-2*prep,
              'roots':sum(p==-1 for p,s in parents.values()), 'complex_compensation_floor':recipe['complex_primitive_floor'],
              'census_edges':recipe['census_edges'], 'census_sha256':recipe['census_sha256'],
              'controls':e.controls(word,new,prep), 'programs':{}}
    for orientation in ('forward','backward'):
        baseline=e.replay(programs[orientation],orientation)
        e.require(baseline['real_primitives'] == checks[orientation]['real_component_primitive_bound'], 'baseline count')
        e.require(baseline['macros'] == checks[orientation]['scalar_macros'], 'baseline macros')
        e.require(baseline['positive_prefix_upper'] == checks[orientation]['inherited_prefix_upper'], 'baseline prefix mismatch')
        candidate=e.replay(e.replace(programs[orientation],word,new,orientation),orientation)
        e.require(candidate['paid_profile'] == baseline['paid_profile'] == checks[orientation]['paid_profile'], 'paid profile changed')
        e.require(candidate['prefix_bits'] <= checks[orientation]['charged_payload_bits'], 'prefix exceeds inherited allocation')
        result['programs'][orientation]={'baseline':baseline,'candidate':candidate,
                                        'saved_real_primitives':baseline['real_primitives']-candidate['real_primitives']}
        print(orientation, 'real',baseline['real_primitives'],'->',candidate['real_primitives'],
              'prefix_bits',baseline['prefix_bits'],'->',candidate['prefix_bits'],flush=True)
    import independent
    result['independent'] = independent.verify(recipe,word)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',type=Path,help='development only: save a newly computed receipt')
    args=parser.parse_args()
    result=compute()
    if args.write:
        # Explicit development command only. Normal verification is read-only.
        with args.write.open('x') as out: out.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        expected=json.loads((HERE/'EXPECTED.json').read_text())
        e.require(e.canonical(result)==e.canonical(expected),'receipt mismatch')
    print('PASS_X4_TARGET_FOREST compensation=6320->2324 saved_real=47690/47690 forest_floor=10883 columns=737 orientations=2 no_new_kappa')


if __name__=='__main__': main()
