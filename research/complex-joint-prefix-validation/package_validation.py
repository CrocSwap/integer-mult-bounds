"""Package two completed source-frozen replays; never run reconstruction here.

Adapted from pr569-review/package_validation.py. This script must be run only
after both final replays and the final independent source review are complete.
It makes no change to the source package and creates the validation sibling
only after all preflight comparisons have succeeded.
"""
import copy
import gzip
import hashlib
import importlib.util
import json
import shutil
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TREE = ROOT.parent / 'imb-joint-prefix-pr'
P = TREE / 'research/complex-joint-prefix'
DEST = TREE / 'research/complex-joint-prefix-validation'
STATUS = 'PASS_ALL72_JOINT_PREFIX_NATIVE_COMPLEX_AND_CITED_BIT'
PROVIDERS = ('eightcold_eight', 'width7_eight')
FILES = ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'LOCAL-CHECKS.json',
         'INDEPENDENT-LOCAL-REPLAY.json', 'CLIFFORD-RECIPES.json',
         'CLIFFORD-REVIEW.json', 'RESIDUAL-ADAPTERS.json')
STAGES = [
    'standard-library-packing-rebuild', 'frozen558-full-replay',
    'portable-promotion-identity-controls', 'first-cold-construction',
    'first-cold-kernel-omissions', 'eightcold-construction',
    'eightcold-all-kernel-omissions', 'eightcold-inherited44-omissions',
    'eightcold-rank5-omissions', 'width7-construction',
    'width7-all-kernel-omissions',
    'width7-independent-scalar-identity-and-omission-transfer',
]
for _name in ('eightcold', 'width7'):
    STAGES += [_name + '-' + suffix for suffix in (
        'joint-prefix-construction', 'joint-prefix-all-kernel-omissions',
        'joint-prefix-rank5-omissions', 'independent-joint-prefix-and-coverage',
        'all-columns-native-frames', 'both-reflected-ledgers',
        'independent-local-controls', 'normalized-wrappers')]
STAGES += [
    'eightcold-all-phase-edges', 'width7-all-phase-edges', 'bind-two-providers',
    'emit-two-provider-controller', 'independent-literal-owner-geometry',
    'independent-controller-and-controls', 'fresh-two-provider-invoice',
    'conservative-and-native-exact-assembly', 'admission-mutation-controls',
    'phase-timing-portability-controls',
    'generated-artifact-content-and-recompression-controls',
]


def require(test, message):
    if not test:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload_sha(path):
    return hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest()


def json_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode('utf-8')).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')


def child(directory, relative):
    path = (directory / relative).resolve()
    require(path.is_relative_to(directory.resolve()), 'Escaping receipt path: ' + relative)
    return path


def receipt_files(source, receipt, prefix, copies):
    for rel, digest in receipt['artifacts'].items():
        path = child(source, rel)
        require(sha(path) == digest, 'Changed receipt artifact: ' + str(path))
        copies[prefix / rel] = path
    for stage in receipt['steps']:
        require(stage['exit_code'] == 0, 'Failed stage: ' + stage['name'])
        log = child(source, stage['name'] + '.log')
        require(sha(log) == stage['log_sha256'], 'Changed stage log: ' + str(log))
        copies[prefix / log.name] = log


def assembly_projection(source, assembly):
    """Retain every field except three explicitly validated runtime references."""
    owner_path = source / 'mixed-global/audit/OWNERS-AND-PROFILE.json'
    invoice_path = source / 'mixed-global/audit/PREFIX-AND-INVOICE.json'
    template_path = source / 'mixed-global/hosted/GLOBAL-TEMPLATE.json.gz'
    owner, invoice = read(owner_path), read(invoice_path)
    require(assembly['template_sha256'] == payload_sha(template_path)
            == owner['template_sha256'] == invoice['template_sha256'],
            'Stale assembly template reference')
    require(assembly['input_sha256']['owner_audit'] == sha(owner_path)
            == invoice['owner_audit_sha256'], 'Stale assembly owner reference')
    require(assembly['input_sha256']['fresh_invoice'] == sha(invoice_path),
            'Stale assembly invoice reference')
    for rel, digest in assembly['input_sha256'].items():
        if rel not in ('owner_audit', 'fresh_invoice'):
            require(sha(child(P, rel)) == digest, 'Changed assembly source input: ' + rel)
    value = copy.deepcopy(assembly)
    del value['template_sha256']
    del value['input_sha256']['owner_audit']
    del value['input_sha256']['fresh_invoice']
    return value


