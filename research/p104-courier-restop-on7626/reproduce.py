#!/usr/bin/env python3
"""Materialize the verified mapped bytes only; no path rewriting or science."""
import argparse,hashlib,json,os,runpy,stat
from pathlib import Path
INTEGRITY_SHA='5ac9a3873d7400e3ed36a9d10e335c3825661d5b1b4976885da0908fe138316f'
def need(v,m):
    if not v: raise ValueError(m)
def main():
    p=argparse.ArgumentParser();p.add_argument('--work',required=True);a=p.parse_args()
    lexical=a.work
    need(lexical and all(x not in ('.','..') for x in lexical.split('/')),'ambiguous output path')
    root=Path(os.path.abspath(Path(__file__).parent));work=Path(os.path.abspath(lexical))
    need(not work.is_relative_to(root) and not root.is_relative_to(work),'package/work overlap')
    verifier=root/'INTEGRITY.py';need(verifier.is_file() and not verifier.is_symlink() and hashlib.sha256(verifier.read_bytes()).hexdigest()==INTEGRITY_SHA,'integrity verifier pin')
    functions=runpy.run_path(str(verifier));verified=functions['verify']()
    need(verified.get('status')=='PASS_ARTIFACT_INTEGRITY_ONLY' and verified.get('frozen_inputs')==450 and verified.get('scientific_code_executed') is False,'integrity prerequisite')
    functions['check_ancestors'](work.parent)
    need(not os.path.lexists(work), 'output exists')
    mapping=functions['parse_json']((root/'EXPORT-MAP.json').read_bytes());rows=mapping['files']
    functions['unique_names']([r['portable_path'] for r in rows]+['MATERIALIZED.json'])
    # Validated, non-symlink existing parent; mkdir is exclusive. Inside the new
    # tree each component is checked, and files are created exclusively.
    work.mkdir()
    for row in rows:
        rel=functions['safe'](row['portable_path']);obj=functions['safe'](row['package_path'])
        source=root/obj;functions['check_ancestors'](source)
        st=source.lstat();need(stat.S_ISREG(st.st_mode) and st.st_nlink==1,'source link or nonregular')
        data=source.read_bytes();need(len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],'source bytes')
        parent=work
        for component in rel.parts[:-1]:
            parent=parent/component
            try: parent.mkdir()
            except FileExistsError: pass
            st=parent.lstat();need(stat.S_ISDIR(st.st_mode) and not stat.S_ISLNK(st.st_mode),'unsafe destination parent')
        dest=parent/rel.name
        flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0)
        fd=os.open(dest,flags,0o600)
        with os.fdopen(fd,'wb') as out: out.write(data)
    receipt=work/'MATERIALIZED.json'
    data=(json.dumps({'status':'MATERIALIZED_ONLY','science_executed':False,'frozen_inputs':450,'original_absolute_paths_rewritten':False,'mapping_sha256':hashlib.sha256((root/'EXPORT-MAP.json').read_bytes()).hexdigest()},indent=2)+'\n').encode()
    fd=os.open(receipt,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0),0o600)
    with os.fdopen(fd,'wb') as out: out.write(data)
if __name__=='__main__': main()
