#!/usr/bin/env python3
"""Prepare a flat, accepted-source copy plan; never copies or builds an archive.

Final generation requires the integration owner's frozen accepted manifest.
The copy plan retains source locations for the packager; the public map contains
only flat src paths, scientific pins and checking requirements.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import offline_check as check


def prepare(root, baseline_map, accepted_manifest, scientific_inputs=None):
    base = json.loads(baseline_map.read_text())
    caps = {m['module']:m.get('timeout_seconds',60) for m in base['modules']}
    accepted = json.loads(accepted_manifest.read_text())
    if isinstance(accepted,dict): accepted=accepted['modules']
    check.need(isinstance(accepted,list) and accepted,'Empty accepted manifest')
    modules, copies = [], []
    for item in accepted:
        check.need(item.get('status','PASS')=='PASS','Nonaccepted module in manifest')
        name=item['module'];check.need(bool(check.NAME.fullmatch(name)),'Bad module name')
        source=check.relative_file(root,item['source']);raw=source.read_bytes()
        check.need(check.digest(raw)==item['source_sha256'],f'Changed accepted module:{name}')
        imports,prints=check.source_commands(raw.decode())
        check.need(len(prints)==item['declarations'],f'Audit-count mismatch:{name}')
        modules.append(dict(module=name,source=item['source'],source_sha256=item['source_sha256'],
                            declarations=item['declarations'],imports=imports,expected_axiom_commands=prints,
                            timeout_seconds=caps.get(name,60)))
        copies.append(dict(source=item['source'],destination='src/'+name.replace('.','/')+'.lean',
                           sha256=item['source_sha256'],kind='accepted Lean source'))
    names={m['module']for m in modules}
    external=sorted({n for m in modules for n in m['imports'] if n not in names})
    inputs=scientific_inputs or []
    original=dict(target_commit=base['target_commit'],accepted_module_count=len(modules),
                  accepted_declarations=sum(m['declarations']for m in modules),modules=modules,
                  external_imports=external,scientific_inputs=[dict(path=i['source'],sha256=i['sha256'])for i in inputs])
    # Reuse the driver's own hash/name/dependency validation before relocation.
    with tempfile.TemporaryDirectory(prefix='lean-map-check-') as tmp:
        path=Path(tmp)/'map.json';path.write_text(json.dumps(original))
        _,_,_,order,_=check.load_plan(path,root)
    relocated=[]
    for m in modules:
        relocated.append(dict(m,source='src/'+m['module'].replace('.','/')+'.lean'))
    for item in inputs:
        check.need(not Path(item['destination']).is_absolute() and '..'not in Path(item['destination']).parts,
                   'Unsafe scientific-input destination')
        copies.append(dict(item,kind='pinned scientific input'))
    destinations=[x['destination']for x in copies]
    check.need(len(destinations)==len(set(destinations)),'Colliding curated destination')
    public=dict(target_commit=base['target_commit'],accepted_module_count=len(relocated),
                accepted_declarations=sum(m['declarations']for m in relocated),modules=relocated,
                ordered_modules=order,external_imports=external,
                scientific_inputs=[dict(path=i['destination'],sha256=i['sha256'])for i in inputs],
                scope='Exact accepted finite Lean sources and pinned scientific inputs. No all-size theorem implied.',
                compiler=dict(version='4.21.0',commit='6741444a63ee'),
                axiom_policy=sorted(check.ALLOWED_AXIOMS),
                resource_policy='One Lean job,64MiB stack,4GiB address space; original per-module60/120/300second caps.')
    return public,dict(status='COPY_PLAN_ONLY',archive_built=False,source_root=str(root.resolve()),
                       accepted_manifest_sha256=check.file_hash(accepted_manifest),copies=copies)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--verification-root',type=Path,required=True)
    p.add_argument('--baseline-map',type=Path,required=True)
    p.add_argument('--accepted-manifest',type=Path,required=True)
    p.add_argument('--scientific-inputs',type=Path,help='List of source,destination,sha256 scientific files')
    p.add_argument('--public-map',type=Path,required=True)
    p.add_argument('--copy-plan',type=Path,required=True)
    a=p.parse_args()
    inputs=json.loads(a.scientific_inputs.read_text())if a.scientific_inputs else []
    public,plan=prepare(a.verification_root,a.baseline_map,a.accepted_manifest,inputs)
    check.atomic_json(a.public_map,public);check.atomic_json(a.copy_plan,plan)
    print(json.dumps(dict(accepted_modules=public['accepted_module_count'],
                          accepted_declarations=public['accepted_declarations'],
                          scientific_inputs=len(inputs),archive_built=False),indent=2))


if __name__=='__main__':main()
