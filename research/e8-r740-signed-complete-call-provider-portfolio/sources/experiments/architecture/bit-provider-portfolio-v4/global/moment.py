from pathlib import Path
import json,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
s=importlib.util.spec_from_file_location('M',ROOT/'experiments/architecture/complex-direct8-eleven451/work/pr361/code/engines/moment.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
g=json.load(open(P/'NOMINATION.json'));H={int(k):v for k,v in g['profile'].items()};r=M.certify(H,78,9600,True);(P/'MOMENT.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
