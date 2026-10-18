"""Exact content admission for two inherited deterministic promotions.

Prepared with OpenAI Codex assistance; Apache-2.0. The original recipes stay
byte-pinned. Only regenerated gzip containers admit alternate compression.
See proof/PORTABLE-BASELINE.json for original-source and witness provenance.
"""
import gzip
import hashlib
import json

if not __debug__:
    raise RuntimeError('Assertions required; refusing optimized verification')

SOURCE_CONTENT_SHA256 = '58e469f7f96dc1a79380d430f176a5d448f81643e5a639f5b447929cf36474be'
PINS = {
    'eight': {
        'recipe_sha256': '9ad34faa8611a6ea7f161d2e1fe331ab1ba5ccec8fca3978e31c3e7bf789bc31',
        'source_sha256': 'a30810b755cf80e1128c0b932728bd51ca8e0bb31225fc415675afb42a766c8f',
        'word_sha256': '375bd23001cd805707968005a9342827d5464e3f8e3a754197b31c46fc3f63c2',
        'word_content_sha256': '2b67fd69853dfc28f30ab5bb928f573077ae9d2bfa12cc36254d018d56133a5d',
    },
    'four': {
        'recipe_sha256': '90417f8d54ea9272bb5041ed9144a58dcbc194a22dd0845e7de89d4b717f1b74',
        'source_sha256': 'a30810b755cf80e1128c0b932728bd51ca8e0bb31225fc415675afb42a766c8f',
        'word_sha256': '2a2ef59a5376cca2c8c3d2d7a9476d98cd527275e8bf4bc0047eaba4d8c2591c',
        'word_content_sha256': 'fd694fd6e23c572e4cdb93b1513344a9914addbe4f952e1e9375b2688596e4aa',
    },
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def admitted_input(kind, source, recipe_path):
    pin = PINS[kind]
    recipe_bytes = recipe_path.read_bytes()
    assert digest(recipe_bytes) == pin['recipe_sha256'], 'changed frozen promotion recipe'
    recipe = json.loads(recipe_bytes)
    for field in ('source_sha256', 'word_sha256', 'word_content_sha256'):
        assert recipe[field] == pin[field], ('original recipe identity', field)
    payload = gzip.decompress(source.read_bytes())
    assert digest(payload) == SOURCE_CONTENT_SHA256, 'changed promotion input payload'
    return recipe, payload


def admitted_output(kind, container):
    payload = gzip.decompress(container)
    assert digest(payload) == PINS[kind]['word_content_sha256'], 'changed promotion output payload'
    return payload
