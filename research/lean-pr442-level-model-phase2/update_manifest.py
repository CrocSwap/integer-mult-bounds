#!/usr/bin/env python3
"""Regenerate reviewed Phase 2 inventory, exact statements and axiom probes.

This is a maintainer operation, never a verification step. Frozen predecessor
hashes in PROTECTED-FILES.json and published pins in SOURCES.json are not changed.
"""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
MODULES = ['FieldEntrance', 'RouteTransport', 'EntranceContinuity', 'IdleOperators']
NAMESPACE = 'PR442LevelModel.Phase2'
WORKFLOW = '../../.github/workflows/pr442-level-model-phase2.yml'


def declarations():
    rows = []
    for module in MODULES:
        source = (HERE / (module + '.lean')).read_text()
        namespaces = re.findall(r'^namespace (\S+)\s*$', source, re.M)
        if namespaces != [NAMESPACE]:
            raise RuntimeError('Review namespace inventory extraction: ' + module)
        # Each new declaration must be named. Generated anonymous declarations
        # from a named definition are included transitively in its axiom probe.
        if re.search(r'^(?:noncomputable )?(instance|structure|inductive|class)\b', source, re.M):
            raise RuntimeError('Review generated declaration audit: ' + module)
        for kind, name in re.findall(
                r'^(?:noncomputable )?(def|abbrev|theorem|lemma)\s+([^\s:(]+)', source, re.M):
            rows.append({'module': module, 'kind': kind, 'name': NAMESPACE + '.' + name})
    names = [row['name'] for row in rows]
    if len(names) != len(set(names)):
        raise RuntimeError('Duplicate audited declaration')
    return rows


def theorem_document():
    parts = ['# Exact Phase 2 theorem statements\n',
             'AI-assisted inventory extracted from the Lean sources. All declarations '
             'are in `PR442LevelModel.Phase2`. This document does not establish '
             'compilation; the validation receipt records measured results.\n']
    for module in MODULES:
        source = (HERE / (module + '.lean')).read_text()
        for match in re.finditer(r'^(theorem|lemma)\s+([^\s:(]+)\b', source, re.M):
            tail = source[match.start():]
            proof = re.search(r'\s*:=', tail)
            if proof is None:
                raise RuntimeError('Review theorem extraction: ' + match[2])
            line = source[:match.start()].count('\n') + 1
            parts.append(f'\n`{module}.lean:{line}`\n\n```lean\n'
                         + tail[:proof.start()].rstrip() + '\n```\n')
    return '\n'.join(parts)


def main():
    rows = declarations()
    (HERE / 'THEOREMS.md').write_text(theorem_document())
    audit = (''.join('import ' + module + '\n' for module in MODULES) + '\n'
             '/-! Permanent axiom audit of every named Phase 2 definition and theorem. -/\n'
             + ''.join('#print axioms ' + row['name'] + '\n' for row in rows))
    (HERE / 'Audit.lean').write_text(audit)
    paths = [p for p in HERE.rglob('*') if p.is_file()
             and not any(x in ('.lake', '__pycache__', 'validation')
                         for x in p.relative_to(HERE).parts)
             and p.name != 'MANIFEST.json']
    files = {p.relative_to(HERE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(paths)}
    manifest = {'schema': 1, 'scope': 'PR442 children 1 and 2, all 120 ports and both sides',
                'workflow': {'path': WORKFLOW, 'sha256': hashlib.sha256(
                    (HERE / WORKFLOW).read_bytes()).hexdigest()},
                'modules': MODULES, 'declarations': rows, 'files': files}
    (HERE / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Manifest: {len(files)} files; audit: {len(rows)} declarations; '
          f'theorems: {sum(r["kind"] in ("theorem", "lemma") for r in rows)}')


if __name__ == '__main__':
    main()
