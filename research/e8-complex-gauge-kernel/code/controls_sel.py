"""Selection-level mutation controls.  usage: controls_sel.py BASE_FULL-WORD.json.gz SELECTION.json OUT.json  (Apache-2.0)"""
import gzip, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import controls_gk as C
base = json.load(gzip.open(sys.argv[1])); sel = json.loads(Path(sys.argv[2]).read_text())
res = C.selection_controls(base, sel)
Path(sys.argv[3]).write_text(json.dumps(dict(status='PASS_SELECTION_MUTATION_CONTROLS', refused=res), indent=2) + '\n'); print(len(res), 'selection controls refused')
