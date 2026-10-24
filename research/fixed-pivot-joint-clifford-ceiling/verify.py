#!/usr/bin/env python3
"""Read-only replay of three separate frozen geometric certificates.
Prepared by Chris R / Clear1nsight with substantial OpenAI Codex assistance.
Apache-2.0. No author search/census/model/native/compiler is executed.
"""
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent


def main():
    spec = importlib.util.spec_from_file_location('joint_clifford_portable', HERE / 'portable.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    manifest = json.loads((HERE / 'PACKAGE-FILES.json').read_bytes())
    module.authenticate(HERE, manifest)
    module.authenticate(HERE, json.loads((HERE / 'ARCHIVE-FILES.json').read_bytes()))
    result = module.run()
    module.authenticate(HERE, manifest)
    print(json.dumps({'status': 'PASS_THREE_SEPARATE_JOINT_CHART_CERTIFICATES', **result,
                      'saving_domain': '[0,1/200]', 'claims_combined_as_global_class': False,
                      'author_search_rerun': False, 'source_census_rerun': False,
                      'native_or_compiler_execution': False, 'new_kappa': None}, sort_keys=True))


if __name__ == '__main__':
    main()
