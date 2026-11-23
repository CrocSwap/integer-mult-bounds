"""Authenticate and rebuild the #8076 signed six-column addendum from public artifacts."""
from argparse import ArgumentParser
from datetime import datetime, timezone
from hashlib import sha1,sha256
from pathlib import Path, PurePosixPath
from shutil import copyfile,copytree
from tempfile import TemporaryDirectory
import json
import runpy
import subprocess
import sys
import tarfile

HEAD='d502eb21637717fe22fc16d4c4e3ede6ec59a106'
PREVIOUS_SHA='1ffaf4eed67cfe2271820bc94d62721573ff715829c829c5d9936b561eacb270'
PEER_SHA='0e0d559bdb15e7b647f88a2b5e27fcdc9e28e81d8f4145459876ba6da2e9314c'
PEER_NAME='six-column-8073/peer8057.tar.gz'
SCIENCE=['invoice','independent_price','cutoff','placement','calendar','ownership',
         'exterior','nested','raw','product','stages','ordinary_floor','setup','corrupted_owner']
EXTRA=['source_invoice','ordinary_tariff','stage_caps']
HERE=Path(__file__).resolve().parent


def utc():
    return datetime.now(timezone.utc).isoformat()


def verify_member_names(archive):
    known=set()
    for m in archive:
        p=PurePosixPath(m.name)
        if not (m.isfile() or m.isdir()) or p.is_absolute() or '..' in p.parts or (
                p.as_posix()!=m.name or m.name in known or '\\' in m.name):
            raise ValueError('Unexpected archive member '+m.name)
        known.add(m.name)
    return known


def restore(peer_container,root):
    if sha256(peer_container.read_bytes()).hexdigest()!=PREVIOUS_SHA:
        raise ValueError('Expected the exact frozen #8073 six-column archive')
    with tarfile.open(peer_container,'r:gz') as archive:
        names=verify_member_names(archive)
        if len(names)!=28 or PEER_NAME not in names:
            raise ValueError('Unexpected preceding capsule directory')
        data=archive.extractfile(PEER_NAME).read()
    if sha256(data).hexdigest()!=PEER_SHA:
        raise ValueError('Shared #8057 peer archive digest differs')
    (root/'peer8057.tar.gz').write_bytes(data)
    with tarfile.open(root/'peer8057.tar.gz','r:gz') as archive:
        verify_member_names(archive)
    provenance=json.loads((HERE/'source-blobs.json').read_bytes())
    assert provenance['head']==HEAD and provenance['pr']==8076 and len(provenance['files'])==15
    for relative,git_id in provenance['files'].items():
        path=PurePosixPath(relative)
        assert path.parent.as_posix()=='research/p104-weighted-child-tariff'
        dest=root/path.name
        if path.name!='peer8057.tar.gz':
            copyfile(HERE/'source8076'/path.name,dest)
        b=dest.read_bytes()
        assert sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()==git_id
    peer=runpy.run_path(str(root/'verify.py'))['restore'](root/'peer')
    runpy.run_path(str(root/'prepare.py'))['materialize'](peer)
    subprocess.run([sys.executable,'-IB',str(peer/'bootstrap.py'),str(root/'runtime')],check=True)
    for p in (HERE/'changes').iterdir():
        assert p.is_file() and p.suffix=='.py'
        copyfile(p,root/p.name)
    subprocess.run([sys.executable,'-IB',str(root/'build_successor.py')],check=True)
    return peer


def run_extra(scope,root,peer,out):
    runtime=root/'successor/runtime'
    if scope=='source_invoice':
        args=[str(peer/'receipt.py'),str(root/'runtime')]
    elif scope=='ordinary_tariff':
        args=[str(root/'check_tariff.py'),str(peer/'independent_price.py'),str(runtime)]
    else:
        args=[str(root/'stage_caps.py')]
    start=utc()
    completed=subprocess.run([sys.executable,'-IB',*args],capture_output=True)
    end=utc()
    (out/f'{scope}.out').write_bytes(completed.stdout)
    (out/f'{scope}.err').write_bytes(completed.stderr)
    completed.check_returncode()
    if scope=='source_invoice':
        assert completed.stdout==(root/'RESULT.json').read_bytes()
    if scope=='stage_caps':
        assert json.loads(completed.stdout)==json.loads((HERE/'stage-caps.json').read_bytes())
    return {'mode':scope,'started_at':start,'finished_at':end,'code':0,
            'output_sha256':sha256(completed.stdout).hexdigest()}


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--predecessor-archive',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--scope',choices=SCIENCE+EXTRA,nargs='+',default=EXTRA+SCIENCE)
    args=parser.parse_args()
    start=utc()
    out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((HERE/'MANIFEST.json').read_bytes())
    for name,digest in manifest.items():
        path=PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts and path.as_posix()==name
        assert sha256((HERE/name).read_bytes()).hexdigest()==digest
    records={}
    with TemporaryDirectory(prefix='six-8076-') as scratch:
        root=Path(scratch)
        peer=restore(args.predecessor_archive.resolve(),root)
        for scope in args.scope:
            if scope in EXTRA:
                records[scope]=run_extra(scope,root,peer,out)
        wanted=[s for s in args.scope if s in SCIENCE]
        if wanted:
            result=subprocess.run([sys.executable,'-IB',str(root/'run_successor.py'),*wanted])
            logs=root/'successor/logs'
            copytree(logs,out/'logs')
            for s in wanted:
                rec=json.loads((logs/f'{s}.json').read_bytes())
                assert rec['code']==0 and rec['output_sha256']==sha256((logs/f'{s}.out').read_bytes()).hexdigest()
                records[s]=rec
            result.check_returncode()
            if 'invoice' in wanted:
                assert (logs/'invoice.out').read_bytes()==(HERE/'candidate-result.json').read_bytes()
        copyfile(root/'successor/delta-pins.json',out/'delta-pins.json')
    (out/'cold-result.json').write_text(json.dumps({'source_head':HEAD,'tested':records,'pass':True,
        'started_at':start,'finished_at':utc(),'verified_addendum_files':len(manifest),
        'pr8076_scientific_blobs':15,'pr8057_peer_files':88},indent=2)+'\n')
    print('PASS',len(records),'scopes')


if __name__=='__main__':
    main()
