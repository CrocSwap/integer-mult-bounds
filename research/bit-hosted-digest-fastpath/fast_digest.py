"""Exact JSON-line digest adapter. Matthieu Pascal / OpenAI Codex, Apache-2.0.

The original instruction mapping is by the PR463/510 hosted-audit authors;
PR555's parameterizer is by eumemic; the PR589 word is by DreamingOfClouds. No receipt is cached across calls.
"""
import ast
import hashlib
import json
from pathlib import Path
import sys
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
AUDITOR = ('research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/'
           'vendor/e8-r715-eleven-stage-whole/code/audit_hosted_k.py')
PARAMETERIZER = 'research/e8-bit-p111-tuned/code/adapt9p.py'
FIXTURE = 'research/community-hyperplane599-audit/pr589/bit589'


def checked_bytes(path, expected):
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f'source SHA-256 mismatch: {path}')
    return data


def pins():
    return {x['path']: x['sha256'] for x in
            json.loads((PACKAGE / 'SOURCES.json').read_text(encoding='utf-8'))['files']
            if x['usage'] == 'input'}


def load_auditor():
    """Apply only the five hosted-auditor edits listed in frozen adapt9p.py."""
    if not __debug__:
        raise RuntimeError('the inherited auditor requires assertions; remove -O/PYTHONOPTIMIZE')
    sources = pins()
    original = checked_bytes(ROOT / AUDITOR, sources[AUDITOR]).decode('utf-8')
    adapter = checked_bytes(ROOT / PARAMETERIZER, sources[PARAMETERIZER]).decode('utf-8')
    assignments = [n for n in ast.parse(adapter).body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'EDITS' for t in n.targets)]
    if len(assignments) != 1:
        raise ValueError('expected one EDITS dictionary')
    edits_dict = assignments[0].value
    entries = [v for k, v in zip(edits_dict.keys, edits_dict.values)
               if ast.literal_eval(k) == 'audit_hosted_k.py']
    if len(entries) != 1:
        raise ValueError('expected one hosted-auditor edit list')
    edits = ast.literal_eval(entries[0].elts[1])
    if len(edits) != 5:
        raise ValueError('expected five parameterization edits')
    for old, new in edits:
        if original.count(old) != 1:
            raise ValueError('parameterization anchor mismatch')
        original = original.replace(old, new)
    module = types.ModuleType('pinned_hosted_auditor')
    module.__file__ = str(ROOT / AUDITOR)
    exec(compile(original, module.__file__, 'exec'), module.__dict__)
    return module


def encoded(value):
    return json.dumps(value, separators=(',', ':')).encode()


def instruction_chunks(template, chunk_bytes=1024 * 1024):
    """Yield (JSON-line bytes, event count), preserving original mapping/order.

    All tables live for this invocation only. Storage is proportional to the
    local programs, one call's owners and one output chunk, not the expanded
    emitted program. A chunk can exceed the limit by one instruction.
    """
    if chunk_bytes <= 0:
        raise ValueError('chunk_bytes must be positive')
    owner_limit = len(template['calls'][0]['owners'])  # exactly 2*V + R upstream
    private = encoded([template['live'], ['private', 0]])
    programs = {}
    pending = bytearray()
    count = 0
    for call in template['calls']:
        orientation = call['orientation']
        if orientation not in programs:
            instructions = []
            for z in template['local_programs'][orientation]:
                # JSON arrays concatenate at element boundaries. Empty tails
                # need no comma; strings retain json.dumps's escaping rules.
                tail = encoded(z[2:] if z[0] == 0 else z[3:])[1:-1]
                suffix = (b',' + tail if tail else b'') + b']\n'
                instructions.append((b'[' + encoded(z[0]) + b',', z[1],
                                     z[0] != 0, None if z[0] == 0 else z[2], suffix))
            programs[orientation] = instructions
        owners = [encoded(owner) for owner in call['owners']]
        for prefix, destination, has_source, source, suffix in programs[orientation]:
            pending.extend(prefix)
            pending.extend(owners[destination])
            if has_source:
                pending.extend(b',')
                pending.extend(owners[source] if source < owner_limit else private)
            pending.extend(suffix)
            count += 1
            if len(pending) >= chunk_bytes:
                yield bytes(pending), count
                pending.clear()
                count = 0
    if count:
        yield bytes(pending), count


def digest(template):
    h = hashlib.sha256()
    count = 0
    for chunk, events in instruction_chunks(template):
        h.update(chunk)
        count += events
    return h.hexdigest(), count


def main():
    # Same three arguments as the frozen auditor: parent, hosted, output.
    auditor = load_auditor()
    auditor.digest = digest
    auditor.main()


if __name__ == '__main__':
    main()
