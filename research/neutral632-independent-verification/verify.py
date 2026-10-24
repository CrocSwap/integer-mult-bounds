#!/usr/bin/env python3
"""Independent neutral632 evidence companion. Chris R / Clear1nsight,
with substantial OpenAI Codex assistance; Apache-2.0. No author engine imports.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent
BASE='1ec1119972c9aefe42525172d07b332fcff81cb4'
PRIMARY='0c1fa2f47fb5ea17b93a4b67063d08e49cc38e51'
OLD='174fb211493b43a42210434083e9702b4fb7a2ce'
INTEGRITY_SHA256='c9e34564b51fe5902a6e044ca5b160567fad50be0aec74e411508f485fa844a0'
ASSUMPTIONS=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery']
DECISION='PASS_CONDITIONAL_MATHEMATICAL_SOURCE_APPLICATION_CONJUNCTION_AT_FROZEN_BYTES'

def require(ok,message):
    if not ok:raise ValueError(message)

def authenticate(data,digest):
    require(hashlib.sha256(data).hexdigest()==digest,'SHA256 authentication failed')

def load(name):return json.loads((ROOT/name).read_bytes())

def inventory():
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.rglob('*')) if p.is_file()}

def object_id(kind, data):
    return hashlib.sha1(kind.encode()+b' '+str(len(data)).encode()+b'\0'+data).hexdigest()

def origin(proof, raw, expected_commit, expected_path):
    require(proof['commit'] == expected_commit and proof['path'] == expected_path, 'origin identity changed')
    commit = base64.b64decode(proof['commit_bytes_base64'], validate=True)
    require(object_id('commit',commit)==expected_commit, 'raw commit hash failed')
    require(commit.startswith(b'tree '), 'commit tree header missing')
    child = commit.splitlines()[0][5:].decode('ascii')
    parts = expected_path.split('/')
    require(len(parts)==len(proof['trees']), 'origin tree depth mismatch')
    for part, row in zip(parts,proof['trees']):
        tree=base64.b64decode(row['bytes_base64'],validate=True)
        require(row['oid']==child==object_id('tree',tree), 'raw tree hash failed')
        require(row['component']==part, 'path component mismatch')
        entries={}; cursor=0
        while cursor<len(tree):
            space=tree.index(b' ',cursor); zero=tree.index(b'\0',space)
            name=tree[space+1:zero].decode('utf-8'); mode=tree[cursor:space]
            require(name not in entries and zero+21<=len(tree),'malformed tree')
            entries[name]=(mode,tree[zero+1:zero+21].hex());cursor=zero+21
        require(part in entries,'path component absent')
        mode,child=entries[part]
        require(mode in ((b'100644',b'100755') if part==parts[-1] else (b'40000',)), 'unexpected object mode')
    require(child==proof['blob']==object_id('blob',raw),'original Git blob failed')
    require(len(raw)==proof['bytes'],'source byte count mismatch')
    authenticate(raw,proof['sha256'])

def stable(value):return {k:v for k,v in value.items() if k!='environment'}

def authenticate_packet(folder,manifest):
    for row in load(folder+'/'+manifest)['files']:
        raw=(ROOT/folder/row['path']).read_bytes()
        require(len(raw)==row['bytes'],'frozen byte count changed')
        authenticate(raw,row['sha256'])

def verify(replay=True):
    before=inventory()
    raw=(ROOT/'INTEGRITY.json').read_bytes();authenticate(raw,INTEGRITY_SHA256)
    manifest=json.loads(raw)
    expected={r['path'] for r in manifest['files']}|{'INTEGRITY.json','verify.py'}
    require(set(before)==expected,'package file inventory differs')
    for row in manifest['files']:
        p=ROOT/row['path']
        require(p.is_file() and not p.is_symlink(),'immutable file absent or aliased')
        data=p.read_bytes();require(len(data)==row['bytes'],'input length mismatch');authenticate(data,row['sha256'])
    authorities={'canonical':BASE,'primary5413':PRIMARY,'old5398':OLD}
    for row in load('ORIGINS.json'):
        origin(row['proof'],(ROOT/row['retained']).read_bytes(),authorities[row['authority']],row['proof']['path'])
    authenticate_packet('screen','MANIFEST-v2.json')
    authenticate_packet('applicability','AUDIT-OUTPUT-MANIFEST-FINAL.json')
    primary=load('primary/SOURCE-BINDINGS.json')
    primary_rows={r['path']:r for r in primary['files']}
    claims=load('primary/CLAIMS.json');joins=load('PRIMARY-JOIN.json')
    require(joins['primary_commit']==PRIMARY and joins['canonical_base']==BASE,'primary identity mismatch')
    require(joins['joined_count']==len(joins['joined_inputs'])==20,'final20 join count mismatch')
    for row in joins['joined_inputs']:
        require(row['primary_paths'],'joined source missing from primary')
        for path in row['primary_paths']:
            entry=primary_rows[path]
            require(entry['sha256']==row['sha256'] and entry['bytes']==row['bytes'],'review/public source binding differs')
    # Authenticate the retained public source-class texts without running their code.
    for p in sorted((ROOT/'primary').rglob('*')):
        if p.is_file() and p.name!='SOURCE-BINDINGS.json':
            rel=p.relative_to(ROOT/'primary').as_posix();authenticate(p.read_bytes(),primary_rows[rel]['sha256'])
    aggregate=load('applicability/final-v5-frozen/NEUTRAL-CLOSURE-v1.json')
    raw_aggregate=(ROOT/'applicability/final-v5-frozen/NEUTRAL-CLOSURE-v1.json').read_bytes()
    authenticate(raw_aggregate,claims['conjunction_sha256'])
    authenticate(raw_aggregate,primary_rows['reports/expected/conjunction.json']['sha256'])
    audit=load('applicability/OBLIGATION-MAP-FINAL-v3.json')
    require(audit['decision']==DECISION and audit['conditional_mathematical_application'] is True,'frozen source-application decision mismatch')
    require(audit['conditional_assumptions']==ASSUMPTIONS==aggregate['assumptions'],'five assumptions changed')
    require([r['id'] for r in claims['assumptions']]==ASSUMPTIONS,'primary assumption tuple differs')
    require(aggregate['premise_count']==len(aggregate['premises'])==25,'aggregate25 premises changed')
    require(len(audit['aggregate_named_checks'])==25 and all(r['recorded_pass'] for r in audit['aggregate_named_checks']),'audited named-premise coverage changed')
    require({r['id'] for r in audit['aggregate_named_checks']}==set(aggregate['premises']),'auditor/aggregate premise IDs differ')
    require(all(aggregate['premises'].values()),'frozen aggregate premise rejected')
    require(len(audit['obligations'])==15 and len(audit['outer_guards'])==58,'obligation/outer coverage changed')
    require(aggregate['economic_profile_gain']==0 and not claims['raw_signed_profile_changed'] and not claims['raw_ceiling_changed'],'neutral scope changed')
    require(not claims['selected_record_changed'] and not aggregate['selected_record_changed'],'selection boundary changed')
    require(claims['candidate_kappa']=='.003027288235' and claims['tested_saving']=='.003027288245','source parameter mismatch')
    publication=load('publication/PUBLICATION-DELTA-v2.json')
    require(publication['publication_commit']==PRIMARY,'publication review head differs')
    require(publication['four_detailed_replays']['all_conjunction_sha256']==claims['conjunction_sha256'],'recorded primary replay conjunction differs')
    require(not publication['readonly_export']['empty_PATH_claimed'],'historical primary empty-PATH scope changed')
    reference=load('screen/receipts/screen-root-v1.json')
    require(reference['status']=='PASS_LITERAL_BINDING_AND_TWO_POINT_NECESSARY_SCREEN','wrong independent-screen status')
    guard=load('screen/receipts/ROOT-GUARD-v1.json')
    authenticate((ROOT/'screen/receipts/ROOT-stdout-v1.log').read_bytes(),guard['log_sha256'])
    require(guard['exit_code']==0 and guard['termination'] is None,'original root screen did not pass')
    # Exercise both byte and source-authority boundaries with actual mutations.
    source=(ROOT/'screen/inputs/candidate.json').read_bytes()
    try:authenticate(source+b'MUTANT',hashlib.sha256(source).hexdigest())
    except ValueError:pass
    else:raise ValueError('source-byte mutant survived')
    bad=load('ORIGINS.json')[0];bad['proof']['trees'][0]['oid']='0'*40
    try:origin(bad['proof'],(ROOT/bad['retained']).read_bytes(),BASE,bad['proof']['path'])
    except ValueError:pass
    else:raise ValueError('forged-origin mutant survived')
    if replay:
        with tempfile.TemporaryDirectory(prefix='neutral632-independent-') as folder:
            receipt=Path(folder)/'fresh.json'
            argv=[sys.executable,'-I','-B','-X','pycache_prefix='+str(Path(folder)/'cache')]+(['-O'] if sys.flags.optimize else [])+[str(ROOT/'screen/check_neutral.py'),'--receipt',str(receipt)]
            done=subprocess.run(argv,capture_output=True,text=True,timeout=30)
            # Preserve exact fresh receipt and child stdout/stderr in the guarded log, including failures.
            print('FRESH_INDEPENDENT_SCREEN_EVIDENCE '+json.dumps({'command':argv,'exit_code':done.returncode,'receipt_utf8':receipt.read_text() if receipt.exists() else None,'stdout':done.stdout,'stderr':done.stderr},sort_keys=True))
            require(done.returncode==0,'tiny independent-screen replay failed: '+done.stderr)
            require(not done.stderr,'independent screen emitted stderr')
            fresh=json.loads(receipt.read_bytes())
            require(stable(fresh)==stable(reference),'fresh independent scientific output differs')
    after=inventory()
    require(after==before,'immutable package/source bytes changed during verification')
    custody=hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest()
    return {'status':'PASS_INDEPENDENT_SCREEN_AND_RETAINED_APPLICABILITY_EVIDENCE',
            'primary_head':PRIMARY,'canonical_base':BASE,'fresh_necessary_screen':replay,
            'optimized':bool(sys.flags.optimize),'immutable_files':len(before),'pre_custody_sha256':custody,'post_custody_sha256':hashlib.sha256(json.dumps(after,sort_keys=True).encode()).hexdigest(),'inputs_unchanged':True,
            'static_source_application_review':DECISION,'named_premises':25,'structured_obligations':15,'outer_guards':58,
            'assumptions':ASSUMPTIONS,'economic_profile_gain':0,'selected_record_changed':False,
            'new_engine_scope':'literal invoice, signed neutrality, two-point necessary-price screen only',
            'retained_primary_replays':'historical authenticated evidence; not rerun by this companion'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--integrity-only',action='store_true');a=ap.parse_args()
    print(json.dumps(verify(not a.integrity_only),sort_keys=True))
