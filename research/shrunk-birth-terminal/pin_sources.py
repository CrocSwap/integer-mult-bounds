#!/usr/bin/env python3
"""Explicitly freeze the complete portable source/input closure before verification."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
REPOSITORY_FILES=['.gitattributes','Makefile','.github/workflows/verify.yml','README.md','NOTICE','LICENSE','scripts/check_lean_axioms.py','tests/test_shrunk_birth_terminal.py','formal/lean/KappaCheck.lean','formal/lean/KappaCheck/ShrunkBirthTerminal.lean','formal/lean/AuditAll.lean','formal/lean/sources.py','formal/lean/SOURCES.md','research/joint-dual/SOURCE.json','certificates/joint-dual-kappa.json','certificates/joint-dual-validation.json']
def sha(p):return sha256(p.read_bytes()).hexdigest()
def main():
    files={str(p.relative_to(HERE)):sha(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='SOURCE.json' and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    # Archived source manifests are data and must themselves be pinned.
    for p in HERE.rglob('SOURCE.json'):
        if p!=HERE/'SOURCE.json':files[str(p.relative_to(HERE))]=sha(p)
    record={'schema':1,'author':'Chafik Boukhalfa with OpenAI Codex assistance','base_commit':'56b66d58297deca1d7dd130247d720e960f77a37','scope':'Complete selected finite construction, portable reproduction, exact arithmetic, original sources and scoped Lean companion. Repository-validation receipts are derived and excluded from this freeze.','package_files':dict(sorted(files.items())),'repository_files':{p:sha(ROOT/p) for p in sorted(REPOSITORY_FILES)}}
    (HERE/'SOURCE.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print('Pinned',len(files),'package files and',len(REPOSITORY_FILES),'repository integration files')
if __name__=='__main__':main()
