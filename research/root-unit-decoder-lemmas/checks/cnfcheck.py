"""usage: cnfcheck.py CNF SOURCES.json -- prints PASS/FAIL for sha256(CNF) == the pin of SOURCES.json (derived.d5_zr.cnf) and the header counts."""
import hashlib, json, sys
cnf, src = sys.argv[1], sys.argv[2]
pin = json.load(open(src))['derived']['d5_zr.cnf']
raw = open(cnf, 'rb').read(); h = hashlib.sha256(raw).hexdigest()
first = raw.split(b'\n', 1)[0].decode().split()
ok = h == pin['sha256'] and first[:4] == ['p', 'cnf', str(pin['vars']), str(pin['clauses'])]
print(('PASS' if ok else 'FAIL') + f" G5.cnf-sha256  regenerated D5 CNF: sha256 {h} == pin, p cnf {first[2]} {first[3]}" if ok else f"FAIL G5.cnf-sha256  got {h} header {first}")
sys.exit(0 if ok else 1)
