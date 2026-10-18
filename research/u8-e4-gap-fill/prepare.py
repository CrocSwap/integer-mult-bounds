"""Bind one E4 invocation to the inherited T37 runtime and bank envelope.

Runtime verifier code is exactly PR942's documented adaptation. This file
changes construction data only. Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import copy
import shutil
from pathlib import Path
from support import P, dump, identity, load, read, require, sha


def provider(directory, pid, semantic):
    word = read(directory / 'CANONICAL-WORD.json.gz')
    checks = read(directory / 'LOCAL-CHECKS.json')
    widths = [len(word['frames'][word['final'][r]]) - len(word['frames'][word['start'][r]])
              for r in range(224, 728)]
    return dict(directory='providers/' + pid,
                artifact_sha256={name: sha(directory / name) for name in semantic.FILES},
                artifact_semantic_sha256=semantic.artifact_identities(directory),
                ports=word['ports'], centers=word['centers'], widths=widths,
                actual_paid_profile=word['local_profile'],
                orientation_program_sha256={orientation: checks[orientation]['sha256']
                                            for orientation in ('forward', 'backward')})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--baseline942', type=Path, required=True)
    args = parser.parse_args()
    work, baseline = args.work, args.baseline942
    claim = read(P / 'CLAIM.json')
    plan = read(baseline / 'lift/PLAN.json')
    owners = work / 'construction/OWNERS.json.gz'
    semantic = load(work / 'runtime/code/generated_identity.py', 'e4_semantic')
    registry = {pid: provider(directory, pid, semantic) for pid, directory in (
        ('gauge44', baseline / 'native/local'), ('gauge44_e4', work / 'native/local'))}
    require(registry['gauge44']['artifact_semantic_sha256'] ==
            plan['provider_registry']['gauge44']['artifact_semantic_sha256'], 'Fresh baseline U8 binding')
    plan = copy.deepcopy(plan)
    plan.update(status='FROZEN_LITERAL_T37_U8_E4_GAP_FILL', mode='one-E4-group-four-unit-gaps',
                solver_status='Literal source-bound edits; no runtime search', profile=claim['profile'],
                provider_registry=registry, assignment_sha256=sha(owners),
                assignment_content_sha256=identity(read(owners)))
    plan['replica_lift']['owners_file_sha256'] = sha(owners)
    for call in plan['provider_calls']:
        pid = 'gauge44_e4' if (call['stage'], call['replica']) == (0, 0) else 'gauge44'
        call['provider'] = pid
        call['local_program_sha256'] = registry[pid]['orientation_program_sha256'][call['orientation']]
    for call in plan['per_call_widths']:
        pid = 'gauge44_e4' if (call['stage'], call['replica']) == (0, 0) else 'gauge44'
        call['widths'] = registry[pid]['widths']
    lift = work / 'lift'
    lift.mkdir()
    shutil.copyfile(baseline / 'lift/GLOBAL-TEMPLATE.json.gz', lift / 'GLOBAL-TEMPLATE.json.gz')
    dump(lift / 'PLAN.json', plan)
    spec = read(work / 'runtime/data/SPEC.json')
    spec['name'] = 'u8-e4-t37-four-unit-gap-fill'
    spec['dispatch'] = [[s, r, 'gauge44_e4' if (s, r) == (0, 0) else 'gauge44']
                        for s, r in spec['call_order']]
    spec['data'] = dict(owners_sha256=sha(owners), plan_sha256=sha(lift / 'PLAN.json'))
    dump(work / 'runtime/data/SPEC.json', spec)
    dump(work / 'PARENT-REFERENCE.json', dict(
        source_path=str((baseline / 'lift/GLOBAL-TEMPLATE.json.gz').resolve()),
        source_sha256=sha(baseline / 'lift/GLOBAL-TEMPLATE.json.gz'),
        source_content_identity=identity(read(lift / 'GLOBAL-TEMPLATE.json.gz')),
        baseline_parent_check_sha256=sha(baseline / 'PARENT-CHECK.json'),
        use='Unchanged checked bank envelope; both native suppliers are freshly bound in the hosted controller.'))
    print('PASS_FROZEN_MIXED_PROVIDER_PLAN')


if __name__ == '__main__':
    main()
