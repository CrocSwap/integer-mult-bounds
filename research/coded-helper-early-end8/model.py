"""Recount the fixed PR626 budget and derive all four mixture deltas."""
from collections import Counter
from construct import read, require

BASE = 'research/complex-k492-owner-repair'
DATA = BASE + '/vendor/multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/inputs/data-base/work/complex-nine-native/DATA-PHASES.json'


def integers(mapping):
    return {int(r): n for r,n in mapping.items()}


def difference(left, right):
    return {r: left.get(r,0)-right.get(r,0) for r in set(left)|set(right) if left.get(r,0)!=right.get(r,0)}


def build(root, original, retimed):
    spec = read(root / BASE / 'data/SPEC.json')
    plan = read(root / BASE / 'data/PLAN.json')
    data = read(root / DATA)
    calls = Counter(pid for _,_,pid in spec['dispatch'])
    require(calls == {'ck':8,'jp8':64} and plan['M']==data['m']==73 and
            plan['L']==9 and plan['T']==8 and data['ports']==112, 'Fixed comparison geometry')
    require([[c['stage'],c['replica'],c['provider']] for c in plan['provider_calls']] == spec['dispatch'], 'Dispatch binding')
    caps = Counter()
    for capacity,times in plan['windows'].values():
        caps[capacity] += data['ports']
    independent_caps = Counter()
    for recipe in data['recipes']:
        for child in recipe['idle_children']:
            independent_caps[child['rank']] += plan['T']
    require(independent_caps.pop(0)==2*112*8 and caps==independent_caps, 'Independent capacity census')
    local, widths = Counter(), Counter()
    for pid,count in calls.items():
        source = spec['providers'][pid]
        profile, inventory = integers(source['expected_profile']), integers(source['inventory'])
        registry = plan['provider_registry'][pid]
        require(integers(registry['actual_paid_profile'])==profile and Counter(registry['widths'])==inventory, 'Provider source billing')
        local.update({r:n*count for r,n in profile.items()})
        widths.update({w:n*count for w,n in inventory.items()})
    require(widths==Counter(w for call in plan['per_call_widths'] for w in call['widths']), 'Complete helper demand')
    global_profile = integers(spec['expected']['global_profile'])
    require(local+Counter(integers(spec['expected']['idle_remainder_profile']))==global_profile==integers(plan['profile']), 'Complete baseline invoice')
    require(plan['live']==spec['expected']['live']==7168 and
            sum(r*n for r,n in global_profile.items())==spec['expected']['rank_mass']==plan['live']*73-plan['deficit'], 'Baseline rank/deficit')
    variants = {}
    for family,receipts in [('original9',original),('early8',retimed)]:
        for placement in ('positive','negative'):
            deltas = []
            for pid in ('ck','jp8'):
                receipt = receipts[placement+'-'+pid]
                require(receipt['live_columns_each_orientation']==224+receipt['helpers'] and
                        receipt['status']=='PASS_CHANGED_WORD_ALL_COLUMNS_AND_NATIVE_FRAMES', 'Exact native obligation')
                deltas.append(dict(profile=difference(integers(receipt['local_profile']),integers(spec['providers'][pid]['expected_profile'])),
                                   widths=difference(dict(Counter(receipt['widths'])),integers(spec['providers'][pid]['inventory']))))
            require(deltas[0]==deltas[1], 'Provider-independent variant billing')
            variants[family+'-'+placement] = deltas[0]
    result = dict(endpoint=spec['expected']['complex_lower'],m=73,live=7168,calls=72,
                rank_mass=spec['expected']['rank_mass'],capacities=dict(caps),widths=dict(widths),
                local=dict(local),variants=variants)
    result['global'] = global_profile
    return result
