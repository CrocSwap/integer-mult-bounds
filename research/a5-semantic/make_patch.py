#!/usr/bin/env python3
"""Focused A5 extension patch against pinned PR23 source, not original upstream."""
from difflib import unified_diff
from hashlib import sha256
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parents[2]
FILES=['README.md','NOTICE','Makefile','docs/research/current-status.md',
       'research/a5-semantic/README.md','research/a5-semantic/witness.py',
       'research/a5-semantic/controls.py','research/a5-semantic/a5-block.tex',
       'research/a5-semantic/make_patch.py','research/a5-semantic/SOURCE.json',
       'notes/a5-semantic-note.tex','tests/test_a5_semantic.py']

def main():
    source=json.loads((ROOT/'research/a5-semantic/SOURCE.json').read_text());base=source['base_commit']
    for path,digest in source['base_input_sha256'].items():
        assert sha256(subprocess.check_output(['git','show',base+':'+path],cwd=ROOT)).hexdigest()==digest,path
    check=ROOT/'build/a5-semantic/pinned-patch-check';check.mkdir(parents=True,exist_ok=True);patch=[]
    for path in FILES:
        r=subprocess.run(['git','show',base+':'+path],cwd=ROOT,capture_output=True)
        before=r.stdout.decode() if r.returncode==0 else '';after=(ROOT/path).read_text()
        out=check/path;out.parent.mkdir(parents=True,exist_ok=True)
        if r.returncode==0:out.write_text(before)
        elif out.exists():out.unlink()
        patch.extend(unified_diff(before.splitlines(keepends=True),after.splitlines(keepends=True),
                                  fromfile='a/'+path if before else '/dev/null',tofile='b/'+path))
    target=ROOT/'patches/a5-semantic.patch';target.write_text(''.join(patch))
    cmd=['git','apply','--directory='+str(check.relative_to(ROOT))]
    subprocess.run(cmd+['--check',str(target)],cwd=ROOT,check=True)
    subprocess.run(cmd+[str(target)],cwd=ROOT,check=True)
    assert all((check/p).read_bytes()==(ROOT/p).read_bytes() for p in FILES)
    print('PASS focused A5 patch against pinned PR23 '+base+'; '+str(len(FILES))+' source files')

if __name__=='__main__':main()
