"""Pinned native-profile consistency gate, separate from independent arithmetic.

Apache-2.0. Prepared with substantial OpenAI Codex assistance.
This module imports no producer. Native answers are comparison targets for
input wiring, not an implementation of geometry or scalar verification.
"""
import gzip
import hashlib
import json
from pathlib import Path

PIN = '7fb2194801e3a10f54772c7f0d5505035a4fc0ad'
PACKAGE = 'research/paired-cube-local-168/'
SELECT = PACKAGE+'selected/complex/'
INPUT_NAMES = ('paired-cube-complex-input.json', 'paired-cube-sinks-input.json',
               'paired-cube-bit-physical-input.json')
NATIVE_HASHES = {'research/paired-cube-local-168/certificate.json': '1e72ed46c81f1fada5adc71da38145f155872912fd39546b3294130cd0eeb9ed', 'research/paired-cube-local-168/SOURCE.json': '30c3878dde69a4ed29beed26856d1015ad3180da464d96154e5b005f728847bf', 'research/paired-cube-local-168/selected/complex/profile-before.json.gz': '89a46f6c9bc2e49a903a44952539034165acbc26ef6b7f14504554299ca8e2c6', 'research/paired-cube-local-168/selected/complex/profile.json.gz': '9d470b72ae31e2debd945b61481bde9c68df93054013f657cb331e0e49b53105', 'research/paired-cube-local-168/selected/complex/sinks.json': 'f4d0c85db8bc90b4c0ad243adb5332e0da6fa1a8db1be6b1ad58d93a5e19fdbe', 'certificates/paired-cube-bit-physical-input.json': '6735294e8639da09eb3eb2234cbc5814298442a6c946b5534bcf6e48903547f3'}
DIAGNOSTICS = {'numerical_complex_root', 'gauge_cost_rejections',
               'gauge_trial_saving', 'gauge_selection'}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def positive_bins(hist, maximum):
    require(type(hist) is dict, 'native component histogram object')
    out = {}
    for key, count in hist.items():
        require(type(key) is str and key.isascii() and key.isdigit() and str(int(key)) == key,
                'native component rank key')
        rank = int(key)
        require(0 <= rank <= maximum and type(count) is int and count >= 0,
                'native component rank/count')
        if rank and count:
            out[key] = count
    return out

def bind_objects(native, inputs):
    """Pure consistency check; mathematical mutations bypass byte hash guards."""
    require(set(inputs) == set(INPUT_NAMES), 'precision input names')
    logical = inputs['paired-cube-complex-input.json']
    physical = inputs['paired-cube-sinks-input.json']
    bit = inputs['paired-cube-bit-physical-input.json']
    expected_logical = {k:v for k,v in native['logical'].items() if k not in DIAGNOSTICS}
    require(logical == expected_logical, 'native logical scalar profile mismatch')
    require(tuple(logical[k] for k in ('h', 'v', 'R', 'c', 'q', 'matched', 'total_M_operations', 'loss'))
            == (22, 1320, 13042, 21249, 3157, 11364, 32971, 440), 'native scalar dimensions')
    require(logical['R'] == logical['c']+logical['q']-logical['matched'], 'native logical role identity')
    published = native['certificate']['complex']['physical']['physical']
    profile = native['certificate']['complex']['profile']
    sink = native['sinks']
    require(published['terminal_sinks'] == profile['terminal_sinks'] == sink['eligible_count'] == 44,
            'native terminal population')
    require(physical['sinks'] == 44, 'native copied terminal population')
    for key in ('h', 'v', 'R', 'pairs', 'physical_R', 'loss', 'm', 'W_per_vertex',
                'rank_per_vertex', 'deficit_per_vertex'):
        require(type(physical[key]) is int and physical[key] == published[key],
                'native physical dimension mismatch: '+key)
    require((physical['m'],physical['W_per_vertex'],physical['rank_per_vertex'],
             physical['deficit_per_vertex'],physical['physical_R']) == (66,13328,878328,1320,10688),
            'native final stock/rank')
    require(physical['R'] == logical['R'] and physical['pairs'] == profile['reuse_pairs'] == 2310,
            'native logical/alias coupling')
    require(physical['physical_R'] == physical['R']-physical['pairs']-physical['sinks'] == profile['R'],
            'native physical role recount')
    require(profile['scalar_role_reserve'] == logical['R'] and profile['c'] == logical['c']
            and profile['q'] == logical['q'] and profile['total_M_operations'] == logical['total_M_operations'],
            'native full scalar charge inventory')
    component_sha256 = {}
    for field in ('local_histogram', 'source_data_histogram', 'target_data_histogram',
                  'physical_gauge_histogram', 'child_histogram'):
        maximum = 65 if field == 'child_histogram' else 22
        ours = positive_bins(physical[field], maximum)
        require(ours == positive_bins(published[field], maximum), 'native '+field+' mismatch')
        component_sha256[field] = canonical(ours)
    require(positive_bins(physical['local_histogram'],22) == positive_bins(sink['local_histogram'],22),
            'native selected sink local histogram mismatch')
    require(positive_bins(physical['target_data_histogram'],22) == positive_bins(sink['target_histogram'],22),
            'native selected sink target histogram mismatch')
    require(positive_bins(physical['child_histogram'],65) == positive_bins(sink['child_histogram'],65)
            == positive_bins(profile['child_histogram'],65), 'native selected sink paid inventory mismatch')
    before = native['profile_before_terminal']
    require((before['R'],before['physical_R'],before['pairs'],before['W_per_vertex'],before['rank_per_vertex'])
            == (13042,10732,2310,13372,881232), 'native pre-terminal physical stock')
    require(before['source_data_histogram'] == published['source_data_histogram'], 'native source inventory changed')
    require(bit == native['bit'], 'native unchanged bit profile mismatch')
    native_zero = published['target_data_histogram'].get('0',0)
    ours_zero = physical['target_data_histogram'].get('0',0)
    require(type(native_zero) is int and type(ours_zero) is int and native_zero >= 0 and ours_zero >= 0,
            'native zero-rank diagnostics')
    return dict(status='pinned_native_profile_binding_pass',upstream_commit=PIN,
                paid_component_sha256=component_sha256,logical_profile_sha256=canonical(logical),
                bit_profile_sha256=canonical(bit),zero_rank_target_events=dict(native=native_zero,
                independent_literal_recount=ours_zero,difference=ours_zero-native_zero),
                scope='Native input consistency only. Positive rank bins and all paid dimensions agree. '
                      'Zero-rank events create no child, rank mass or characteristic charge; full c/M scalar '
                      'charges remain paid. Native scalar_replay metadata is not copied or treated as fresh evidence.')

def load_native(root):
    root = Path(root)
    for path, expected in NATIVE_HASHES.items():
        require(hashlib.sha256((root/path).read_bytes()).hexdigest() == expected,
                'native source byte mismatch: '+path)
    read = lambda name: json.loads((root/name).read_bytes())
    zipped = lambda name: json.loads(gzip.decompress((root/name).read_bytes()))
    return dict(certificate=read(PACKAGE+'certificate.json'), logical=zipped(SELECT+'profile-before.json.gz'),
                profile_before_terminal=zipped(SELECT+'profile.json.gz'), sinks=read(SELECT+'sinks.json'),
                bit=read('certificates/paired-cube-bit-physical-input.json'))

def check_native_inputs(root, inputs):
    require(len(NATIVE_HASHES) == 6, 'complete native binding pin set')
    return bind_objects(load_native(root), inputs)
