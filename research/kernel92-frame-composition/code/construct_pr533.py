"""Rebuild PR531's raw factory and apply the frozen 92-pivot selection.
Prepared by OpenAI Codex. Attributed predecessor implementations stay unchanged.
"""
from pathlib import Path
import gzip,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'vendor/pr531';out=Path(sys.argv[1]).resolve();assert not out.exists();out.mkdir()
subprocess.run([sys.executable,'-B',str(ROOT/'code/run.py'),str(P/'code/construct_504.py'),str(P/'inputs/hamming'),str(out/'raw')],check=True)
sys.path.insert(0,str(P/'vendor/gk'));import gk_word as G;import gk_common as C
G.V=C.V=112;G.DATA=C.DATA=7168
w=json.load(gzip.open(out/'raw/FULL-WORD.json.gz'));selection=json.loads((ROOT/'data/SELECTION.json').read_text());w=G.build(w,selection,check=True)
assert sum(len(c['pivots'])for c in selection['kernel'])==92
assert len(selection['gauge'])==72
(out/'SELECTED.json.gz').write_bytes(G.dump(w))
subprocess.run([sys.executable,'-B',str(ROOT/'code/run.py'),str(P/'code/coalesce_frames.py'),'--word',str(out/'SELECTED.json.gz'),'--out',str(out/'coalesced')],check=True)
