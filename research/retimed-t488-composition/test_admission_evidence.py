#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Receipt-link mutation tests, not a scientific verification or admission.

Requires --package, --run, --source, and fresh --work outside the publication.
Builds a clearly synthetic terminal fixture from recorded finite data, whether or
not the real full run has completed. Nothing is copied into the publication.
"""
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
import argparse, gzip, json, shutil
import admission_evidence as ae


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for flag in ('package','run','source','work'): ap.add_argument('--'+flag, required=True, type=Path)
    args=ap.parse_args()
    work=args.work.resolve();package=args.package.resolve()
    ae.need(not work.exists() and package not in work.parents, 'fresh external test work directory')
    work.mkdir(parents=True)
    # Snapshot only the small, pinned inputs used by the link checker.
    fake=work/'synthetic-package'
    paths=['full-replay/DEPENDENCIES.json','full-replay/SPEC.json',
           'full-replay/comparator/PR3642-CLAIM.json','owners/upstream/EXPECTED.json','owners/NATIVE-BINDING.json']
    for tag in ('base','extra'):
        paths += ['owners/native/checked-'+tag+'/CANONICAL-WORD.json.gz',
                  'local-audit/words/RETIMED644-660-'+tag+'.json.gz']
    for rel in paths:
        dest=fake/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(package/rel,dest)
    blobs={k:(args.run/rel).read_bytes() for k,rel in ae.FILES.items() if k!='release'}
    blobs['source_manifest']=(args.source/'MANIFEST.json').read_bytes()
    data={k:json.loads(v) for k,v in blobs.items() if k!='fill'}
    spec=ae.read(fake/'full-replay/SPEC.json');C=Q(spec['expected_complex_lower'])
    K=C-Q(spec['outer_margin'])-Q(spec['grid_margin'])
    # Synthetic completion exists ONLY inside the external test fixture.
    stages=data['stages'][:6]
    stages.append(dict(name='release',exit_code=0,script_sha256=data['manifest']['verify_release.py'],
                       command=['SYNTHETIC_TEST_ONLY'],seconds=0,log_sha256='0'*64))
    data['stages']=stages
    data['release']=dict(status='PASS_RELEASE',kappa_decimal=str(K),manifest_sha256=ae.digest(blobs['manifest']),
                         proof='SYNTHETIC RECEIPT-LINK TEST FIXTURE: NOT A SCIENTIFIC RESULT')
    data['admission'].update(status='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE',
        kappa=str(K),kappa_decimal=str(K),complex_lower=str(C),stages=stages,
        package_manifest_sha256=ae.digest(blobs['manifest']))
    def encode(x):return (json.dumps(x,indent=2)+'\n').encode()
    blobs['release']=encode(data['release']);data['admission']['release_receipt_sha256']=ae.digest(blobs['release'])
    blobs['admission']=encode(data['admission']);blobs['stages']=encode(data['stages'])
    prior=Q(ae.read(fake/'full-replay/comparator/PR3642-CLAIM.json')['kappa'])
    summary=dict(schema='retimed-t488-recorded-admission/v1',status='PASS_T488_RETIMER_COMPLETE_CONDITIONAL_RELEASE',
        profile=data['admission']['profile'],kappa=str(K),prior_PR3642=str(prior),absolute_gain=str(K-prior),
        comparison_claim_sha256=ae.digest((fake/'full-replay/comparator/PR3642-CLAIM.json').read_bytes()),
        admission_stages=stages,files={},scope='SYNTHETIC TEST ONLY; NOT SCIENTIFIC ADMISSION')
    bundle=work/'synthetic-recorded';bundle.mkdir()
    baseline=deepcopy(blobs);base_summary=deepcopy(summary)
    def write_case(b,s):
        for key,raw in b.items():
            name=key+('.json.gz' if key=='fill' else '.json');(bundle/name).write_bytes(raw)
            s['files'][key]=dict(path=name,sha256=ae.digest(raw))
        (bundle/'COMPLETE-ADMISSION.json').write_bytes(encode(s))
    def checked():return ae.check(fake,bundle/'COMPLETE-ADMISSION.json',spec['expected_complete_profile'],str(K),args.run/'allocation')
    write_case(deepcopy(baseline),deepcopy(base_summary));checked()
    results=[]
    def mutate(name,fn):
        b,s=deepcopy(baseline),deepcopy(base_summary)
        fn(b,s);write_case(b,s)
        try:checked()
        except (ValueError,KeyError) as exc:results.append(dict(name=name,rejected=True,reason=str(exc)))
        else:raise RuntimeError('Accepted mutation: '+name)
    def change(b,key,fn):
        x=json.loads(b[key]);fn(x);b[key]=encode(x)
    def relink(b):
        change(b,'release',lambda x:x.update(manifest_sha256=ae.digest(b['manifest'])))
        change(b,'admission',lambda x:x.update(release_receipt_sha256=ae.digest(b['release']),
            package_manifest_sha256=ae.digest(b['manifest']),native_receipt_sha256=ae.digest(b['native'])))
    mutate('pending raw admission',lambda b,s:change(b,'admission',lambda x:x.update(status='PREPARED_REPLICA_SAME_WORD_DERIVATIVE_NOT_ADMITTED')))
    mutate('wrong comparator with unchanged kappa',lambda b,s:s.update(comparison_claim_sha256='0'*64))
    mutate('wrong full modern endpoint',lambda b,s:s.update(kappa=str(K+Q(1,10**80))))
    def source(b,s):
        change(b,'source_manifest',lambda x:x.update({next(iter(x)):'0'*64}))
        change(b,'admission',lambda x:x.update(source_manifest_sha256=ae.digest(b['source_manifest'])))
        change(b,'native',lambda x:x.update(manifest_sha256=ae.digest(b['source_manifest'])))
        relink(b)
    mutate('different source with repaired internal hashes',source)
    def native(b,s):
        change(b,'native',lambda x:x['providers']['base'].update(word_sha256='0'*64));relink(b)
    mutate('different supplier word with repaired receipt hash',native)
    def canon(b,s):
        change(b,'native',lambda x:x['providers']['extra']['complete_native_files'].update({'local/CANONICAL-WORD.json.gz':'0'*64}));relink(b)
    mutate('different canonical native word',canon)
    def dupstage(b,s):
        t=json.loads(b['stages']);t[3]=deepcopy(t[0]);b['stages']=encode(t)
        change(b,'admission',lambda x:x.update(stages=t));s['admission_stages']=t
    mutate('seven zero exits but repeated scientific stage',dupstage)
    def script(b,s):
        t=json.loads(b['stages']);t[2]['script_sha256']='0'*64;b['stages']=encode(t)
        change(b,'admission',lambda x:x.update(stages=t));s['admission_stages']=t
    mutate('stage ran different script',script)
    def failedrelease(b,s):
        change(b,'release',lambda x:x.update(status='FAIL_RELEASE'));relink(b)
    mutate('failed raw release with repaired hash',failedrelease)
    def geometry(b,s):
        change(b,'spec',lambda x:x['expected'].update(physical=x['expected']['physical']-91))
        change(b,'manifest',lambda x:x.update({'new/SPEC.json':ae.digest(b['spec'])}));relink(b)
    mutate('private buffer cost omitted with repaired package hash',geometry)
    def fill(b,s):
        x=json.loads(gzip.decompress(b['fill']));x['rows'][0][2]=(x['rows'][0][2]+1)%spec['replicas']
        b['fill']=gzip.compress(json.dumps(x,separators=(',',':')).encode(),mtime=0)
        change(b,'manifest',lambda x:x.update({'new/borrow-fill/FILL.json.gz':ae.digest(b['fill'])}))
        change(b,'admission',lambda x:x.update(fill_sha256=ae.digest(b['fill'])));relink(b)
    mutate('different owner row with unchanged profile and repaired hashes',fill)
    # Descriptor corruption must also be caught before interpreting receipts.
    write_case(deepcopy(baseline),deepcopy(base_summary))
    p=bundle/'release.json';p.write_bytes(p.read_bytes()+b' ')
    try:checked()
    except ValueError as exc:results.append(dict(name='raw receipt bytes changed',rejected=True,reason=str(exc)))
    else:raise RuntimeError('Accepted changed bytes')
    write_case(deepcopy(baseline),deepcopy(base_summary));checked()
    # Exercise the actual export path on synthetic receipts, including refusal
    # to expose a COMPLETE file for nonterminal raw admission.
    synthetic_run=work/'synthetic-run'
    for key,rel in ae.FILES.items():
        target=synthetic_run/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(baseline[key])
    shutil.copyfile(args.run/'allocation/FILL.json.gz',synthetic_run/'allocation/FILL.json.gz')
    exported=ae.export(fake,synthetic_run,args.source,work/'synthetic-export')
    ae.need(exported.is_file() and not (exported.parent/'CANDIDATE-ADMISSION.json').exists(),'validated export promotion')
    pending=synthetic_run/'admission/RESULT.json';pending_data=ae.read(pending)
    pending_data['status']='PREPARED_REPLICA_SAME_WORD_DERIVATIVE_NOT_ADMITTED';pending.write_bytes(encode(pending_data))
    try:ae.export(fake,synthetic_run,args.source,work/'pending-export')
    except ValueError:ae.need(not (work/'pending-export').exists(),'pending export wrote evidence')
    else:raise RuntimeError('exported pending scientific run')
    result=dict(status='PASS_RECORDED_ADMISSION_LINK_MUTATION_TESTS',synthetic_fixture_only=True,
                positive_fixture_passed=True,export_roundtrip_passed=True,pending_export_rejected=True,rejected_controls=results,
                scope='Only receipt consistency was tested. Synthetic terminal fixture is not evidence of scientific admission.')
    (work/'RESULT.json').write_bytes(encode(result));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
