"""One cold authenticated Full/FftWord/H source cohort.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The byte-identical retained sources preserve their authors and notices.
"""
from contextlib import contextmanager
from hashlib import sha1,sha256
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import tarfile
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FULL=HERE/'vendor/full'


def need(condition,message):
    if not condition:
        raise ValueError(message)


def blob(raw):
    return sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def authenticate():
    rows=[r for r in json.loads((HERE/'SOURCES.json').read_text())['files']
          if r['usage']=='input']
    checked={}
    for row in rows:
        path=ROOT/row['path']
        need(path.is_file() and not path.is_symlink(),'regular scalar-join source: '+row['path'])
        raw=path.read_bytes()
        need(row['path'] not in checked and sha256(raw).hexdigest()==row['sha256']
             and blob(raw)==row['git_blob'],'exact scalar-join source: '+row['path'])
        checked[row['path']]=row['sha256']
    manifest=json.loads((HERE/'VENDOR.json').read_text())
    for row in manifest['files']:
        path=HERE/row['path']
        need(path.is_file() and not path.is_symlink(),'regular retained Full source')
        raw=path.read_bytes()
        need(len(raw)==row['bytes'] and sha256(raw).hexdigest()==row['sha256']
             and blob(raw)==row['git_blob'],'byte-identical retained Full source: '+row['path'])
    return checked


def load(name,path):
    need(name not in sys.modules,'cold scalar-join module: '+name)
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name,None)
        raise
    return module


@contextmanager
def full_sources():
    """Use the retained loader's explicit raw-source argument unchanged."""
    authenticate()
    names=('sources','compiler','reference')
    need(not any(name in sys.modules for name in names),'cold Full preparation aliases')
    modules={}
    manifest=json.loads((FULL/'SOURCES.json').read_text())
    raw={row['path']:(ROOT/row['path']).read_bytes() for row in manifest['files']
         if row['usage']=='input'}
    # Preserve the retained loader's relative layout without modifying ROOT,
    # code, or any authentication operation. Its nested lowering loader reads
    # its exact SOURCES.json from that layout even with explicit raw inputs.
    with tempfile.TemporaryDirectory(prefix='full-source-layout-') as directory:
        mirror=Path(directory)
        package=mirror/'research/full-global-tensor-caller'
        package.mkdir(parents=True)
        for filename in (*[name+'.py' for name in names],'SOURCES.json'):
            (package/filename).write_bytes((FULL/filename).read_bytes())
        lower_manifest=mirror/'research/rational-fft-fixed-h/SOURCES.json'
        lower_manifest.parent.mkdir(parents=True)
        lower_manifest.write_bytes(raw['research/rational-fft-fixed-h/SOURCES.json'])
        try:
            for name in names:
                modules[name]=load(name,package/(name+'.py'))
            dense,lower,source=modules['sources'].load(overrides=raw)
            yield dense,lower,source,modules['compiler'],modules['reference']
        finally:
            for name,module in modules.items():
                if sys.modules.get(name) is module:
                    del sys.modules[name]


def archived_python():
    """Read only metadata/source bytes in the already authenticated archive.

    All nested tar bytes are covered by its fixed outer digest. No extraction
    or source execution occurs in this inventory pass.
    """
    result={}
    def visit(handle):
        with tarfile.open(fileobj=handle,mode='r:') as archive:
            for member in archive.getmembers():
                if not member.isfile():
                    continue
                if member.name.endswith('.py'):
                    name=Path(member.name).stem
                    if name.isidentifier():
                        raw=archive.extractfile(member).read()
                        result.setdefault(name,set()).add(sha256(raw).hexdigest())
                elif member.name.endswith('.tar'):
                    with archive.extractfile(member) as nested:
                        visit(nested)
    with (ROOT/'research/physical-fft-word/inputs/ring-export.tar').open('rb') as handle:
        visit(handle)
    recorded=json.loads((HERE/'COLD-NAMES.json').read_text())
    need(recorded['names']==sorted(result),'complete archived Python cold-name inventory')
    return result


