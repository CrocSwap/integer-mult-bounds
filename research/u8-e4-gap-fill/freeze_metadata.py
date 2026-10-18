"""Derive two-provider metadata after the inherited single-provider freezer.

No verifier code or admission predicate changes. The control count comes from
the pinned control generator's literal lists and its width-pair/spot loops.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import ast
from collections import Counter
from pathlib import Path
from support import dump, read, require, sha


def derive(work):
    source = work / 'runtime/code/assembly_controls.py'
    tree = ast.parse(source.read_text())
    base_lists = [n.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'controls' for t in n.targets)
                  and isinstance(n.value, ast.List)]
    provider_lists = [n.value for n in ast.walk(tree) if isinstance(n, ast.AugAssign)
                      and isinstance(n.target, ast.Name) and n.target.id == 'controls'
                      and isinstance(n.value, ast.List)]
    require(len(base_lists) == len(provider_lists) == 1, 'Pinned literal control-list structure')
    common, per_provider = len(base_lists[0].elts), len(provider_lists[0].elts)
    require((common, per_provider) == (31, 17), 'Control generator literal inventories')
    spec = read(work / 'runtime/data/SPEC.json')
    counts = dict(Counter(pid for _, _, pid in spec['dispatch']))
    require(counts == {'gauge44_e4': 1, 'gauge44': 332}, 'Two actual selected providers')
    plan = read(work / 'lift/PLAN.json')
    spots = spec.get('width_spot_helpers', [270, 282, 294, 306])
    # Two mutations for each unordered distinct-width pair, then one per spot.
    widths = {pid: len(set(plan['provider_registry'][pid]['widths'])) for pid in counts}
    total = common + 1 + sum(per_provider + n*(n-1) + len(spots) for n in widths.values())
    require(total == 114, 'Complete two-provider mutation count, including wrong owner receipt hash')
    controller = read(work / 'discovery/global/audit/ASYNC-AUDIT.json')
    require(controller['mutation_controls_run'] and controller['provider_counts'] == counts, 'Discovery controller coverage')
    return dict(assembly_controls_rejected=total, provider_counts=counts,
                mutations_rejected=len(controller['mutations_rejected'])), dict(
        source_sha256=sha(source), common_controls=common, wrong_owner_hash_controls=1,
        per_provider_literal_controls=per_provider, distinct_widths=widths,
        width_spots=len(spots), note='Strict replay must execute and reject every mutation.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    metadata, derivation = derive(args.work)
    path = args.work / 'runtime/data/SPEC.json'
    spec = read(path)
    before = {k: spec['expected'][k] for k in metadata}
    require(before == dict(assembly_controls_rejected=69, provider_counts={'gauge44': 333},
                           mutations_rejected=15), 'Inherited one-provider freezer metadata')
    spec['expected'].update(metadata)
    dump(path, spec)
    dump(args.work / 'discovery/FREEZE-METADATA.json', dict(
        status='PASS_DERIVED_TWO_PROVIDER_FREEZE_METADATA', before=before, after=metadata,
        derivation=derivation))
    print('PASS_DERIVED_TWO_PROVIDER_FREEZE_METADATA', metadata['assembly_controls_rejected'])


if __name__ == '__main__':
    main()
