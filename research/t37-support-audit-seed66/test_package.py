"""Obligation-specific package and independent arithmetic controls (Apache-2.0)."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run(package, expected):
    process = subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py')],
                             cwd=package.parent, capture_output=True, text=True)
    need((process.returncode == 0) == expected, 'unexpected acceptance: '+process.stdout+process.stderr)
    if expected:
        need('PASS_T37_UNIFORM_SUPPORT_AUDIT' in process.stdout, 'missing success marker')
    return process.stdout


def main():
    spec = importlib.util.spec_from_file_location('independent_controls', HERE/'independent.py')
    independent = importlib.util.module_from_spec(spec); spec.loader.exec_module(independent)
    for name, value in [('PRICES', (-1,-20,-8,-2,5)), ('LOG_TERMS', 0)]:
        old = getattr(independent, name)
        try:
            setattr(independent, name, value)
            try:
                independent.audit()
            except ValueError:
                pass
            else:
                raise ValueError('independent mutation accepted: '+name)
        finally:
            setattr(independent, name, old)
    with tempfile.TemporaryDirectory(prefix='T37 audit relocation ') as tmp:
        package = Path(tmp)/'standalone proof with spaces'
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        run(package, True)
        certificate_path = package/'CERTIFICATE.json'
        original = certificate_path.read_bytes()
        certificate = json.loads(original)
        mutations = []
        for label, edit in [
            ('margin', lambda x: x['support'][0].update(normalized_margin_lower='0')),
            ('missing rank', lambda x: x['support'].pop()),
            ('bin witness', lambda x: x['maximizing_bin_witnesses']['2'][1].__setitem__(0, 999)),
            ('equality profile', lambda x: x['inventory']['normalized_idle'].update({'1':'1/37'})),
            ('bool instead of zero', lambda x: x['u'].update({'0':False})),
            ('float instead of integer', lambda x: x.update(bin_vectors=1163.0)),
        ]:
            changed = json.loads(original); edit(changed)
            mutations.append((label, json.dumps(changed).encode()))
        mutations.append(('duplicate field', original.replace(b'"assignment_seed": 66,', b'"assignment_seed": 66, "assignment_seed": 66,')))
        for label, raw in mutations:
            certificate_path.write_bytes(raw); run(package, False)
        certificate_path.write_bytes(original)
        sources_path = package/'SOURCES.json'; original_sources = sources_path.read_bytes()
        sources = json.loads(original_sources)
        # Each consumed source is genuinely changed on disk and must fail.
        for entry in sources['files']:
            path = package/entry['retained_path']; raw = path.read_bytes()
            path.write_bytes(raw+b'\ncorrupted source\n'); run(package, False); path.write_bytes(raw)
        # Even after recomputing both retained-content digests, changed literal
        # accounting constants must fail the independent source-data contract.
        entry = sources['files'][1]; path = package/entry['retained_path']; raw = path.read_bytes()
        changed = raw.replace(b'PRICES = (-1, -20, -8, -2, 4)', b'PRICES = (-1, -20, -8, -2, 5)')
        need(changed != raw, 'constant mutation located')
        path.write_bytes(changed)
        entry['sha256'] = hashlib.sha256(changed).hexdigest()
        entry['git_blob'] = hashlib.sha1(b'blob '+str(len(changed)).encode()+b'\0'+changed).hexdigest()
        sources_path.write_text(json.dumps(sources)); run(package, False)
        path.write_bytes(raw); sources_path.write_bytes(original_sources)
        run(package, True)
        # Fresh output regeneration agrees on every typed proof-relevant field.
        fresh = package/'fresh certificate.json'
        process = subprocess.run([sys.executable,'-I','-O','-B',str(package/'verify.py'),'--write',str(fresh)],
                                 capture_output=True,text=True)
        need(process.returncode == 0 and fresh.read_bytes() == original, 'exact certificate regeneration')
        second = subprocess.run([sys.executable,'-I','-O','-B',str(package/'verify.py'),'--write',str(fresh)],
                                capture_output=True,text=True)
        need(second.returncode != 0 and fresh.read_bytes() == original, 'existing output preserved')
    print('PASS_T37_SUPPORT_PACKAGE relocation=1 certificate_regeneration=1 on_disk_corruptions=12 independent_mutations=2')


if __name__ == '__main__':
    main()
