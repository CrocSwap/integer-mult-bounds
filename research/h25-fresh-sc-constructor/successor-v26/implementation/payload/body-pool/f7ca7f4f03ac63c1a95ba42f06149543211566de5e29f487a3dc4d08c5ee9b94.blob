"""Parent-owned integration; called only inside the serial scientific runner."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import sys
import sysconfig
from types import BuiltinFunctionType, ModuleType


def custody(root, lanes):
    """Pay selected new source authentication inside every measured process."""
    selected = set() if lanes == 'none' else ({'sets', 'guards', 'trace'} if lanes == 'all' else {lanes})
    files = ['integration/full_driver.py', 'integration/adapters.py', 'integration/derive_driver.py',
             'integration/DERIVATION.json', 'PLAN.md', 'PLAN.json']
    for lane, directory in (('sets', 'set-reuse'), ('guards', 'runtime-guards'), ('trace', 'trace-encoding')):
        if lane in selected:
            files.extend(str(path.relative_to(root)) for path in sorted((root / 'priorities' / directory).iterdir())
                         if path.is_file() and path.suffix in ('.py', '.c'))
    manifest = json.loads((root / 'STAGE.json').read_bytes())
    result = {}
    for name in files:
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise RuntimeError('Missing or symlinked new source: ' + name)
        row = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'mode': path.stat().st_mode & 0o777}
        if row != manifest['files'][name]:
            raise RuntimeError('New source custody failed: ' + name)
        result[name] = row
    return result


def load(path, name):
    if name in sys.modules:
        raise RuntimeError('Isolated adapter name already imported: ' + name)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError('Missing isolated adapter loader')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def build_encoder(source, directory):
    if directory.exists():
        raise RuntimeError('Refusing to reuse a trace build directory')
    directory.mkdir()
    raw = source.read_bytes()
    target = directory / ('_trace_encoding' + sysconfig.get_config_var('EXT_SUFFIX'))
    command = shlex.split(sysconfig.get_config_var('CC') or 'cc') + [
        '-shared', '-fPIC', '-O3', '-std=c11', '-Wall', '-Wextra', '-Werror',
        '-I' + sysconfig.get_paths()['include'], str(source), '-o', str(target)]
    completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, timeout=90, check=False)
    receipt = {'command': command, 'returncode': completed.returncode,
               'stdout': completed.stdout, 'stderr': completed.stderr,
               'source_sha256': hashlib.sha256(raw).hexdigest(), 'no_cached_binary': True}
    (directory / 'build.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    if completed.returncode != 0 or source.read_bytes() != raw:
        raise RuntimeError('Trace compilation or source custody failed; no retry')
    receipt['extension_sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
    module = load(target, '_trace_encoding')
    (directory / 'build.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    return module, receipt


def extra_guard_type(base, backend, entries):
    """Check the new encoder's owner/entry at every original guard boundary."""
    _type, _get = backend._TYPE, backend._DICT_GET
    error = backend._RUNTIME_ERROR
    for owner, name, function in entries:
        if not (_type(owner) is ModuleType and _type(function) is BuiltinFunctionType and
                function.__self__ is owner and _get(owner.__dict__, name) is function):
            raise error('Invalid trace encoder owner or entry')

    class ExtendedGuard(base):
        def __init__(self, module, label, native, original_functions):
            self._h25_entries = entries
            base.__init__(self, module, label, native, original_functions)

        def check(self):
            base.check(self)
            for owner, name, function in self._h25_entries:
                if not (_type(owner) is ModuleType and _get(owner.__dict__, name) is function):
                    raise error('Runtime drift: trace encoder entry point ' + name)

    return ExtendedGuard


def prepare(root, backend, native, output, lanes, phases):
    selected = set() if lanes == 'none' else ({'sets', 'guards', 'trace'} if lanes == 'all' else {lanes})
    if not selected <= {'sets', 'guards', 'trace'}:
        raise RuntimeError('Unsupported frozen lane selection')
    state = {'selected': selected, 'controls': {}, 'trace_type': backend.ComplementTrace,
             'set_binding': None, 'encoder_build': None, 'encoder': None}
    if 'guards' in selected:
        state['guard_adapter'] = load(root / 'priorities/runtime-guards/guard_candidate.py', '_h25_guard_candidate')
        state['guard_controls'] = load(root / 'priorities/runtime-guards/guard_controls.py', '_h25_guard_controls')
        state['reference_backend'] = load(Path(backend.__file__), '_h25_reference_backend')
        backend.RuntimeGuard = state['guard_adapter'].make_runtime_guard(backend)
    if 'trace' in selected:
        directory = root / 'priorities/trace-encoding'
        encoder, build = phases.call('trace_cold_compile_link_load', build_encoder,
                                     directory / 'trace_encoder.c', output / 'trace-cold-build')
        adapter = load(directory / 'trace_adapter.py', 'trace_adapter')
        trace_type = adapter.make_trace_type(backend, encoder)
        state.update(encoder=encoder, encoder_build=build, trace_type=trace_type,
                     trace_controls=load(directory / 'trace_controls.py', '_h25_trace_controls'))
        backend.RuntimeGuard = extra_guard_type(backend.RuntimeGuard, backend, trace_type._h25_native_entries)
    if 'sets' in selected:
        directory = root / 'priorities/set-reuse'
        state['set_adapter'] = load(directory / 'set_reuse.py', 'set_reuse')
        state['set_controls'] = load(directory / 'finite_set_controls.py', '_h25_set_controls')
    return state


