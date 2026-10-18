"""Rebuild PR533 and compose the frozen PR534 delivery-frame lifts.
Prepared for rohanarun with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import gzip,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'vendor/pr531';out=Path(sys.argv[1]).resolve()
subprocess.run([sys.executable,'-B',str(ROOT/'code/run.py'),str(ROOT/'code/construct_pr533.py'),str(out)],check=True)
sys.path.insert(0,str(P/'vendor/gk'));import gk_word as G;import gk_common as C
G.V=C.V=112;G.DATA=C.DATA=7168
w=json.load(gzip.open(out/'SELECTED.json.gz'));frames=json.loads((ROOT/'data/DELIVERY-FRAMES.json').read_text());assert len(frames)==len(w['B'])
for e,f in zip(w['B'],frames):e[-1]=f
w['report']['local_profile']={str(k):v for k,v in sorted(G.profile(w).items())}
new=out/'coalesced/FULL-WORD.json.gz';new.write_bytes(G.dump(w))
subprocess.run([sys.executable,'-B',str(ROOT/'code/check_frame_lifts.py'),str(out/'SELECTED.json.gz'),str(new),str(out/'FRAME-LIFTS.json')],check=True)
