"""Independent literal two-phase provider metadata; no native introspection.

These synthetic address maps are test data only, never process/TCB evidence.
They exercise pure predicates with an actual parse of independent import bytes.
"""
from copy import deepcopy
from hashlib import sha256
from elf_literal_fixture_v1 import make_import_fixture
from receipt_contract_v1 import need, record, finish

CASE_IDS = ('provider-valid-two-phase', 'provider-global-interposition-rejected',
 'provider-map-drift', 'provider-unknown-map', 'provider-new-dependency',
 'provider-project-global', 'provider-project-definition', 'provider-unknown-scope',
 'provider-scope-order', 'provider-procfd-alias', 'provider-service-alias',
 'provider-lazy-flags', 'provider-global-flags', 'provider-namespace',
 'provider-not-retained', 'provider-not-initialized', 'provider-map-before-results',
 'provider-weak-nonzero', 'provider-wrong-address', 'provider-wrong-owner',
 'provider-result-order', 'provider-between-phase-map-drift',
 'provider-ifunc-without-family', 'provider-hidden-definition',
 'provider-absolute-definition', 'provider-map-receipt-corruption')
NORMAL_CASE_COUNT = 26
OPTIMIZED_CASE_COUNT = 26


def fixtures(parsed):
    segments = ((0, 4096, 4), (4096, 8192, 5), (8192, 12288, 6))
    def mapping(ident, name):
        return {'id': ident, 'name': name, 'kind': 'interpreter', 'identity_kind': 'file',
                'sha256': 'a' * 64, 'phdr_offset': 64, 'segments': segments,
                'aliases': (name,), 'global': True, 'retained': True,
                'relocated': True, 'initialized': True, 'dependencies': ()}
    first, second = mapping('main', '/fixture/python'), mapping('system', '/fixture/libsystem.so')
    second['kind'] = 'os'
    definition = {'version': None, 'binding': 1, 'type': 2, 'visibility': 0,
                  'section_index': 1, 'value': 0x1100, 'size': 16, 'ifunc_families': ()}
    strong = {'name': '__h25_fixture_symbol', 'version': None, 'weak': False, 'symbol_type': 2,
              'search': (('main', definition), ('system', None))}
    weak = {'name': '__h25_fixture_weak', 'version': None, 'weak': True, 'symbol_type': 2,
            'search': (('main', None), ('system', None))}
    policy = {'schema': 'h25-runtime-provider-policy-v1', 'launch_tcb_sha256': '1' * 64,
              'history_sha256': '2' * 64, 'root_binding_sha256': '3' * 64,
              'provider_metadata_sha256': '4' * 64,
              'static_policy_sha256': parsed['policy_sha256'], 'service_sha256': parsed['sha256'],
              'namespace': 0, 'flags': 2, 'global_scope': ('main', 'system'),
              'maps': (first, second), 'needed': (), 'symbols': (strong, weak)}
    def native_map(base, name):
        return (base, base + 64, name, tuple((base + a, base + b, f) for a, b, f in segments))
    maps = (native_map(0x100000, first['name']), native_map(0x200000, second['name']))
    map_only = {'schema': 'h25-native-provider-snapshot-v1', 'namespace': 0, 'flags': 2,
                'scope': 'retained-main-handle', 'maps_before': maps, 'maps_after': maps,
                'symbol_results': ()}
    resolved = dict(map_only)
    resolved['symbol_results'] = (
        ('__h25_fixture_symbol', None, False, 2, 0x101100, 0x100000, '/fixture/python', 2, 0x101100),
        ('__h25_fixture_weak', None, True, 2, 0, 0, '', None, None))
    return policy, map_only, resolved


def expectations():
    result = {CASE_IDS[0]: {'requests': [['__h25_fixture_symbol', None, False, 2],
                                      ['__h25_fixture_weak', None, True, 2]],
                           'accepted_symbols': 2, 'phases': ['maps', 'requests', 'results']}}
    for name in CASE_IDS[1:]:
        result[name] = {'accepted': False, 'exception': 'ELFAdmissionError'}
    need(len(result) == 26, 'provider literal inventory')
    return result


