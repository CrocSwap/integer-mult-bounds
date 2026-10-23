"""Reuse the unchanged, hash-pinned independently authored pricing primitive."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import support
_original=support.load_authored('_published_price_candidate','../p10/arithmetic/price_candidate.py')
globals().update({k:v for k,v in vars(_original).items()if not k.startswith('__')})
