#!/usr/bin/env python3
"""Authenticate actual working inputs; never substitute Git objects for them."""
import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path, PurePosixPath

MAIN='1ec1119972c9aefe42525172d07b332fcff81cb4'
EXPECTED={5383:('4bd6efa51a495a7c7b7754915cf0244e7e60969e','151333/50000000','2aee5e997df99726fc763e510d9cb69fbe4f86114dc8d2cd33ad26c6c462a21d',288),5387:('b1ab650d36f59e5be682a813145b7c67e219e341','605334953/200000000000','9aa0d7112b4e13f1aa13a93dab0af6f4435ffe99b842aad841685becdafee492',261)}
ASSUMPTIONS=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery']
FROZEN_ENGINES={'capsule/agents/falsifier/check_mutants.py': '326a813b2373502cfaf179de89a9a2736a82413e40b26b52f8681495e5fd4359', 'capsule/agents/outer/check_outer.py': '6338e7c30403f2077ec1c3397db05707c26fa0dd811c7863b6d84b288fb484ac', 'capsule/agents/ownership/check.py': '69ab58e41ccf548d68d24c45b673ed9918e22845d5d819588d431eb7807eff24', 'capsule/agents/applicability/check_applicability.py': '07d09997ad1e0cf3b16a7a0dc152dcd4305c91b6c5fa8e9a5985f69f44277873', 'capsule/agents/algebra/check_joint.py': '3ee4ae79a55188d5abf2306f678179f4aafb799602ffb970fc1bc8f76cb061d9', 'capsule/agents/prices/check_prices.py': 'e5f828e06b896723da4b58ca8c780609b8b94bde374a2ffeda1cab143323a335'}

def require(ok,message):
    if not ok: raise ValueError(message)

def regular(root,relative):
    parts=PurePosixPath(relative).parts
    require(parts and not relative.startswith('/') and all(p not in ('','.','..') for p in parts) and str(PurePosixPath(relative))==relative,'Noncanonical input path: '+relative)
    here=root
    for part in parts:
        here=here/part
        require(not here.is_symlink(),'Symlink input component: '+str(here))
    require(here.is_file(),'Missing regular input: '+relative)
    return here

