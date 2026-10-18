#!/usr/bin/env python3
"""Read-only replay, authenticating all external runtime/proof inputs first."""
import argparse
from copy import deepcopy
from hashlib import sha1, sha256
import json
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
LIVE_INPUTS=(
    'certificates/selected-result.json',
    'research/community-hyperplane599-audit/pr589/bit589/v9/hosted/GLOBAL-TEMPLATE.json.gz',
    'research/community-hyperplane599-audit/pr589/bit589/v9/nine/GEOMETRY.json',
    'research/e8-bit-p111-tuned/tune/EXPECTED.json',
    'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz',
    'research/pr589-five-helper-hosting/PROOF.md',
    'research/pr589-five-helper-hosting/verify.py',
    'research/recursive-parking-boundary/README.md',
    'research/selected-bit-local-ring-sweeps/PROOF.md',
    'research/selected-bit-recursive-closure/PROOF.md',
    'upstream/build/sections/02-streams.tex',
)
FROZEN_FILES=(
    'NOTICE.md','PROOF.md','README.md','RESULT.json','SOURCES.json','TASK.json','VERIFY.json',
    'cardinal_counts.py','catalogue.py','check_headers.py','check_layout.py','check_runtime.py',
    'check_sources.py','consumer.py','control.py','control_checks.py','driver.py','fresh_rows.py',
    'layout.py','model.py','node.py','packet_engine.py','peel.py','topology.py',
    'vendor/binding.py','vendor/bitstream.py','vendor/cardinality.py','vendor/check_support.py',
    'vendor/children.py','vendor/controller.py','vendor/counts.py','vendor/directory.py',
    'vendor/episode.py','vendor/forms.py','vendor/low_codes.py','vendor/matrices.py',
    'vendor/numeric.py','vendor/oracle.py','vendor/packet.py','vendor/plan.py','vendor/records.py',
    'vendor/residual.py','vendor/routes.py','vendor/selection.py','vendor/sources.py',
    'vendor/stream.py','vendor/stream_runner.py','vendor/trace.py','vendor/words.py','verify.py',
)
SUITES=('source','node','recursion','nested','controls')
EVIDENCE_FILES={
    'evidence/pr2731-README.md':'46c0c3554608a1096816ad668c755d3b5b7a8c0b',
    'evidence/pr2708-README.md':'2982489cc00a17bd1c7ee1e206e975eda9bcb64d',
    'evidence/pr2688-PROOF.md':'1b9e1ed8793ffdde3c4b115641f0e644a9289923',
    'evidence/pr2688-NOTICE.md':'1b9e1ed8793ffdde3c4b115641f0e644a9289923',
}


def need(condition,message):
    if not condition:raise ValueError(message)


def canonical(value):
    # Preserve JSON scalar types; 1.0 and true must not stand in for integer 1.
    return json.dumps(json.loads(json.dumps(value)),sort_keys=True,separators=(',',':'),allow_nan=False)


def payload(path):
    need(path.is_file() and not path.is_symlink(),'regular pinned file: '+str(path))
    return path.read_bytes()


def authenticate(sources=None,predecessor=None,manifest=None,here=HERE,root=ROOT,evidence=None):
    sources=json.loads((here/'SOURCES.json').read_text()) if sources is None else sources
    predecessor=json.loads((here/'PREDECESSOR.json').read_text()) if predecessor is None else predecessor
    manifest=json.loads((here/'VERIFY.json').read_text()) if manifest is None else manifest
    evidence=json.loads((here/'EVIDENCE.json').read_text()) if evidence is None else evidence
    live=[item for item in sources['files'] if item['usage']=='input']
    need(sorted(item['path'] for item in live)==list(LIVE_INPUTS),'exact live source inventory')
    need(sorted(manifest['inputs'])==list(LIVE_INPUTS),'exact replay invalidation inventory')
    need(predecessor['head']=='a53fdf4bcbe33c6732f0bec1badc8c023380f9d1','exact executable predecessor')
    need(sorted(predecessor['files'])==sorted(FROZEN_FILES),'exact predecessor source inventory')
    physical=sorted(str(path.relative_to(here/'predecessor'))
                    for path in (here/'predecessor').rglob('*') if path.is_file()
                    and '__pycache__' not in path.parts)
    need(physical==sorted(FROZEN_FILES),'no omitted or extra predecessor files')
    need(sorted(row['path'] for row in evidence['files'])==sorted(EVIDENCE_FILES),
         'exact predecessor proof inventory')
    for row in evidence['files']:
        need(row['commit']==EVIDENCE_FILES[row['path']],'exact predecessor proof commit')
    for name,item,path in [(item['path'],item,root/item['path']) for item in live]+[
            (name,item,here/'predecessor'/name) for name,item in predecessor['files'].items()]+[
            (item['path'],item,here/item['path']) for item in evidence['files']]:
        data=payload(path)
        need(sha256(data).hexdigest()==item['sha256'],'pinned bytes changed: '+name)
        blob=sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        need(blob==item['git_blob'],'pinned Git blob changed: '+name)
    return {'live_inputs':len(live),'frozen_files':len(FROZEN_FILES),
            'frozen_proofs':len(EVIDENCE_FILES),'predecessor_head':predecessor['head']}


