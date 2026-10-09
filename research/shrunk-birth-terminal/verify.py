#!/usr/bin/env python3
"""Reconstruct the selected physical word and its exact portable certificate.

This executes only the selected new composition. Archived external submissions
are immutable reference material, not admission gates. Prepared by Chafik
Boukhalfa with OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
import argparse, gzip, json, os, pickle, subprocess, sys, tempfile, time, resource

if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):
    raise RuntimeError('Assertions must remain enabled')
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
read=lambda p:json.loads(p.read_text())
sha=lambda p:sha256(p.read_bytes()).hexdigest()
def require(ok,reason):
    if not ok:raise ValueError(reason)
def verify_sources():
    manifest=read(HERE/'SOURCE.json')
    for name,digest in manifest['package_files'].items():
        require(sha(HERE/name)==digest,'Package source mismatch: '+name)
    for name,digest in manifest['repository_files'].items():
        require(sha(ROOT/name)==digest,'Repository source mismatch: '+name)
    return sha(HERE/'SOURCE.json')
def unpack_inputs(destination):
    destination.mkdir(parents=True,exist_ok=False)
    pins=read(HERE/'selected/INPUTS.json')
    for name,entry in pins.items():
        stored=(HERE/'selected/inputs'/entry['stored_name']).read_bytes()
        require(sha256(stored).hexdigest()==entry['stored_sha256'],'Stored input hash: '+name)
        data=gzip.decompress(stored) if entry['encoding']=='gzip' else stored
        require(len(data)==entry['bytes'] and sha256(data).hexdigest()==entry['sha256'],'Decoded input hash: '+name)
        (destination/name).write_bytes(data)
    return pins

def canonical_geometry_bytes(graph):
    def normalize(value):
        if isinstance(value,dict):return {str(k):normalize(v) for k,v in value.items()}
        if isinstance(value,(set,frozenset)):return [normalize(v) for v in sorted(value)]
        if isinstance(value,(list,tuple)):return [normalize(v) for v in value]
        return value
    geometry={k:v for k,v in graph.items() if k!='base_profile'}
    geometry['bytarget']={k:sorted(v) for k,v in geometry['bytarget'].items() if v}
    return json.dumps(normalize(geometry),sort_keys=True,separators=(',',':')).encode()
def bind_geometry(fixture,regenerated,receipt,expected_fixture_sha):
    require(sha(fixture)==expected_fixture_sha==receipt['selected_fixture_sha256'],'Geometry replay selected-fixture hash mismatch')
    original=canonical_geometry_bytes(pickle.loads(fixture.read_bytes()))
    fresh=canonical_geometry_bytes(pickle.loads(regenerated.read_bytes()))
    require(original==fresh,'Regenerated geometry differs from actual selected fixture')
    digest=sha256(original).hexdigest()
    require(digest==receipt['canonical_geometry_sha256'],'Selected canonical geometry digest mismatch')
    return digest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,help='Optional fresh-run receipt outside the frozen source closure')
    args=p.parse_args();start=time.monotonic();source=verify_sources()
    with tempfile.TemporaryDirectory(prefix='shrunk-birth-terminal-') as folder:
        work=Path(folder);inputs=work/'inputs';pins=unpack_inputs(inputs);out=work/'physical'
        subprocess.run([sys.executable,str(HERE/'search/reproduce_geometry.py'),'--out',str(work/'geometry')],check=True)
        geometry_digest=bind_geometry(inputs/'FRAMES.pkl',work/'geometry/FRAMES.pkl',read(work/'geometry/REPRODUCTION.json'),pins['FRAMES.pkl']['sha256'])
        command=[sys.executable,str(HERE/'construction/compose_terminal.py'),'--frames',str(inputs/'FRAMES.pkl'),'--matches',str(inputs/'BIRTH_MATCHES.json.gz'),'--readouts',str(inputs/'READOUTS.pkl'),'--scalar-bill',str(inputs/'READOUT_COST.json'),'--terminal-roles',str(inputs/'TERMINAL_ROLES.json'),'--out',str(out)]
        subprocess.run(command,check=True)
        actual=gzip.decompress((out/'word.json.gz').read_bytes());expected=gzip.decompress((HERE/'selected/word.json.gz').read_bytes())
        require(actual==expected,'Complete regenerated physical word differs')
        require(read(out/'complex-profile.json')==read(HERE/'selected/complex-profile.json'),'Complete regenerated profile differs')
        require(read(out/'READOUT_COST.json')==read(HERE/'selected/READOUT_COST.json'),'Exact scalar bill differs')
        require(read(out/'majorization.json')==read(HERE/'selected/majorization.json'),'Complete majorization proof differs')
        audit=read(out/'physical-audit.json');saved=read(HERE/'selected/physical-audit.json')
        volatile={'seconds','rss_bytes','input_pins','word_file_sha256'}
        require({k:v for k,v in audit.items() if k not in volatile}=={k:v for k,v in saved.items() if k not in volatile},'Physical audit mathematical fields differ')
        inventory=read(out/'inventory.json');oldinventory=read(HERE/'selected/inventory.json')
        require({k:v for k,v in inventory.items() if k!='input_sha256'}=={k:v for k,v in oldinventory.items() if k!='input_sha256'},'Exact terminal selection differs')
        for key,entry in pins.items():require(audit['input_pins'][key]['sha256']==entry['sha256'],'Reconstruction input binding: '+key)
        # The arithmetic entrypoint reconstructs exact moments and every transfer
        # parameter using two independent enclosure implementations.
        subprocess.run([sys.executable,str(HERE/'arithmetic/certificate.py'),'--profile',str(out/'complex-profile.json'),'--scalar-bill',str(out/'READOUT_COST.json'),'--certificate',str(HERE/'certificate.json')],check=True)
        subprocess.run([sys.executable,str(HERE/'arithmetic/validate.py'),'--certificate',str(HERE/'certificate.json'),'--reference-certificate',str(HERE/'audit/independent-prepackage-certificate.json'),'--receipt',str(work/'arithmetic-validation.json')],check=True)
        subprocess.run([sys.executable,str(HERE/'search/audit_selected_semantics.py'),'--selected',str(out),'--certificate',str(HERE/'certificate.json'),'--out',str(work/'selected-semantics.json')],check=True)
        subprocess.run([sys.executable,str(HERE/'audit_lean.py')],check=True)
        require(source==verify_sources(),'Source manifest changed during verification')
        record={'status':'PASS selected full physical word, both orientations, all source/dirty columns, frames, complete profile, scalar charge, two exact arithmetic enclosures and Lean input linkage','source_sha256':source,'canonical_geometry_sha256':geometry_digest,'geometry_matches_actual_selected_fixture':True,'certificate_sha256':sha(HERE/'certificate.json'),'word_sha256':sha256(actual).hexdigest(),'source_columns':audit['source_columns'],'dirty_columns':audit['dirty_columns'],'terminal_eliminations':audit['terminal_roles_eliminated'],'birth_reuses':audit['birth_reuses_preserved'],'mutations':audit['mutations'],'seconds':time.monotonic()-start,'rss_bytes':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*(1024 if sys.platform=='linux' else 1),'scope':'Finite exact construction and rational arithmetic; retained all-size analytic, routing, fixed-tape and stopped-product contracts remain assumptions. Fresh Lean compilation is a separate formal CI gate.'}
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
        print(json.dumps(record,indent=2,sort_keys=True))
if __name__=='__main__':main()
