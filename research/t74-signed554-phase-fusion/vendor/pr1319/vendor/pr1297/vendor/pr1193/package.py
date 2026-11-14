"""Pin this package and the retained source closure; no network is used."""
from pathlib import Path
from common import P,ROOT,read,sha,load

def validate():
    manifest=read(P/'MANIFEST.json')
    actual={str(p.relative_to(P)):sha(p)for p in P.rglob('*')if p.is_file() and p.name!='MANIFEST.json' and '__pycache__'not in p.parts}
    assert actual==manifest,'Package manifest mismatch'
    dependencies=read(P/'DEPENDENCY-PINS.json')
    for rel,pin in dependencies.items():
        q=(ROOT/rel).resolve()
        assert not Path(rel).is_absolute() and q.is_relative_to(ROOT.resolve())
        assert sha(q)==pin,'Changed retained source: '+rel
    retained=load(ROOT/'research/complex-t37-owners/package.py','retained_package_validation').validate()
    return dict(manifest_sha256=sha(P/'MANIFEST.json'),dependency_manifest_sha256=sha(P/'DEPENDENCY-PINS.json'),dependencies=len(dependencies),retained=retained)
