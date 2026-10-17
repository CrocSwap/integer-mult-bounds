#!/usr/bin/env python3
"""assemble.py SRC DEST --providers P.json --words BASE.json.gz EXTRA.json.gz --label L --note TEXT [--extra-json K=V ...]
Copies a checked T74 fill directory (FILL/ORDER/DISPATCH/OWNER-CHECK/CONTROLS) into PR2917's allocation layout:
PROFILE.json reformatted (indent 2, int-ordered, no newline), PROVIDERS.json = the given registry bytes, vendor/ = PR2917's engine/PLAN/TEMPLATE,
SEARCH.json (method/lineage/numbers), then writes DEST-PINS (sha256 of every file) next to DEST."""
import argparse, hashlib, json, pathlib, shutil
ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('dest'); ap.add_argument('--providers', required=True)
ap.add_argument('--words', nargs=2, required=True); ap.add_argument('--label', required=True); ap.add_argument('--note', default='')
a = ap.parse_args()
P17 = pathlib.Path('S/r13/vendor/pr2917/research/paired-helper-extension')
src, dest = pathlib.Path(a.src), pathlib.Path(a.dest)
assert not dest.exists()
(dest / 'vendor').mkdir(parents=True)
for n in ['FILL.json.gz', 'ORDER.json', 'DISPATCH.json', 'OWNER-CHECK.json']:
    shutil.copy(src / n, dest / n)
shutil.copy(a.providers, dest / 'PROVIDERS.json')
for n in ['independent_owners.py', 'PLAN.json.gz', 'TEMPLATE.json.gz']:
    shutil.copy(P17 / 'allocation/vendor' / n, dest / 'vendor' / n)
prof = json.load(open(src / 'PROFILE.json'))
(dest / 'PROFILE.json').write_text(json.dumps({str(k): prof[str(k)] for k in sorted(int(k) for k in prof)}, indent=2))
oc = json.load(open(src / 'OWNER-CHECK.json'))
ct = json.load(open(src / 'CONTROLS.json')) if (src / 'CONTROLS.json').exists() else {}
words = {t: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() for t, p in zip(('base', 'extra'), a.words)}
search = dict(status='C1_FLOW_ROUTE_LITERAL_FILL_' + a.label, note=a.note, words_sha256=words, chronology=oc.get('chronology'), solver=oc.get('solver'), seed=oc.get('seed'),
              catalogue=oc.get('catalogue'), pattern_mix=oc.get('pattern_mix'), idle_histogram=oc['idle'], profile=oc['profile'], roles=oc['roles'], replicas=oc['T'], calls=oc['calls'],
              physical=oc['physical'], kappa_root_bracket=[oc['kappa_lower'], oc['kappa_upper']], kappa_root_lower_decimal=oc['kappa_lower_decimal'],
              relaxation_cap_bracket=[oc['relaxation_cap_lower'], oc['relaxation_cap_upper']], gap_to_relaxation_cap_float=oc['gap_to_relaxation_cap'],
              moment_auditor=ct.get('moment', {}).get('status'), headline=ct.get('headline_target'), order_and_dispatch_unchanged_vs_PR2917=True,
              lineage='PR2917 (mason-hale) chronology/engine; PR2930/PR2942 fills; r14 lane A words; PR2857 flow model and realization; PR2839 owner engine; lane C r12 relax/root/fill tools; r13/r14 lane C1.')
(dest / 'SEARCH.json').write_text(json.dumps(search, sort_keys=True, indent=1) + '\n')
pins = {p.relative_to(dest).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dest.rglob('*')) if p.is_file()}
pathlib.Path(str(dest) + '-PINS.json').write_text(json.dumps(pins, sort_keys=True, indent=1))
print('assembled', dest); [print(v, k) for k, v in pins.items()]
