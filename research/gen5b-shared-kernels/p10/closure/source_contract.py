"""Portable source contract for the fixed bounded screen."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from support import SOURCE,HEAD,verify_inputs,OUTPUT,HERE
ROOT=OUTPUT/'closure'
ROOT.mkdir(parents=True,exist_ok=True)
REVIEW=HERE
