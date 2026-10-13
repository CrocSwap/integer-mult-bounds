"""make_recipe.py BASEWORD SOLUTION.json BUILTWORD OUT: discovery-side recipe writer (CP-SAT solution -> data recipe)."""
import sys, json, gzip, hashlib
base = gzip.decompress(open(sys.argv[1], 'rb').read()); s = json.load(open(sys.argv[2]))
built = gzip.decompress(open(sys.argv[3], 'rb').read()); bw = json.loads(built)
key = {'A': 0, 'B': 1, 'T': 2}
r = dict(input_content_sha256=hashlib.sha256(base).hexdigest(),
         groups=sorted(int(h) for h in s['newstarts']),
         entrances={h: s['newstarts'][h] for h in sorted(s['newstarts'], key=int)},
         gate_frames=sorted(s['changed'], key=lambda c: (key[c[0]], c[1])),
         expected=dict(output_content_sha256=hashlib.sha256(built).hexdigest(),
                       local_profile=bw['report']['local_profile'], width_inventory=bw['report']['width_inventory']))
json.dump(r, open(sys.argv[4], 'w'), indent=1)
