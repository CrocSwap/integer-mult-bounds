#!/usr/bin/env python3
"""Capture Git objects for the two pinned PR279 heads; no checkout is changed.

Adam Gall (@adamgall), with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import base64
import json
from pathlib import Path
import subprocess

REVIEWED = '4d8c31eec7ae618645cb058101cb4e72a97268d3'
CANDIDATE = '913ccc48a0bc1173709ea92280b96252256b7754'
PACKAGE = 'research/five-stage-gen4-banks'
WORKFLOW = '.github/workflows/five-stage-gen4-banks.yml'


def git(*args):
    return subprocess.check_output(['git', *args])


def entries(raw):
    result = {}
    pos = 0
    while pos < len(raw):
        end = raw.index(b'\0', pos)
        mode, name = raw[pos:end].split(b' ', 1)
        result[name.decode('utf-8')] = (mode.decode('ascii'), raw[end + 1:end + 21].hex())
        pos = end + 21
    return result


def capture():
    trees = {}

    def tree(oid):
        if oid not in trees:
            trees[oid] = git('cat-file', 'tree', oid)
        return entries(trees[oid])

    commits = {oid: git('cat-file', 'commit', oid) for oid in (REVIEWED, CANDIDATE)}
    roots = [commits[oid].splitlines()[0].split()[1].decode() for oid in (REVIEWED, CANDIDATE)]

    def subtree(oid):
        for mode, child in tree(oid).values():
            if mode == '40000':
                subtree(child)

    def path(root, name, recursive=False):
        oid = root
        for part in name.split('/'):
            mode, oid = tree(oid)[part]
        if recursive:
            subtree(oid)

    def changed(left, right):
        if left == right:
            return
        old, new = tree(left), tree(right)
        for name in old.keys() | new.keys():
            a, b = old.get(name), new.get(name)
            if a == b:
                continue
            if a and b and a[0] == b[0] == '40000':
                changed(a[1], b[1])
            else:
                for item in (a, b):
                    if item and item[0] == '40000':
                        subtree(item[1])

    changed(*roots)
    for root in roots:
        path(root, PACKAGE, recursive=True)
        path(root, WORKFLOW)
    return {
        'schema': 'pr279-parent-git-proof/1',
        'commits': {oid: base64.b64encode(raw).decode() for oid, raw in commits.items()},
        'trees': {oid: base64.b64encode(raw).decode() for oid, raw in sorted(trees.items())},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(capture(), stream, indent=2, sort_keys=True)
        stream.write('\n')


if __name__ == '__main__':
    main()
