#!/usr/bin/env python3
"""Regenerate the inventory and permanent axiom audit after reviewed changes."""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
MODULES = ['LevelSourceData', 'LevelFrameJoins', 'LevelSchedule', 'BaseLevel']


def declarations():
    result = []
    for module in MODULES:
        text = (HERE / (module + '.lean')).read_text()
        # These modules each use one explicit namespace. Anonymous derived
        # declarations are covered transitively by the named declarations.
        namespaces = re.findall(r'^namespace (\w+)\s*$', text, re.M)
        if namespaces != ['PR442LevelModel']:
            raise RuntimeError('Review audit extraction for ' + module)
        for kind, name in re.findall(
                r'^(?:noncomputable )?(def|abbrev|theorem|lemma)\s+(\w+)', text, re.M):
            result.append({'module': module, 'kind': kind,
                           'name': 'PR442LevelModel.' + name})
    return result


def main():
    decls = declarations()
    statements = ['# Exact Phase 1 theorem statements\n',
                  'AI-written inventory extracted from the Lean sources. '
                  'All declarations are in `PR442LevelModel`. '
                  'This file is documentation; `Audit.lean` is the permanent axiom inventory.\n']
    for module in MODULES:
        source = (HERE / (module + '.lean')).read_text()
        for match in re.finditer(r'^theorem (\w+)\b', source, re.M):
            rest = source[match.start():]
            proof = re.search(r'\s*:=\s*by\b', rest)
            if proof is None:
                raise RuntimeError('Review theorem statement extraction: ' + match[1])
            line = source[:match.start()].count('\n') + 1
            statements.append(f'\n`{module}.lean:{line}`\n\n```lean\n'
                              + rest[:proof.start()].rstrip() + '\n```\n')
    (HERE / 'THEOREMS.md').write_text('\n'.join(statements))
    audit = ('import BaseLevel\nimport LevelSchedule\n\n'
             '/-! Permanent audit of every named definition and theorem in Phase 1. -/\n'
             + ''.join('#print axioms ' + row['name'] + '\n' for row in decls))
    (HERE / 'Audit.lean').write_text(audit)
    paths = [p for p in HERE.rglob('*') if p.is_file()
             and not any(x in ('.lake', '__pycache__', 'validation')
                         for x in p.relative_to(HERE).parts)
             and p.name != 'MANIFEST.json']
    files = {p.relative_to(HERE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(paths)}
    workflow = '../../.github/workflows/pr442-level-model.yml'
    manifest = {'schema': 1, 'scope': 'PR442 two-child level model, Phase 1 only',
                'workflow': {'path': workflow, 'sha256': hashlib.sha256(
                    (HERE / workflow).read_bytes()).hexdigest()},
                'modules': MODULES, 'declarations': decls, 'files': files}
    (HERE / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Manifest: {len(files)} files; audit: {len(decls)} declarations')


if __name__ == '__main__':
    main()
