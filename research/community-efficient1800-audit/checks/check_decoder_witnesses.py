"""Independent dynamic-programming check of all stored walk witnesses and provenance.

This supplements, and never replaces, each declared exhaustive census.
"""
from pathlib import Path
from itertools import permutations
from math import comb
import hashlib, json, platform, subprocess, sys, time

P = Path('/tmp/pr-efficient1800')
REPO = Path('/tmp/integer-mult-efficient1100-20261015')

def need(ok, message):
    if not ok:
        raise ValueError(message)

def costs(walk, parity=0):
    # Iterate occurrences, storing shortest subset for each (mask, parity).
    requested = parity
    states = {(0, 0): 0}
    for value in walk:
        updated = dict(states)
        for (mask, parity), cost in states.items():
            key = (mask ^ value, 1-parity)
            updated[key] = min(updated.get(key, 100), cost+1)
        states = updated
    return {mask:cost for (mask, parity),cost in states.items() if parity == requested}

def price(pair, shared=False):
    for w in pair:
        need(len(w) >= 2 and w[0] == 0, 'bad restored walk')
        need(all(type(x) is int and 0 <= x < 32 for x in w), 'bad label')
        need(all(a != b for a,b in zip(w, w[1:]+[0])), 'zero edge')
    tables = [costs(w) for w in pair]
    merged = {}
    for a, ca in tables[0].items():
        for b, cb in tables[1].items():
            merged[a ^ b] = min(merged.get(a ^ b, 100), ca+cb)
    if shared:
        odds = [costs(w, 1) for w in pair]
        for a, ca in odds[0].items():
            for b, cb in odds[1].items():
                merged[a ^ b] = min(merged.get(a ^ b, 100), ca+cb)
    need(len(merged) == 32, 'stored witness does not cover')
    r = sum(merged[m] for m in range(1, 32))
    x = sum(2*((a ^ b).bit_count()-1) for w in pair for a,b in zip(w,w[1:]+[0]))
    return r,x

def witnesses(node, shared=False):
    count = 0
    if isinstance(node, dict):
        if 'walks' in node:
            r,x = price(node['walks'], shared)
            need(node['R_shared' if shared else 'R'] == r and node['path_X'] == x, 'stored champion mismatch')
            need(node['tariff'] == 38*8+2*r+2*x, 'stored champion tariff')
            if shared:
                need(price(node['walks'])[0] == node['R_independent'], 'independent comparator')
            count += 1
        for key in ('first_witness', 'first_witnesses'):
            for r,pair in node.get(key, {}).items():
                actual,_ = price(pair, shared)
                need(actual == int(r), 'stored spectrum witness mismatch')
                count += 1
        count += sum(witnesses(value, shared) for value in node.values())
    elif isinstance(node, list):
        count += sum(witnesses(value, shared) for value in node)
    return count

def ordering_check():
    counts = []
    for labels, expected in [((1,1,2,2,4),12), ((1,1,1,2,4),2)]:
        valid = [(0,)+p for p in set(permutations(labels)) if
                 all(a != b for a,b in zip((0,)+p,p+(0,)))]
        need(len(valid) == expected, 'ordered representative count')
        need(all(costs(w) == costs((0,)+labels) for w in valid), 'permutation changed readout')
        counts.append(len(valid))
    need(comb(31,2)*29 == 31*comb(30,2) == 13485, 'multiset count')
    need(13485*sum(counts) == 188790, 'ordered total')
    return dict(multisets=26970, nonzero_ordered_walks=188790, orders_per_shape=counts)

for number in map(int, sys.argv[1:]):
    start = time.monotonic()
    root = P/'sources'/str(number)
    package = next((root/'research').glob('shared-dirt-walks*' if number == 2867 else 'independent-walks*'))
    source = json.loads((package/'SOURCES.json').read_text())
    bindings = 0
    for rec in source['files']:
        if rec['usage'] != 'input':
            continue
        spec = source['base_commit']+':'+rec['path']
        raw = subprocess.check_output(['git','show',spec],cwd=REPO)
        need(raw == (root/rec['path']).read_bytes(), 'original Git input mismatch')
        need(hashlib.sha256(raw).hexdigest() == rec['sha256'], 'SHA256 input mismatch')
        need(subprocess.check_output(['git','rev-parse',spec],cwd=REPO,text=True).strip() == rec['git_blob'], 'Git blob mismatch')
        bindings += 1
    cert = json.loads((package/'CERTIFICATE.json').read_text())
    need(cert['claim']['no_new_kappa'] is True, 'scope flag type')
    need(cert['unit_tariff'] == {'b':38,'a':2,'x':2}, 'fixed tariff')
    count = witnesses(cert, shared=number == 2867)
    detail = dict(original_git_bindings=bindings, independently_checked_stored_witnesses=count)
    if number == 2860:
        detail['ordering_clarification'] = ordering_check()
    log = P/f'check-{number}-supplement.log'
    log.write_text(json.dumps(dict(status='PASS', **detail),sort_keys=True)+'\n')
    receipt = dict(number=number,head=json.loads((P/f'{number}.json').read_text())['headRefOid'],
        status='passed',seconds=time.monotonic()-start,commands=[dict(argv=[sys.executable,str(Path(__file__).resolve()),str(number)],exit_code=0)],
        input_sha256={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in
            (Path(__file__),package/'CERTIFICATE.json',package/'SOURCES.json')},
        log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),
        environment=dict(python=sys.version,platform=platform.platform()),details=detail,
        scope='Independent DP of stored witnesses and exact original input binding; declared exhaustive coverage and inherited comparison claims remain separate.')
    (P/f'check-{number}-supplement.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(number,log.read_text().strip(),flush=True)
