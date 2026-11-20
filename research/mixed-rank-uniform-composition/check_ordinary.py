"""Check the actual stock address routines and cold radix swap on opaque records."""

import itertools
import subprocess
import sys
import types
from collections import Counter


BASE = "e54523517d0f03e58352e647c403a5af3e525a57"
NATIVE = "a7f99a5f5f919dd3ffb2987f90c1e7d6527feb1e"


def load_module(name, head, path):
    source = subprocess.check_output(["git", "show", f"{head}:{path}"])
    module = types.ModuleType(name)
    sys.modules[name] = module
    exec(compile(source, f"{head}:{path}", "exec"), module.__dict__)
    return module


def require(statement, reason):
    if not statement:
        raise ValueError(reason)


def stock_rows(Layout):
    checked = 0
    for L, H, depth in itertools.product((2, 3, 5), (1, 2, 5), (1, 2, 3)):
        layer = Layout(L, H, depth, 2)
        power = (L*H)**depth
        for j in range(depth):
            remaining = depth-j-1
            # Fix the earlier low labels independently from the retained high digits.
            for earlier in itertools.product(range(L), repeat=j):
                counted = Counter()
                for hi in itertools.product(range(H), repeat=j):
                    prefix = sum((l*H+h)*(L*H)**i for i, (l,h) in enumerate(zip(earlier, hi, strict=True)))
                    ancestor = sum(h*H**i for i,h in enumerate(hi))
                    for tail, low, high in itertools.product(range(2*(L*H)**remaining), range(L), range(H)):
                        row = prefix + (low*H + high + L*H*tail)*(L*H)**j
                        expected = (tail*H + high)*H**j + ancestor
                        types, current = layer.descend(row, j+1)
                        require(types == earlier+(low,) and current == expected and layer.return_address(types,current) == row,
                                "literal retained split/return or high index")
                        counted[hi,low] += 1
                        checked += 1
                require(set(counted.values()) == {2*H*(L*H)**remaining}, "fresh complete low packet at fixed ancestry")
        # The final genuine row occupies the first current low of the second slab.
        subset = [r for r in range(power, power+1)]
        bad = sum(layer.split(r,0)[0] == 0 for r in subset)
        require(bad == len(subset) and L*bad != len(subset), "early padding removal control")
    return checked


def padded_swap(cold_swap):
    checked = 0
    for q, E, prefix_count, gap, tail in itertools.product((3,5), range(1,6), (1,2), (1,3), (1,2)):
        base = 2**E
        d = 0
        while q**d < base:
            d += 1
        side = q**d
        require(base <= side < q*base, "fixed volume factor")
        dims = (range(prefix_count),range(side),range(gap),range(side),range(tail))
        # The padding has distinct nonzero tokens. An incorrect intermediate gate
        # cannot pass by assuming the designated padding values stay zero.
        padded = list(itertools.product(*dims))
        swapped = cold_swap(padded, q, d, prefix_count, gap, tail)
        for address, old in zip(itertools.product(*dims), swapped, strict=True):
            p, a, g, b, s = address
            require(old == (p,b,g,a,s), "actual q-digit swaps on the whole padded stream")
            if a < base and b < base:
                require(old[1] < base and old[3] < base, "binary rectangle after whole return")
        checked += len(padded)
    return checked


def weighted_wrapper():
    checked = 0
    for q, w, atoms in itertools.product((3,5), (1,2), (1,2,3,4)):
        modulus = q**w
        for case in range(12):
            H = tuple((7*case+3*i*i+i) % modulus for i in range(atoms))
            D = tuple((13*case+5*i+2) % modulus for i in range(atoms))
            difference = tuple((v-u) % modulus for u,v in zip(H,D,strict=True))
            h,d = difference[::-1], H[::-1]
            d = tuple((u+v) % modulus for u,v in zip(h,d,strict=True))
            h,d = d[::-1], h[::-1]
            d = tuple((u-v) % modulus for u,v in zip(h,d,strict=True))
            require((h,d) == (D,H), "two reversed swaps and ordered additions")
            checked += 1
    return checked


if __name__ == "__main__":
    layout = load_module("pinned_all_depth_layout",BASE,"research/delayed-cover-batch-allocation/layout.py")
    cover = load_module("pinned_grade_native_cover",NATIVE,"research/grade14-native-realization/cover.py")
    print("live wide row/return occurrences", stock_rows(layout.Layout))
    print("complete radix-padded opaque records", padded_swap(cover.cold_swap))
    print("ordered ordinary wrapper checks", weighted_wrapper())