def receipt(result):
    return {'full_result_sha256':sha256(canonical(result).encode()).hexdigest(),'result':result}


def compare(observed,expected):
    need(canonical(observed)==canonical(expected),'retained exact receipt differs')


def verifier_controls():
    sources=json.loads((HERE/'SOURCES.json').read_text())
    frozen=json.loads((HERE/'PREDECESSOR.json').read_text())
    manifest=json.loads((HERE/'VERIFY.json').read_text())
    rejected=[]
    def reject(label,action):
        try:action()
        except ValueError:rejected.append(label)
        else:raise ValueError('negative control accepted: '+label)
    for name in LIVE_INPUTS:
        changed=deepcopy(sources)
        changed['files']=[row for row in changed['files'] if row['path']!=name]
        reject('omitted_source:'+name,lambda:authenticate(sources=changed))
    changed=deepcopy(manifest);changed['inputs'].pop()
    reject('omitted_CI_input',lambda:authenticate(manifest=changed))
    changed=deepcopy(frozen);del changed['files']['vendor/controller.py']
    reject('omitted_executable_predecessor',lambda:authenticate(predecessor=changed))
    changed=json.loads((HERE/'EVIDENCE.json').read_text());changed['files'].pop()
    reject('omitted_proof_predecessor',lambda:authenticate(evidence=changed))
    changed=deepcopy(sources)
    next(row for row in changed['files'] if row['usage']=='input')['sha256']='0'*64
    reject('wrong_live_hash',lambda:authenticate(sources=changed))
    with TemporaryDirectory(prefix='recursive-caller-source-control-') as temporary:
        location=Path(temporary)
        shutil.copytree(HERE/'predecessor',location/'predecessor',ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(HERE/'evidence',location/'evidence')
        shutil.copyfile(HERE/'EVIDENCE.json',location/'EVIDENCE.json')
        path=location/'predecessor'/'vendor'/'controller.py'
        path.write_bytes(path.read_bytes()+b'\n# deliberate changed executable source\n')
        reject('changed_executable_bytes',lambda:authenticate(sources,frozen,manifest,location))
    base=receipt({'integer':1,'flag':True})
    for label,value in [('receipt_wrong_type',{'integer':1.0,'flag':True}),
                        ('receipt_wrong_value',{'integer':2,'flag':True}),
                        ('receipt_extra_field',{'integer':1,'flag':True,'extra':0})]:
        reject(label,lambda:compare(receipt(value),base))
    changed=deepcopy(base);changed['full_result_sha256']='0'*64
    reject('receipt_wrong_digest',lambda:compare(changed,base))
    return {'rejected':rejected,'before_executable_imports':True,'verification_writes_receipts':False}


def evaluate(suite):
    import bootstrap
    if suite=='source':
        from catalogue import Catalogue
        from check_sources import catalogue_checks,consumer_probes,global_scalar
        from check_layout import extents,selected_peel,complete_gapped
        from check_headers import sampled_packet
        catalogue=Catalogue(3)
        return {'selected_sources':catalogue_checks(catalogue),
                'selected_consumers':consumer_probes(catalogue),
                'global_scalar':global_scalar(catalogue),'gapped_extents':extents(),
                'generated_peel':selected_peel(catalogue),'gapped_endpoint':complete_gapped(),
                'sampled_high_packet':sampled_packet()}
    if suite=='node':
        from check_runtime import complete_node
        return complete_node(gap_size=1)
    if suite=='recursion':
        from check_recursion import run
        return run()
    if suite=='nested':
        from check_nested_model import run
        return run()
    from check_sign import run
    from control_checks import stale_controls,bridge_and_exchange,rejections_and_counts
    return {'linear_sign':run(),'stale_state':stale_controls(),
            'bridge_exchange':bridge_and_exchange(),'rejections_counts':rejections_and_counts(),
            'verifier_mutations':verifier_controls()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite',required=True,choices=SUITES)
    parser.add_argument('--emit-to',type=Path,help='Explicit generation to a NEW file; never overwrite a retained receipt')
    args=parser.parse_args()
    need(not sys.flags.optimize,'assertion-based independent checkers require optimization disabled')
    if args.emit_to is not None:need(not args.emit_to.exists(),'refuse to overwrite an existing receipt')
    authentication=authenticate()
    observed=receipt(evaluate(args.suite))
    if args.emit_to is not None:
        with args.emit_to.open('x') as handle:json.dump(observed,handle,indent=2,sort_keys=True);handle.write('\n')
        print('GENERATED_RECURSIVE_CALLER '+args.suite+' '+str(args.emit_to))
    else:
        retained=json.loads((HERE/'RESULT.json').read_text())
        need(sorted(retained)==sorted(SUITES),'exact retained suite inventory')
        compare(observed,retained[args.suite])
        print('PASS_SELECTED_BIT_RECURSIVE_CALLER '+args.suite+' '+observed['full_result_sha256'])
    return authentication


if __name__=='__main__':main()
