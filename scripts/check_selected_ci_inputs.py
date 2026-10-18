#!/usr/bin/env python3
"""Fast guard for live-checkout inputs of the selected cold replay.

The selected `reproduce` command passes `--main ROOT` to package stages that
hash-assert repository files outside the selected package roots, through each
root's data/UPSTREAM-PINS.json and construction/INPUTS.json `files.main`. Its
first stage also checks the checkpoint records the driver names. The per-PR
check of the selected record (verify_selected_result.py) covers neither, so a
changed byte could otherwise surface only inside the cold replay.

Hard checks (standard library only, about a second):
1. every such live pin matches the checkout, with no conflicting pins, and any
   in-root pin equals the selected source inventory;
2. every selected-result-format record named by the driver's static script
   closure passes verify_selected_result.check.

Advisory report (enforced only with --require-triggers): the one workflow whose
run commands invoke the driver, or its make target, must trigger on push and
pull_request for every live pin, every inventoried root file, the driver's
script closure and the repository files that closure names, including the
named records' certificates, manifests and inventories. Trigger
forms this reader cannot evaluate exactly are reported, never assumed.

A trigger and drift guard, not a replay or a mathematical check.
Sagar Thakrar with substantial Anthropic Claude assistance. Apache-2.0.
"""
import argparse
import ast
from functools import lru_cache
from hashlib import sha256
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PIN_FILES = ('data/UPSTREAM-PINS.json', 'construction/INPUTS.json')
EVENTS = ('push', 'pull_request')
RECORD_KEYS = {'kappa', 'certificate', 'certificate_sha256', 'source_manifest', 'proof_supplements'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_bytes())


def relative(name):
    p = PurePosixPath(name) if type(name) is str else None
    require(p is not None and name and not p.is_absolute() and '..' not in p.parts and
            p.as_posix() == name and '\\' not in name, 'Invalid repository path: ' + repr(name))
    return name


def inside(name, roots):
    return any(name == r or name.startswith(r + '/') for r in roots)


def live_pins(root=ROOT):
    """Return (record, manifest, pins) for pinned files outside the selected roots."""
    record = read(root/'certificates/selected-result.json')
    manifest = read(root/relative(record['source_manifest']))
    roots = [relative(r) for r in manifest['package_roots']]
    pins = {}
    for package in roots:
        for name in PIN_FILES:
            path = root/package/name
            if not path.is_file():
                continue
            value = read(path)
            if name.endswith('INPUTS.json'):
                value = value['files']['main']
            require(type(value) is dict, 'Pin map is not an object: ' + package + '/' + name)
            for rel, digest in value.items():
                relative(rel)
                require(type(digest) is str and re.fullmatch('[0-9a-f]{64}', digest), 'Invalid pin: ' + rel)
                if inside(rel, roots):
                    require(manifest['files'].get(rel) == digest,
                            'Live pin differs from the selected source inventory: ' + rel)
                    continue
                require(pins.setdefault(rel, digest) == digest, 'Conflicting live pins: ' + rel)
    return record, manifest, pins


def drift(pins, root=ROOT):
    bad = []
    for rel, digest in sorted(pins.items()):
        path = root/rel
        if not path.is_file() or sha256(path.read_bytes()).hexdigest() != digest:
            bad.append(rel)
    return bad


def driver(record, root=ROOT):
    """Return (make target, driver script) for the record's reproduce command."""
    words = record['reproduce'].split()
    require(len(words) == 2 and words[0] == 'make', 'Unsupported reproduce command')
    lines = (root/'Makefile').read_text().splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith(words[1] + ':')]
    require(len(starts) == 1, 'Reproduce target not unique in Makefile')
    scripts = []
    for line in lines[starts[0]+1:]:
        if not line.startswith('\t'):
            break
        scripts += re.findall(r'scripts/[\w.-]+\.py', line)
    require(len(set(scripts)) == 1, 'Reproduce target must run exactly one driver script')
    return words[1], scripts[0]


