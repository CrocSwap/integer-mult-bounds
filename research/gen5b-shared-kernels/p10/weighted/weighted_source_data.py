"""Portable pinned inert-data loader; no upstream program is executed."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from support import HERE as PACKAGE_ROOT,OUTPUT as PACKAGE_OUTPUT,SOURCE,HEAD,read_bytes,read as _read,verify_inputs,materialize_word
OUTPUT=PACKAGE_OUTPUT/'weighted'
OUTPUT.mkdir(parents=True,exist_ok=True)
def read(name):
 name={'graph.json':'bitword/selected/bit/graph_p10.json','frames.json':'bitword/selected/bit/frames_p10.json.gz','kchron.json':'bitword/selected/bit/kchron_p10.json'}.get(name,name)
 return _read(name)
def verify():
 verify_inputs();materialize_word()