def main():
    require(__debug__, 'Assertions in imported identity checker must remain enabled')
    require(not DEST.exists(), 'Validation destination already exists')
    require(len(STAGES) == len(set(STAGES)) == 39, 'Wrong expected stage inventory')
    manifest = read(P / 'MANIFEST.json')
    actual = {f.relative_to(P).as_posix(): sha(f) for f in P.rglob('*')
              if f.is_file() and f != P / 'MANIFEST.json' and '__pycache__' not in f.parts}
    require(manifest == actual, 'Source manifest mismatch')
    manifest_hash = sha(P / 'MANIFEST.json')
    pins = read(P / 'SOURCE-PINS.json')['files']
    for rel, pin in pins.items():
        require(sha(child(P, rel)) == pin['sha256'], 'Source pin mismatch: ' + rel)
    plan = read(P / 'data/PLAN.json')
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('final_generated_identity', P / 'code/generated_identity.py')
    identities = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(identities)
    require(tuple(identities.FILES) == FILES, 'Changed seven-artifact identity contract')
    rows, claims, provider_maps, copies = [], [], [], {}
    for label, version, platform in (('windows314', '3.14.', 'Windows'), ('linux312', '3.12.', 'Linux')):
        source = ROOT / ('final-' + label)
        receipt, result = read(source / 'RECEIPT.json'), read(source / 'RESULT.json')
        require(receipt['status'] == result['status'] == STATUS, 'Incomplete final replay: ' + label)
        require(receipt['manifest_sha256'] == manifest_hash and receipt['inputs_unchanged'] is True,
                'Replay is not bound to this frozen package: ' + label)
        require(receipt['immutable_source_pins_checked'] == len(pins), 'Incomplete source-pin admission')
        require([s['name'] for s in receipt['steps']] == STAGES, 'Incomplete or reordered top-level stages')
        require(read(source / 'STAGES.json') == receipt['steps'], 'Changed stage inventory')
        runtime = receipt['runtime']
        require(runtime['python'].startswith(version) and platform in runtime['platform'],
                'Unexpected replay runtime: ' + label)
        require(all(runtime[k] for k in ('zlib_version', 'zlib_runtime_version')), 'Missing zlib metadata')
        prefix = Path(label)
        receipt_files(source, receipt, prefix, copies)
        for name in ('RECEIPT.json', 'STAGES.json'):
            copies[prefix / name] = source / name
        baseline = source / 'baseline558'
        nested = read(baseline / 'RECEIPT.json')
        require(nested['status'] == 'PASS_COMPLEX_EIGHT_RANK5_PIVOTS_AND_CITED_BIT', 'Incomplete PR558 replay')
        require(nested['dispatcher_source_sha256'] == sha(P / 'code/replay558_portable.py'),
                'Wrong baseline replay dispatcher')
        for rel, digest in nested['derived_source_sha256'].items():
            require(sha(child(P, rel)) == digest, 'Changed baseline derivative: ' + rel)
        receipt_files(baseline, nested, prefix / 'baseline558', copies)
        for f in baseline.iterdir():
            if f.is_file() and f.suffix in ('.json', '.log'):
                copies[prefix / 'baseline558' / f.name] = f
        assembly = read(source / 'ASSEMBLY.json')
        projection = assembly_projection(source, assembly)
        require(result['kappa_decimal'] == assembly['kappa_decimal']
                and result['conservative_kappa_decimal'] == assembly['conservative_kappa_decimal'],
                'Result and assembly disagree')
        require(Fraction(assembly['kappa_decimal']) > Fraction('0.001600682403612293'),
                'Final construction does not beat PR571')
        claims.append(projection)
        binding = read(source / 'mixed-global/BINDING.json')
        maps, raw = {}, {}
        for pid in PROVIDERS:
            directory = source / 'mixed-global/base/providers' / pid
            maps[pid] = identities.artifact_identities(directory)
            raw[pid] = {name: sha(directory / name) for name in FILES}
            require(maps[pid] == plan['provider_registry'][pid]['artifact_semantic_sha256']
                    == binding['providers'][pid]['artifact_semantic_sha256'], 'Changed provider identity: ' + pid)
            require(raw[pid] == binding['providers'][pid]['artifact_sha256'], 'Stale raw provider binding: ' + pid)
            emitted = source / ('eightcold-local' if pid == 'eightcold_eight' else 'width7-local')
            require(identities.artifact_identities(emitted) == maps[pid], 'Bound provider differs from fresh local output')
        provider_maps.append(maps)
        rows.append(dict(label=label, runtime=runtime, seconds=result['seconds'], stages=len(receipt['steps']),
                         receipt_sha256=sha(source / 'RECEIPT.json'), result_sha256=sha(source / 'RESULT.json'),
                         assembly_sha256=sha(source / 'ASSEMBLY.json'),
                         exact_mathematical_projection_sha256=json_sha(projection),
                         provider_raw_artifact_sha256=raw, provider_semantic_artifact_sha256=maps))
    require(claims[0] == claims[1], 'Cross-runtime mathematical assembly mismatch')
    require(provider_maps[0] == provider_maps[1], 'Cross-runtime semantic provider mismatch')
    final_review = read(ROOT / 'audit/FINAL-SOURCE-REVIEW.json')
    require(final_review['status'].startswith('PASS') and final_review['manifest_sha256'] == manifest_hash,
            'Missing independent review of this frozen manifest')
    for name in ('FINAL-SOURCE-REVIEW.json', 'GLOBAL-HANDOFF.json', 'PR571-INDEPENDENT-REVIEW.json'):
        copies[Path(name)] = ROOT / 'audit' / name
        require(read(copies[Path(name)])['status'].startswith('PASS'), 'Incomplete review: ' + name)
    optional = set((ROOT / 'audit').glob('*PR572*.json'))
    optional.update((ROOT / 'audit').glob('*FRONTIER*.json'))
    optional.update(ROOT / 'audit' / name for name in (
        'FINAL-REPLAY-REVIEW.json', 'SOURCE-PIN-CONTROLS.json', 'SOURCE-PIN-REPAIR.json',
        'PACKAGE-PROVENANCE-REVIEW.json'))
    optional_scopes = {}
    for path in sorted(optional):
        if path.is_file():
            if 'FRONTIER' in path.name or path.name == 'PACKAGE-PROVENANCE-REVIEW.json':
                review = read(path)
                status = review.get('status', '')
                known_snapshot = status == 'NO_HIGHER_COMPARABLE_CLAIM_IDENTIFIED_IN_SNAPSHOT_AND_NO_PR572_BLOCKER_FOUND'
                require(status.startswith('PASS') or known_snapshot,
                        'Unadmitted optional review status: ' + path.name)
                scope = review.get('scope')
                if known_snapshot:
                    scope = ('PR572 metadata/source and retained frontier snapshot review; '
                             'not a fresh full physical replay or an exhaustive frontier proof.')
                require(isinstance(scope, str) and bool(scope.strip()),
                        'Missing explicit optional review scope: ' + path.name)
                optional_scopes[path.name] = dict(status=status, scope=scope)
            copies[Path(path.name)] = path
    prior_review = ROOT.parent / 'pr569-review/audit/FINAL-SOURCE-REVIEW.json'
    historical_review = read(prior_review)
    require(historical_review['status'] == 'PASS_FROZEN_PUBLICATION_SOURCE_AND_PROVENANCE_REVIEW',
            'Missing retained baseline compatibility review')
    copies[Path('baseline/PR569-FINAL-SOURCE-REVIEW.json')] = prior_review
    prior = ROOT.parent / 'imb-doublecold-pr/research/complex-doublecold-validation'
    prior_manifest = read(prior / 'MANIFEST.json')
    for f in (prior / 'baseline').rglob('*'):
        if f.is_file():
            rel = f.relative_to(prior)
            require(sha(f) == prior_manifest[rel.as_posix()], 'Changed retained baseline evidence: ' + str(rel))
            copies[rel] = f
    baseline_review = read(prior / 'baseline/BASELINE-RECOVERY.json')
    require(sha(prior / 'baseline/BASELINE-RECOVERY.json')
            == historical_review['baseline_evidence']['receipt_sha256'],
            'Retained baseline receipt differs from prior source review')
    require(baseline_review['repository_head'] == historical_review['baseline_evidence']['old_commit'],
            'Wrong retained baseline source commit')
    require(baseline_review['status'] == 'PASS_ALL_18_BASELINE_GROUPS_AFTER_DEPENDENCY_RECOVERY',
            'Incomplete retained mandatory baseline')
    require(baseline_review['initial_run_succeeded'] is False, 'Unexpected initial baseline claim')
    copies[Path('README.md')] = ROOT / 'VALIDATION-README.md'
    copies[Path('package_validation.py')] = Path(__file__)
    for rel, source in copies.items():
        require(source.is_file(), 'Missing retained evidence: ' + str(source))
    # All checks above precede any validation-directory creation.
    DEST.mkdir(parents=True)
    for rel, source in copies.items():
        target = child(DEST, str(rel))
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    comparison = dict(
        status='PASS_TWO_COMPLETE_SOURCE_FROZEN_JOINT_PREFIX_REPLAYS',
        manifest_sha256=manifest_hash, source_files=len(manifest), source_pins_checked=len(pins),
        runtimes=rows, exact_mathematical_agreement=True, all_seven_provider_semantic_artifacts_agree=True,
        mathematical_projection_exclusions=['template_sha256', 'input_sha256.owner_audit', 'input_sha256.fresh_invoice'],
        excluded_runtime_references_individually_verified=True,
        generated_identity_checker_sha256=sha(P / 'code/generated_identity.py'),
        kappa_decimal=claims[0]['kappa_decimal'], conservative_kappa_decimal=claims[0]['conservative_kappa_decimal'],
        gain_over_pr571_percent=claims[0]['gain_over_pr571_percent'],
        included_optional_reviews=sorted(path.name for path in optional if path.is_file()),
        optional_frontier_and_provenance_scopes=optional_scopes,
        scope='Two complete 39-stage reconstructions from one immutable self-contained source package. '
              'Every mathematical assembly field is equal; only three validated runtime file references '
              'are excluded from that comparison. Seven proof-relevant identities of each provider are '
              'recomputed and equal. Prior 18 mandatory repository groups are retained evidence, with '
              'the prior source compatibility review; they are not claimed freshly rerun. The final '
              'source review covers the new package. PR543 bit profile is repriced, not rebuilt.')
    write(DEST / 'COMPARISON.json', comparison)
    write(DEST / 'MATHEMATICAL-ASSEMBLY.json', claims[0])
    write(DEST / 'MANIFEST.json', {f.relative_to(DEST).as_posix(): sha(f)
                                  for f in sorted(DEST.rglob('*')) if f.is_file()})
    print(json.dumps(comparison, indent=2))


if __name__ == '__main__':
    main()
