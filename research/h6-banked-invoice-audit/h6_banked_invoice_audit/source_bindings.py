"""SHA-256 gate for the exact four-file PR606 import closure.

These are full-file hashes supplied in the public-source handoff. All four
files must authenticate before any upstream module is imported. The original
files are redistributed unchanged. This is not a geometry/source_check replay.
"""
from pathlib import Path
import hashlib
import importlib.util
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REVISION = '81e81af67714bdc8d1693b0bf5c29468b92f62ff'
FILES = {
    'research/niemeier-lattices/workbench/paid-controller/banked.py':
        '8fb244f0f8dd007b29bc033c709bc04acd39fb562fb9c5382e7b4573233fb079',
    'research/niemeier-lattices/workbench/paid-controller/portable.py':
        '95d245eb15ff930847b6872eb10e9d1feb382ce135013e18ab5737ae626efde8',
    'research/niemeier-lattices/code/costs.py':
        '885303fde89db6153b9cf74e229e5ababe511f971c2f928f93355ac4740631e8',
    'research/leech-lattice/code/screen.py':
        '6118abd81e8860bdb551526029d8b36958835de52adb8f50c1a43bb247005385',
}


def check_bytes(data: bytes, expected: str, name: str) -> None:
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('Source SHA256 mismatch: ' + name)


def authenticate() -> list[dict]:
    result = []
    for relative, expected in sorted(FILES.items()):
        data = (HERE / 'vendor' / relative).read_bytes()
        check_bytes(data, expected, relative)
        result.append({'path': relative, 'bytes': len(data), 'sha256': expected,
                       'url': 'https://raw.githubusercontent.com/CrocSwap/'
                              'integer-mult-bounds/' + REVISION + '/' + relative})
    return result


def import_banked():
    """Import only after authenticating the whole closure, including screen.py."""
    authenticate()
    path = HERE / 'vendor/research/niemeier-lattices/workbench/paid-controller/banked.py'
    spec = importlib.util.spec_from_file_location('h6_authenticated_banked', path)
    if spec is None or spec.loader is None:
        raise ValueError('Unable to construct banked.py module loader')
    # banked.py imports the sibling name `portable`; do not accept an unrelated
    # preloaded module from a caller's environment.
    saved_portable = sys.modules.pop('portable', None)
    saved_path = sys.path[:]
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        expected_portable = path.with_name('portable.py').resolve()
        if Path(sys.modules['portable'].__file__).resolve() != expected_portable:
            raise ValueError('Unexpected portable.py import location')
    finally:
        sys.path[:] = saved_path
        sys.modules.pop('portable', None)
        if saved_portable is not None:
            sys.modules['portable'] = saved_portable
    return module
