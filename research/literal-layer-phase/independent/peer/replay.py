"""Portable entry point for the unchanged independent review checker."""
import argparse
import importlib.util
from pathlib import Path
import sys

parser = argparse.ArgumentParser()
parser.add_argument('package', type=Path, help='path to research/literal-layer-phase')
arguments = parser.parse_args()
spec = importlib.util.spec_from_file_location('independent_phase_review', Path(__file__).with_name('check.py'))
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
module.PACKAGE = arguments.package.resolve()
module.main()
