#!/usr/bin/env python3
"""Rebuild a selected producer and its literal whole-chain clone edits.

Only the pinned public source, authored campaign code and retained JSON
witnesses are needed. All derived DAGs, labels, executables and audit outputs
are written to a fresh external directory. No old execution file is read.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

from check_compiled_witness import check
from positive_clone_search import opportunities, rewrite
from producer_search import digest, initialize, worker


def producer(document):
    return dict(document['producer']) if 'producer' in document else dict(document)


def rebuild(source, work, parent_path, selected_path, dirty=False):
    source, work = Path(source).resolve(), Path(work).resolve()
    assert source.is_dir() and not work.exists()
    work.mkdir(parents=True)
    builds = work / 'builds'
    builds.mkdir()
    authored = Path(__file__).resolve().parent
    parent = producer(json.loads(Path(parent_path).read_text()))
    selected = json.loads(Path(selected_path).read_text())
    config = dict(parent['configuration'])
    envelope_source = (authored / 'frame_match_envelope.cpp' if 'frame_mode' in config
                       else source / 'scripts' / 'partial_swap' / 'match_exported_dag.cpp')
    for src, name in ((envelope_source, 'match_exported_dag'),
                      (authored / 'moment_match_positive.cpp', 'moment_match_positive'),
                      (authored / 'moment_match_rank_node.cpp', 'moment_match_rank_node')):
        subprocess.run(['c++', '-O3', '-std=c++17', str(src), '-o', str(builds / name)], check=True)
    initialize(source, work, builds / 'moment_match_positive')
    if 'hierarchy_policy' in config:
        from hierarchy_clone_search import configure_points
        configure_points(config)
        evaluate = worker
    elif 'reflection_mode' in config:
        from alternating_refinement import evaluate
    elif 'point_policy' in config:
        from point_order_search import evaluate
    elif 'frame_mode' in config:
        from refine_tree_search import evaluate
    else:
        evaluate = worker
    row = evaluate(config)
    assert row['status'] != 'failed', row
    assert row['dag_sha256'] == parent['dag_sha256'], 'Initial DAG differs'
    assert row['positive_sha256'] == parent['positive_sha256'], 'Initial literal frames differ'
    assert row['witness_sha256'] == parent['witness_sha256'], 'Initial actual matching differs'
    initial = dict(row)
    stages = []
    clone_config = selected['producer']['configuration']
    policy, limit, seed = (clone_config[k] for k in ('policy', 'limit', 'seed'))
    for index, recorded in enumerate(selected['stages']):
        jobs, diagnostics, order, frames = opportunities(row, limit, policy, seed + 1000003 * index)
        if recorded.get('terminal'):
            assert not jobs, 'Recorded terminal round now has eligible clones'
            break
        assert jobs == recorded['chosen'], 'Selected complete chains differ'
        target = work / 'clones' / f'round-{index+1}'
        dag, constructed = rewrite(row, jobs, order, frames, target)
        witness = target / 'selected-links.json'
        matched = subprocess.run([str(builds / 'moment_match_rank_node'), str(dag),
                                  str(dag) + '.positive', str(seed + index), '2', str(witness)],
                                 text=True, capture_output=True, check=True)
        new = json.loads(matched.stdout)
        assert new['R'] == recorded['new_roles']
        assert digest(dag) == recorded['new_dag_sha256'], 'Edited scalar DAG differs'
        new.update(dag_path=str(dag), dag_sha256=digest(dag),
                   positive_sha256=digest(str(dag) + '.positive'), witness_path=str(witness),
                   witness_sha256=digest(witness), schedule='rank-node',
                   configuration=dict(policy=policy, limit=limit, seed=seed, round=index+1))
        stages.append(dict(round=index+1, clones=len(jobs), R=new['R'],
                           dag_sha256=new['dag_sha256'], rewrite_path=str(target/'rewrite.json')))
        row = new
    expected = selected['producer']
    assert row['dag_sha256'] == expected['dag_sha256']
    assert row['positive_sha256'] == expected['positive_sha256']
    assert row['histogram'] == expected['histogram']
    assert row['witness_sha256'] == expected['witness_sha256']
    audit = check(dict(producer=row), dirty)
    result = dict(status='complete selected rebuild and independent audit PASS',
                  source_revision='11817ccacb564bb7f98789c20dc11d3fece207e3',
                  parent_fixture=str(parent_path), selected_fixture=str(selected_path),
                  parent_fixture_sha256=digest(parent_path), selected_fixture_sha256=digest(selected_path),
                  initial_producer=initial, producer=row, stages=stages, independent=audit,
                  source_sha256={p.name:digest(p) for p in authored.glob('*.py')},
                  command=sys.argv, completed_utc=datetime.now(timezone.utc).isoformat())
    (work / 'rebuild-result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(dict(status=result['status'], h=row['h'], R=row['R'],
                          clones=sum(s['clones'] for s in stages), audit=audit['status'])), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--parent', type=Path, required=True)
    parser.add_argument('--selected', type=Path, required=True)
    parser.add_argument('--dirty', action='store_true')
    args = parser.parse_args()
    rebuild(args.source, args.work, args.parent, args.selected, args.dirty)


if __name__ == '__main__':
    main()
