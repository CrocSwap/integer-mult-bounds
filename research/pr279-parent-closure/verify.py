#!/usr/bin/env python3
"""Authenticate PR279's complete retained parent inventory to its Git commit.

No network, Git executable, checkout metadata, or mathematical replay is used.
Adam Gall (@adamgall), with substantial OpenAI Codex assistance. Apache-2.0.
"""
import base64
from collections import Counter
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMPANION = ROOT / 'research/pr279-target-prefix-reconciliation'
PACKAGE = 'research/five-stage-gen4-banks'
WORKFLOW = '.github/workflows/five-stage-gen4-banks.yml'
REVIEWED = '4d8c31eec7ae618645cb058101cb4e72a97268d3'
CANDIDATE = '913ccc48a0bc1173709ea92280b96252256b7754'
PINS = {
    'verify.py': '8af5b16b17f586b9971b9ce4d5b5beb2ab113c2f3c6b96e180fb9d1e0b9e53a4',
    'SOURCE.json': '6208c7f90a03fb6093241f964674bf0d18445ec193385c8558db082c48ea1e40',
    'EVIDENCE.json': '5144c468cf42ee64d1a28a6e8f6c59f295485dce2a56af61233732f63a93f957',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def object_id(kind, data):
    return sha1(kind.encode('ascii') + b' ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def parse_tree(raw):
    result = {}
    position = 0
    while position < len(raw):
        end = raw.find(b'\0', position)
        require(end >= position and end + 21 <= len(raw), 'Truncated Git tree entry')
        header = raw[position:end].split(b' ', 1)
        require(len(header) == 2, 'Malformed Git tree header')
        mode, name = header[0].decode('ascii'), header[1].decode('utf-8')
        require(mode in ('40000', '100644', '100755', '120000', '160000'), 'Invalid Git mode')
        require(name not in ('', '.', '..') and '/' not in name and name not in result,
                'Ambiguous Git tree name')
        result[name] = (mode, raw[end + 1:end + 21].hex())
        position = end + 21
    return result


class Proof:
    def __init__(self, document):
        require(document['schema'] == 'pr279-parent-git-proof/1', 'Wrong proof schema')
        require(set(document['commits']) == {REVIEWED, CANDIDATE}, 'Wrong commit inventory')
        self.commits = {}
        self.trees = {}
        self.used = set()
        for kind, encoded, destination in (
                ('commit', document['commits'], self.commits),
                ('tree', document['trees'], self.trees)):
            for oid, text in encoded.items():
                raw = base64.b64decode(text, validate=True)
                require(object_id(kind, raw) == oid, 'Git object hash mismatch: ' + oid)
                destination[oid] = raw
        candidate_headers = self.commits[CANDIDATE].split(b'\n\n', 1)[0].splitlines()
        require([row for row in candidate_headers if row.startswith(b'parent ')] ==
                [b'parent ' + REVIEWED.encode('ascii')], 'Wrong reviewed parent')

    def root(self, commit):
        first = self.commits[commit].splitlines()[0]
        require(first.startswith(b'tree '), 'Missing commit tree')
        return first[5:].decode('ascii')

    def tree(self, oid):
        require(oid in self.trees, 'Missing tree proof: ' + oid)
        self.used.add(oid)
        return parse_tree(self.trees[oid])

    def at(self, root, path):
        mode, oid = '40000', root
        for component in path.split('/'):
            require(mode == '40000', 'Non-directory path prefix')
            entries = self.tree(oid)
            require(component in entries, 'Missing source path: ' + path)
            mode, oid = entries[component]
        return mode, oid

    def leaves(self, mode, oid, prefix=''):
        if mode != '40000':
            return {prefix: (mode, oid)}
        files = {}
        for name, child in self.tree(oid).items():
            path = prefix + '/' + name if prefix else name
            files.update(self.leaves(*child, path))
        return files

    def changes(self, old, new, prefix=''):
        if old == new:
            return {}
        if old and new and old[0] == new[0] == '40000':
            a, b = self.tree(old[1]), self.tree(new[1])
            result = {}
            for name in sorted(a.keys() | b.keys()):
                path = prefix + '/' + name if prefix else name
                result.update(self.changes(a.get(name), b.get(name), path))
            return result
        a = self.leaves(*old, prefix) if old else {}
        b = self.leaves(*new, prefix) if new else {}
        return {name: (a.get(name), b.get(name)) for name in a.keys() | b.keys()
                if a.get(name) != b.get(name)}


def compare_payloads(entries, payloads, label):
    require(set(entries) == set(payloads), label + ': incomplete or additional file coverage')
    for path, data in payloads.items():
        mode, oid = entries[path]
        require(mode in ('100644', '100755'), label + ': non-regular source file')
        require(object_id('blob', data) == oid, label + ': wrong blob at ' + path)


def audit(document, candidate, historical, workflow, comparison, source):
    proof = Proof(document)
    old_root, new_root = proof.root(REVIEWED), proof.root(CANDIDATE)
    old_package = proof.at(old_root, PACKAGE)
    new_package = proof.at(new_root, PACKAGE)
    old_files = proof.leaves(*old_package)
    new_files = proof.leaves(*new_package)
    require((len(old_files), len(new_files)) == (113, 115), 'Unexpected package cardinality')
    compare_payloads(old_files, historical, 'Reviewed package')
    compare_payloads(new_files, candidate, 'Candidate package')
    old_workflow, new_workflow = proof.at(old_root, WORKFLOW), proof.at(new_root, WORKFLOW)
    require(old_workflow == new_workflow, 'Workflow changed')
    compare_payloads({WORKFLOW: new_workflow}, {WORKFLOW: workflow}, 'Workflow')

    changes = proof.changes(('40000', old_root), ('40000', new_root))
    require(len(changes) == 12, 'Unexpected repository-wide update count')
    recorded_changes = {PACKAGE + '/' + row['path']: row for row in source['changes']}
    require(set(changes) == set(recorded_changes), 'Source update misses a repository change')
    statuses = Counter()
    for path, (old, new) in changes.items():
        require(new is not None and new[0] in ('100644', '100755'), 'Deleted or special update')
        if old:
            require(old[0] == new[0], 'Unexpected mode change')
        status = 'modified' if old else 'added'
        statuses[status] += 1
        row = recorded_changes[path]
        require((row['status'], row['old_git_blob'], row['new_git_blob']) ==
                (status, old[1] if old else None, new[1]), 'Incorrect update attribution')
    require(statuses == {'modified': 10, 'added': 2}, 'Wrong change classification')

    universe = {PACKAGE + '/' + name: entry for name, entry in new_files.items()}
    universe[WORKFLOW] = new_workflow
    matched, unresolved = comparison['matched'], comparison['unresolved']
    rows = matched + unresolved
    require(comparison['total'] == len(rows) == len(universe) == 116, 'Wrong parent inventory size')
    require(len({row['path'] for row in rows}) == len(rows), 'Duplicate parent inventory path')
    require({row['path'] for row in rows} == set(universe), 'Parent inventory path omission')
    for row in rows:
        require(row['blob'] == universe[row['path']][1], 'Parent inventory blob mismatch')
    require(len(matched) == 104 and len(unresolved) == 12, 'Wrong coverage partition')
    require({row['path'] for row in unresolved} == set(changes), 'Wrong unresolved partition')
    require(proof.used == set(proof.trees), 'Unused tree proof objects')
    return {
        'status': 'PASS_PR279_PARENT_COMMIT_CLOSURE',
        'reviewed_head': REVIEWED, 'candidate_head': CANDIDATE,
        'reviewed_tree': old_root, 'candidate_tree': new_root,
        'reviewed_package_tree': old_package[1], 'candidate_package_tree': new_package[1],
        'authenticated_commits': 2, 'authenticated_trees': len(proof.trees),
        'parent_paths': len(universe), 'retained_paths': len(matched),
        'companion_paths': len(unresolved), 'repository_changes': dict(sorted(statuses.items())),
        'fresh_mathematical_execution': False,
        'scope': 'Source identity and retained evidence only; parent disposition remains a maintainer decision.',
    }


def load_inputs():
    for name, digest in PINS.items():
        require(sha256((COMPANION / name).read_bytes()).hexdigest() == digest,
                'Changed inherited checker or evidence metadata: ' + name)
    spec = importlib.util.spec_from_file_location('pr279_companion', COMPANION / 'verify.py')
    companion = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(companion)
    source, candidate = companion.collect_candidate(ROOT, COMPANION)
    retained = companion.check_retained_evidence(COMPANION, source)
    historical_root = ROOT / PACKAGE
    old_names = set(json.loads((historical_root / 'MANIFEST.json').read_text(encoding='utf-8'))['files'])
    historical = {name: (historical_root / name).read_bytes() for name in old_names | {'MANIFEST.json'}}
    comparison = json.loads((ROOT / 'research/pr-reconciliation-20261012/content-comparison.json')
                            .read_text(encoding='utf-8'))['279']
    document = json.loads((HERE / 'TREE-PROOF.json').read_text(encoding='utf-8'))
    return (document, candidate, historical, (ROOT / WORKFLOW).read_bytes(), comparison, source), retained


def main():
    inputs, retained = load_inputs()
    report = audit(*inputs)
    report['retained_replay'] = retained
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
