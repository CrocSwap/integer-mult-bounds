"""Actual bytes, source origin and scoped claims; no scientific evaluator imports."""
import gzip,hashlib,json
from pathlib import Path,PurePosixPath
MAIN='1ec1119972c9aefe42525172d07b332fcff81cb4'
HEAD='3348fccea855082786d5f0fc5558b73d4974e745'
CLIFFORD='848cdce9003262c4b6e02ec4558f302e4fae56ad'
CLAIMS_EXPECTED={'admitted_kappa': None, 'canonical_main': '1ec1119972c9aefe42525172d07b332fcff81cb4', 'clifford': {'finite_oracle': 'bounded implementation evidence only', 'full_provider_replay': False, 'fusion_census_replayed': False, 'head': '848cdce9003262c4b6e02ec4558f302e4fae56ad', 'positive_compact_equality_independent_certificate': False, 'pr': 5376, 'written_all_n_criterion': 'sound under fixed-coefficient exact dyadic-Clifford hypotheses'}, 'closure_budget': {'actual_extra_autonomous_H8_admitted': 0, 'closure_constructed': False, 'hypothetical_unearned_extra_H8': 144, 'paid_144_H8_cancels_hypothetical_credit': True, 'providers': 18, 'status': 'conditional necessary comparison only', 'unpriced_terms': ['closure paid calls', 'lost targets', 'changed main/idle profile', 'physical ordinary work', 'full caller precision and compiler/outer funding']}, 'completed_caller': False, 'new_unconditional_or_formal_kernel_theorem': False, 'provider': {'admission': 'independent partial coupled component', 'arbitrary_owned_inputs': 9, 'autonomous_credit_from_coupled_helpers': 0, 'autonomous_helpers': 400, 'coupled_helpers': 8, 'head': '3348fccea855082786d5f0fc5558b73d4974e745', 'original_inputs': 632, 'owned_outputs_zero': 9, 'paid': {'1': 2193, '2': 412, '3': 510, '4': 127, '5': 40}, 'phase_bindings': 1240, 'pr': 5402}, 'review_status': 'READY_FOR_COLD_REPLAY', 'schema_version': 1, 'selected_record_changed': False, 'local_envelope': {'head': '3348fccea855082786d5f0fc5558b73d4974e745', 'max_field_l2_exponent': 18996, 'joint_field_l2_exponent': 19012, 'copy_count': 16, 'scope': 'one-provider abstract scalar/unitary transcript; arbitrary contiguous intervals and suffixes; local residuals measured in the same stated field norm', 'full_caller_precision_admitted': False}}
def require(ok,message):
    if not ok:raise ValueError(message)

def regular(root,relative):
    parts=PurePosixPath(relative).parts
    require(parts and not relative.startswith('/') and all(p not in ('','.','..') for p in parts) and str(PurePosixPath(relative))==relative,'Noncanonical input path: '+relative)
    here=root
    for part in parts:
        here=here/part
        require(not here.is_symlink(),'Symlink input component: '+str(here))
    require(here.is_file(),'Missing regular input: '+relative)
    require(here.stat().st_nlink==1,'Hardlinked input alias: '+relative)
    return here

