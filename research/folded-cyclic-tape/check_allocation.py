"""Run the separately authored exact numerical/source allocation review."""
from pathlib import Path
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    source = load('folded_reference_adapter', HERE / 'reference_source.py')
    raw = source.authenticated_inputs(HERE)
    pages = load('folded_page_review_target', HERE / 'pages.py')
    review = load('folded_independent_allocation', HERE / 'allocation_review.py')
    receipt = review.run(pages, lambda parameters: source.make_reference(raw, parameters))
    print(json.dumps(receipt, sort_keys=True))
    print('PASS_INDEPENDENT_FOLDED_ALLOCATION')


if __name__ == '__main__':
    main()
