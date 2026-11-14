"""Two exact caller seams: literal headers plus keys, then literal retirement.

The numerical source, current lease, source commit and radix remain retained.
Apache-2.0; prepared for @CubeJerry with substantial OpenAI assistance.
"""
from hashlib import sha256
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
JOIN_SHA = '99b8c714db5e88044c61dbf25cc42fb809420720e34f412bfd2ce5ee7ee8de92'
CALLER_SHA = '055e86590e1cb03555f9ef6f1d585f8c23453a4cc10cd7feda7362c77f7bce1c'
OLD_BUILD = '''        m.route.emit_headers(m.join, iterator, lease, headers, width)
        observed = {name: ''.join(tape.cells) for name, tape in headers.items()}
        observed['width'] = ''.join(width.cells)
        if fault == 'stale_offset':
            zero_counter(headers['offsets'], offset=True)
        prepare_keys(m.route, point, headers, record, width, index, address, private,
                     False if fault == 'forward_rows_in_inverse' else reverse,
                     stale_wire=fault == 'stale_wire')
'''
NEW_BUILD = '''        need(fault is None, 'fault controls mutate the fixed graph, not its caller')
        ports = (*private, headers['h'], headers['modulus'], headers['offsets'],
                 headers['selected_layer'], address, width, index, _BitPort(record.tape),
                 _NativePort(iterator.source), _NativePort(iterator.counters['axis']),
                 _NativePort(lease.actual.guide), _NativePort(result),
                 _NativePort(iterator.counters['width']))
        literal = point.run(ports, 'INVERSE' if reverse else 'FORWARD')
        need(literal['status'] == 'DONE', 'literal current headers and complete keys accept')
        observed = {name: ''.join(tape.cells) for name, tape in headers.items()}
        observed['width'] = ''.join(width.cells)
'''
OLD_RETIRE = '''    width.erase()
    for header in headers.values():
        header.erase()
'''
NEW_RETIRE = '''    retired = point.run(ports, 'RETIRE')
    need(retired['status'] == 'RETIRED', 'literal owned header retirement accepts')
'''


def bind(native_port, bit_port):
    old_path = HERE/'inputs/keypass/join.py'
    raw = old_path.read_bytes()
    if sha256(raw).hexdigest() != JOIN_SHA:
        raise ValueError('exact B7 source seam changed')
    old = types.ModuleType('_retained_keypass_source_join')
    old.__file__ = str(old_path)
    sys.modules[old.__name__] = old
    exec(compile(raw, str(old_path), 'exec'), old.__dict__)
    module = old.bind(bit_port)
    caller_path = HERE/'inputs/keypass/inputs/route/inputs/point/caller.py'
    caller_raw = caller_path.read_bytes()
    if sha256(caller_raw).hexdigest() != CALLER_SHA:
        raise ValueError('exact actual current source caller changed')
    function = 'def run_leg('+caller_raw.decode().split('def run_leg(', 1)[1]
    if function.count(OLD_BUILD) != 1 or function.count(OLD_RETIRE) != 1:
        raise ValueError('exact two source seams not unique')
    replaced = function.replace(OLD_BUILD, NEW_BUILD).replace(OLD_RETIRE, NEW_RETIRE)
    module._NativePort = native_port
    exec(compile(replaced, str(caller_path)+'[two declared header seams]', 'exec'), module.__dict__)
    module.exact_header_seams = {
        'B7_join_sha256': JOIN_SHA, 'caller_sha256': CALLER_SHA,
        'original_function_sha256': sha256(function.encode()).hexdigest(),
        'adapted_function_sha256': sha256(replaced.encode()).hexdigest(),
        'build_removed_sha256': sha256(OLD_BUILD.encode()).hexdigest(),
        'build_replacement_sha256': sha256(NEW_BUILD.encode()).hexdigest(),
        'retirement_removed_sha256': sha256(OLD_RETIRE.encode()).hexdigest(),
        'retirement_replacement_sha256': sha256(NEW_RETIRE.encode()).hexdigest()}
    return module
