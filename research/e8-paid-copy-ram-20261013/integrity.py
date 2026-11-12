"""Fixed-version PR647 evidence coverage, not self-authentication.

Prepared locally for Artus's Tintagel campaign with OpenAI Codex assistance.
Apache-2.0. The required inventory and retained evidence pins come from the
independently authenticated PR647 head 956bb581e7f97328e1b53baa5aca3d2490f2f607.
Trust this checker/contract through an out-of-band reviewed revision or archive
digest. A coherently rewritten whole package, including this code, can defeat
any self-contained manifest. Passing is not semantic proof verification.
"""
from hashlib import sha256, sha1
import json
from pathlib import Path

# These sets are part of the reviewed contract, not read from candidate lists.
REQUIRED_FILES = frozenset({
    'CYCLIC-COROLLARY.md', 'NOTICE.md', 'NOVELTY.md', 'PROVIDER-PROOF.md',
    'README.md', 'RESULTS.json', 'REVIEW.md', 'SOURCE.json', 'SHA256SUMS.json',
    'imports/openai-math/LICENSE', 'imports/openai-math/all-lengths.tex',
    'imports/openai-math/local.tex', 'imports/openai-math/synchronization.tex',
    'verify.py', 'integrity.py', 'test_integrity.py',
})
REQUIRED_PROOF_FILES = frozenset({
    'PROVIDER-PROOF.md', 'CYCLIC-COROLLARY.md',
    'imports/openai-math/local.tex', 'imports/openai-math/synchronization.tex',
    'imports/openai-math/all-lengths.tex',
})
REQUIRED_SOURCE_PROOFS = (
    'PROVIDER-PROOF.md', 'imports/openai-math/local.tex',
    'imports/openai-math/synchronization.tex', 'imports/openai-math/all-lengths.tex',
)
# These retained byte pins are independent of SOURCE.json and the new manifest.
# README/verify/new integrity code/tests intentionally change; their release
# authenticity requires the externally pinned reviewed revision, not this table.
RETAINED_SHA256 = {
    'CYCLIC-COROLLARY.md': '250250cfc817fe8f835e1b54e391feb6d89fdf3f6ce34a9855a87046fe8e9718',
    'NOTICE.md': 'a2151fd291023846f7629f5cc2e7c20b467923552628a76a663a067c115edf90',
    'NOVELTY.md': '7bd41b0a5338152626193394eb48026f8ad3893bead346bac5030c529ebc3225',
    'PROVIDER-PROOF.md': 'cdc496acb844de3b3bcf03f811d1bd345e476b40f0b1cb7c866066612770e834',
    'RESULTS.json': '094ce1afb700ba6cf4854f482fdb7110347d2ebbead8328cc044c25e40ceddaa',
    'REVIEW.md': '129e142959323cfabaf6e3f45d0893346d322929a5531e7d5dbf07f26d4a586d',
    'SOURCE.json': 'f987bed89214c8ca44694c8867fd98ccd96b80d2a648d957e0d7c5312ce5e631',
    'imports/openai-math/LICENSE': 'c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4',
    'imports/openai-math/all-lengths.tex': '9dfb302812971062af2990918c4b02190e3ad0ca8f271dc207241976b23c45c7',
    'imports/openai-math/local.tex': '616e2707aabf2f7591a687331d4cb0f2fa486f92c3f7fe96a133b90faff60561',
    'imports/openai-math/synchronization.tex': '4c461713ce43d5d2dd8fca84f3260925b8fb69b819e96067bc2a76e3d75c306c',
}
IMPORTED_BLOBS = {
    'imports/openai-math/local.tex': '260a19bd8f7189afbe89b0af0508d979cd1e1ca6',
    'imports/openai-math/synchronization.tex': 'cdc0f6bfb8224fcdb25b08552612522555cd5f3f',
    'imports/openai-math/all-lengths.tex': '8e2281f08c336865025a3dc10b6c790e9bfc68ed',
}

class IntegrityError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise IntegrityError(message)

def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result

def authenticate(root):
    """Check a stable, ordinary-file package against the fixed version contract.

    Returns the original mathematical receipt's authentication fields. No
    mathematical constructor, subprocess, network action or provider import.
    """
    root = Path(root).resolve()
    require(root.is_dir(), 'Package directory missing')
    files = {}
    for path in root.rglob('*'):
        require(not path.is_symlink(), 'Package symlinks are not admitted')
        if path.is_file():
            files[path.relative_to(root).as_posix()] = path
    require(set(files) == REQUIRED_FILES, 'Required complete package file inventory differs')
    data = {name: path.read_bytes() for name, path in files.items()}
    manifest = json.loads(data['SHA256SUMS.json'], object_pairs_hook=_unique_object)
    require(isinstance(manifest, dict) and
            set(manifest) == REQUIRED_FILES - {'SHA256SUMS.json'},
            'Required manifest digest coverage differs')
    for name, expected in manifest.items():
        require(isinstance(expected, str) and sha256(data[name]).hexdigest() == expected,
                'Manifest digest differs: ' + name)
    for name, expected in RETAINED_SHA256.items():
        require(sha256(data[name]).hexdigest() == expected,
                'Independently pinned retained evidence differs: ' + name)
    require(REQUIRED_PROOF_FILES <= set(manifest), 'Required proof digest coverage missing')
    source = json.loads(data['SOURCE.json'], object_pairs_hook=_unique_object)
    rows = source.get('included_proof_sources')
    require(isinstance(rows, list) and all(isinstance(row, dict) for row in rows),
            'Invalid included proof-source inventory')
    names = [row.get('file') for row in rows]
    require(len(names) == len(REQUIRED_SOURCE_PROOFS) and
            all(isinstance(name, str) for name in names) and
            set(names) == set(REQUIRED_SOURCE_PROOFS),
            'Required included proof-source inventory differs')
    by_name = {row['file']: row for row in rows}
    blobs = []
    for name in REQUIRED_SOURCE_PROOFS:
        row = by_name[name]
        require(row.get('sha256') == RETAINED_SHA256[name], 'Proof-source pin differs: ' + name)
        if name in IMPORTED_BLOBS:
            expected = IMPORTED_BLOBS[name]
            actual = sha1(b'blob ' + str(len(data[name])).encode() + b'\0' + data[name]).hexdigest()
            require(row.get('git_blob') == expected and actual == expected,
                    'Imported proof Git blob differs: ' + name)
            blobs.append({'file': name, 'git_blob': actual})
    return {'included_source_blobs': blobs, 'verbatim_Pro_provider_proof': True}
