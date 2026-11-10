#!/usr/bin/env python3
"""Passive package membership and SHA-256 integrity only."""
from pathlib import Path
import hashlib,json
def main():
 root=Path(__file__).resolve().parent
 inventory=json.loads((root/'INVENTORY.json').read_text())
 rows=inventory['files']
 expected=set(rows)|{'INVENTORY.json'}
 actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
 if actual!=expected:raise RuntimeError('Package file membership differs')
 for name,row in rows.items():
  parts=Path(name).parts
  if Path(name).is_absolute() or '..' in parts:raise RuntimeError('Invalid member')
  p=root
  for part in parts:
   p=p/part
   if p.is_symlink():raise RuntimeError('Symlink member')
  raw=p.read_bytes()
  if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:
   raise RuntimeError('Member bytes differ: '+name)
 print(json.dumps({'status':'PASS','files':len(rows),'scope':'Passive package bytes only'},sort_keys=True))
if __name__=='__main__':main()

