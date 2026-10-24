"""Pick the best receiver choice for each of the top-40 distinct profiles in stage C (skipping ones already tuned)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
done = {json.dumps(s, sort_keys=True) for s in json.load(open(os.path.join(HERE, "..", "tuned", "pick1.json")))}
rows = sorted((json.loads(l) for l in open(os.path.join(HERE, "..", "results_C.jsonl"))), key=lambda r: -r["kappa"])
seen, out = set(), []
done_k = {round(json.load(open(os.path.join(HERE, "..", "tuned", f)))["base_kappa"], 12)
          for f in os.listdir(os.path.join(HERE, "..", "tuned")) if f.endswith("-result.json")}
for r in rows:
    key = json.dumps(r["profile"], sort_keys=True)
    sel = r["receivers"]
    if key in seen or round(r["kappa"], 12) in done_k or json.dumps(sel, sort_keys=True) in done:
        continue
    seen.add(key)
    out.append(sel)
    print("%.12f R %s %s" % (r["kappa"], r["R"], sel))
    if len(out) == 40:
        break
json.dump(out, open(os.path.join(HERE, "..", "tuned", "pick2.json"), "w"))
