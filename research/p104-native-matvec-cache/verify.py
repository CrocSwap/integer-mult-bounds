"""Exact key/invalidation tests plus unchanged complete native replay."""
from functools import lru_cache
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('p104_acceleration', HERE/'accelerated.py')
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)


def independent_product(rows, address):
    out = 0
    for i, row in enumerate(rows):
        bit = 0
        for j in range(9):
            bit ^= ((row >> j) & 1) * ((address >> j) & 1)
        out |= bit << i
    return out


def controls():
    module = A.checked_module()
    memo = lru_cache(maxsize=A.CACHE_SIZE)(module.N.mul)
    identity = tuple(1 << i for i in range(9))
    matrices = {identity}
    for i in range(9):
        for j in range(9):
            if i != j:
                rows = list(identity)
                rows[i] ^= rows[j]
                matrices.add(tuple(rows))
            if i < j:
                rows = list(identity)
                rows[i], rows[j] = rows[j], rows[i]
                matrices.add(tuple(rows))
    evaluations = 0
    for rows in sorted(matrices):
        for address in range(512):
            A.require(memo(rows, address) == independent_product(rows, address), 'independent full-address product')
            evaluations += 1
    # More than CACHE_SIZE distinct subsequent entries have displaced this
    # first enumerated key. Measure an actual miss on its first revisit.
    first = sorted(matrices)[0]
    before_misses = memo.cache_info().misses
    A.require(memo(first, 0) == independent_product(first, 0) and
              memo.cache_info().misses == before_misses+1, 'evicted entry recomputes on a miss')
    warm = memo(identity, 1)
    changed = (3,)+identity[1:]
    A.require(memo(changed, 2) == 3 and memo(identity, 2) == 2 and warm == 1,
              'matrix and address both participate in key')
    A.require(memo.cache_info().currsize == A.CACHE_SIZE, 'bounded eviction exercised')
    wrong_matrix_only = {identity: module.N.mul(identity, 1)}
    A.require(wrong_matrix_only[identity] != independent_product(identity, 2), 'address-omission negative control')
    wrong_address_only = {2: module.N.mul(identity, 2)}
    A.require(wrong_address_only[2] != independent_product(changed, 2), 'matrix-omission negative control')
    before = memo.cache_info().hits
    A.require(memo(tuple(list(identity)), 1) == 1 and memo.cache_info().hits == before+1,
              'equal immutable matrices reuse correctly')
    memo.cache_clear()
    A.require(memo.cache_info().currsize == 0, 'cache cleared after replay')
    return {'matrices': len(matrices), 'all_address_evaluations': evaluations,
            'cache_bound': A.CACHE_SIZE, 'controls': ['address_omission', 'matrix_omission',
            'value_equal_key', 'eviction_recompute', 'cache_clear']}


def main():
    result = controls()
    replay = A.replay(True)
    A.require(replay['cache_statistics']['hits'] > replay['cache_statistics']['misses'], 'fixture exercises reuse')
    result['source_receipt'] = replay['source_receipt']
    expected = json.loads((HERE/'RESULT.json').read_text())
    A.require(result == expected, 'exact complete receipt changed')
    print('PASS_P104_NATIVE_MATVEC_CACHE_VALIDATION matrices='+str(result['matrices'])+
          ' addresses='+str(result['all_address_evaluations'])+' original_controls=5 full_private_columns=4096')


if __name__ == '__main__':
    main()
