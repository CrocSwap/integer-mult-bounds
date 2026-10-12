#!/usr/bin/env python3
"""Extract exact packing templates from immutable PR527 data. No model inference.
The JSON-to-Lean association is an external trust boundary, recorded in README.
"""
from pathlib import Path
from collections import defaultdict, Counter
import argparse, gzip, hashlib, json

ROOT = Path(__file__).resolve().parent

def require(condition, message):
    if not condition:
        raise ValueError(message)

def extract(plan, roles):
    groups, calls = defaultdict(list), defaultdict(list)
    for r in roles:
        for key in ('owner_replica', 'child', 'port', 'time', 'helper', 'family', 'offset', 'width'):
            require(type(r[key]) is int and r[key] >= 0, f'invalid {key}')
        require(r['width'] > 0, 'empty helper')
        require(r['helper'] < len(plan['baseline_widths']), 'helper index')
        require(r['width'] == plan['baseline_widths'][r['helper']], 'helper width')
        require(r['time'] < len(plan['order']), 'call time')
        require([r['stage'], r['replica']] == plan['order'][r['time']], 'call identity')
        g = (r['owner_replica'], r['child'], r['port'])
        capacity, times = plan['windows'][f'{g[0]},{g[1]}']
        require(r['time'] in times, 'outside declared window')
        groups[g].append(r)
        calls[r['time']].append(r)
    require(set(calls) == set(range(len(plan['order']))), 'missing call')
    for rows in calls.values():
        require(sorted(r['helper'] for r in rows) == list(range(len(plan['baseline_widths']))), 'helper census')
        require(len({r['family'] for r in rows}) == len(rows), 'owner family collision')
    templates = Counter()
    assignments = []
    for g, rows in sorted(groups.items()):
        capacity = plan['windows'][f'{g[0]},{g[1]}'][0]
        rows = sorted(rows, key=lambda r: r['offset'])
        end = 0
        for r in rows:
            require(r['offset'] == end, 'gap or overlap')
            end += r['width']
        require(end <= capacity, 'owner capacity exceeded')
        key = (capacity, tuple(r['width'] for r in rows))
        templates[key] += 1
        assignments.append((g, key))
    return templates, assignments

def render(templates, namespace="PR527"):
    literals = ',\n  '.join(f'({cap}, [{", ".join(map(str, ws))}])' for cap, ws in sorted(templates))
    source = '''/- Exact data derived from pinned owner records; regenerate with generate.py. -/
import OwnerTransport
namespace OwnerTransport.PR527

def templates : List (Nat × List Nat) := [
  ''' + literals + ''']

def widthAt (ws : List Nat) (i : Nat) : Nat := (ws[i]?).getD 0

def Fits (t : Nat × List Nat) : Prop :=
  offset (widthAt t.2) t.2.length ≤ t.1

instance (t : Nat × List Nat) : Decidable (Fits t) :=
  inferInstanceAs (Decidable (offset (widthAt t.2) t.2.length ≤ t.1))

/-- Every extracted packing template passes the Lean kernel's arithmetic check. -/
theorem all_templates_fit : templates.all (fun t => decide (Fits t)) = true := by
  decide

/-- Membership in the checked table supplies the actual capacity hypothesis. -/
theorem listed_template_fits (t : Nat × List Nat) (h : t ∈ templates) : Fits t := by
  have ht := (List.all_eq_true.mp all_templates_fit) t h
  exact of_decide_eq_true ht

/-- Each listed template defines legal addresses for all its occupied coordinates. -/
theorem listed_address_lt (t : Nat × List Nat) (h : t ∈ templates)
    (i k : Nat) (hi : i < t.2.length) (hk : k < widthAt t.2 i) :
    offset (widthAt t.2) i + k < t.1 := by
  exact transported_address_lt (widthAt t.2) (widthAt t.2) t.2.length t.1 i k
    (fun _ _ => Nat.le_refl _) (listed_template_fits t h) hi hk

/-- The table's occupied coordinates form a nonaliasing, gap-free prefix. -/
theorem listed_template_correct (t : Nat × List Nat) (h : t ∈ templates) :
    offset (widthAt t.2) t.2.length ≤ t.1 ∧
    (∀ i j a b, a < widthAt t.2 i → b < widthAt t.2 j →
      offset (widthAt t.2) i + a = offset (widthAt t.2) j + b → i = j ∧ a = b) ∧
    (∀ x, x < offset (widthAt t.2) t.2.length →
      ∃ i, i < t.2.length ∧ ∃ k, k < widthAt t.2 i ∧ offset (widthAt t.2) i + k = x) := by
  exact compaction_correct (widthAt t.2) (widthAt t.2) t.2.length t.1
    (fun _ _ => Nat.le_refl _) (listed_template_fits t h)

end OwnerTransport.PR527
'''
    return source.replace('OwnerTransport.PR527', 'OwnerTransport.' + namespace)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    summaries = {}
    for namespace, directory, manifest_name in [
            ('PR527', 'source', 'SOURCE.json'), ('PR531', 'source531', 'SOURCE531.json')]:
        manifest = json.loads((ROOT / manifest_name).read_text())
        for name, digest in manifest['sha256'].items():
            require(hashlib.sha256((ROOT/directory/name).read_bytes()).hexdigest() == digest, f'source hash: {name}')
        plan = json.loads((ROOT/directory/'PLAN.json').read_text())
        roles = json.loads(gzip.decompress((ROOT/directory/'OWNERS.json.gz').read_bytes()))
        templates, assignments = extract(plan, roles)
        rendered = render(templates, namespace)
        target = ROOT/(namespace+'Templates.lean')
        if args.check:
            require(target.read_text() == rendered, 'generated Lean source differs: '+namespace)
        else:
            target.write_text(rendered)
        summaries[namespace] = {'roles':len(roles), 'owner_groups':len(assignments), 'templates':len(templates), 'calls':len(plan['order']), 'status':'PASS_EXTERNAL_SOURCE_BINDING'}
    print(json.dumps(summaries, sort_keys=True))

if __name__ == '__main__':
    main()