def oid(kind,raw):
    return hashlib.sha1(kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def tree_entries(raw):
    entries={};i=0
    while i<len(raw):
        split=raw.index(b' ',i);zero=raw.index(b'\0',split)
        require(zero+21<=len(raw),'Truncated Git tree')
        name=raw[split+1:zero].decode('utf8')
        require(name and '/' not in name and name not in ('.','..') and name not in entries,'Invalid Git tree name')
        entries[name]=(raw[i:split].decode(),raw[zero+1:zero+21].hex());i=zero+21
    require(i==len(raw),'Truncated Git tree')
    return entries


def custody(root,number):
    base='custody/'+number+'/'
    report=json.loads(regular(root,base+'SOURCE-CUSTODY.json').read_bytes())
    require(report['head']=={'5402':HEAD,'5376':CLIFFORD}[number],'Wrong source head')
    def obj(identity,kind):
        row=report['raw_git_origin_objects'][identity]
        raw=regular(root,base+row['path']).read_bytes()
        require(row['kind']==kind and len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'] and oid(kind,raw)==identity,'Raw source Git identity')
        return raw
    for identity,row in report['raw_git_origin_objects'].items():obj(identity,row['kind'])
    def origin(binding,raw):
        commit=obj(binding['commit'],'commit')
        first=commit.split(b'\n',1)[0].split()
        require(len(first)==2 and first[0]==b'tree','Missing commit root')
        current=first[1].decode();parts=PurePosixPath(binding['path']).parts
        require(str(PurePosixPath(binding['path']))==binding['path'] and all(x not in ('.','..') for x in parts),'Noncanonical source origin')
        require(len(parts)==len(binding['tree_objects']),'Wrong origin depth')
        for part,treepath in zip(parts,binding['tree_objects']):
            require(report['raw_git_origin_objects'][current]['path']==treepath,'Wrong origin tree path')
            entries=tree_entries(obj(current,'tree'));require(part in entries,'Missing Git tree member');mode,current=entries[part]
        require(mode in ('100644','100755') and mode==binding['git_mode'] and current==binding['git_blob']==oid('blob',raw),'Source Git blob binding')
    driver=json.loads(regular(root,base+'REGISTERED-DRIVER-BINDING.json').read_bytes())
    require(driver['head']==report['head'] and driver['path']=='scripts/research_package.py','Wrong registered driver identity')
    def driver_object(identity,kind):
        row=driver['raw_origin_objects'][identity]
        raw=regular(root,base+'registered-driver/'+identity+'.'+kind).read_bytes()
        require(row['kind']==kind and len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'] and oid(kind,raw)==identity,'Registered driver raw origin')
        return raw
    commit=driver_object(driver['head'],'commit');current=commit.split(b'\n',1)[0].split()[1].decode()
    for part,identity in zip(['scripts','research_package.py'],driver['origin_tree_chain']):
        require(current==identity,'Registered driver tree chain')
        mode,current=tree_entries(driver_object(identity,'tree'))[part]
    raw=regular(root,base+'registered-driver/research_package.py').read_bytes()
    require(mode in ('100644','100755') and oid('blob',raw)==current==driver['git_blob'] and hashlib.sha256(raw).hexdigest()==driver['sha256'],'Registered driver blob binding')
    repository='capsule/'+('repository/' if number=='5402' else 'clifford-repository/')
    for row in report['runtime_files']:
        raw=regular(root,base+'source-capsule/'+row['path']).read_bytes()
        require(len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],'Runtime source SHA')
        require(raw==regular(root,repository+row['path']).read_bytes(),'Runtime replay copy differs')
        origin(row['origin'],raw)
    for row in report['source_rows']:
        raw=regular(root,base+row['stored_source']).read_bytes();origin(row['origin'],raw)
        require(hashlib.sha256(raw).hexdigest()==row['declared']['sha256'] and oid('blob',raw)==row['declared']['git_blob'],'Declared original source binding')
        if row['declared'].get('retained_copy'):
            require(raw==regular(root,base+'source-capsule/'+report['package']+'/'+row['declared']['retained_copy']).read_bytes(),'Retained source copy differs')
    return {'head':report['head'],'runtime_files':len(report['runtime_files']),'source_rows':len(report['source_rows']),'raw_git_objects':len(report['raw_git_origin_objects']),'status':'PASS_FRESH_OFFLINE_SOURCE_CUSTODY'}
def check(root):
    root=Path(root).absolute()
    for part in [root,*root.parents]:require(not part.is_symlink(),'Symlink package ancestor')
    regular(root,'verify.py')
    claims=json.loads(regular(root,'CLAIMS.json').read_bytes())
    require(claims==CLAIMS_EXPECTED,'Changed or unsupported scientific claim')
    manifest=json.loads(regular(root,'SOURCE-BINDINGS.json').read_bytes())
    require(manifest['canonical_main']==MAIN,'Wrong canonical pin')
    rows=manifest['files'];paths=[r['path'] for r in rows]
    require(len(paths)==len(set(paths)),'Duplicate manifest path')
    actual=set()
    for path in root.rglob('*'):
        require(not path.is_symlink(),'Symlink anywhere in package')
        require(path.name!='__pycache__' and path.suffix not in ('.pyc','.pyo'),'Bytecode cache in package')
        if path.is_file():actual.add(path.relative_to(root).as_posix())
    require(actual==set(paths)|{'verify.py','SOURCE-BINDINGS.json'},'Missing or undeclared input')
    digests={}
    for row in rows:
        raw=regular(root,row['path']).read_bytes();digest=hashlib.sha256(raw).hexdigest()
        require(len(raw)==row['bytes'] and digest==row['sha256'],'Changed working bytes: '+row['path'])
        if row.get('payload_sha256'):require(hashlib.sha256(gzip.decompress(raw)).hexdigest()==row['payload_sha256'],'Changed compressed payload')
        digests[row['path']]=digest
    for path,digest in manifest['frozen_engines'].items():require(digests.get(path)==digest,'Changed mathematical engine')
    sources={n:custody(root,n) for n in ['5402','5376']}
    engine=json.loads(regular(root,'reports/clifford-proof/SOURCE-MANIFEST.json').read_bytes())
    for path,digest in engine['sources'].items():require(digests['capsule/clifford-repository/research/clifford-tensor-gram/'+path]==digest,'Clifford DUT/proof source mismatch')
    pins=json.loads(regular(root,'capsule/agents/budget/inputs/ALL-PINS.json').read_bytes())
    for row in pins:require(digests['capsule/agents/budget/'+row['local']]==row['sha256'],'Budget frozen pin mismatch')
    for row in json.loads(regular(root,'capsule/agents/budget/envelope-inputs/SOURCES.json').read_bytes()):
        require(digests['capsule/agents/budget/'+row['local']]==row['sha256']==digests['capsule/repository/'+row['source_path']],'Envelope original source pin mismatch')
    budget=json.loads(regular(root,'reports/budget/RESULT-v3.json').read_bytes())
    require(budget['executed_checker_sha256']==digests['capsule/agents/budget/screen_v3.py'],'Budget v3 execution source mismatch')
    require(budget['boundary_scalar_units']==42 and budget['scalar_tariff_units_including_swaps']==175022,'Wrong final emitted-scale tariff')
    envelope=json.loads(regular(root,'reports/budget/LOCAL-ENVELOPE-v1.json').read_bytes())
    require(envelope['executed_checker_sha256']==digests['capsule/agents/budget/independent_local_envelope.py'],'Envelope execution source mismatch')
    require(envelope['total_max_field_l2_exponent']==18996 and envelope['total_joint_field_l2_exponent']==19012 and envelope['copy_count']==16,'Wrong local norm envelope')
    algebra=json.loads(regular(root,'reports/algebra/RESULT.json').read_bytes())
    for path,digest in algebra['consumed_sha256'].items():require(digests['capsule/repository/'+path]==digest,'Algebra consumed source mismatch')
    for path,digest in algebra['checker_files_sha256'].items():require(digests['capsule/agents/algebra/'+path]==digest,'Algebra checker mismatch')
    require('check_same_chart_cache_mutant.py' not in algebra['checker_files_sha256'],'Original root receipt unexpectedly includes later helper')
    derived=json.loads(regular(root,'reports/algebra/RESULT.json').read_bytes())
    derived['checker_files_sha256']['check_same_chart_cache_mutant.py']=digests['capsule/agents/algebra/check_same_chart_cache_mutant.py']
    replay_expected=json.loads(regular(root,'reports/algebra/REPLAY-EXPECTED.json').read_bytes())
    require(replay_expected==derived,'Replay expectation differs beyond authenticated adjacent-code inventory row')

    conclusion=json.loads(regular(root,'reports/clifford-proof/CONCLUSION.json').read_bytes())
    require(conclusion['status']=='PASS_BOUNDED_SCOPE' and conclusion['head']==CLIFFORD,'Wrong companion scope')
    require(conclusion['all_n_written_proof']=='sound under fixed-coefficient exact dyadic-Clifford hypotheses','Wrong all-n scope')
    author=regular(root,'reports/root-runs/provider5402-author-registered/stdout.log').read_bytes()
    receipt=json.loads(regular(root,'reports/root-runs/provider5402-author-registered/RECEIPT.json').read_bytes())
    require(receipt['exit_code']==0 and hashlib.sha256(author).hexdigest()==receipt['log_sha256'],'Root author evidence binding')
    author_rows=[json.loads(line.split(' ',1)[1]) for line in author.decode().splitlines() if line.startswith('PASS_NATIVE_RANK8_HELPER_PROVIDER ')]
    require(len(author_rows)==2,'Frozen author normal/-O pair missing')
    expected={k:claims['provider'][k] for k in ['original_inputs','arbitrary_owned_inputs','owned_outputs_zero','autonomous_helpers','coupled_helpers','paid','phase_bindings']}
    for row in author_rows:
        row.pop('seconds');require(row==expected,'Author pair scientific fields changed')
    for name in ['provider5402-independent-algebra','provider5402-budget-final-v3','provider5402-local-envelope','clifford5376-independent-pilot','provider5402-same-chart-cache-control']:
        b='reports/root-runs/'+name+'/'
        receipt=json.loads(regular(root,b+'RECEIPT.json').read_bytes())
        require(receipt['exit_code']==0 and hashlib.sha256(regular(root,b+'stdout.log').read_bytes()).hexdigest()==receipt['log_sha256'],'Root run/log binding: '+name)
    return {'status':'PASS_ACTUAL_WORKING_INPUT_BINDINGS','files':len(rows),'custody':sources,'frozen_author_pair':'authenticated reuse; no fresh author science','digests':digests}
