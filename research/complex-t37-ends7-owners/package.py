"""Pin the complete package and the retained repository source closure."""
from common import P,ROOT,read,sha,load
COPY_TREES=('research/complex-k492-owner-repair',
 'research/structural-gain/frontier-composition',
 'research/community-k492-audit/pr622/replay/baseline558',
 'research/e8-bit-p111-tuned','research/e8-bit-carrier-skeleton',
 'research/complex-sw4-frame8','research/gauge44-frames-x','scripts')
COPY_FILES=('research/direct-delivery504-global/EXPECTED.json',)

def manifest(package=P):
    expected=read(package/'MANIFEST.json')
    actual={p.relative_to(package).as_posix():sha(p)for p in package.rglob('*')
      if p.is_file() and p!=package/'MANIFEST.json' and '__pycache__'not in p.parts}
    if actual!=expected:raise ValueError('Package manifest mismatch')
    return sha(package/'MANIFEST.json')

def validate():
    digest=manifest()
    dependencies=read(P/'DEPENDENCY-PINS.json')
    for relative,expected in dependencies.items():
        path=(ROOT/relative).resolve()
        assert path.is_relative_to(ROOT.resolve()) and not __import__('pathlib').Path(relative).is_absolute()
        assert sha(path)==expected,'Changed retained source: '+relative
    predecessor=load(ROOT/'research/complex-t37-owners/package.py','retained_t37_package').validate()
    return dict(manifest_sha256=digest,dependency_manifest_sha256=sha(P/'DEPENDENCY-PINS.json'),
      dependencies=len(dependencies),retained_t37=predecessor)

if __name__=='__main__':print(validate())
