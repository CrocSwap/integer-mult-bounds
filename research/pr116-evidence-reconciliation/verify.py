#!/usr/bin/env python3
"""Offline PR116 source identity and historical CI evidence reconciliation.

No contributor verifier is imported or executed. This is not a mathematical
certificate replay. Apache-2.0; Ross Richardson with OpenAI Codex assistance.
"""
import argparse
import base64
from collections import Counter
from datetime import datetime
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

OLD = '97750ec74fc714638c0aa4f31aaa880e56cb8b4d'
NEW = '295a48a3b966428896057a98c6b4834c0b4b7416'
MERGE = '0db8566d07ae1fd7765d5d98fbb32ad22775ed32'
BASE = '8bddbee377e2f3ce1f1247196c4b290d55767d20'
PREFIX = 'research/cube-deferred/'
WORKFLOW = '.github/workflows/cube-deferred.yml'
RUN = 37865435177
KAPPA = Fraction(49349675169, 500000000000000)


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def unique_pairs(pairs):
    d = {}
    for key, value in pairs:
        require(key not in d, 'duplicate JSON key: ' + key)
        d[key] = value
    return d


def json_read(text):
    return json.loads(text, object_pairs_hook=unique_pairs)


def parse_tree(data):
    """Parse Git's binary tree format, independently of git ls-tree/diff."""
    entries = {}
    order = []
    pos = 0
    while pos < len(data):
        end = data.find(b'\0', pos)
        require(end >= 0 and end + 21 <= len(data), 'truncated tree entry')
        pair = data[pos:end].split(b' ', 1)
        require(len(pair) == 2, 'invalid tree entry')
        mode, name = pair
        require(mode in (b'40000', b'100644', b'100755', b'120000', b'160000'), 'tree mode')
        require(name and b'/' not in name and name not in (b'.', b'..'), 'tree name')
        text = name.decode('utf-8')
        require(text not in entries, 'duplicate tree name')
        entries[text] = (mode.decode(), data[end + 1:end + 21].hex())
        order.append(name + (b'/' if mode == b'40000' else b'\0'))
        pos = end + 21
    require(order == sorted(order), 'tree order')
    return entries


def check_ci(receipt, ci):
    recorded = receipt['research_head_ci']
    require(recorded['commit'] == OLD, 'receipt CI head')
    checks = ci['checks']
    require(type(ci['total_count']) is int and ci['total_count'] == len(checks) == 42,
            'CI count or incomplete response')
    require(recorded['successful_checks'] == len(recorded['checks']) == 42, 'receipt check count')
    require(len({c['id'] for c in checks}) == len(checks), 'duplicate check id')
    live = {c['details_url']: c for c in checks}
    require(len(live) == len(checks), 'duplicate check URL')
    saved = {c['detailsUrl']: c for c in recorded['checks']}
    require(len(saved) == len(recorded['checks']) and saved.keys() == live.keys(), 'CI coverage')
    for url, c in live.items():
        require(c['head_sha'] == OLD, 'observed CI head')
        require(c['status'] == 'completed' and c['conclusion'] == 'success', 'CI outcome')
        require(re.fullmatch(r'https://github.com/CrocSwap/integer-mult-bounds/actions/runs/\d+/job/\d+', url), 'CI URL')
        require(int(url.rsplit('/', 1)[1]) == c['id'], 'check URL identity')
        for a, b in [('name', 'name'), ('startedAt', 'started_at'),
                     ('completedAt', 'completed_at'), ('status', 'status'), ('conclusion', 'conclusion')]:
            require(str(saved[url][a]).lower() == str(c[b]).lower(), 'CI field: ' + a)
    counts = Counter(c['workflowName'] for c in saved.values())
    require(counts == {'Verify research artifacts': 36, 'Verify cube deferred witness': 3,
                       'Verify cyclic deferred witness': 3}, 'workflow coverage')
    run = ci['cube_run']
    require(run['id'] == RUN and run['head_sha'] == OLD and run['event'] == 'pull_request'
            and run['path'] == WORKFLOW and run['run_attempt'] == 1
            and run['status'] == 'completed' and run['conclusion'] == 'success', 'focused run provenance')
    focused = {url: c for url, c in live.items() if f'/runs/{RUN}/' in url}
    jobs = ci['cube_jobs']
    require(jobs['total_count'] == len(jobs['jobs']) == len(focused) == 3, 'focused job count')
    require(len({j['id'] for j in jobs['jobs']}) == 3, 'duplicate focused job')
    require({j['html_url'] for j in jobs['jobs']} == focused.keys(), 'focused job coverage')
    require(set(ci['log_excerpts']) == {'focused (3.11)', 'focused (3.13)', 'focused (3.14)'}, 'log coverage')
    for job in jobs['jobs']:
        require(job['head_sha'] == OLD and job['status'] == 'completed'
                and job['conclusion'] == 'success', 'focused job outcome')
        c = focused[job['html_url']]
        require(job['id'] == c['id'] and job['name'] == c['name'] and
                job['started_at'] == c['started_at'] and job['completed_at'] == c['completed_at'], 'focused job identity')
        for command in ('Run python3 research/cube-deferred/verify.py', 'Run git diff --exit-code'):
            steps = [s for s in job['steps'] if s['name'] == command]
            require(len(steps) == 1 and steps[0]['status'] == 'completed'
                    and steps[0]['conclusion'] == 'success', 'required focused step')
        lines = ci['log_excerpts'][job['name']]
        require(all(l.startswith(job['name'] + '\t') for l in lines), 'log job association')
        positions = [i for i, l in enumerate(lines) if 'git log -1 --format=%H' in l]
        require(len(positions) == 1 and positions[0] + 1 < len(lines), 'checkout log command')
        require(lines[positions[0] + 1].split()[-1] == MERGE, 'actual checkout')
        require(any('Ran 14 tests in ' in l for l in lines), 'package controls not logged')
        require(any('PASS read-only finite package verification; inherited transfer remains conditional' in l for l in lines), 'package pass not logged')
    return dict(total_checks=42, focused_jobs=3, workflow_counts=dict(sorted(counts.items())),
                ci_checkout=MERGE, ci_associated_head=OLD)


