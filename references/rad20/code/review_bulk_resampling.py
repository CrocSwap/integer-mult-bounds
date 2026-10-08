#!/usr/bin/env python3
"""Independent ordered mixed-radix controls for bulk resampling layout.

Executed small-field moves use binary complete-block split/interleave.
Halo emitters use alternating overlap buffers and a monotone source.
Large gathering is a model of the separately accepted coordinate router.
Selector line maps test provenance/order, not numerical Gaussian accuracy.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
from itertools import product
import json
from math import prod
from pathlib import Path
import resource
import time


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def decode(rank, sizes):
    out = [0]*len(sizes)
    for i in range(len(sizes)-1, -1, -1):
        out[i], rank = rank % sizes[i], rank // sizes[i]
    require(rank == 0, 'Address rank outside complete shape')
    return out


def encode(address, sizes):
    out = 0
    for x, n in zip(address, sizes):
        require(0 <= x < n, 'Coordinate outside complete field')
        out = out*n+x
    return out


def ceil_div(a, b):
    return -((-a)//b)


def windows(s, t, L, halo):
    return [(ceil_div((2*(k*L-halo)-1)*s, 2*t),
             ceil_div((2*((k+1)*L+halo)-1)*s, 2*t)) for k in range(t//L)]


def nearest(s, t, j):
    return (2*t*j+s)//(2*s)


class Stream:
    def __init__(self, fields, data):
        self.fields = list(fields)
        self.data = list(data)
        self.stats = dict(binary_split_passes=0, binary_interleave_passes=0,
                          complete_block_records=0, small_field_moves=0,
                          current_field_only_paddings=0, halo_rows=0,
                          monotone_new_records=0, mirrored_overlap_records=0,
                          prefix_suffix_scan_records=0, factor_page_visits=0,
                          line_maps=0, maximum_persistent_volume=len(data),
                          maximum_temporary_volume=len(data))
        self.check()

    def check(self):
        require(len(self.data) == prod(n for _, n in self.fields), 'Incomplete rectangular stream')
        require(len({name for name, _ in self.fields}) == len(self.fields), 'Duplicate field name')

    def index(self, name):
        return next(i for i, (field, _) in enumerate(self.fields) if field == name)

    def resize(self, name, new_size, verify_zero=False):
        i = self.index(name)
        old_size = self.fields[i][1]
        R = prod(n for _, n in self.fields[i+1:])
        A = prod(n for _, n in self.fields[:i])
        out = []
        for a in range(A):
            row = self.data[a*old_size*R:(a+1)*old_size*R]
            if new_size >= old_size:
                out.extend(row)
                out.extend([None]*((new_size-old_size)*R))
            else:
                if verify_zero:
                    require(all(x is None for x in row[new_size*R:]), 'Cropping a nonzero padded field')
                out.extend(row[:new_size*R])
        self.data = out
        self.fields[i] = name, new_size
        self.stats['complete_block_records'] += A*(old_size+new_size)*R
        self.stats['maximum_temporary_volume'] = max(self.stats['maximum_temporary_volume'], len(out))
        self.check()

    def bit_left(self, index, destination):
        require(self.fields[index][1] == 2 and destination <= index, 'Bad one-bit left move')
        A = prod(n for _, n in self.fields[:destination])
        B = prod(n for _, n in self.fields[destination:index])
        R = prod(n for _, n in self.fields[index+1:])
        out = []
        for a in range(A):
            zero, one = [], []
            start = a*B*2*R
            # Only forward complete-R reads and two sequential output tapes.
            for b in range(B):
                zero.extend(self.data[start+(2*b)*R:start+(2*b+1)*R])
                one.extend(self.data[start+(2*b+1)*R:start+(2*b+2)*R])
            out.extend(zero)
            out.extend(one)
        bit = self.fields.pop(index)
        self.fields.insert(destination, bit)
        self.data = out
        self.stats['binary_split_passes'] += 1
        self.stats['complete_block_records'] += 2*len(out)
        self.check()

    def bit_right(self, index, destination):
        require(self.fields[index][1] == 2 and destination >= index, 'Bad one-bit right move')
        A = prod(n for _, n in self.fields[:index])
        B = prod(n for _, n in self.fields[index+1:destination+1])
        R = prod(n for _, n in self.fields[destination+1:])
        out = []
        for a in range(A):
            start = a*2*B*R
            zero = self.data[start:start+B*R]
            one = self.data[start+B*R:start+2*B*R]
            # Two complete halves, each with an increasing head, interleaved.
            for b in range(B):
                out.extend(zero[b*R:(b+1)*R])
                out.extend(one[b*R:(b+1)*R])
        bit = self.fields.pop(index)
        self.fields.insert(destination, bit)
        self.data = out
        self.stats['binary_interleave_passes'] += 1
        self.stats['complete_block_records'] += 2*len(out)
        self.check()

    def move(self, name, destination):
        index = self.index(name)
        if index == destination:
            return
        original_size = self.fields[index][1]
        padded = 1 << (original_size-1).bit_length()
        if padded != original_size:
            self.resize(name, padded)
            self.stats['current_field_only_paddings'] += 1
        bits = padded.bit_length()-1
        names = [f'{name}:bit:{j}' for j in range(bits)]
        self.fields[index:index+1] = [(n, 2) for n in names]
        if destination < index:
            for j, bit in enumerate(names):
                self.bit_left(self.index(bit), destination+j)
        else:
            crossed = self.fields[index+bits:index+bits+(destination-index)]
            for bit in reversed(names):
                end = self.index(crossed[-1][0]) if crossed else self.index(bit)
                self.bit_right(self.index(bit), end)
        if bits:
            location = self.index(names[0])
            require([n for n, _ in self.fields[location:location+bits]] == names,
                    'Small-field significance order changed')
            self.fields[location:location+bits] = [(name, padded)]
        else:
            self.fields.insert(destination, (name, 1))
        if padded != original_size:
            self.resize(name, original_size, verify_zero=True)
        self.stats['small_field_moves'] += 1
        self.check()

    def fuse(self, first, second, new_name):
        i = self.index(first)
        require(self.fields[i+1][0] == second, 'Fusing nonadjacent fields')
        n = self.fields[i][1]*self.fields[i+1][1]
        self.fields[i:i+2] = [(new_name, n)]
        self.check()

    def split(self, name, new_fields):
        i = self.index(name)
        require(prod(n for _, n in new_fields) == self.fields[i][1], 'Incomplete field split')
        self.fields[i:i+1] = new_fields
        self.check()

    def large_layout(self, target_fields, axis_widths, L):
        """Named-bit permutation model of the separately accepted router."""
        old_names = [name for name, _ in self.fields]
        target_names = [name for name, _ in target_fields]
        old_sizes = [n for _, n in self.fields]
        new_sizes = [n for _, n in target_fields]
        out = [None]*len(self.data)
        filled = [False]*len(self.data)
        for rank, value in enumerate(self.data):
            old = dict(zip(old_names, decode(rank, old_sizes)))
            new = {'P': old['P'], 'R': old['R']}
            for axis in range(len(axis_widths)):
                if f'J{axis}' in old:
                    new[f'K{axis}'], new[f'I{axis}'] = divmod(old[f'J{axis}'], L)
                else:
                    new[f'J{axis}'] = old[f'K{axis}']*L+old[f'I{axis}']
            address = [new[name] for name in target_names]
            location = encode(address, new_sizes)
            require(not filled[location], 'Gathering duplicates an address')
            filled[location] = True
            out[location] = value
        require(all(filled), 'Gathering leaves an address hole')
        self.fields, self.data = list(target_fields), out
        self.check()

    def emit_axis_windows(self, axis, original_s, physical_size, L, halo, source_mode):
        first, local = f'K{axis}', f'I{axis}'
        self.move(local, self.index(first)+1)
        fused = f'J{axis}'
        self.fuse(first, local, fused)
        i = self.index(fused)
        require(self.fields[i][1] == physical_size, 'Unexpected axis size before halo pass')
        A = prod(n for _, n in self.fields[:i])
        R = prod(n for _, n in self.fields[i+1:])
        desired = windows(original_s, physical_size, L, halo) if source_mode else [
            (k*L-halo, (k+1)*L+halo) for k in range(physical_size//L)]
        output_size = L if source_mode else L+2*halo
        period = original_s if source_mode else physical_size
        out = []
        for a in range(A):
            start = a*physical_size*R
            row = [self.data[start+j*R:start+(j+1)*R] for j in range(period)]
            self.stats['prefix_suffix_scan_records'] += 3*period*R
            # Boundary buffers are complete blocks. The extended source is
            # then visited monotonically; no source-table lookup per window.
            lo, hi = desired[0][0], desired[-1][1]
            require(lo > -period and hi < 2*period, 'More than bounded periodic scans needed')
            extended = row[period+lo:] if lo < 0 else []
            extended += row
            if hi > period:
                extended += row[:hi-period]
            base = min(lo, 0)
            pointer = desired[0][0]-base
            overlaps = [[], []]
            previous_end = desired[0][0]
            for k, (left, right) in enumerate(desired):
                require(left < right and right-left <= output_size, 'Halo does not fit local field')
                old_overlap = overlaps[k % 2] if k else []
                require(not k or len(old_overlap) == previous_end-left, 'Bad saved overlap length')
                current = list(old_overlap)
                next_tail = desired[k+1][0] if k+1 < len(desired) else right
                require(not k or next_tail >= previous_end,
                        'Next overlap would require shifting the previous buffer')
                saved = []
                position = previous_end if k else left
                while position < right:
                    block = extended[pointer]
                    pointer += 1
                    current.append(block)
                    self.stats['monotone_new_records'] += R
                    if position >= next_tail:
                        saved.append(block)
                        self.stats['mirrored_overlap_records'] += R
                    position += 1
                require(len(current) == right-left, 'Monotone window length mismatch')
                expected = [row[j % period] for j in range(left, right)]
                require(current == expected, 'Alternating overlap tapes emitted wrong periodic window')
                for block in current:
                    out.extend(block)
                out.extend([None]*((output_size-len(current))*R))
                overlaps[(k+1) % 2] = saved
                previous_end = right
                self.stats['halo_rows'] += 1
        self.fields[i:i+1] = [(first, physical_size//L), (local, output_size)]
        self.data = out
        self.stats['maximum_persistent_volume'] = max(self.stats['maximum_persistent_volume'], len(out))
        self.check()
        desired_names = ['P']+[f'K{j}' for j in range(self.axes)]+[f'I{j}' for j in range(self.axes)]+['R']
        self.move(local, desired_names.index(local))

    def selector(self, axis, s, t, L, halo, compress):
        local = f'I{axis}'
        self.move(local, len(self.fields)-2)
        i = self.index(local)
        require(self.fields[-1][0] == 'R', 'Line coefficient field lost')
        R = self.fields[-1][1]
        M = self.fields[i][1]
        prefix_fields = self.fields[:i]
        prefix_sizes = [n for _, n in prefix_fields]
        out = []
        visited = []
        page = None
        for prefix in range(prod(prefix_sizes)):
            address = dict(zip((name for name, _ in prefix_fields), decode(prefix, prefix_sizes)))
            k = address[f'K{axis}']
            page_key = tuple(address[name] for name, _ in prefix_fields[:self.index(f'K{axis}')])+ (k,)
            if page_key != page:
                require(page is None or page_key > page, 'Catalogue access is not sequential')
                page = page_key
                visited.append(page_key)
                self.stats['factor_page_visits'] += 1
            row = self.data[prefix*M*R:(prefix+1)*M*R]
            if compress:
                left, right = k*L*s//t, (k+1)*L*s//t
                positions = [nearest(s,t,j)-(k*L-halo) for j in range(left,right)]
            else:
                begin = windows(s,t,L,halo)[k][0]
                positions = [((k*L+r)*s//t)-begin for r in range(L)]
            require(positions == sorted(positions) and all(0 <= q < M for q in positions),
                    'Local line selection leaves supplied halo or breaks order')
            for q in positions:
                out.extend(row[q*R:(q+1)*R])
            out.extend([None]*((L-len(positions))*R))
            self.stats['line_maps'] += 1
        self.fields[i] = local, L
        self.data = out
        self.check()
        canonical = ['P']+[f'K{j}' for j in range(self.axes)]+[f'I{j}' for j in range(self.axes)]+['R']
        self.move(local, canonical.index(local))

    def assemble_source_axis(self, axis, s, t, L):
        first, local, fused = f'K{axis}', f'I{axis}', f'J{axis}'
        self.move(local, self.index(first)+1)
        self.fuse(first, local, fused)
        i = self.index(fused)
        A = prod(n for _, n in self.fields[:i])
        R = prod(n for _, n in self.fields[i+1:])
        out = []
        for a in range(A):
            begin = a*t*R
            total = 0
            for k in range(t//L):
                length = (k+1)*L*s//t-k*L*s//t
                start = begin+k*L*R
                out.extend(self.data[start:start+length*R])
                require(all(x is None for x in self.data[start+length*R:start+L*R]),
                        'Final assembly would discard noncore values')
                total += length
            require(total == s, 'Fractional source cores do not cover source period')
            out.extend([None]*((t-s)*R))
        self.data = out
        self.split(fused, [(first,t//L),(local,L)])
        canonical = ['P']+[f'K{j}' for j in range(self.axes)]+[f'I{j}' for j in range(self.axes)]+['R']
        self.move(local, canonical.index(local))


def fixture(sizes, targets, L, halo, P, R, compress):
    D = len(sizes)
    initial_sizes = targets if compress else sizes
    fields = [('P',P)]+[(f'J{i}',n) for i,n in enumerate(initial_sizes)]+[('R',R)]
    data = list(product(range(P), *(range(n) for n in initial_sizes), range(R)))
    stream = Stream(fields,data)
    stream.axes = D
    if not compress:
        for i,t in enumerate(targets):
            stream.resize(f'J{i}',t)
    dyadic_fields = [('P',P)]+[(f'J{i}',n) for i,n in enumerate(targets)]+[('R',R)]
    inner = [('P',P)]+[(f'K{i}',n//L) for i,n in enumerate(targets)]+[(f'I{i}',L) for i in range(D)]+[('R',R)]
    stream.large_layout(inner, targets, L)
    original_volume = P*prod(targets)*R
    for i,(s,t) in enumerate(zip(sizes,targets)):
        stream.emit_axis_windows(i,s,t,L,halo,source_mode=not compress)
        if not compress:
            require(len(stream.data) == original_volume, 'Source halo padding changes target volume')
    if compress:
        require(len(stream.data) < 2*original_volume, 'All target halos exceed volume bound')
    for i,(s,t) in enumerate(zip(sizes,targets)):
        stream.selector(i,s,t,L,halo,compress)
    if compress:
        for i,(s,t) in enumerate(zip(sizes,targets)):
            stream.assemble_source_axis(i,s,t,L)
    stream.large_layout(dyadic_fields, targets, L)
    if compress:
        for i,s in enumerate(sizes):
            stream.resize(f'J{i}',s,verify_zero=True)
    output_sizes = sizes if compress else targets
    checked = 0
    for rank,value in enumerate(stream.data):
        address = decode(rank,[P,*output_sizes,R])
        expect = [address[0]]
        for i,j in enumerate(address[1:-1]):
            expect.append(nearest(sizes[i],targets[i],j) % targets[i] if compress else j*sizes[i]//targets[i])
        expect.append(address[-1])
        require(value == tuple(expect), 'Complete bulk route/early crop/final ordered assembly differs')
        checked += 1
    return dict(sizes=sizes,targets=targets,L=L,halo=halo,P=P,R=R,
                compression=compress,exact_output_records=checked,
                target_volume=original_volume,stats=stream.stats)


def algebra():
    checks = 0
    counterexample = dict(s=20,w=3,interval=[1,20],edge=[1,19],
                          cyclic_distance=2,unwrapped_distance=18)
    # Exact worst-sign cyclic Neumann fixtures, independently constructed.
    for s,w,g in ((17,1,Q(1,16)),(23,2,Q(1,8)),(29,3,Q(1,32))):
        F = [[Q(0) for _ in range(s)] for _ in range(s)]
        for i in range(s):
            for step in range(1,w+1):
                F[i][(i+step)%s] = -(1-g)/(2*w)
                F[i][(i-step)%s] = -(1-g)/(2*w)
        for start,J in product((0,s-2,s-5),(1,2)):
            length = 2*J*w+3
            if s-length <= w:
                continue
            ii = [(start+j)%s for j in range(length)]
            local = [[F[i][j] for j in ii] for i in ii]
            for core in (J*w,J*w+1):
                pg = [Q(int(j==ii[core])) for j in range(s)]
                pl = [Q(int(j==core)) for j in range(length)]
                for degree in range(J):
                    embedded = [Q(0)]*s
                    for index,value in zip(ii,pl):embedded[index] = value
                    require(embedded == pg, 'Independent wrapped short-path locality failed')
                    checks += s
                    pg = [sum((pg[k]*F[k][j] for k in range(s)),Q(0)) for j in range(s)]
                    pl = [sum((pl[k]*local[k][j] for k in range(length)),Q(0)) for j in range(length)]
    cutoff_controls = []
    for p in (101,127,256,1023):
        L = 1 << (p**8-1).bit_length()
        A = 4096*p**3
        d = p
        require(L >= 64*d*A, 'Near-one source halo headroom fails')
        require((L+2*A)**d < 2*L**d, 'Target halo product exceeds two')
        require(A//2-3 > 512*p**3, 'Neumann halo shorter than accepted core distance')
        require(32*p < 2**(16*p), 'Neumann tail does not fit accepted accuracy')
        cutoff_controls.append(dict(p=p,L=L,A=A,d=d,all_exact=True))
    return dict(exact_short_path_entries=checks,
                complement_gap_counterexample=counterexample,cutoffs=cutoff_controls)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'Use a fresh output path')
    start = time.monotonic()
    cases = []
    for sizes,targets,L,halo,P,R in [
        ([27,28],[32,32],16,1,3,2),
        ([55,57],[64,64],32,1,1,3),
        ([27,27,27],[32,32,32],16,1,1,1)]:
        require(Q(prod(targets),prod(sizes)) < 2, 'Fixture violates source/target capacity')
        for compress in (False,True):
            cases.append(fixture(sizes,targets,L,halo,P,R,compress))
    result = dict(status='PASS independent ordered bulk-resampling provenance and locality controls',
        generated_at=datetime.now(timezone.utc).isoformat(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        cases=cases,algebra=algebra(),seconds=time.monotonic()-start,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        scope=['No producer import','Sequential complete-block small-field and halo controls',
               'Large gather models previously reviewed coordinate-router contract',
               'Selector line maps test layout/provenance; Gaussian precision uses separate reviewed analytic proof',
               'Small fixtures satisfy actual halo fit/capacity/overlap tests, not asymptotic p^8 halo constants'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS',sum(c['exact_output_records'] for c in cases),'complete output records;',
          len(cases),'joined tensor schedules',flush=True)


if __name__ == '__main__':
    main()
