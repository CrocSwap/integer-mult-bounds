"""Hash-verified inert inputs only; upstream programs never execute."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from support import SOURCE,HEAD,read_bytes,verify_inputs,out,read as _read
OUTPUT=out('bridge15','placeholder').parent
ALIASES={'graph.json':'bitword/selected/bit/graph_p10.json','frames.json':'bitword/selected/bit/frames_p10.json.gz','kchron.json':'bitword/selected/bit/kchron_p10.json'}
def read(name):return _read(ALIASES.get(name,name))
def verify():return verify_inputs()
