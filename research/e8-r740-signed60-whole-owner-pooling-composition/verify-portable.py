"""Run the complete frozen verifier with one explicit gzip-container adaptation."""
from pathlib import Path
from hashlib import sha256
import json

if not __debug__:
    raise SystemExit('Assertions required')

packet = Path(__file__).resolve().parent
manifest = json.loads((packet / 'PORTABLE-GZIP-REPAIR.json').read_text())
assert manifest['status'] == 'STRICT_GENERATED_GZIP_CONTAINER_ADAPTATION'
assert set(manifest['files']) == {'verify-portable.py', 'gzip_word_identity.py'}
for name, checksum in manifest['files'].items():
    assert sha256((packet / name).read_bytes()).hexdigest() == checksum, name
assert sha256((packet / 'SOURCE-MANIFEST.json').read_bytes()).hexdigest() == manifest['original_source_manifest_sha256']
original = packet / 'verify.py'
assert sha256(original.read_bytes()).hexdigest() == manifest['original_verifier_sha256']
source = original.read_text()
before = " assert (A/'local'/n).read_bytes()==(B/n).read_bytes(),n\n"
after = " if n=='word.json.gz':assert_word_identity(A/'local'/n,B/n)\n else:assert (A/'local'/n).read_bytes()==(B/n).read_bytes(),n\n"
assert source.count(before) == 1, 'Unexpected frozen comparison source'
adapted = source.replace(before, after)
assert sha256(adapted.encode()).hexdigest() == manifest['adapted_verifier_sha256']
from gzip_word_identity import assert_word_identity
exec(compile(adapted, str(original), 'exec'), {
    '__name__': '__main__', '__file__': str(original),
    'assert_word_identity': assert_word_identity,
})
