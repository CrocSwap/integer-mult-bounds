"""Reconstruct both public six-column capsules and compare every installed source file."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path,PurePosixPath
from tempfile import TemporaryDirectory
import json
import runpy
import subprocess
import sys
import tarfile

PINS={'old':'1ffaf4eed67cfe2271820bc94d62721573ff715829c829c5d9936b561eacb270',
      'new':'bacfc6ec44616063eae1584e6af07a1dbbfaf7948df1745bc059aa4510c7c9a0'}

def unpack(path,pin,folder):
    if sha256(path.read_bytes()).hexdigest()!=pin:raise ValueError('Incorrect capsule digest')
    names=set()
    with tarfile.open(path,'r:gz') as archive:
        for m in archive:
            p=PurePosixPath(m.name)
            if not m.isfile() or p.is_absolute() or '..' in p.parts or (
                    p.as_posix()!=m.name or m.name in names or '\\' in m.name):
                raise ValueError('Unexpected capsule member')
            names.add(m.name)
            dest=folder/p
            dest.parent.mkdir(exist_ok=True,parents=True)
            dest.write_bytes(archive.extractfile(m).read())

def file_table(folder):
    return {f.relative_to(folder).as_posix():sha256(f.read_bytes()).hexdigest()
            for f in folder.rglob('*') if f.is_file() and '__pycache__' not in f.parts}

def compare(old,new):
    output={}
    for subtree in ('runtime','peer'):
        a=file_table(old/subtree)
        b=file_table(new/subtree)
        if a.keys()!=b.keys():raise ValueError('Installed file list differs')
        dif={k:[a[k],b[k]] for k in a if a[k]!=b[k]}
        shared={k:v for k,v in a.items() if b[k]==v}
        fingerprint=sha256(json.dumps(shared,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        output[subtree]={'files':len(a),'identical_files':len(shared),
                         'same_file_table_sha256':fingerprint,'differences':dif}
    return output

def main():
    cli=ArgumentParser(description=__doc__)
    cli.add_argument('--predecessor-archive',type=Path,required=True)
    cli.add_argument('--addendum-archive',type=Path,required=True)
    cli.add_argument('--output',type=Path,required=True)
    args=cli.parse_args()
    with TemporaryDirectory(prefix='compare-six-columns-') as temporary:
        leaf=Path(temporary)
        unpack(args.predecessor_archive,PINS['old'],leaf)
        unpack(args.addendum_archive,PINS['new'],leaf)
        old=leaf/'six-column-8073'
        new=leaf/'six-column-8076'
        subprocess.run([sys.executable,'-IB',str(old/'compose8073.py')],check=True)
        work=leaf/'reconstructed-8076'
        work.mkdir()
        verifier=runpy.run_path(str(new/'replay8076.py'))
        verifier['restore'](args.predecessor_archive,work)
        out=compare(old/'combined/successor',work/'successor')
        expected=json.loads((new/'physical-equivalence.json').read_bytes())
        if out!=expected:raise ValueError('Reconstructed comparison differs from the published observation')
    with args.output.open('x') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
    print('PASS',out['runtime']['identical_files'],'of',out['runtime']['files'],'runtime files;',
          out['peer']['identical_files'],'of',out['peer']['files'],'peer files')

if __name__=='__main__':
    main()