def run_provider_controls(admit_elf, admit_maps, requests0, admit_results, admission_error_type, mode):
    raw, static_policy = make_import_fixture()
    parsed = admit_elf(raw, sha256(raw).hexdigest(), static_policy)
    policy0, maps0, resolved0 = fixtures(parsed)
    expected, rows = expectations(), []
    admitted0 = admit_maps(maps0, policy0)
    requests = requests0(parsed, policy0)
    receipt = admit_results(parsed, resolved0, policy0, admitted0)
    need(type(receipt) is dict, 'provider actual receipt type')
    # The literal inputs require one interpreter definition and weak-zero result.
    accepted = receipt['symbols']
    need(accepted[0][0:5] == ('__h25_fixture_symbol', None, 'ordinary-definition', 'main', 0x101100) and
         accepted[1][0:5] == ('__h25_fixture_weak', None, 'unresolved-weak-zero', None, 0),
         'provider independent winner and weak-zero expectations')
    rows.append(record(CASE_IDS[0], {'requests': [list(row) for row in requests],
      'accepted_symbols': len(accepted), 'phases': ['maps', 'requests', 'results']}, expected[CASE_IDS[0]]))
    for name in CASE_IDS[1:]:
        policy, maps, resolved = deepcopy(policy0), deepcopy(maps0), deepcopy(resolved0)
        admitted = deepcopy(admitted0)
        phase = 'maps'
        if name == 'provider-global-interposition-rejected':
            # RTLD_LOCAL=2 remains unchanged. A different globally found winner
            # must still be rejected against the admitted first definition.
            resolved['symbol_results'] = (('__h25_fixture_symbol', None, False, 2, 0x201100, 0x200000, '/fixture/libsystem.so', 2, 0x201100),) + resolved['symbol_results'][1:]
            phase = 'results'
        elif name == 'provider-map-drift': maps['maps_after'] = maps['maps_after'][:1]
        elif name == 'provider-unknown-map':
            maps['maps_before'] = maps['maps_after'] = maps['maps_before'] + ((0x300000, 0x300040, '/fixture/unknown.so', ((0x300000, 0x301000, 4),)),)
        elif name == 'provider-new-dependency': policy['maps'][0]['dependencies'] = ('not-admitted',)
        elif name == 'provider-project-global': policy['maps'][0]['kind'] = 'ordinary_project'
        elif name == 'provider-project-definition':
            policy['maps'][0]['kind'] = 'ordinary_project'
            policy['maps'][0]['global'] = False
        elif name == 'provider-unknown-scope': policy['global_scope'] = ('main', 'unknown')
        elif name == 'provider-scope-order': policy['symbols'][0]['search'] = tuple(reversed(policy['symbols'][0]['search']))
        elif name == 'provider-procfd-alias': policy['maps'][0]['aliases'] += ('/proc/self/fd/17',)
        elif name == 'provider-service-alias': policy['maps'][0]['aliases'] += ('_h25_field_service_v1',)
        elif name == 'provider-lazy-flags': policy['flags'] = 1
        elif name == 'provider-global-flags': policy['flags'] = 258
        elif name == 'provider-namespace': policy['namespace'] = 1
        elif name == 'provider-not-retained': policy['maps'][0]['retained'] = False
        elif name == 'provider-not-initialized': policy['maps'][0]['initialized'] = False
        elif name == 'provider-map-before-results': maps['symbol_results'] = resolved['symbol_results']
        elif name == 'provider-weak-nonzero':
            resolved['symbol_results'] = resolved['symbol_results'][:1] + (('__h25_fixture_weak', None, True, 2, 0x101100, 0x100000, '/fixture/python', 2, 0x101100),)
            phase = 'results'
        elif name == 'provider-wrong-address':
            item = list(resolved['symbol_results'][0]); item[4] += 1
            resolved['symbol_results'] = (tuple(item),) + resolved['symbol_results'][1:]
            phase = 'results'
        elif name == 'provider-wrong-owner':
            item = list(resolved['symbol_results'][0]); item[6] = '/fixture/unknown.so'
            resolved['symbol_results'] = (tuple(item),) + resolved['symbol_results'][1:]
            phase = 'results'
        elif name == 'provider-result-order':
            resolved['symbol_results'] = tuple(reversed(resolved['symbol_results'])); phase = 'results'
        elif name == 'provider-between-phase-map-drift':
            resolved['maps_before'] = resolved['maps_after'] = resolved['maps_before'][:1]; phase = 'results'
        elif name == 'provider-ifunc-without-family':
            policy['maps'][0]['kind'] = 'os'; policy['symbols'][0]['search'][0][1]['type'] = 10
        elif name == 'provider-hidden-definition': policy['symbols'][0]['search'][0][1]['visibility'] = 2
        elif name == 'provider-absolute-definition': policy['symbols'][0]['search'][0][1]['section_index'] = 0xFFF1
        elif name == 'provider-map-receipt-corruption': admitted['receipt_sha256'] = '0' * 64; phase = 'results'
        error = message = None
        try:
            if phase == 'maps': admit_maps(maps, policy)
            else: admit_results(parsed, resolved, policy, admitted)
        except BaseException as exc:
            need(type(exc) is admission_error_type, 'provider exact rejection exception')
            error, message = type(exc).__name__, str(exc)
        rows.append(record(name, {'accepted': error is None, 'exception': error}, expected[name],
                           {'exception_message': message, 'phase': phase}))
    return finish(rows, CASE_IDS, NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT, expected, mode)
