"""Immutable source binding for additive work on PR118; no Git HEAD check."""
from hashlib import sha256
import json
from pathlib import Path

PIN='ec862a5af51537495c745d9f2323e8a5736ee265'
INHERITED='research/cube-deferred/SOURCE.json'
INHERITED_SHA='9c5cc05d04537e6604a2dfa0e5f19295599df2fd6f7b72e4822eca51b854b583'
PACKAGE='research/deferred-replayed-117'
FILES={
    PACKAGE+'/README.md':'2f05a3ba46119473a8a0b332c2ba5ef8955a362b417b4756756856c8163be0aa',
    PACKAGE+'/bit-profile.json':'7293f330518b78650bd86d76b93681e43f3a55541cdb8110993714148a4b4a6a',
    PACKAGE+'/bit_round7.py':'35d261a9248c2e06f9179e3c47e554a96b8fe763a9a3de2731256b8c0fbc74b0',
    PACKAGE+'/certificate.json':'a4590e06ce9d5095d97909e78a1e4c891ad385ef430279b97e37a6079ce8555b',
    PACKAGE+'/certificate.py':'97e78f7d466721bb8141b948f618584fd2f6c92560f96378c254d40ef330e2dc',
    PACKAGE+'/complex-dag.json.gz':'3c034d0aae388ef567a454826f4f48b26fd8a94c71e8ffed4835271b349a783b',
    PACKAGE+'/complex-profile.json':'ff5e9bbc1a3794d8dd3f75e194ea002cef8439c40a5d434c4a84e46967edc98e',
    PACKAGE+'/complex_deferred.py':'ebc3f0f5df35faaca953a4dedbea8fad011b2d252118760a7e4912a07903eb33',
    PACKAGE+'/producer.py':'34bcc5f7753fb9bfbf7a555ac4e3279fb48de7d7ec598c3cfa1e9254f64d3d5a',
    PACKAGE+'/replayed.py':'99c1e3694ae06a7ce7a370b04ecb45ea3fcfe69a6e6e7f4c4606e0a6c74c3184',
    'scripts/endpoint_gauge/match_complex_general.cpp':'fb83c08125521128a38f5ee53f91d192904cc3372ad8f196ad9576e5f4f727da',
    'scripts/partial_swap/binary_io.hpp':'d0be783f61ac4b7981e7e48a8c1139b52572302ba76c191c0e9a1b16a1a05e0e',
    'scripts/experiments/binary_frame_math.py':'1f96e8aafc8ae89f8eeec5d03800131d93d58e01bf8a7fca8feb03702d1740d0',
}


def check_base(repo):
    if not __debug__:raise ValueError('Assertions must remain enabled')
    repo=Path(repo).resolve();manifest=repo/INHERITED
    if sha256(manifest.read_bytes()).hexdigest()!=INHERITED_SHA:
        raise ValueError('Changed inherited manifest')
    old=json.loads(manifest.read_text());files=dict(FILES)
    for name,digest in old['package_files'].items():files['research/cube-deferred/'+name]=digest
    for name,digest in old['repository_files'].items():files[name]=digest
    for name,digest in files.items():
        p=(repo/name).resolve()
        if not p.is_relative_to(repo) or sha256(p.read_bytes()).hexdigest()!=digest:
            raise ValueError('Changed or escaping pinned source: '+name)
    return dict(pin=PIN,inherited_manifest_sha256=INHERITED_SHA,files=files)
