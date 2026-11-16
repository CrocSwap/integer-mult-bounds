"""Read-only, non-scientific checks on the fixed #7624 receipt structure."""
from fractions import Fraction
import hashlib,json
from pathlib import Path

CANDIDATE = 'df521d552dc35de6271e67655e4f9c466bc9247d37a5196b85613870209106a2'
SOURCE = 'c14f365d254598f6a2daa349b47f815d20c649f0439cc36897b531412e19a3de'
PAIR_SHA = '93beb8935e9e5ed75f36b287c80230d25813b95ec5a6a0e2b8d329e609870d76'

def need(value, message):
    if not value:
        raise ValueError(message)

def verify_audit_capture(capture, raw):
    """Validate the two exact controller audit outcomes, without source execution."""
    need(isinstance(capture,dict),'audit capture type')
    if capture.get('status')=='ABSENT':
        need(set(capture)=={'status','rows'} and type(capture['rows']) is int and capture['rows']==0 and raw is None,'contradictory absent audit')
        return True
    need(capture.get('status')=='ARCHIVED' and set(capture)=={'status','sha256','bytes','rows'},'audit archive fields')
    need(isinstance(raw,bytes) and 0<len(raw)<=4*1024*1024 and raw.endswith(b'\n'),'audit raw bytes')
    rows=raw.splitlines();need(type(capture['bytes']) is int and type(capture['rows']) is int and capture['bytes']==len(raw) and capture['rows']==len(rows)>0 and capture['sha256']==hashlib.sha256(raw).hexdigest(),'audit archive counts/hash')
    known={'source_sha256':'35a3a38c6fe57cfb703a57a0382ef6f6b738131753b5fb5b97a68185b82994e1','before':'str(arc.relative_to(HERE))','after':'arc.relative_to(HERE).as_posix()','adapted_sha256':'57d9c83ecbcb3e9d7697dfa0d78bce6ff98958a1ee53267bffb710e362844caf','path_name':'source.py'}
    need(all(json.loads(row)==known for row in rows),'audit row vocabulary')
    return True

def verify_source7(folder, resource_bytes, identity, service):
    folder=Path(folder);obs_raw=(folder/'OBSERVATION.json').read_bytes()
    need(hashlib.sha256(obs_raw).hexdigest()=='000571ad2e8b3beefa628f7a47e6409c840a450b3141c44901db439c8f9a0c9d','source7 observation pin')
    obs=json.loads(obs_raw);resource=json.loads(resource_bytes)
    need(obs['status']=='AUTHOR_OBSERVED_COMPLETED_SOURCE7_INTERMEDIATE_FILES' and obs['author_observation_not_independent_attestation'] is True and obs['run_id']==identity['run_id'] and obs['service']==service and obs['source_resource_sha256']==hashlib.sha256(resource_bytes).hexdigest(),'source7 observation identity')
    need(resource['status']=='DERIVED_FRESH_SOURCE_RESOURCE_ONLY' and resource['source_catalogue_rerun'] is False and resource['native_word_sha256']==identity['source_canonical_sha256'] and resource['candidate_native_receipt_sha256']==obs['candidate_native_result_sha256']=='2cf79508c3dbffb56a1f0609710ccc921590dd4747850279edefe8f71238b682','source7 source scope')
    scripts={'emit_odd_type_b.py','emit_odd_type_ab.py','check_odd_caller_exact_grid.py','check_odd_physical_binding.py','check_odd_precision.py','check_odd_partial_admission.py','check_odd_fixed_tape_counts.py'}
    outputs={'ODD-ADMISSION-PARTIAL.json','ODD-CALLER-EXACT-GRID.json','ODD-FIXED-TAPE-COUNTS.json','ODD-PHYSICAL-BINDING.json','ODD-PRECISION.json','ODD-TYPE-AB-REPLAY.json','ODD-TYPE-B-REPLAY.json'}
    extras={'ODD-TYPE-AB-CALLER.json','CURRENT-PRICE.json','COHORT-PRICE.json','DERIVED-NATIVE.json','WORD.json.gz'}
    expected=scripts|outputs|extras;need(len(obs['files'])==19 and {x['name'] for x in obs['files']}==expected,'source7 inventory')
    children=list(folder.iterdir());need(all(x.is_file() and not x.is_symlink() for x in children) and {x.name for x in children}==expected|{'OBSERVATION.json'},'source7 directory')
    rows={r['name']:r for r in obs['files']}
    for name in expected:
        b=(folder/name).read_bytes();need(len(b)==rows[name]['bytes'] and hashlib.sha256(b).hexdigest()==rows[name]['sha256'],'source7 observed bytes')
    need(set(resource['check_sha256'])==outputs,'source7 output set')
    for name in outputs:need(rows[name]['sha256']==resource['check_sha256'][name],'source7 output binding')
    need(set(resource['adapter']['adapted_sha256'])=={'emit_odd_type_ab.py','check_odd_partial_admission.py','check_odd_precision.py'},'source7 adapted script set')
    for name,digest in resource['adapter']['adapted_sha256'].items():need(rows[name]['sha256']==digest,'source7 adapted script binding')
    for name,key in [('DERIVED-NATIVE.json','source_native_derived_sha256'),('WORD.json.gz','source_word_gzip_sha256'),('ODD-TYPE-AB-CALLER.json','caller_sha256'),('CURRENT-PRICE.json','source_current_price_sha256'),('COHORT-PRICE.json','source_cohort_price_sha256')]:need(rows[name]['sha256']==resource[key],'source7 resource binding')
    return True

