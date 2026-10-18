"""Read-only source archive retention for the attributed PR3624 engines."""
import hashlib,json,tarfile,tempfile,importlib.util
from pathlib import Path
P=Path(__file__).resolve().parent
_temporary=None
def source():
 global _temporary
 manifest=json.loads((P/'PR3624-SOURCE.json').read_text());archive=P/'PR3624-SOURCE.tar.gz'
 if hashlib.sha256(archive.read_bytes()).hexdigest()!=manifest['archive_sha256']:raise ValueError('retained source archive hash')
 _temporary=tempfile.TemporaryDirectory(prefix='three-kappa-source-');root=Path(_temporary.name)
 with tarfile.open(archive)as tf:
  for m in tf:
   if m.isdir():continue
   if not m.isfile()or Path(m.name).is_absolute()or '..' in Path(m.name).parts or m.name not in manifest['files']:raise ValueError('unexpected archive member')
   raw=tf.extractfile(m).read()
   if hashlib.sha256(raw).hexdigest()!=manifest['files'][m.name]['sha256']:raise ValueError('retained member hash')
   path=root/m.name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
 for name in manifest['files']:
  if not(root/name).is_file():raise ValueError('missing archive member')
 return root/'research/staged-width-t450'
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
