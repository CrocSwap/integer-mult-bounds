#!/usr/bin/env python3
"""Package independently checked operator bodies from the frozen 235-word result."""

import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path


NATIVE = 'f5f77093ee3f8f7447726f36fe6967b21a08005d503a99441181b57e280a5970'
CENSUS = 'e1ee0b6c1b53ff269c162d6b134a5e9126be4f86cc8f4bd909e2eb8329f0d1e5'


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def sha(blob):
    return sha256(blob).hexdigest()


def read(path, pin=None):
    raw = path.read_bytes()
    if pin is not None:
        need(sha(raw) == pin,f'{path.name} byte pin')
    return json.loads(gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw)


def build(root):
    native = read(root/'NATIVE-RESULT.json',NATIVE)
    census = read(root/'SOURCE-CATALOGUE.json',CENSUS)
    rows = census['rows']
    need(native['source']['word'] == census['baseline_word'] and native['candidate']['word'] == census['candidate_word']
         and native['union_maps_exact_signed_pauli_and_phase'] == 3026, 'prior exact native result')
    recipes = {}
    for shard,pin in enumerate(native['catalogue_shard_result_sha256']):
        folder = root/f'catalogue-{shard:02d}'
        receipt = read(folder/'RESULT.json',pin)
        need(receipt['status'] == 'PASS_16_PAIRED_NATIVE_CATALOGUE_SHARD' and receipt['source_catalogue_sha256'] == CENSUS
             and receipt['phase_only_control_rejected_at'] and (receipt['shard'],receipt['shards']) == (shard,6),
             'old actual shard custody')
        for row,index in zip(read(folder/'RECIPES.json',receipt['artifact_sha256']['RECIPES.json']),
                             range(shard,len(rows),6),strict=True):
            census_record = rows[index]
            charts = row['charts']
            needs_column = census_record['prior_all_column_proof'] is None
            need(row['index'] == index and census_record['charts'] == charts
                 and row['signed_pauli_and_absolute_phase']
                 and row['literal_columns_each_direction'] == (512 if needs_column else 0)
                 and row['prior_all_column_proof'] == census_record['prior_all_column_proof'], 'same prior verified map')
            recipes[index] = [charts,census_record['ordered_basis'],row['recipe'],shard,pin]
    need(len(recipes) == len(rows) == 3026, 'complete ordered-basis custody')
    emitted = [recipes[index] for index in range(len(rows))]
    semantic = [[*charts,recipe] for charts,_,recipe,_,_ in emitted]
    need(sha(canonical(semantic)) == native['recipe_union_semantic_sha256'], 'actual old recipe union identity')
    return {'source':native['source']['word'],'candidate':native['candidate']['word'],
            'native_result_sha256':NATIVE,'map_census_sha256':CENSUS,'engines':census['exact_engines'],
            'semantic_recipe_sha256':native['recipe_union_semantic_sha256'],'maps':emitted}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    a=parser.parse_args()
    raw=canonical(build(a.root))
    packed=gzip.compress(raw,mtime=0)
    with a.out.open('xb') as stream:
        stream.write(packed)
    print(json.dumps({'maps':3026,'decoded_sha256':sha(raw),'packed_sha256':sha(packed)}))


if __name__=='__main__':
    main()
