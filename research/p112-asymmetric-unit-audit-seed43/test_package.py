"""Small exact controls for the standard-library F2 and sink encodings."""
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("p112_d077_verify",HERE/"verify.py")
if spec is None or spec.loader is None: raise RuntimeError("load verifier")
v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
need=v.f2_rank([[1,0,1],[0,1,1],[1,1,0]])==2
if not need: raise ValueError("F2 rank control")
if v.bits9(378) != [1,0,1,1,1,1,0,1,0]: raise ValueError("sink word bit order")
print("PASS_P112_D077_SMALL_CONTROLS rank_f2=2 sink_bits=PASS")