def pairs(rows, count, label):
    need(isinstance(rows, list) and len(rows) == count and count > 0, label + ' denominator')
    out = []
    for row in rows:
        need(isinstance(row, list) and len(row) == 2 and all(type(x) is int and x >= 0 for x in row), label + ' pair shape')
        out.append(tuple(row))
    need(len(set(out)) == count, label + ' duplicate')
    return set(out)

def verify_native_pairs(ledger, manifest, receipts):
    need(manifest['schema'] == 'contact7624-native-pairs/v1' and manifest['candidate_canonical_sha256'] == CANDIDATE and manifest['source_canonical_sha256'] == SOURCE, 'pair identity')
    source = pairs(manifest['source_vs7481_pairs'], 1075, 'source')
    pinned = pairs(manifest['pinned_source_pairs'], 1075, 'pinned')
    direct = pairs(manifest['candidate_vs7481_pairs'], 1073, 'candidate')
    route = pairs(manifest['splice_route_pairs'], 12, 'splice')
    union = pairs(manifest['full_validation_pairs'], 1075, 'union')
    need(source == pinned and union == source | pinned | direct | route and type(manifest['source_affected_count']) is int and manifest['source_affected_count'] == 1075 and manifest['splice_changed_fields'] == [902, 1091], 'pair union')
    info = ledger['native']
    for key, value in [('candidate_pair_count',1075), ('source_pair_count',1075), ('candidate_vs7481_pair_count',1073)]:
        need(type(info[key]) is int and info[key] == value, 'ledger ' + key)
    need(info['candidate_pair_manifest_sha256'] == PAIR_SHA, 'pair manifest binding')
    need(isinstance(receipts,list) and len(receipts)==1075, 'native receipt denominator')
    values=[]
    for row in receipts:
        pair=row['pair']; need(isinstance(pair,list) and len(pair)==2 and all(type(x) is int and x>=0 for x in pair), 'receipt pair shape')
        need(type(row['columns']) is int and row['columns']==512 and type(row['adjoint_columns']) is int and row['adjoint_columns']==512 and row['absolute_phase_verified'] is True, 'positive column coverage')
        values.append(tuple(pair))
    need(len(set(values))==1075 and set(values)==union, 'receipt identity or duplicate')
    return True

def verify_certificates(report):
    need(report['status']=='PASS_CERTIFICATES_204', 'certificate status')
    for name in ('source','candidate'):
        group=report[name]; rows=group['records']
        need(len(rows)==204 and group['final_public_rank']==1501 and group['zero_rows']==7, 'certificate denominator/rank')
        need(len({row['clear_index'] for row in rows})==204 and {row['clear_index'] for row in rows}==set(range(204)), 'certificate index')
        zeros=0
        for row in rows:
            need(type(row['all_remaining_live_count']) is int and type(row['nonzero_remaining_live_count']) is int and 1501 <= row['nonzero_remaining_live_count'] <= row['all_remaining_live_count'], 'nonzero live count')
            need(type(row['all_remaining_live_matrix_rank']) is int and row['all_remaining_live_matrix_rank']==1501, 'live rank')
            erased=row['erased']; cert=row['certificate']
            need(isinstance(erased,dict) and isinstance(cert,dict), 'certificate row type')
            need(all(Fraction(v)!=0 for v in erased.values()) and all(Fraction(v)!=0 for v in cert.values()), 'zero coefficient encoded')
            if not erased:
                zeros+=1; need(not cert and row['public_support']==0, 'zero row provider')
            else:
                need(cert and type(row['public_support']) is int and row['public_support']==len(cert), 'nonzero row needs nonzero public provider')
        need(zeros==7, 'zero rows')
    return True

def verify_signed(signed):
    need(signed['status']=='PASS_CONTACT7624_COMPLETE_SIGNED_APPLICATION', 'signed status')
    cat=signed['catalogue'];need(isinstance(cat,list) and bool(cat), 'empty catalogue')
    size=cat[0]['catalogue_size'];need(type(size) is int and size>0 and signed['catalogue_size']==size, 'catalogue denominator')
    cursor=0;boundary=0
    for row in cat:
        need(type(row['slice_start']) is int and type(row['slice_stop']) is int and type(row['checked_maps']) is int and type(row['main_boundary_pairs']) is int and row['main_boundary_pairs']>=0, 'catalogue integers')
        need(row['slice_start']==cursor and row['slice_stop']>cursor and row['checked_maps']==row['slice_stop']-cursor and row['catalogue_size']==size and row['phase_control_rejected'] is True and row['word_sha256']=='501876971143a0588403d653852b2305893d9b385be94f0f5d7134ebd97e03f0', 'catalogue slice')
        cursor=row['slice_stop'];boundary+=row['main_boundary_pairs']
    need(cursor==size and boundary==104, 'catalogue coverage and boundaries')
    after=signed['price']['after'];need(sum(after['P'].values())==110043 and sum(after['T'].values())==22461 and after['S']==1424,'signed invoice')
    before=signed['price']['baseline_7624'];need(sum(before['P'].values())==110060 and sum(before['T'].values())==22461 and before['S']==1424,'source signed invoice')
    source=signed['source_resource'];need(source['status']=='DERIVED_FRESH_SOURCE_RESOURCE_ONLY' and source['source_catalogue_rerun'] is False, 'source resource scope')
    tape=signed['checks']['ODD-FIXED-TAPE-COUNTS.json'];need(tape['native_invocations']==17, 'signed invocation count')
    outer=signed['price']['public_claim_gate']['outer'];need(outer['strict_count']==54 and outer['functional_count']==4,'58 outer predicates')
    return True
