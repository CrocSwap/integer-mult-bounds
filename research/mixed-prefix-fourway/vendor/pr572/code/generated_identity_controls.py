"""Actual gzip/receipt portability and consistently rebound semantic controls.

Only scratch copies of generated provider files are changed. Each assembly
control recomputes raw artifact links, all seven portable identities and the
owner/invoice digests. This tests identity admission, not a replacement for the
full physical replay. Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import json
import math
import shutil
import tempfile
from pathlib import Path

import os
os.environ['GAIN_PR564_SOURCE']=str(Path(__file__).resolve().parents[1]/'vendor/pr568')
from assemble import assemble, PROVIDERS
from generated_identity import FILES, artifact_identities, json_identity, sha

if not __debug__:
    raise RuntimeError('Assertions required; refusing optimized verification')


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def write_json(path, value):
    # Nonfinite numbers are emitted only by deliberate invalid-timing controls.
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8', newline='\n')


def write_gzip(path, value):
    payload = json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    path.write_bytes(gzip.compress(payload, compresslevel=1, mtime=123456789))


def refresh_links(directory):
    """Rebind only the three actual gzip references and the phase recipe link."""
    native = read(directory/'INDEPENDENT-LOCAL-REPLAY.json')
    native['canonical_word_sha256'] = sha(directory/'CANONICAL-WORD.json.gz')
    native['local_programs_sha256'] = sha(directory/'LOCAL-PROGRAMS.json.gz')
    write_json(directory/'INDEPENDENT-LOCAL-REPLAY.json', native)
    phase = read(directory/'CLIFFORD-REVIEW.json')
    phase['canonical_word_sha256'] = sha(directory/'CANONICAL-WORD.json.gz')
    phase['recipe_sha256'] = sha(directory/'CLIFFORD-RECIPES.json')
    write_json(directory/'CLIFFORD-REVIEW.json', phase)


def rebound(owner, invoice, pid, directory):
    """Return complete consistent receipt links to the changed actual files."""
    identities = artifact_identities(directory)
    o, i = copy.deepcopy(owner), copy.deepcopy(invoice)
    p = i['providers'][pid]
    for name in FILES:
        raw = sha(directory/name)
        p['artifacts'][name] = raw
        o['source_artifacts']['providers/'+pid+'/'+name] = raw
    p['semantic_artifact_sha256'] = identities
    o['provider_artifact_semantic_sha256'][pid] = identities
    phase = identities['CLIFFORD-REVIEW.json']
    o['provider_phase_semantic_sha256'][pid] = phase
    i['provider_phase_semantic_sha256'][pid] = phase
    owner_hash = json_identity(o)
    i['owner_audit_sha256'] = owner_hash
    return o, i, owner_hash, json_identity(i), identities


def run(base, audit, out, provider_root=None):
    assert not out.exists()
    out.parent.mkdir(parents=True, exist_ok=True)
    source = provider_root or base/'providers'
    owner_path, invoice_path = audit/'OWNERS-AND-PROFILE.json', audit/'PREFIX-AND-INVOICE.json'
    owner, invoice = read(owner_path), read(invoice_path)
    baseline = assemble(owner, invoice, sha(owner_path), sha(invoice_path))
    accepted, rejected, references, source_identities = [], [], [], {}
    raw_changed = {}
    with tempfile.TemporaryDirectory(prefix='generated-identity-controls-', dir=out.parent) as td:
        scratch = Path(td)
        for pid in sorted(PROVIDERS):
            original = source/pid
            ids = artifact_identities(original)
            assert ids == PROVIDERS[pid]['artifact_semantic_sha256']
            source_identities[pid] = dict(raw={name:sha(original/name) for name in FILES}, semantic=ids)
            # The optional provider-root can use another Python/zlib environment.
            o, i, oh, ih, _ = rebound(owner, invoice, pid, original)
            assert assemble(o, i, oh, ih)['kappa'] == baseline['kappa']

            def fresh(tag):
                directory = scratch/(pid+'-'+tag)
                directory.mkdir()
                for name in FILES:
                    shutil.copyfile(original/name, directory/name)
                return directory

            def reject_semantics(tag, mutate, changed_file):
                directory = fresh(tag)
                mutate(directory)
                refresh_links(directory)
                o, i, oh, ih, new_ids = rebound(owner, invoice, pid, directory)
                assert new_ids[changed_file] != ids[changed_file], (tag, 'mutation disappeared from identity')
                try:
                    assemble(o, i, oh, ih)
                except AssertionError:
                    rejected.append(dict(provider=pid, case=tag, changed_identity=changed_file,
                                         all_raw_and_semantic_links_rebound=True))
                else:
                    raise AssertionError('semantic mutation accepted: '+tag)

            def json_mutation(name, change):
                def mutate(directory):
                    value = read(directory/name)
                    change(value)
                    write_json(directory/name, value)
                return mutate

            directory = fresh('recompression')
            changed = []
            for name in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz'):
                before = (directory/name).read_bytes()
                payload = gzip.decompress(before)
                after = gzip.compress(payload, compresslevel=1, mtime=123456789)
                assert after != before and gzip.decompress(after) == payload
                (directory/name).write_bytes(after)
                changed.append(name)
            refresh_links(directory)
            o, i, oh, ih, new_ids = rebound(owner, invoice, pid, directory)
            assert new_ids == ids
            assert assemble(o, i, oh, ih)['kappa'] == baseline['kappa']
            accepted.append(dict(provider=pid, case='recompressed_same_payloads', changed_raw_artifacts=changed,
                                 all_seven_identities_unchanged=True, all_raw_links_rebound=True))
            raw_changed[pid] = {name:[sha(original/name),sha(directory/name)] for name in changed}

            # A stale literal link must fail before any normalization can hide it.
            for tag, name, receipt, field in (
                ('stale_native_word_link','CANONICAL-WORD.json.gz','INDEPENDENT-LOCAL-REPLAY.json','canonical_word_sha256'),
                ('stale_native_program_link','LOCAL-PROGRAMS.json.gz','INDEPENDENT-LOCAL-REPLAY.json','local_programs_sha256'),
                ('stale_phase_word_link','CANONICAL-WORD.json.gz','CLIFFORD-REVIEW.json','canonical_word_sha256'),
                ('stale_phase_recipe_link','CLIFFORD-RECIPES.json','CLIFFORD-REVIEW.json','recipe_sha256')):
                directory = fresh(tag)
                value = read(directory/receipt)
                value[field] = '0'*64
                write_json(directory/receipt, value)
                try:
                    artifact_identities(directory)
                except AssertionError:
                    references.append(dict(provider=pid, case=tag, rejected_before_projection=True))
                else:
                    raise AssertionError('stale literal reference normalized away: '+tag)

            def change_scalar(directory):
                programs = read(directory/'LOCAL-PROGRAMS.json.gz')
                event = next(e for e in programs['forward'] if e[0]=='scalar' and e[1][0]=='add')
                event[1][3] = -event[1][3]
                write_gzip(directory/'LOCAL-PROGRAMS.json.gz', programs)
            reject_semantics('changed_actual_scalar', change_scalar, 'LOCAL-PROGRAMS.json.gz')

            def change_frame(directory):
                word = read(directory/'CANONICAL-WORD.json.gz')
                old = word['start'][518]
                replacement = next(j for j,f in enumerate(word['frames'])
                                   if j != old and len(f) == len(word['frames'][old]))
                word['start'][518] = replacement
                write_gzip(directory/'CANONICAL-WORD.json.gz', word)
            reject_semantics('changed_actual_start_frame_same_rank', change_frame, 'CANONICAL-WORD.json.gz')
            reject_semantics('native_false_restoration', json_mutation('INDEPENDENT-LOCAL-REPLAY.json',
                             lambda x:x['local']['forward'].__setitem__('private_work_erased',False)),
                             'INDEPENDENT-LOCAL-REPLAY.json')
            reject_semantics('native_wrong_column_count', json_mutation('INDEPENDENT-LOCAL-REPLAY.json',
                             lambda x:x['local']['backward'].__setitem__('all_exact_columns',727)),
                             'INDEPENDENT-LOCAL-REPLAY.json')
            reject_semantics('native_changed_profile', json_mutation('INDEPENDENT-LOCAL-REPLAY.json',
                             lambda x:x['paid_profiles']['forward'].__setitem__('1',x['paid_profiles']['forward']['1']+1)),
                             'INDEPENDENT-LOCAL-REPLAY.json')
            reject_semantics('phase_false_global_equality', json_mutation('CLIFFORD-REVIEW.json',
                             lambda x:x.__setitem__('all_child_equalities_include_global_phase',False)),
                             'CLIFFORD-REVIEW.json')

            # This event hash is proof data, even when its value equals a gzip hash.
            def change_event_hash(directory):
                value = read(directory/'LOCAL-CHECKS.json')
                value['forward']['sha256'] = sha(directory/'CANONICAL-WORD.json.gz')
                write_json(directory/'LOCAL-CHECKS.json', value)
                assert artifact_identities(directory)['LOCAL-CHECKS.json'] == json_identity(value)
            reject_semantics('local_event_hash_is_not_a_container_reference', change_event_hash, 'LOCAL-CHECKS.json')
            reject_semantics('unrelated_native_root_seconds_retained', json_mutation('INDEPENDENT-LOCAL-REPLAY.json',
                             lambda x:x.__setitem__('seconds',7)), 'INDEPENDENT-LOCAL-REPLAY.json')
            reject_semantics('nested_phase_seconds_retained', json_mutation('CLIFFORD-REVIEW.json',
                             lambda x:x.__setitem__('additional_evidence',{'seconds':7})), 'CLIFFORD-REVIEW.json')

            for tag,value in [('negative',-1),('boolean',True),('string','1'),('nan',float('nan')),
                              ('infinity',float('inf'))]:
                directory = fresh('invalid-timing-'+tag)
                phase = read(directory/'CLIFFORD-REVIEW.json');phase['seconds'] = value
                write_json(directory/'CLIFFORD-REVIEW.json', phase)
                try:
                    artifact_identities(directory)
                except AssertionError:
                    references.append(dict(provider=pid,case='invalid_phase_seconds_'+tag,
                                           rejected_before_projection=True))
                else:
                    raise AssertionError('invalid timing silently erased: '+tag)
    assert len(accepted)==2 and len(rejected)==18 and len(references)==18
    report=dict(status='PASS_GENERATED_ARTIFACT_RECOMPRESSION_AND_REBOUND_MUTATIONS',
                kappa=baseline['kappa'], source_owner_sha256=sha(owner_path),source_invoice_sha256=sha(invoice_path),
                source_providers=source_identities,recompression_changed_raw_hashes=raw_changed,
                accepted=accepted,semantic_mutations_rejected=rejected,invalid_references_or_metadata_rejected=references,
                counts=dict(recompression_accepted=2,semantic_rejected=18,reference_or_metadata_rejected=18),
                scope='Actual copied gzip streams and receipt JSON are changed. All seven content identities, raw source links and owner/invoice digests are recomputed consistently before assembly. Only identical decompressed payloads are accepted; scalar, same-rank frame, native proof fields, global phase, event hashes and unrelated seconds remain pinned. Literal references and invalid phase timing are rejected before normalization. Full physical replay remains a separate prerequisite.')
    write_json(out,report)
    print(report['status'],report['counts'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('base','audit','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--provider-root',type=Path)
    args=parser.parse_args()
    run(args.base,args.audit,args.out,args.provider_root)
