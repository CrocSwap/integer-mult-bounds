#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Required source-only launcher for the frozen H6 entrypoints.

Run with python3 -I -B [and optionally -O]. All application source bytes are
hashed before execution. The entrypoint and both ordinary/explicit-path
SourceFileLoader imports compile those same retained bytes, never a .pyc.
Trusted interpreter/stdlib, stable package layout, single-threaded execution.
No mathematical changes; existing source/evidence provenance stays intact.
For Andrey Mas by ChatGPT (GPT-6 Astra Pro); Codex coordination is separate.
"""
import argparse
import hashlib
import importlib.machinery
from pathlib import Path
import sys
import types

ORIGINAL = 'h6_banked_invoice_audit'
APPENDIX = 'h6_full_pr1424_appendix'
COMMON = {
    ORIGINAL+'/model.py':
        'd18c4c589e37de077d29120d7b4688ad6a335cd63d225f93621a2573cd23cd80',
    ORIGINAL+'/source_bindings.py':
        'f247b8a5ef341737318af2d926808b92d26d90ff6db9abf2f714ba132ff6f335',
    ORIGINAL+'/vendor/research/niemeier-lattices/workbench/paid-controller/banked.py':
        '8fb244f0f8dd007b29bc033c709bc04acd39fb562fb9c5382e7b4573233fb079',
    ORIGINAL+'/vendor/research/niemeier-lattices/workbench/paid-controller/portable.py':
        '95d245eb15ff930847b6872eb10e9d1feb382ce135013e18ab5737ae626efde8',
    ORIGINAL+'/vendor/research/niemeier-lattices/code/costs.py':
        '885303fde89db6153b9cf74e229e5ababe511f971c2f928f93355ac4740631e8',
    ORIGINAL+'/vendor/research/leech-lattice/code/screen.py':
        '6118abd81e8860bdb551526029d8b36958835de52adb8f50c1a43bb247005385',
}
ENTRYPOINTS = {
    'audit': (ORIGINAL+'/audit.py',
        '458c7f01a5151ddc7e532d165992d8177f7be6644cf9309ef25cfadf01c251c0'),
    'verify': (ORIGINAL+'/verify_certificate.py',
        '8bc83e304ce2f259295bc81f1ab9dc681def9d7e54fb09fc2915386fd2b31f58'),
    'appendix': (APPENDIX+'/appendix.py',
        '69b1981b049df19655c497387741ab04c93a40d82b48135b157b4d472f3ae345'),
}
AUTHOR = (APPENDIX+'/author_source/price_h6.py',
          'ed83a457ae9deb1a8e06551404735ad3c6d71153ef4a22ec64f615f8d1a5d92a')


def require(test, message):
    if not test:
        raise ValueError(message)


def run_authenticated(root: Path, entry: str, arguments: list[str],
                      manifest: dict[str, str]) -> None:
    """Execute one pinned closure; manifest is fixed by main(), not CLI data."""
    root = root.resolve()
    blobs = {}
    for relative, expected in sorted(manifest.items()):
        path = (root/relative).resolve()
        require(path.is_relative_to(root), 'Source outside package root: '+relative)
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == expected,
                'Source SHA256 mismatch: '+relative)
        blobs[path] = data
    entry_path = (root/entry).resolve()
    require(entry_path in blobs, 'Unauthenticated entrypoint')
    # Fresh isolated CLI invocations have no application modules preloaded.
    require(not any(name in sys.modules for name in ('model', 'source_bindings', 'portable')),
            'Application module already loaded; use a fresh isolated process')
    loader_type = importlib.machinery.SourceFileLoader
    saved_get_code = loader_type.get_code

    def source_code(loader, fullname):
        path = Path(loader.path).resolve()
        if path in blobs:
            return compile(blobs[path], str(path), 'exec', dont_inherit=True)
        require(not path.is_relative_to(root), 'Unlisted application source: '+str(path))
        return saved_get_code(loader, fullname)

    saved_argv, saved_path = sys.argv, sys.path[:]
    saved_main = sys.modules.get('__main__')
    program = types.ModuleType('__main__')
    program.__file__ = str(entry_path)
    program.__package__ = None
    program.__spec__ = None
    try:
        # Covers the nested explicit loaders in banked.py and costs.py too.
        loader_type.get_code = source_code
        sys.argv = [str(entry_path), *arguments]
        sys.modules['__main__'] = program
        exec(compile(blobs[entry_path], str(entry_path), 'exec', dont_inherit=True),
             program.__dict__)
    finally:
        loader_type.get_code = saved_get_code
        sys.argv = saved_argv
        sys.path[:] = saved_path
        if saved_main is None:
            sys.modules.pop('__main__', None)
        else:
            sys.modules['__main__'] = saved_main


def main():
    require(sys.flags.isolated and sys.dont_write_bytecode,
            'Use python3 -I -B authenticated_run.py')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent,
                        help='Parent of the two sibling package directories')
    parser.add_argument('mode', choices=ENTRYPOINTS)
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    forwarded = args.arguments
    if forwarded[:1] == ['--']:
        forwarded = forwarded[1:]
    # argparse also accepts abbreviations such as --ori; block those too.
    require(not any(x.startswith('--') and '--original'.startswith(x.split('=',1)[0])
                    for x in forwarded),
            'Use launcher --root, not appendix --original')
    entry, digest = ENTRYPOINTS[args.mode]
    manifest = dict(COMMON)
    manifest[entry] = digest
    if args.mode == 'appendix':
        manifest[AUTHOR[0]] = AUTHOR[1]
    run_authenticated(args.root, entry, forwarded, manifest)


if __name__ == '__main__':
    main()