def check(data):
    require(data['schema'] == 1 and data['base'] == BASE, 'schema or research base')
    require(data['commits'] == dict(historical=OLD, current=NEW, ci_checkout=MERGE), 'commit anchors')
    objects = {}
    used = set()
    for oid, item in data['objects'].items():
        require(re.fullmatch('[0-9a-f]{40}', oid) is not None, 'object id')
        kind = item['type']
        require(kind in ('blob', 'tree', 'commit'), 'object type')
        raw = base64.b64decode(item['base64'], validate=True)
        header = kind.encode() + b' ' + str(len(raw)).encode() + b'\0'
        require(hashlib.sha1(header + raw).hexdigest() == oid, 'Git object digest')
        require(hashlib.sha256(raw).hexdigest() == item['sha256'], 'object SHA256')
        objects[oid] = (kind, raw)

    def get(oid, kind):
        require(oid in objects and objects[oid][0] == kind, 'missing object or incorrect type')
        used.add(oid)
        return objects[oid][1]

    def commit(oid):
        header = get(oid, 'commit').split(b'\n\n', 1)[0].splitlines()
        trees = [l[5:].decode() for l in header if l.startswith(b'tree ')]
        require(len(trees) == 1, 'commit tree')
        return trees[0], [l[7:].decode() for l in header if l.startswith(b'parent ')]

    def flatten(oid, prefix='', ancestors=()):
        require(oid not in ancestors, 'tree cycle')
        result = {}
        for name, (mode, child) in parse_tree(get(oid, 'tree')).items():
            if mode == '40000':
                result.update(flatten(child, prefix + name + '/', ancestors + (oid,)))
            else:
                result[prefix + name] = (mode, child)
        return result

    old_root, _ = commit(OLD)
    new_root, parents = commit(NEW)
    merge_root, merge_parents = commit(MERGE)
    require(parents == [OLD], 'evidence head parent')
    require(merge_parents == ['56b66d58297deca1d7dd130247d720e960f77a37', OLD], 'merge parents')
    require(merge_root == old_root, 'CI checkout tree differs from historical head')
    before, after = flatten(old_root), flatten(new_root)
    changes = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
    require(changes == [PREFIX + p for p in ('README.md', 'SOURCE.json', 'validation.json')], 'unexpected changed paths')
    require(len(before) == 1559 and len(after) == 1560, 'complete tree coverage')
    require(PREFIX + 'validation.json' not in before, 'receipt not newly added')
    require(not any(p.endswith('/full-verify-evidence.tar.gz') or p == 'full-verify-evidence.tar.gz'
                    for p in after), 'local evidence archive unexpectedly available')

    def blob(tree, path):
        require(path in tree and tree[path][0] == '100644', 'expected regular source file')
        return get(tree[path][1], 'blob')

    old_readme = blob(before, PREFIX + 'README.md')
    new_readme = blob(after, PREFIX + 'README.md')
    a, b = old_readme.decode().splitlines(), new_readme.decode().splitlines()
    changed = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    require(len(a) == len(b) and changed == [15] and a[15].startswith('Draft status:')
            and b[15].startswith('Full verification passed on research commit `' + OLD + '`:'), 'README status-only change')
    source_old = json_read(blob(before, PREFIX + 'SOURCE.json'))
    source_new = json_read(blob(after, PREFIX + 'SOURCE.json'))
    require(source_old['package_files']['README.md'] == hashlib.sha256(old_readme).hexdigest()
            and source_new['package_files']['README.md'] == hashlib.sha256(new_readme).hexdigest(), 'README manifest binding')
    normalized = json.loads(json.dumps(source_new))
    normalized['package_files']['README.md'] = source_old['package_files']['README.md']
    require(normalized == source_old, 'unexpected source manifest delta')
    require(len(source_old['package_files']) == 18 and len(source_old['repository_files']) == 24, 'source dependency inventory')
    dependencies = {PREFIX + p for p in source_old['package_files']} | set(source_old['repository_files'])
    require(len(dependencies) == 42 and all(p in before and p in after for p in dependencies), 'missing dependency')
    unchanged = dependencies - {PREFIX + 'README.md'}
    require(all(before[p] == after[p] for p in unchanged), 'dependency source changed')
    certificate = blob(before, PREFIX + 'certificate.json')
    require(hashlib.sha256(certificate).hexdigest() == source_old['package_files']['certificate.json'], 'scientific certificate digest')
    require(Fraction(json_read(certificate)['kappa']) == KAPPA, 'historical kappa')
    workflow = blob(before, WORKFLOW).decode()
    require(before[WORKFLOW] == after[WORKFLOW] and
            '      - run: python3 research/cube-deferred/verify.py' in workflow and
            '      - run: git diff --exit-code' in workflow, 'workflow commands')
    receipt = json_read(blob(after, PREFIX + 'validation.json'))
    require(receipt['research_commit'] == OLD and receipt['verification'] == 'passed', 'local receipt head')
    require(len(receipt['runs']) == 1, 'local run count')
    run = receipt['runs'][0]
    commands = [['make', '-j1', 'verify'], ['python', PREFIX + 'verify.py'],
                ['python', PREFIX + 'test_controls.py']]
    require(run['status']['tested_commit'] == OLD and run['status']['state'] == 'passed'
            and type(run['status']['returncode']) is int and run['status']['returncode'] == 0
            and run['status']['commands'] == run['executed_commands'] == commands
            and run['status']['git_status'] == '' and run['status']['drift'] == []
            and run['source_drift_patch_empty'] is True, 'local author receipt consistency')
    duration = (datetime.fromisoformat(run['status']['completed_at']) -
                datetime.fromisoformat(run['status']['started_at'])).total_seconds()
    require(abs(duration - run['status']['elapsed_seconds']) < .001, 'local receipt duration')
    ci = check_ci(receipt, data['ci'])
    require(used == objects.keys(), 'unreferenced capsule object')
    return dict(status='PASS_PR116_EVIDENCE_RECONCILIATION',
                base=BASE, historical_head=OLD, current_head=NEW,
                tracked_paths_before=len(before), tracked_paths_after=len(after),
                changed_paths=changes, unchanged_dependency_objects=len(unchanged),
                manifest_entries=42, historical_kappa=str(KAPPA),
                git_objects=len(objects), **ci,
                source_delta='README status, matching README pin, and added author receipt only',
                local_archive='Not tracked at either pinned head; original full local run not independently replayed',
                scope='Source identity and recovered historical CI evidence, not mathematical acceptance or a fresh supplier replay')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--certificate', type=Path, default=Path(__file__).with_name('CERTIFICATE.json'))
    p.add_argument('--write-result', type=Path)
    a = p.parse_args()
    result = check(json_read(a.certificate.read_bytes()))
    if a.write_result:
        a.write_result.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    else:
        require(result == json_read(Path(__file__).with_name('RESULT.json').read_bytes()), 'result receipt mismatch')
    print(result['status'], 'changed_paths=3 unchanged_dependencies=41 checks=42 focused_jobs=3')


if __name__ == '__main__':
    main()