def imported_bytes(inventory):
    checked=0
    for name,hashes in inventory.items():
        module=sys.modules.get(name)
        if module is None:
            continue
        path=Path(getattr(module,'__file__',''))
        need(path.is_file() and not path.is_symlink()
             and sha256(path.read_bytes()).hexdigest() in hashes,
             'actual authenticated imported scalar/H source: '+name)
        checked+=1
    return checked


@contextmanager
def opened():
    """Open the exact FftWord child, then bind unchanged Full methods to it."""
    authenticate()
    inventory=archived_python()
    extra=('fft_word_sources','fft_word_plan','fft_word_codec','fft_word_engine',
           'physical_sources','physical_controls','physical_engine',
           'frontend','global_h_boundary','join_engine')
    need(not any(name in sys.modules for name in set(inventory).union(extra)),
         'one cold Full/FftWord/H cohort')
    # These additional files are authenticated above and loaded explicitly.
    explicit={name:ROOT/'research/physical-fft-word'/(name+'.py')
              for name in ('fft_word_sources','fft_word_plan','fft_word_codec','fft_word_engine')}
    explicit.update({name:FULL/(name+'.py')
                     for name in ('physical_sources','physical_controls','physical_engine')})
    explicit.update(frontend=FULL/'vendor/global-boundary/frontend.py',
                    global_h_boundary=FULL/'vendor/global-boundary/bridge.py')
    for name,path in explicit.items():
        inventory.setdefault(name,set()).add(sha256(path.read_bytes()).hexdigest())
    old_path=sys.path[:]
    try:
        word_path=ROOT/'research/physical-fft-word'
        sys.path.insert(0,str(word_path))
        source=load('fft_word_sources',word_path/'fft_word_sources.py')
        with source.opened() as state:
            for name in ('fft_word_plan','fft_word_codec','fft_word_engine'):
                module=importlib.import_module(name)
                need(Path(module.__file__).resolve()==(word_path/(name+'.py')).resolve(),
                     'actual authenticated FFT-word source path: '+name)
            for name in ('word_product','ring_words','fft_arithmetic','product_plan',
                         'twiddle_setup','ring_engine'):
                module=importlib.import_module(name)
                need(Path(module.__file__).resolve()==(state.ring_package/(name+'.py')).resolve(),
                     'actual retained normalized-product source path: '+name)
            expected={
                'composed_sources':'5b9a507a5f5eb7d32d76792cac4b876070d29e91',
                'composed_engine':'646c451a4cbdf0244c7782d958f257f6606b962f',
                'composed_plan':'300ee75d4171c8f0d97118a01a4e439b72ca01d6',
            }
            for name,identity in expected.items():
                module=importlib.import_module(name)
                need(blob(Path(module.__file__).read_bytes())==identity,
                     'identical retained raw-H source: '+name)
            load('frontend',FULL/'vendor/global-boundary/frontend.py')
            boundary=load('global_h_boundary',FULL/'vendor/global-boundary/bridge.py')
            # The old source module supplies only its unchanged `need` here.
            # Its opened() and Karatsuba-only constructor are never invoked.
            load('physical_sources',FULL/'physical_sources.py')
            load('physical_controls',FULL/'physical_controls.py')
            full=load('physical_engine',FULL/'physical_engine.py')
            from cardinal_counts import Count
            from records import Tape
            from fft_word_engine import FftWord
            from fft_arithmetic import Arithmetic
            need(full.Count is boundary.Count is Count and full.Tape is boundary.Tape is Tape
                 and full.Arithmetic is Arithmetic,'one exact Count/Tape/signed-arithmetic identity')
            state.full_class=full.FullPhysical
            state.fast_word_class=FftWord
            state.full_boundary=boundary
            state.fast_full=load('join_engine',HERE/'join_engine.py')
            state.authenticated_imports=imported_bytes(inventory)
            yield state
            imported_bytes(inventory)
    finally:
        sys.path[:]=old_path
