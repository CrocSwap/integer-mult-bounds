"""Ensure wrapper -O cannot strip scientific or direct-loader assertions."""
from pathlib import Path
import importlib.util,json
HERE=Path(__file__).resolve().parent
if not __debug__:raise ValueError('Scientific main compiled with optimization')
s=importlib.util.spec_from_file_location('direct_assertion_probe',HERE/'assertion_module.py')
m=importlib.util.module_from_spec(s)
try:s.loader.exec_module(m)
except AssertionError as error:
    if str(error)!='EXPECTED_DIRECT_MODULE_ASSERTION':raise
else:raise ValueError('Direct-loader assertion stripped')
out=HERE/'FRESH.json'
if out.exists():raise ValueError('Immutable output exists')
out.write_text(json.dumps({'scientific_main_optimization':0,'direct_file_loader_assertion_retained':True},sort_keys=True)+'\n')