def check(root):
    root=Path(root).absolute()
    claims=json.loads(regular(root,'CLAIMS.json').read_bytes())
    manifest=json.loads(regular(root,'SOURCE-BINDINGS.json').read_bytes())
    require(claims['canonical_main']==manifest['canonical_main']==MAIN,'Wrong canonical main')
    require(claims['selected_baseline']=='.0030217758' and claims['selected_kappa']=='15108879/5000000000','Wrong selected baseline claim')
    require(claims['same_selected_assumptions_required'] is True and all(claims[k] is False for k in ('new_unconditional_or_Lean_theorem','uniform_word_materialized','selected_record_changed')),'Wrong conditional scope flags')
    require(claims['selection_authorized'] is False,'Selected-record promotion is outside this package')
    require([x['id'] for x in claims['assumptions']]==ASSUMPTIONS,'Wrong or missing retained assumptions')
    require(len(claims['candidates'])==2 and {c['pr'] for c in claims['candidates']}==set(EXPECTED),'Two distinct separately bound candidates required')
    for c in claims['candidates']:
        require((c['head'],c['kappa'],c['word_payload_sha256'],c['last_pivot'])==EXPECTED[c['pr']],'Wrong candidate head/claim/payload/pivot')
        require(Fraction(c['decimal'])==Fraction(c['kappa']),'Wrong headline decimal')
    rows=manifest['files']; paths=[x['path'] for x in rows]
    require(len(paths)==len(set(paths)),'Duplicate input binding')
    capsule_paths=list((root/'capsule').rglob('*'))
    require(not (root/'capsule').is_symlink() and all(not p.is_symlink() for p in capsule_paths),'Symlink anywhere in capsule')
    actual={p.relative_to(root).as_posix() for p in capsule_paths if p.is_file()}
    require(actual=={p for p in paths if p.startswith('capsule/')},'Capsule has missing or undeclared files')
    digests={}
    for row in rows:
        raw=regular(root,row['path']).read_bytes()
        require(len(raw)==row['bytes'],'Wrong input size: '+row['path'])
        digest=hashlib.sha256(raw).hexdigest()
        require(digest==row['sha256'],'Changed actual working input: '+row['path'])
        if row.get('git_blob'):
            require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'Wrong original Git blob: '+row['path'])
        if row.get('payload_sha256'):
            require(hashlib.sha256(gzip.decompress(raw)).hexdigest()==row['payload_sha256'],'Wrong decompressed payload: '+row['path'])
        digests[row['path']]=digest
    require(all(digests.get(name)==value for name,value in FROZEN_ENGINES.items()),'Changed frozen independent scientific engine')
    # Raw commit and tree objects prove each vendored origin offline. Git itself
    # is never invoked by replay, and no private shared object store is needed.
    def tree_entries(raw):
        entries={}; i=0
        while i<len(raw):
            split=raw.index(b' ',i); zero=raw.index(b'\0',split)
            name=raw[split+1:zero].decode('utf-8')
            require(name not in entries,'Duplicate Git tree name')
            entries[name]=(raw[i:split].decode(),raw[zero+1:zero+21].hex());i=zero+21
        require(i==len(raw),'Truncated Git tree')
        return entries
    for row in rows:
        if row.get('git_object_type'):
            raw=regular(root,row['path']).read_bytes();kind=row['git_object_type']
            require(kind in ('commit','tree'),'Unexpected raw Git object kind')
            require(hashlib.sha1(kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_object_sha1'],'Wrong raw Git object')
        if row.get('origin_commit'):
            require(row['origin_commit'] in {MAIN,*[x[0] for x in EXPECTED.values()]},'Unrecognized source head')
            raw=regular(root,row['commit_object']).read_bytes()
            require(hashlib.sha1(b'commit '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['origin_commit'],'Wrong source commit object')
            head=raw.split(b'\n',1)[0].split();require(head[0]==b'tree','Commit lacks root tree')
            oid=head[1].decode(); parts=PurePosixPath(row['origin_path']).parts
            require(len(parts)==len(row['tree_objects']),'Wrong Git membership depth')
            for part,treepath in zip(parts,row['tree_objects']):
                tree=regular(root,treepath).read_bytes()
                require(hashlib.sha1(b'tree '+str(len(tree)).encode()+b'\0'+tree).hexdigest()==oid,'Wrong Git membership tree')
                mode,oid=tree_entries(tree)[part]
            require(mode in ('100644','100755') and mode==row['git_mode'] and oid==row['git_blob'],'Wrong original file tree membership')
    for candidate in claims['candidates']:
        label=str(candidate['pr']); wordpath=manifest['candidate_words'][label]
        payload=gzip.decompress(regular(root,wordpath).read_bytes())
        require(hashlib.sha256(payload).hexdigest()==candidate['word_payload_sha256'],'Wrong literal candidate payload')
        result=json.loads(regular(root,manifest['candidate_claim_records'][label]).read_bytes())
        # Author records are claim/parameter consistency inputs, never a PASS oracle.
        require(result['word_payload_sha256']==candidate['word_payload_sha256'],'Claim record binds a different word')
        require(result['arithmetic']['kappa']==candidate['kappa'],'Claim record has wrong kappa')
    selected=json.loads(regular(root,manifest['selected_record']).read_bytes())
    require(selected['decimal']=='0.0030217758' and selected['kappa']==claims['selected_kappa'],'Wrong frozen selected provenance')
    source=regular(root,manifest['source_word']).read_bytes()
    source_digest=hashlib.sha256(gzip.decompress(source)).hexdigest()
    require(source_digest=='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd','Wrong original source word')
    receipt=json.loads(regular(root,manifest['selected_phase_receipt']).read_bytes())
    # Its historical status is provenance only. The new program is checked afresh.
    require(receipt['claim']['word_payload_sha256']==source_digest,'Historical phase receipt has wrong source')
    require(receipt['results']['native']['actual_payload_sha256']==source_digest,'Native historical receipt has wrong source')
    require(claims['assumptions']==receipt['claim']['assumptions'],'Changed literal retained premise statements')
    return {'status':'PASS_ACTUAL_WORKING_INPUT_BINDINGS','files':len(rows),'digests':digests,'source_payload_sha256':source_digest}

if __name__=='__main__':
    print(json.dumps(check(Path(__file__).resolve().parent),sort_keys=True))