def run_controls(state, backend, native, phases):
    result = state['controls']
    if 'guards' in state['selected']:
        result['guards'] = phases.call('new_guard_differential_controls',
                                      state['guard_controls'].run_guard_controls,
                                      state['reference_backend'], backend, native)
    if 'trace' in state['selected']:
        result['trace'] = phases.call('new_trace_original_differential_controls',
                                     state['trace_controls'].run_controls, backend, state['encoder'])
        result['trace_entry_freshness'] = phases.call('new_trace_entry_freshness_controls',
                                                     entry_controls, backend, native, state)
    if 'sets' in state['selected']:
        result['sets'] = phases.call('new_private_set_controls',
                                     state['set_controls'].run_controls, backend, state['set_adapter'])
    return result


def entry_controls(backend, native, state):
    module = backend.load_source('_h25_trace_entry_controls')
    trace = state['trace_type'](module.Label)
    calls = []
    binding = backend.bind(module, native, calls, trace)
    small, big = object.__new__(module.Label), object.__new__(module.Label)
    small.basis, big.basis = {0: 1}, {0: 1, 1: 2}
    wide_small, wide_big = object.__new__(module.Label), object.__new__(module.Label)
    wide_small.basis, wide_big.basis = {0: 1 << 100}, {0: 1, 1: 1 << 100}
    original = state['encoder'].encode_record
    outcomes = []
    before = (dict(binding['counters']), list(calls), trace.receipt())
    try:
        state['encoder'].encode_record = lambda *args: b'corrupt'
        for action in (binding['runtime_guard'].check, small.nondegenerate, lambda: small.complement_in(big),
                       wide_small.nondegenerate, lambda: wide_small.complement_in(wide_big)):
            try:
                action()
            except RuntimeError as error:
                if str(error) != 'Runtime drift: trace encoder entry point encode_record':
                    raise
                outcomes.append(str(error))
            else:
                raise RuntimeError('Changed trace entry was not rejected before arithmetic')
        if (dict(binding['counters']), list(calls), trace.receipt()) != before:
            raise RuntimeError('Changed trace entry executed arithmetic or observations')
    finally:
        state['encoder'].encode_record = original
    binding['runtime_guard'].check()
    return {'status': 'PASS', 'negative_actions': len(outcomes), 'rejected_before_arithmetic_and_observation': True}


def install_set(state, module):
    if 'sets' not in state['selected']:
        return
    binding = state['set_adapter'].bind_verify_map(module)
    module.Checks.verify_map = binding['verify_map']
    owner = binding['owner']
    circuit_init, checks_init = module.ComplexSideCircuit.__init__, module.Checks.__init__

    def captured_circuit(self, *args, **kwargs):
        circuit_init(self, *args, **kwargs)
        owner.capture_c(self)

    def captured_checks(self, *args, **kwargs):
        checks_init(self, *args, **kwargs)
        owner.capture_checks(self)

    module.ComplexSideCircuit.__init__ = captured_circuit
    module.Checks.__init__ = captured_checks
    state['set_binding'] = binding


def seal(state):
    if state['set_binding'] is not None:
        state['set_binding']['owner'].seal()


def arm(state):
    if state['set_binding'] is not None:
        state['set_binding']['owner'].arm_cli()


def disarm(state):
    if state['set_binding'] is not None:
        state['set_binding']['owner'].disarm_cli()


def receipt(state):
    result = {'lanes': sorted(state['selected']), 'new_controls': state['controls'],
              'encoder_build': state['encoder_build'],
              'original_observer_retained_for_old_controls': True}
    if state['set_binding'] is not None:
        result['set_reuse'] = dict(state['set_binding']['receipt'])
        if result['set_reuse']['fast_admissions'] != 1 or result['set_reuse']['fallback_calls'] != 0:
            raise RuntimeError('Complete caller did not use the single admitted set-reuse lease')
        if (result['set_reuse']['private_operand_sets_constructed'] != 2300 or
                result['set_reuse']['reservations'] != 1 or result['set_reuse']['reservations_expired'] != 1):
            raise RuntimeError('Private set construction or one-use lease count changed')
    return result
