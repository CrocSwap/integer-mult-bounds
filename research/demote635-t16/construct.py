"""Reverse one entrance promotion and fill literal unit gaps; Apache-2.0.

Prepared for seslly with substantial OpenAI Codex assistance.
No optimizer is needed to reconstruct this certificate.
"""
from collections import defaultdict
import copy
import gzip
import hashlib
import json
from pathlib import Path
import shutil

if not __debug__:
    raise RuntimeError('Assertions required; do not use -O')
HERE = Path(__file__).resolve().parent


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, sort_keys=True, separators=(',', ':'))+'\n')


def build_word(output):
    recipe = read(HERE/'data/RECIPE.json')
    raw = gzip.decompress((HERE/'data/BASELINE-WORD.json.gz').read_bytes())
    assert hashlib.sha256(raw).hexdigest() == recipe['input_sha256']
    word = json.loads(raw)
    for helper, before, after in recipe['entrances']:
        assert word['start_extra'][str(helper)] == before
        word['start_extra'][str(helper)] = after
    for section, index, before, after in recipe['frames']:
        assert word[section][index][-1] == before
        word[section][index][-1] = after
    word['report'].update(local_profile=recipe['local_profile'],
                         local_rank_mass=sum(int(r)*n for r,n in recipe['local_profile'].items()),
                         width_inventory=recipe['width_inventory'])
    raw = json.dumps(word, sort_keys=True, separators=(',', ':')).encode()
    assert hashlib.sha256(raw).hexdigest() == recipe['output_sha256']
    output.write_bytes(gzip.compress(raw, mtime=0))


def nominate(parent, output):
    data = output/'data'
    data.mkdir(parents=True)
    original = read(parent/'data/OWNERS.json.gz')
    owners = copy.deepcopy(original)
    plan = read(parent/'data/PLAN.json')
    recipe = read(HERE/'data/RECIPE.json')
    banks, calls, eligible = defaultdict(list), defaultdict(dict), defaultdict(list)
    def bank(z): return z['owner_replica'], z['child'], z['port']
    for i,z in enumerate(original):
        banks[bank(z)].append(i)
        calls[z['time']][z['helper']] = i
    remaining = {k: plan['windows'][f'{k[0]},{k[1]}'][0] -
                 sum(original[i]['width'] for i in indices) for k,indices in banks.items()}
    for i,z in enumerate(original):
        if z['width'] == 4 and remaining[bank(z)] == 1:
            eligible[z['time']].append(i)
    times = [t for t in range(144) if len(eligible[t]) >= 4]
    assert times == recipe['calls'], 'literal eligible calls'
    fields = ('owner_replica','child','port','copy','family','offset')
    for t in times:
        source = [calls[t][h-224] for h,_,_ in recipe['entrances']]
        destination = eligible[t][:4]
        touched = set(source) | set(destination)
        permutation = dict(zip(source,destination))
        permutation.update(zip(sorted(touched-set(source)), sorted(touched-set(destination))))
        assert set(permutation) == set(permutation.values()), 'within-call bijection'
        for i,j in permutation.items():
            assert original[i]['width'] == original[j]['width'] == 4
            for field in fields: owners[i][field] = original[j][field]
        for i in source: owners[i]['width'] = 5
    banks = defaultdict(list)
    for i,z in enumerate(owners): banks[bank(z)].append(i)
    for k,indices in banks.items():
        if all(owners[i] == original[i] for i in indices): continue
        offset = 0
        for i in sorted(indices, key=lambda j:(owners[j]['time'],owners[j]['helper'])):
            owners[i]['offset'] = offset
            offset += owners[i]['width']
        assert offset <= plan['windows'][f'{k[0]},{k[1]}'][0], 'whole-bin capacity'
    dump(data/'OWNERS.json',owners)
    registry = read(HERE/'data/REGISTRY.json')
    plan['provider_registry']['demote635'] = registry
    for call in plan['provider_calls']:
        if call['time'] in times:
            call['provider'] = 'demote635'
            call['local_program_sha256'] = registry['orientation_program_sha256'][call['orientation']]
    for call in plan['per_call_widths']:
        if plan['order'].index([call['stage'],call['replica']]) in times:
            call['widths'] = registry['widths']
    spec = read(HERE/'data/SPEC.json')
    plan.update(status='FROZEN_DEMOTE635_109_CALLS',mode='demote635',
                profile=spec['expected']['global_profile'],
                solver_status='within-call owner permutations filling four unit gaps',gap=None,
                source_plan_sha256=sha(parent/'data/PLAN.json'),
                source_owners_sha256=sha(parent/'data/OWNERS.json.gz'),
                assignment_sha256=sha(data/'OWNERS.json'),
                assignment_content_sha256=hashlib.sha256(json.dumps(owners,sort_keys=True,separators=(',',':')).encode()).hexdigest())
    dump(data/'PLAN.json',plan)
    assert sha(data/'OWNERS.json') == spec['data']['owners_sha256']
    assert sha(data/'PLAN.json') == spec['data']['plan_sha256']
    shutil.copyfile(HERE/'data/SPEC.json',data/'SPEC.json')
    pivot = Path(spec['pivot_swap']['recipe'])
    (output/pivot).parent.mkdir(parents=True)
    shutil.copyfile(parent/pivot,output/pivot)
