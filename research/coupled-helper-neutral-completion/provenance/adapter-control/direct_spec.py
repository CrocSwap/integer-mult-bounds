"""Control: direct spec-file loading bypasses meta-path finders."""
import importlib.util
from pathlib import Path
path = Path(__file__).with_name('assert_module.py')
spec = importlib.util.spec_from_file_location('neutral_assert_control', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
print('ASSERTION_WAS_INCORRECTLY_STRIPPED')
