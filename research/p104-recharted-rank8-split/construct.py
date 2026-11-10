"""Compose Rohan Arun's #7122 rechart with one charged, causal helper split.
Ali Romman and CubeJerry supply the retained split and retiming mechanisms.
Prepared for dillona with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import json
from rechart import construct as rechart
from retime import prepare as retime
from split import split
HERE=Path(__file__).resolve().parent

def prepare(word,hit):
    changed=rechart(word,json.loads((HERE/'RECHART.json').read_text()))
    return retime(changed,hit)

def construct(word,hit):
    prepared,spec=prepare(word,hit)
    return split(prepared,spec)