def closure(script, root=ROOT):
    """Local script imports and existing repository files named by string literals."""
    seen, files, todo = set(), set(), [script]
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen.add(name)
        for node in ast.walk(ast.parse((root/name).read_bytes())):
            modules = []
            if isinstance(node, ast.Import):
                modules = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                modules = [node.module]
            for module in modules:
                local = 'scripts/' + module.split('.')[0] + '.py'
                if (root/local).is_file():
                    todo.append(local)
            if isinstance(node, ast.Constant) and type(node.value) is str and '/' in node.value:
                value = node.value.rstrip('/')
                if not value.startswith('/') and '..' not in value.split('/') and (root/value).is_file():
                    files.add(value)
                    if value.startswith('scripts/') and value.endswith('.py'):
                        todo.append(value)
    return sorted(seen), sorted(files - seen)


def named_records(named, root=ROOT):
    """Closure-named JSON files in selected-result format (checkpoint records)."""
    out = []
    for name in named:
        if name.startswith('certificates/') and name.endswith('.json'):
            value = read(root/name)
            if type(value) is dict and RECORD_KEYS <= set(value):
                out.append(name)
    return out


def check_records(names, root=ROOT):
    """Run the repository's own selected-record check on each named record."""
    spec = importlib.util.spec_from_file_location('ci_inputs_selected_result', root/'scripts/verify_selected_result.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    failures, files = {}, set()
    for name in names:
        record = read(root/name)
        try:
            module.check(record, root, historical=name != 'certificates/selected-result.json')
        except (ValueError, KeyError, OSError) as error:
            failures[name] = str(error)
        # Proof supplements and reviews are hard-checked above on every PR; the
        # replay trigger needs the certificate, manifest and inventory.
        manifest = read(root/record['source_manifest'])
        files |= {record['certificate'], record['source_manifest'], *manifest['files']}
    return failures, files


def strip_comment(line):
    return '' if line.lstrip().startswith('#') else line.split(' #')[0].rstrip()


def indent(line):
    return len(line) - len(line.lstrip())


def key(line):
    return line.strip().split(':', 1)[0].strip().strip('\'"')


def event_paths(text, event):
    """Read `on.<event>` path filters from block-style workflows.

    Returns None if the event is absent, [] if it has no path filter and the
    list of patterns otherwise. Any other filter (paths-ignore, branches without
    main, types, tags, ...) raises, because its effect is not evaluated here.
    """
    lines = [strip_comment(line) for line in text.splitlines()]
    top = [i for i, line in enumerate(lines) if indent(line) == 0 and line and key(line) == 'on'
           and line.strip().endswith(':')]
    require(len(top) == 1, 'Workflow needs one block-style on: key')
    body = []
    for line in lines[top[0]+1:]:
        if line and indent(line) == 0:
            break
        body.append(line)
    heads = [i for i, line in enumerate(body) if line and key(line) == event]
    if not heads:
        return None
    require(len(heads) == 1 and body[heads[0]].strip().endswith(':'), 'Unsupported ' + event + ' form')
    event_indent, section = indent(body[heads[0]]), []
    for line in body[heads[0]+1:]:
        if line and indent(line) <= event_indent:
            break
        section.append(line)
    entries = [i for i, line in enumerate(section) if line and not line.lstrip().startswith('-')]
    child = min((indent(section[i]) for i in entries), default=None)
    filters = {}
    for i in entries:
        require(indent(section[i]) == child and ':' in section[i], 'Unsupported ' + event + ' layout')
        name, rest = key(section[i]), section[i].split(':', 1)[1].strip()
        require(name not in filters, 'Repeated ' + event + ' key: ' + name)
        if rest:
            require(rest.startswith('[') and rest.endswith(']'), 'Unsupported ' + event + '.' + name)
            filters[name] = [x.strip().strip('\'"') for x in rest[1:-1].split(',') if x.strip()]
            continue
        items = []
        for line in section[i+1:]:
            if not line:
                continue
            if not line.lstrip().startswith('-'):
                break
            items.append(line.strip()[1:].strip().strip('\'"'))
        filters[name] = items
    unsupported = set(filters) - {'paths', 'branches'}
    require(not unsupported, 'Unsupported ' + event + ' filter: ' + ', '.join(sorted(unsupported)))
    if 'branches' in filters:
        require('main' in filters['branches'] and triggers(filters['branches'], 'main'),
                event + ' branch filter excludes main')
    return filters.get('paths', [])


@lru_cache(maxsize=None)
def glob_regex(pattern):
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith('**/', i):
            out.append('(?:.*/)?')
            i += 3
        elif pattern.startswith('**', i):
            out.append('.*')
            i += 2
        elif pattern[i] == '*':
            out.append('[^/]*')
            i += 1
        else:
            # GitHub gives ? and + quantifier meanings; fail closed rather than emulate them.
            require(pattern[i] not in '?+[]{}', 'Unsupported glob syntax: ' + pattern)
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile('^' + ''.join(out) + '$')


def triggers(patterns, name):
    """GitHub semantics: patterns apply in order; a later !pattern excludes."""
    if patterns is None:
        return False
    if not patterns:
        return True
    matched = False
    for pattern in patterns:
        negate = pattern.startswith('!')
        if glob_regex(pattern[1:] if negate else pattern).match(name):
            matched = not negate
    return matched


def run_commands(text):
    """Shell commands of `run:` steps, including block scalars."""
    lines, out, i = text.splitlines(), [], 0
    while i < len(lines):
        line = strip_comment(lines[i])
        item = line.strip()
        if item.startswith('- '):
            item = item[2:].lstrip()
        if item.startswith('run:'):
            rest = item[4:].strip()
            if rest[:1] in ('|', '>'):
                base = indent(line)
                i += 1
                while i < len(lines) and (not lines[i].strip() or indent(lines[i]) > base):
                    out.append(lines[i].strip())
                    i += 1
                continue
            out.append(rest)
        i += 1
    return out


def replay_workflow(target, script, root=ROOT):
    found = []
    for path in sorted((root/'.github/workflows').glob('*.y*ml')):
        commands = run_commands(path.read_text())
        if any(script in c or re.search(r'\bmake\b.*\b' + re.escape(target) + r'\b', c) for c in commands):
            found.append(path)
    require(len(found) == 1, 'Expected one workflow running ' + script + ', found ' +
            str([p.name for p in found]))
    return found[0]


def required_paths(record, manifest, pins, scripts, named, record_files, workflow):
    return sorted(set(pins) | set(manifest['files']) | set(scripts) | set(named) | set(record_files) |
                  {record['source_manifest'], record['certificate'], workflow})


def coverage(root, record, manifest, pins, target, script, scripts, named, record_files):
    workflow = replay_workflow(target, script, root)
    required = required_paths(record, manifest, pins, scripts, named, record_files,
                              workflow.relative_to(root).as_posix())
    text = workflow.read_text()
    uncovered = {}
    for event in EVENTS:
        patterns = event_paths(text, event)
        uncovered[event] = [p for p in required if not triggers(patterns, p)]
    return workflow.relative_to(root).as_posix(), len(required), uncovered


def check(root=ROOT):
    record, manifest, pins = live_pins(root)
    result = dict(live_pins=len(pins), pin_drift=drift(pins, root), driver=None, driver_closure=[],
                  named_files=[], named_records=[], record_failures={}, workflow=None,
                  required_paths=None, uncovered=None, coverage_error=None)
    try:
        target, script = driver(record, root)
        scripts, named = closure(script, root)
    except ValueError as error:
        # A reproduce command this guard cannot resolve is reported, not blocking.
        result['coverage_error'] = 'Driver not resolved: ' + str(error)
        return result
    records = named_records(named, root)
    failures, record_files = check_records(records, root)
    result.update(driver=script, driver_closure=scripts, named_files=named, named_records=records,
                  record_failures=failures)
    try:
        workflow, count, uncovered = coverage(root, record, manifest, pins, target, script,
                                              scripts, named, record_files)
        result.update(workflow=workflow, required_paths=count, uncovered=uncovered)
    except ValueError as error:
        result['coverage_error'] = str(error)
    return result


def complete(result):
    return result['coverage_error'] is None and not any(result['uncovered'].values())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--require-triggers', action='store_true',
                        help='also fail unless the replay workflow triggers on every required path')
    args = parser.parse_args(argv)
    result = check(args.root.resolve())
    ok = not result['pin_drift'] and not result['record_failures']
    if args.require_triggers:
        ok = ok and complete(result)
    print(json.dumps(result, indent=1))
    if not complete(result):
        print('ADVISORY: replay workflow triggers are incomplete or not evaluable')
    print('PASS_SELECTED_CI_INPUTS' if ok else 'FAIL_SELECTED_CI_INPUTS')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
