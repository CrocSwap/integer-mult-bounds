"""Shared immutable input contract for the independent admission checkers."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import support
PACKAGE_ROOT=support.HERE
PACKAGE_OUTPUT=support.OUTPUT
OUTPUT=support.out('admission','placeholder').parent
SOURCE=support.INPUTS
HEAD=support.HEAD
read_bytes=support.read_bytes
pins=support.pins
verify=support.verify_inputs

def read(name):
 name={'graph.json':'bitword/selected/bit/graph_p10.json','frames.json':'bitword/selected/bit/frames_p10.json.gz','kchron.json':'bitword/selected/bit/kchron_p10.json'}.get(name,name)
 return support.read(name)
