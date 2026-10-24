#!/usr/bin/env python3
"""Read-only portable verification of the declared source/edit/product/budget scopes.
Prepared by Chris R / Clear1nsight with substantial OpenAI Codex assistance.
Apache-2.0. This wrapper does not emit or execute a changed native word.
"""
from pathlib import Path
import importlib.util
import json
from hashlib import sha256

HERE = Path(__file__).resolve().parent


def main():
    spec = importlib.util.spec_from_file_location('centre0_portable', HERE / 'portable.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    manifest = json.loads((HERE / 'PACKAGE-FILES.json').read_bytes())
    module.authenticate(HERE, manifest)
    module.authenticate(HERE, json.loads((HERE / 'ARCHIVE-FILES.json').read_bytes()))
    selected = json.loads((HERE / 'INDEPENDENT-SELECTION.json').read_bytes())
    combined = HERE / 'provenance/INDEPENDENT-COMBINED-FREEZE.json'
    module.need(sha256(combined.read_bytes()).hexdigest() == selected['original_combined_manifest_sha256'], 'Original independent freeze index')
    module.authenticate(HERE / 'evidence/outputs/new-approach-verification-20261023', selected['selected_A_files'])
    result = module.run()
    module.authenticate(HERE, manifest)
    print(json.dumps({'status': 'PASS_ACTUAL_CENTRE0_SOURCE_AUDIT_SCOPED', **result}, sort_keys=True))


if __name__ == '__main__':
    main()
