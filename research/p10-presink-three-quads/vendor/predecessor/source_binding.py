"""Immutable PR320 source dependency and exact successor change-set admission.
Prepared with OpenAI Codex assistance; Apache-2.0. No archive extraction or network.
"""
from pathlib import Path,PurePosixPath
import hashlib,json,tarfile
ROOT=Path(__file__).resolve().parent
COMMIT='1b37957d1520c80b6ea796bf418e52be5109c2d4'
SOURCE_MANIFEST='adc6bc2957f472dacd6d1ec4f0533d7ced704b6d28d4655f2f2b7437976381f2'
def sha(data):return hashlib.sha256(data).hexdigest()
def check():
    spec=json.loads((ROOT/'SOURCE.json').read_text())
    assert spec['schema']=='immutable-pr320-presink-source/1'
    assert spec['commit']==COMMIT and spec['package_path']=='research/five-stage-p10-transcript-stages'
    assert spec['upstream_manifest_sha256']==SOURCE_MANIFEST
    assert spec['archive']=='upstream/pr320-package.tar.gz'
    archive=ROOT/spec['archive'];assert sha(archive.read_bytes())==spec['archive_sha256']
    source={}
    with tarfile.open(archive,'r:gz') as tf:
        for member in tf.getmembers():
            path=PurePosixPath(member.name)
            assert member.isfile() and not path.is_absolute() and '..' not in path.parts
            assert member.name==path.as_posix() and member.name not in source
            stream=tf.extractfile(member);assert stream is not None
            source[member.name]=stream.read()
    assert sha(source['MANIFEST.json'])==SOURCE_MANIFEST
    upstream=json.loads(source['MANIFEST.json'])['files']
    assert {name:sha(data) for name,data in source.items() if name!='MANIFEST.json'}==upstream
    current={}
    for path in ROOT.rglob('*'):
        assert not path.is_symlink(),'symlink in successor'
        if path.is_file() and path!=ROOT/'MANIFEST.json':
            current[path.relative_to(ROOT).as_posix()]=sha(path.read_bytes())
    assert set(upstream)<=set(current),'upstream source file removed'
    modified=sorted(name for name,digest in upstream.items() if current[name]!=digest)
    added=sorted(set(current)-set(upstream))
    assert modified==spec['modified_paths'] and added==spec['added_paths'],'unlisted source change'
    for original in ('README.md','STAGES-PROOF.md','PR-STATEMENT.md'):
        assert (ROOT/('UPSTREAM-PR320-'+original)).read_bytes()==source[original]
    return dict(status='PASS_IMMUTABLE_PR320_SOURCE_AND_EXACT_CHANGE_SET',commit=COMMIT,
                archive_sha256=spec['archive_sha256'],upstream_manifest_sha256=SOURCE_MANIFEST,
                upstream_files=len(upstream),unchanged_files=len(upstream)-len(modified),
                modified_paths=modified,added_paths=added)
