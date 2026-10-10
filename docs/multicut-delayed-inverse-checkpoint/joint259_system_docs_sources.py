"""Read-only source views and exact original/public closure binding."""
from __future__ import annotations
import hashlib,json,zipfile,stat
from pathlib import Path,PurePosixPath
BASE=Path(__file__).resolve().parent
BINDING=json.loads((BASE/"joint259_system_docs_source_binding.json").read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical_path(name,allow_directory=False):
    key=name[:-1]if allow_directory and name.endswith('/')else name
    p=PurePosixPath(key)
    if not key or key=='.'or p.is_absolute()or'..'in p.parts or'\\'in key or key!=p.as_posix():raise ValueError('Noncanonical source path')
    return key
class MemoryPath:
    """Minimal read-only Path interface over verified bytes; never extracts."""
    def __init__(self,files,name=""):self.files=files;self.name=PurePosixPath(name)
    def __truediv__(self,child):
        part=PurePosixPath(child)
        if part.is_absolute()or".."in part.parts:raise ValueError("Unsafe source path")
        return MemoryPath(self.files,(self.name/part).as_posix())
    def __eq__(self,other):return isinstance(other,MemoryPath)and self.files is other.files and self.name==other.name
    def read_bytes(self):return self.files[self.name.as_posix()]
    def read_text(self):return self.read_bytes().decode("utf8")
    def is_file(self):return self.name.as_posix()in self.files
    def is_symlink(self):return False
    def rglob(self,pattern):
        if pattern!="*":raise ValueError("Unsupported source scan")
        for key in sorted(self.files):yield MemoryPath(self.files,key)
    def relative_to(self,root):return self.name.relative_to(root.name)
    def resolve(self):return self
def from_mapping(files):
    for k,v in files.items():
        canonical_path(k)
        if not isinstance(v,bytes):raise ValueError("Malformed source mapping")
    return MemoryPath(dict(files))
def open_source(path):
    if isinstance(path,MemoryPath):return path
    path=Path(path)
    if path.is_dir():return path.resolve()
    if not path.is_file()or not zipfile.is_zipfile(path):raise ValueError("Source must be an admitted directory or ZIP")
    with zipfile.ZipFile(path)as z:
        canonical=[canonical_path(r.filename,True)for r in z.infolist()]
        if len(canonical)!=len(set(canonical)):raise ValueError('Duplicate or aliased ZIP member')
        if any(stat.S_ISLNK(r.external_attr>>16)for r in z.infolist()):raise ValueError('ZIP symlink')
        names=[r.filename for r in z.infolist()if not r.is_dir()]
        if len(names)!=len(set(names)):raise ValueError("Duplicate ZIP member")
        if sum(r.file_size for r in z.infolist())>64*1024*1024:raise ValueError("Source ZIP exceeds64MiB")
        candidates=[n for n in names if PurePosixPath(n).name=="MANIFEST.json"]
        if not candidates:raise ValueError("No source manifest")
        depth=min(len(PurePosixPath(n).parts)for n in candidates)
        roots=[n for n in candidates if len(PurePosixPath(n).parts)==depth]
        if len(roots)!=1:raise ValueError("Ambiguous package roots")
        prefix=roots[0][:-len("MANIFEST.json")]
        if any(not n.startswith(prefix)for n in names):raise ValueError("Unpinned siblings outside source root")
        files={n[len(prefix):]:z.read(n)for n in names}
    return from_mapping(files)
def integrity(root,scientific_manifest):
    root=open_source(root)
    if isinstance(root,MemoryPath):from_mapping(root.files)
    digest=sha((root/"MANIFEST.json").read_bytes())
    allowed={scientific_manifest,BINDING["accepted_public_manifest_sha256"]}
    if scientific_manifest!=BINDING["scientific_archive_manifest_sha256"]or digest not in allowed:
        raise ValueError("Unrecognized scientific/public source manifest")
    manifest=json.loads((root/"MANIFEST.json").read_text())["files"]
    paths=list(root.rglob("*"))
    if any(p.is_symlink()for p in paths):raise ValueError("Source symlink")
    actual={p.relative_to(root).as_posix():sha(p.read_bytes())for p in paths if p.is_file()and p!=root/"MANIFEST.json"}
    if actual!=manifest:raise ValueError("Missing, changed or extra source file")
    if any(actual.get(p)!=h for p,h in BINDING["retained_numerical_pins"].items()):raise ValueError("Numerical source binding changed")
    if digest==BINDING["accepted_public_manifest_sha256"]:
        if len(actual)!=136 or sha((root/"expected/certificate.json").read_bytes())!=BINDING["certificate_sha256"]:raise ValueError("Public closure/certificate mismatch")
    elif len(actual)!=143:raise ValueError("Scientific archive member count changed")
    return len(actual)

