"""Pure C05 enabling construction. Never a complete C05 inventory or launcher."""
import hashlib

CONFIGURATION = SOURCE_REVIEW = EXECUTION = None
ROLES = ('pyinit_failure', 'exec_failure')
C = 'dict_probe_fields_v1.c'
L = 'field_loader_snapshot_v1.h'
H = 'field_service_v1.h'
COMMON = {
    C: ('e0188999d41a9ab26e8d3d5c37b18b2238b3af21b1db90895f01f7be76d50b65', 17806),
    L: ('bf7ab049cea89c0a882b279e35b1383ac8f99b66aa4b9b8e1ca22eb9c24c5a8d', 19495),
}
SERVICE = {
    'pyinit_failure': ('7656cd37503986459c4133643372fec13d3e5ad5553881f0bf0343a9a3e11abd', 17354),
    'exec_failure': ('f5066831bd812e7e88fb971ba0e7ca86dbef91fc40a1a68c17b040ce474cd880', 17040),
}
# Whole-source authentication makes this a fixed-source extraction, not a C parser.
SITES = {
    C: ((11, '<Python.h>'), (12, '"internal/pycore_dict.h"'),
        (13, '<stddef.h>'), (14, '<stdint.h>'), (15, '<string.h>'),
        (422, '"field_loader_snapshot_v1.h"'), (456, '"field_service_v1.h"')),
    L: ((13, '<dlfcn.h>'), (14, '<link.h>'), (15, '<elf.h>')),
    H: (),
}

class ConstructionOpen(RuntimeError):
    pass

def require(ok, message):
    if not ok:
        raise ConstructionOpen(message)

def absolute(path):
    require(type(path) is str and 1 < len(path) <= 4096,
            'bounded exact path required')
    require(path.startswith('/') and all(32 <= ord(c) < 127 for c in path)
            and all(p not in ('', '.', '..') for p in path.split('/')[1:]),
            'canonical absolute path required')
    return path

def source_roots(payloads, stage, output, mode):
    """Six (role, filename) keys map to inert original source bytes.

    Site order is deterministic serialization, not preprocessing event order.
    Mode is supplied binding data; 292 is required installation mode, not stat.
    """
    absolute(stage)
    absolute(output)
    require(type(mode) is str and mode in ('normal', 'optimized'), 'mode differs')
    require(output != stage and not output.startswith(stage + '/'), 'output inside stage')
    require(type(payloads) is dict and len(payloads) == 6, 'six exact payload entries required')
    for key in payloads:
        require(type(key) is tuple and len(key) == 2 and
                all(type(x) is str for x in key), 'foreign payload key')
    expected_keys = {(role, name) for role in ROLES for name in (C, L, H)}
    require(set(payloads) == expected_keys, 'six source occurrences required')
    files, sites, commands = [], [], []
    for role in ROLES:
        directory = stage + '/areas/field-negative-variants-v1/' + role
        pins = dict(COMMON, **{H: SERVICE[role]})
        for name in (C, L, H):
            raw = payloads[(role, name)]
            digest, size = pins[name]
            require(type(raw) is bytes and len(raw) == size, 'source length differs')
            require(hashlib.sha256(raw).hexdigest() == digest, 'source digest differs')
            path = absolute(directory + '/' + name)
            files.append({'path': path, 'sha256': digest, 'bytes': size, 'mode': 292})
            lines = raw.decode('ascii').splitlines()
            for line, operand in SITES[name]:
                require(lines[line - 1] == '#include ' + operand, 'source site differs')
                sites.append((role, path, line, operand))
        target = absolute(output + '/' + role + '/_h25_dict_probe.cpython-312-x86_64-linux-gnu.so')
        require(target != stage and not target.startswith(stage + '/'), 'target inside stage')
        commands.append((role, [
            '/usr/bin/x86_64-linux-gnu-gcc-13', '-nostartfiles', '-shared',
            '-fPIC', '-O3', '-std=c11', '-Wall', '-Wextra', '-Werror',
            '-I/usr/include/python3.12', directory + '/' + C, '-o',
            target]))
    return {'mode': mode, 'commands': tuple(commands), 'project_files': files,
            'literal_include_obligations': tuple(sites),
            'full_c05': False, 'runtime_qualified': False}

def no_pch_prefix(name, effective_chain, facts):
    """Conditional ordinary-header subcase; facts are inert observer DATA.

    The caller must separately prove effective_chain, namespace authenticity,
    stability, compatible cache state, inactive remapping/custom construction, and normalized MISSING
    semantics. This function establishes none of those premises.
    A present PCH, symlink, unsupported object or read error leaves the subcase OPEN.
    """
    require(type(name) is str and 0 < len(name) <= 8192 and not name.startswith('/')
            and all(p not in ('', '.', '..') for p in name.split('/')), 'include name differs')
    require(type(effective_chain) is tuple and 0 < len(effective_chain) <= 512,
            'bounded effective chain required')
    require(type(facts) is dict and len(facts) <= 4096, 'bounded fact mapping required')
    for directory in effective_chain:
        absolute(absolute(directory) + '/' + name + '.gch')
    total = 0
    for key, value in facts.items():
        require(type(key) is str and type(value) is tuple and len(value) == 2,
                'foreign lookup fact')
        require(type(value[0]) is str and type(value[1]) is bytes, 'foreign lookup value')
        absolute(key)
        require(value[0] in ('MISSING', 'REGULAR') and len(value[1]) <= 67108864,
                'unsupported lookup disposition')
        require(value[0] != 'MISSING' or value[1] == b'', 'missing fact carries bytes')
        total += len(value[1])
        require(total <= 268435456, 'fact byte bound exceeded')
    events = []
    for directory in effective_chain:
        path = absolute(absolute(directory) + '/' + name)
        # Conservative no-PCH subcase. This does not claim GCC probes a PCH
        # at every site, nor reject a legal compiler configuration globally.
        for candidate, is_pch in ((absolute(path + '.gch'), True), (path, False)):
            require(candidate in facts, 'missing independent lookup observation')
            disposition, raw = facts[candidate]
            if disposition == 'MISSING':
                events.append((candidate, 'MISSING'))
                continue
            require(not is_pch, 'present PCH requires additional source rules')
            events.append((candidate, 'REGULAR', hashlib.sha256(raw).hexdigest(), len(raw)))
            return tuple(events), candidate
    raise ConstructionOpen('no ordinary header resolved')
