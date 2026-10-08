#!/usr/bin/env python3
"""Focused rectangular extension patch against pinned PR25 source, not original upstream."""
from difflib import unified_diff
from hashlib import sha256
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parents[2]
FILES=['README.md','NOTICE','Makefile','docs/research/current-status.md','notes/rectangular-semantic-note.tex','tests/test_rectangular_semantic.py'] + sorted(str(p.relative_to(ROOT)) for p in (ROOT/'research/rectangular-semantic').glob('*') if p.suffix in ('.py','.txt') or p.name in ('SOURCE.json','inputs.json','README.md'))

def main():
    source=json.loads((ROOT/'research/rectangular-semantic/SOURCE.json').read_text());base=source['base_commit']
    for path,digest in source['base_source_sha256'].items():
        assert sha256(subprocess.check_output(['git','show',base+':'+path],cwd=ROOT)).hexdigest()==digest,path
    check=ROOT/'build/rectangular-semantic/pinned-patch-check';check.mkdir(parents=True,exist_ok=True);patch=[]
    for path in FILES:
        r=subprocess.run(['git','show',base+':'+path],cwd=ROOT,capture_output=True)
        before=r.stdout.decode() if r.returncode==0 else '';after=(ROOT/path).read_text()
        out=check/path;out.parent.mkdir(parents=True,exist_ok=True)
        if r.returncode==0:out.write_text(before)
        elif out.exists():out.unlink()
        patch.extend(unified_diff(before.splitlines(keepends=True),after.splitlines(keepends=True),
                                  fromfile='a/'+path if before else '/dev/null',tofile='b/'+path))
    target=ROOT/'patches/rectangular-semantic.patch';target.write_text(''.join(patch))
    cmd=['git','apply','--directory='+str(check.relative_to(ROOT))]
    subprocess.run(cmd+['--check',str(target)],cwd=ROOT,check=True)
    subprocess.run(cmd+[str(target)],cwd=ROOT,check=True)
    assert all((check/p).read_bytes()==(ROOT/p).read_bytes() for p in FILES)
    print('PASS focused rectangular patch against pinned PR25 '+base+'; '+str(len(FILES))+' source files')

if __name__=='__main__':main()
