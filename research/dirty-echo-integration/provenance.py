"""Bind inherited inputs; no network, regeneration, or trust in filenames alone."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def check():
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for name,digest in pins['files'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('inherited source hash mismatch: '+name)
    return pins
