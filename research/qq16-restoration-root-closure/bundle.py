"""Authenticate immutable components without running the historical repo loader.

The original loader and its selected-record guards remain unchanged in PR3087.tar.
This adapter authenticates every byte by the frozen archive identity, extracts
only the retained PR2809 component, and imports its unchanged runtime/fixture.
No original all-repository authentication or selected supplier replay is claimed.
"""
from hashlib import sha256
from pathlib import Path, PurePosixPath
import importlib.util
import io
import sys
import tarfile
import types

HERE = Path(__file__).resolve().parent
ARCHIVE_SHA = 'd7e9c04a5e6d3f76158555d84080786c7cd8028ca31a61c9399de2b2c67bfd53'
CHAIN = [('inputs/pr3055.tar','c76e11cce0696db643715a362631b60fb14f26ba66c1e3bb5b5b0389eb52e95d'),
         ('inputs/pr2899.tar','fc4a2e07423835737c8fb3872664b16ff12aa4cf83b1e26e49878debef40c531'),
         ('inputs/pr2809.tar','ee1d4ec05e3c872d264be3b38f71a8c153acf37427f5d3ba87f8e15440c9ccf0')]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def archive():
    raw = (HERE/'source/PR3087.tar').read_bytes()
    need(sha256(raw).hexdigest()==ARCHIVE_SHA, 'Exact outer archive')
    hashes = {'PR3087.tar':ARCHIVE_SHA}
    outer = {}
    for name, expected in CHAIN:
        with tarfile.open(fileobj=io.BytesIO(raw)) as src:
            for member in ('session.py','ordinary.py','binary.py','compact_engine.py','pair_dispatch.py'):
                try:
                    outer[hashes[next(reversed(hashes))]+':'+member] = src.extractfile(member).read()
                except KeyError:
                    pass
            raw = src.extractfile(name).read()
        need(sha256(raw).hexdigest()==expected, 'Exact nested archive '+name)
        hashes[name] = expected
    return raw, hashes, outer


def materialize(destination):
    raw, hashes, outer = archive()
    files = {}
    with tarfile.open(fileobj=io.BytesIO(raw)) as src:
        for entry in src.getmembers():
            path = PurePosixPath(entry.name)
            need(not path.is_absolute() and '..' not in path.parts, 'Safe frozen path')
            if entry.isdir():
                continue
            need(entry.isfile(), 'Only regular frozen source files')
            data = src.extractfile(entry).read()
            target = destination/str(path)
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as output:
                output.write(data)
            files[str(path)] = sha256(data).hexdigest()
    hashes['component_inventory_sha256'] = sha256(''.join(k+' '+v+'\n' for k,v in sorted(files.items())).encode()).hexdigest()
    return hashes, outer


def activate_component(base):
    """Test component adapter; original source methods/constructors are unchanged."""
    paths = [base, base/'inputs/pr2753',base/'inputs/pr2753/predecessor',
             base/'inputs/pr2753/predecessor/vendor',base/'inputs/pr2769/vendor']
    sys.path[:0] = [str(path) for path in paths]
    state = {'codec':None}
    def activate():
        if state['codec'] is None:
            spec = importlib.util.spec_from_file_location('bank_codec',base/'inputs/pr2769/codec.py')
            module = importlib.util.module_from_spec(spec)
            sys.modules['bank_codec'] = module
            spec.loader.exec_module(module)
            state['codec'] = module
        return state['codec']
    shim = types.ModuleType('loader')
    shim.activate = activate
    shim.CALLER = base/'inputs/pr2753'
    shim.HERE = base
    sys.modules['loader'] = shim
    import macro_checks
    return macro_checks
