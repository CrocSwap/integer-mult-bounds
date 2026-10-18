"""Resolve the exact selected1042 word without executing inherited builders."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import argparse
import copy
import gzip
import json
from pathlib import Path
import tarfile

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
AUDIT = 'research/community-frontier1042-audit/'
BASE = 'ba82555c64e1879e4b7decce28186f208fcb8262'
CHOSEN = 'slots/local/FULL-WORD.json.gz'
OLD = 'research/gauge44-slots-t16/evidence/local/FULL-WORD.json.gz'
PIN = 'research/gauge44-slots/construction/slots/SLOT-PINS-k8.json'
INPUTS = {AUDIT+x for x in ('SELECTED-SOURCE.json','RESULT.json','ASSEMBLY.json',
    'INDEPENDENT-T16.json','T16-REPLAY.json','STAGES.json','selected-replay.tar.gz')}
INPUTS |= {PIN,OLD,'research/gauge44-slots-t16/README.md',
    'research/gauge44-slots-t16/verify_t16.py','scripts/verify_frontier1042.py',
    'docs/research/community-batch1047-review.md'}

def need(ok, why):
    if not ok:
        raise ValueError(why)

def load(raw):
    def pairs(items):
        result = {}
        for k, v in items:
            need(k not in result, 'duplicate JSON key')
            result[k] = v
        return result
    def invalid(value):
        raise ValueError('nonfinite JSON')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def digest(raw):
    return sha256(raw).hexdigest()

def read(path):
    return load((ROOT / path).read_bytes())

def describe(raw):
    payload = gzip.decompress(raw)
    word = load(payload)
    report = word['report']
    return dict(container_sha256=digest(raw), payload_sha256=digest(payload),
                canonical_sha256=digest(canonical(word)), R=report['R'],
                local_profile=report['local_profile'], status=report['status'],
                A=len(word['A']), B=len(word['B']), cleanup=len(word['cleanup']))

def select(raw, pin):
    word = load(gzip.decompress(raw))
    need(digest(canonical(word)) == pin['word_sha256'], 'not the selected canonical word')
    report = word['report']
    need(report['R'] == 480 and sum(report['width_inventory'].values()) == 480,
         'selected helper inventory')
    need(sum(int(k)*n for k,n in report['local_profile'].items()) == report['local_rank_mass'],
         'selected local rank mass')
    return word

def profile_check(local, independent, replay, assembly):
    need(independent['calls'] == replay['complete_invocations'] == 144, 'whole calls')
    combined = Counter({k:144*n for k,n in local.items()})
    combined.update(independent['idle'])
    need(dict(combined) == independent['profile'] == replay['complex_profile'] == assembly['complex_profile'],
         'selected profile lineage')
    mass = sum(int(k)*n for k,n in combined.items())
    need(mass == independent['rank_mass'], 'selected total rank mass')
    return mass

def run():
    sources = load((P/'SOURCES.json').read_bytes())
    need(sources['base_commit'] == BASE, 'base')
    need(set(sources['files']) == INPUTS, 'mandatory source inventory')
    for path, expected in sources['files'].items():
        need(digest((ROOT/path).read_bytes()) == expected, 'source pin: '+path)
    selected = load((P/'BASE-SELECTED.json').read_bytes())
    need(digest((P/'BASE-SELECTED.json').read_bytes()) == sources['selected_snapshot_sha256'], 'selected snapshot')
    manifest = read(AUDIT+'SELECTED-SOURCE.json')
    for path, expected in manifest['files'].items():
        need(digest((ROOT/path).read_bytes()) == expected, 'selected source manifest: '+path)
    receipt = read(AUDIT+'RESULT.json')
    assembly = read(AUDIT+'ASSEMBLY.json')
    independent = read(AUDIT+'INDEPENDENT-T16.json')
    replay = read(AUDIT+'T16-REPLAY.json')
    pin = read(PIN)
    need(selected['certificate'] == AUDIT+'ASSEMBLY.json', 'selected certificate path')
    need(selected['certificate_sha256'] == digest((ROOT/selected['certificate']).read_bytes()) == receipt['selected_assembly_sha256'], 'selected assembly binding')
    need(assembly['kappa'] == receipt['kappa'] == replay['kappa'] == selected['kappa'], 'selected exponent')
    need(assembly['bit_supplier']['pr'] == 589 and assembly['provider_counts'] == {'gauge44':144}, 'actual suppliers')
    stages = receipt['stages']
    names = ['leaver-manifest','slots-manifest','t16-manifest','base','cells','chain','independent-leaver','leaver-global','slots','t16']
    need([s['name'] for s in stages] == names and all(type(s['exit_code']) is int and s['exit_code'] == 0 for s in stages), 'construction stage record')
    need(read(AUDIT+'STAGES.json') == stages, 'stage receipt copy')
    for stage in stages:
        need(digest((ROOT/stage['script']).read_bytes()) == stage['script_sha256'], 'stage source digest')
    words = {}
    members = {}
    with tarfile.open(ROOT/(AUDIT+'selected-replay.tar.gz')) as archive:
        for member in archive:
            need(member.isfile() and member.name not in members, 'regular unique archive members')
            raw = archive.extractfile(member).read()  # Read only; never extract paths.
            members[member.name] = digest(raw)
            if member.name.endswith('FULL-WORD.json.gz'):
                words[member.name] = describe(raw)
            if member.name == CHOSEN:
                chosen_raw = raw
            if member.name == 't16/ASSEMBLY.json':
                need(raw == (ROOT/(AUDIT+'ASSEMBLY.json')).read_bytes(), 'archived selected assembly')
            if member.name == 'RESULT.json':
                need(load(raw) == receipt, 'archived producer receipt')
    need(set(members) == set(receipt['artifacts']) | {'RESULT.json'}, 'complete archived evidence inventory')
    for name, expected in receipt['artifacts'].items():
        need(members[name] == expected, 'archived evidence digest: '+name)
    for stage in stages:
        need(members[stage['name']+'.log'] == stage['log_sha256'], 'stage log digest')
    chosen = select(chosen_raw, pin)
    need(chosen['report']['local_profile'] == independent['local_profile'], 'local profile binding')
    mass = profile_check(chosen['report']['local_profile'], independent, replay, assembly)
    old_raw = (ROOT/OLD).read_bytes()
    old = describe(old_raw)
    aliases = sorted(k for k,v in words.items() if v['canonical_sha256'] == pin['word_sha256'])
    old_aliases = sorted(k for k,v in words.items() if v['canonical_sha256'] == old['canonical_sha256'])
    need(len(aliases) == 5 and old_aliases == ['base/cold44/FULL-WORD.json.gz'], 'word lineage classification')
    controls = []
    def reject(name, fn):
        try:
            fn()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('accepted mutation: '+name)
    reject('retained R492 evidence as selected', lambda:select(old_raw,pin))
    with tarfile.open(ROOT/(AUDIT+'selected-replay.tar.gz')) as archive:
        raw_chain = archive.extractfile('chain/local/FULL-WORD.json.gz').read()
    reject('pre-slot R480 chain as selected',lambda:select(raw_chain,pin))
    changed = copy.deepcopy(chosen); changed['B'].pop()
    reject('omitted word operation',lambda:select(gzip.compress(canonical(changed)),pin))
    bad = copy.deepcopy(independent);bad['idle']['1'] += 1
    reject('idle profile shifted',lambda:profile_check(chosen['report']['local_profile'],bad,replay,assembly))
    bad = copy.deepcopy(replay);bad['complete_invocations'] = 143
    reject('lost whole invocation',lambda:profile_check(chosen['report']['local_profile'],independent,bad,assembly))
    reject('old helper count equals selected',lambda:need(old['R']==chosen['report']['R'],'different generations'))
    reject('container hash used as word pin',lambda:need(digest(chosen_raw)==pin['word_sha256'],'different digest domain'))
    reject('duplicate JSON',lambda:load('{"x":1,"x":2}'))
    # Recompression and whitespace changes preserve every parsed field.
    alternate = gzip.compress(json.dumps(chosen,sort_keys=False,indent=1).encode(),mtime=123)
    need(alternate != chosen_raw and select(alternate,pin) == chosen, 'portable canonical-word acceptance')
    return dict(base_commit=BASE,source_manifest_files=len(manifest['files']),
                archive_members=len(members),bound_artifacts=len(receipt['artifacts']),
                words=words,selected_aliases=aliases,retained_evidence=old,retained_aliases=old_aliases,
                selected_word_sha256=pin['word_sha256'],selected_R=480,retained_R=492,
                kappa=assembly['kappa'],total_rank_mass=mass,stages=names,controls=controls,
                recompressed_reformatted_word_accepted=True,
                scope='Offline provenance reconciliation and exact profile arithmetic; no native rerun, execution authentication, or new admission.')

def main():
    parser = argparse.ArgumentParser();parser.add_argument('--write-certificate',action='store_true');a=parser.parse_args()
    result=run();path=P/'EXPECTED.json'
    if a.write_certificate:
        need(not path.exists(),'certificate already exists')
        path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:
        need(canonical(result)==canonical(load(path.read_bytes())),'certificate mismatch')
    print('PASS_SELECTED1042_LINEAGE selected_R=480 retained_R=492 words=%d aliases=5 controls=8' % len(result['words']))

if __name__ == '__main__':
    main()
