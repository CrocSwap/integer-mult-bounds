"""Exact XOR-index permutations, caching geometry rather than input rows.

Original permutation and cube screen: Douglas R. Colkitt.
Adapter: Ross Richardson, with substantial OpenAI Codex assistance.
Apache-2.0; see the repository LICENSE.
"""


class CachedXorPermuter:
    """One replay's lazy masks; no row, rank, or admission result is cached."""

    def __init__(self):
        self._masks = {}

    def __call__(self, bits, index, n):
        # Keep the original domain check on EVERY call, including warm hits.
        if not (type(n) is int and n > 0 and n & (n - 1) == 0
                and type(index) is int and 0 <= index < n
                and type(bits) is int and 0 <= bits < 1 << n):
            raise ValueError("Invalid packed row or XOR permutation")
        b = 0
        while index:
            if index & 1:
                stride = 1 << b
                key = (n, stride)
                mask = self._masks.get(key)
                if mask is None:
                    # Exactly the retained finite geometric-series mask.
                    mask = ((1 << n) - 1) // ((1 << (2 * stride)) - 1)
                    mask *= (1 << stride) - 1
                    self._masks[key] = mask
                bits = ((bits & mask) << stride) | ((bits >> stride) & mask)
            index >>= 1
            b += 1
        return bits
