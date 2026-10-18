"""Authenticate the scientific source closure before predecessor execution."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
def authenticate():
 for row in json.loads((Path(__file__).parent/'SOURCES.json').read_text())['files']:
  p=ROOT/row['path']
  if p.is_symlink()or not p.is_file()or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:
   raise ValueError('changed scientific source: '+row['path'])
