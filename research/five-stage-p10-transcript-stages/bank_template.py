"""Callable stage-private m-coordinate bank address template (m = 5h; 120 at p = 12, 100 at p = 10).

The caller supplies the freshly admitted actual helper role families and gauge
chart IDs. This module owns no paths, global frame registry or source loading.
Prepared with OpenAI Codex assistance; Apache-2.0.
p = 10 port (DreamingOfClouds, Anthropic Claude assistance): m, h, v from the cube size; the fixed gen5 bank
patterns are replaced by tile(), an exact zero-padding tiling of the actual residual blocks into width-m banks
(every pattern sums to m and every block is used exactly once, as before); the counts are pinned by bank_check.
"""
from collections import Counter
from word_pins import expect,shape


def tile(blocks, m):
    """Exact tiling of {width: number of blocks} into banks of total width m, as ((widths, banks), ...).

    A width dividing m fills pure banks. A width w not dividing m is mixed with a filler width f dividing m:
    banks w^a f^b with a maximal (w*a + f*b = m), then at most one bank w^r f^t for the remainder r. Fillers
    are tried in a fixed order (most blocks first) with backtracking until every pure width also divides out.
    Fails (AssertionError) unless every block is used and every bank is full; there is no padding."""
    blocks = {w: n for w, n in blocks.items() if n}
    assert all(0 < w <= m for w in blocks)
    mixed = sorted(x for x in blocks if m % x)

    def search(i, left, out):
        if i == len(mixed):
            if any(left[w] % (m // w) for w in left): return None
            return out + [(tuple([w]*(m // w)), left[w]//(m // w)) for w in sorted(left) if left[w]]
        w = mixed[i]; n = blocks[w]
        for f in sorted(left, key=lambda x: (-left[x], x)):
            a = next((a for a in range(m // w, 0, -1) if (m - w*a) % f == 0), None)
            if a is None: continue
            b = (m - w*a)//f; q, r = divmod(n, a)
            if r and (m - w*r) % f: continue
            t = (m - w*r)//f if r else 0
            if q*b + t > left[f]: continue
            rest = dict(left); rest[f] -= q*b + t
            found = search(i + 1, rest, out + ([(tuple([w]*a + [f]*b), q)] if q else []) + ([(tuple([w]*r + [f]*t), 1)] if r else []))
            if found is not None: return found
        return None
    out = search(0, {w: n for w, n in blocks.items() if not m % w}, [])
    if out is None: out = economy_tile(blocks, m)
    assert all(sum(widths) == m and count > 0 for widths, count in out)
    used = Counter()
    for widths, count in out:
        for x in widths: used[x] += count
    assert used == Counter(blocks), 'every block used exactly once'
    return tuple(out)


def economy_tile(blocks, m):
    """Exact zero-padding tiling used when the filler search of tile() runs out of filler blocks (the kernel pivots
    and early restorations of the stage stack add many residual widths that do not divide m; the PR #299 analogue at
    p = 12 was the (r^4, 24, 4^(24-r)) re-tiling). The fillers are the two most numerous widths dividing m (here the
    full helper width h and the rank-4 entrance residual). Each other width w, in decreasing order, gets the bank
    w^a F^c f^b (w*a + F*c + f*b = m) that spends the fewest narrow fillers f per w block (then the largest a), plus
    at most one bank w^r F^c' f^b' for the remainder r = n mod a. The leftover fillers fill pure banks F^(m/F),
    f^(m/f) and y residue banks F^j f^k. Every bank sums to m and every block is used exactly once (no padding)."""
    from fractions import Fraction
    blocks = {w: n for w, n in blocks.items() if n}
    div = sorted((w for w in blocks if m % w == 0), key=lambda w: (-blocks[w], w))
    assert len(div) >= 2, ('economy tiling needs two filler widths', blocks)
    F, f = sorted(div[:2], reverse=True)

    def fill(rest):
        """(c, b) with F*c + f*b = rest, c maximal (fewest narrow fillers); None if impossible."""
        return next(((c, (rest - F*c)//f) for c in range(rest//F, -1, -1) if (rest - F*c) % f == 0), None)

    left = {F: blocks[F], f: blocks[f]}; out = []
    for w in sorted((x for x in blocks if x not in (F, f)), reverse=True):
        n = blocks[w]
        opts = [(Fraction(cb[1], a), -a, a, cb) for a in range(m//w, 0, -1) for cb in [fill(m - w*a)] if cb]
        assert opts, ('no bank for width', w)
        _, _, a, (c, b) = min(opts); q, r = divmod(n, a)
        if q: out.append(((w,)*a + (F,)*c + (f,)*b, q)); left[F] -= q*c; left[f] -= q*b
        if r:
            cb = fill(m - w*r); assert cb, ('no remainder bank', w, r)
            out.append(((w,)*r + (F,)*cb[0] + (f,)*cb[1], 1)); left[F] -= cb[0]; left[f] -= cb[1]
    assert left[F] >= 0 and left[f] >= 0, ('fillers exhausted', left)
    pF, pf = m//F, m//f
    for y in range((pF*pf) + 1):
        for j in range(1 if y else 0, pF if y else 1):
            if (m - F*j) % f: continue
            k = (m - F*j)//f; aF, af = left[F] - y*j, left[f] - y*k
            if aF >= 0 and af >= 0 and aF % pF == 0 and af % pf == 0:
                out += ([((F,)*j + (f,)*k, y)] if y else []) + ([((F,)*pF, aF//pF)] if aF else []) + ([((f,)*pf, af//pf)] if af else [])
                return out
    raise AssertionError(('no exact zero-padding tiling', blocks, m))


class BankPlan:
    _shape = shape()
    m, h, stages, replicas, v = _shape['m'], _shape['h'], _shape['stages'], _shape['replicas'], _shape['v']

    active = ((0,1),(1,0),(0,1),(3,2),(2,3))

    def __init__(self, families, gauge_frames, helper_roles=None):
        self.families = {r:tuple(rows) for r,rows in families.items() if rows}
        assert all(0<r<=self.h for r in self.families)
        self.patterns = tile({r:self.replicas*len(rows) for r,rows in self.families.items()}, self.m)
        self.role_index = {}
        for rank,rows in self.families.items():
            assert tuple(sorted(rows)) == rows and len(set(rows)) == len(rows)
            for i,role in enumerate(rows):
                assert role not in self.role_index
                self.role_index[role]=(rank,i)
        self.gauge_frames = dict(gauge_frames)
        assert set(self.gauge_frames) == {role for r,rows in self.families.items() if r<self.h for role in rows}
        self.helper_roles=tuple(sorted(self.role_index) if helper_roles is None else helper_roles)
        assert len(self.helper_roles)==len(self.role_index) and set(self.helper_roles)==set(self.role_index)
        self.local_work=2*self.v+len(self.helper_roles)
        self.banks_per_stage=sum(count for widths,count in self.patterns)
        self.data_families=self.replicas*4*self.v
        self.live_families=self.data_families+self.stages*self.banks_per_stage
        self.work_family=self.live_families
        assert self.banks_per_stage*self.m==self.replicas*sum(r*len(rows) for r,rows in self.families.items()), 'zero padding'
        expect('bank_patterns',self.patterns);expect('banks_per_stage',self.banks_per_stage);expect('literal_stock',self.live_families)
        assert self.data_families==self.replicas*4*self.v
        self.segments={}
        used=Counter();bank_start=0
        for pattern,(widths,count) in enumerate(self.patterns):
            assert sum(widths)==self.m
            for rank in set(widths):
                blocks=tuple(b for b,r in enumerate(widths) if r==rank)
                n=len(blocks)*count
                self.segments.setdefault(rank,[]).append((used[rank],used[rank]+n,pattern,bank_start,blocks))
                used[rank]+=n
            bank_start+=count
        assert used=={r:self.replicas*len(rows) for r,rows in self.families.items()}

    def assignment(self, stage, replica, role):
        """Exact bank family/block for one actual independent helper occurrence."""
        assert 0<=stage<self.stages and 0<=replica<self.replicas
        rank,role_index=self.role_index[role]
        q=role_index*self.replicas+replica
        for lo,hi,pattern,bank_start,blocks in self.segments[rank]:
            if lo<=q<hi:
                bank_offset,within=divmod(q-lo,len(blocks))
                bank=bank_start+bank_offset;block=blocks[within]
                widths=self.patterns[pattern][0]
                return dict(family=self.data_families+stage*self.banks_per_stage+bank,
                            stage_bank=bank,pattern=pattern,block=block,
                            offset=sum(widths[:block]),rank=rank,
                            frame=self.gauge_frames.get(role),scalar=block+1)
        raise AssertionError('unallocated actual helper occurrence')

    def data_family(self, replica, bank, port):
        assert 0<=replica<self.replicas and 0<=bank<4 and 0<=port<self.v
        return (4*replica+bank)*self.v+port

    def normalizer(self, stage, replica, role):
        """Finite exact data for N=scalar Pi embed_stage(B^-1).

        frame=None denotes identity B=I_h. The caller resolves other IDs in
        its freshly admitted frame registry/charts. inverse_chart remains an
        exact rational factor program; no floating matrix is consumed.
        """
        a=self.assignment(stage,replica,role)
        original=tuple(range(self.h*stage,self.h*stage+a['rank']))
        target=tuple(range(a['offset'],a['offset']+a['rank']))
        src=original+tuple(j for j in range(self.m) if j not in original)
        dst=target+tuple(j for j in range(self.m) if j not in target)
        pi=dict(zip(src,dst))
        assert set(pi)==set(pi.values())==set(range(self.m))
        permutation=tuple(pi[j] for j in range(self.m))
        outside=next(j for j in range(self.m) if not self.h*stage<=j<self.h*(stage+1))
        return dict(scalar=a['scalar'],permutation=permutation,
                    inverse_chart_frame=a['frame'],chart_window=stage,
                    outside_column=outside,unit_column_witness=(pi[outside],a['scalar']))

    def address(self, stage, replica, role, cover='d'):
        """Original class d*tau_i routed to the actual bank by N^-1.

        Multiplication order is literal. A consumer must lower the factor
        list right-to-left for inverse N, keeping chart/scalar denominators.
        """
        a=self.assignment(stage,replica,role)
        N=('normalizer',stage,a['pattern'],a['block'],a['frame'])
        return a['family'],('right',cover,('tau',stage),('inverse',N))

    def local_family(self, stage, replica, local):
        """Live family for the admitted local physical register index.

        Family equality does not imply address equality for banked helpers.
        Consumers must use local_address for ADD nonalias/namespace checks.
        """
        assert 0<=stage<self.stages and 0<=replica<self.replicas
        assert 0<=local<=self.local_work
        if local==self.local_work:return self.work_family
        if local<self.v:return self.data_family(replica,self.active[stage][0],local)
        if local<2*self.v:return self.data_family(replica,self.active[stage][1],local-self.v)
        return self.assignment(stage,replica,self.helper_roles[local-2*self.v])['family']

    def local_address(self, stage, replica, local, cover='d'):
        family=self.local_family(stage,replica,local)
        if local==self.local_work:return family,('external_work',0)
        if local<2*self.v:
            route=('class',cover) if stage==0 else ('right',cover,('rho',stage,local%self.v))
            return family,route
        return self.address(stage,replica,self.helper_roles[local-2*self.v],cover)

    def local_from_logical_family(self, stage, family):
        """Invert PR234's logical five-stage family map for one active stage."""
        logical_work=4*self.v+len(self.helper_roles)
        assert 0<=family<=logical_work
        if family==logical_work:return self.local_work
        if family>=4*self.v:return 2*self.v+family-4*self.v
        bank,port=divmod(family,self.v)
        if bank==self.active[stage][0]:return port
        assert bank==self.active[stage][1], 'stage references an inactive data bank'
        return self.v+port

    def map_stage_row(self, stage, replica, row, cover='d'):
        """Lower an unchanged logical8-field MOVE/ADD/COPY/ERASE record.

        All mathematical fields remain unchanged. The two operand slots now
        contain exact (family,route) keys when they denote streams; frame IDs
        in MOVE's old/new slots are not mistaken for stream operands.
        """
        op,a,b,c,f,z,s,rev=row
        assert op in(0,1,2,3) and s==stage and rev==int(stage in(1,3))
        def address(family):
            return self.local_address(stage,replica,self.local_from_logical_family(stage,family),cover)
        physical_a=address(a)
        physical_b=address(b) if op in(1,2) else b
        if op in(1,2):assert physical_a!=physical_b
        return (op,physical_a,physical_b,c,f,z,s,rev)

    def map_boundary_row(self, replica, row, cover='d'):
        """Lower an IDLE/BRIDGE/EXCHANGE with its existing exact projector.

        Boundary projectors already include the checked data-route conjugacy;
        their physical class is d. Independent completion rows must be
        discharged explicitly by the bank endpoint verifier, never skipped
        implicitly by this address mapper.
        """
        op,a,b,c,f,z,s,rev=row
        assert op in(4,5,7), 'only proved bank completion may discharge opcode6'
        def address(family):
            assert 0<=family<4*self.v
            bank,port=divmod(family,self.v)
            return self.data_family(replica,bank,port),('class',cover)
        physical_a=address(a)
        physical_b=address(b) if op in(5,7) else b
        if op in(5,7):assert physical_a!=physical_b
        return (op,physical_a,physical_b,c,f,z,s,rev)

    def phase_schedule(self):
        """Phase-major schedule; every cover class is completed per replica.

        Each emitted stage phase means: for the indicated replica, iterate
        every cover class and execute the entire local scalar telescope.
        Boundary phases occur after all replicas (60) of that stage finish.
        """
        for stage in range(self.stages):
            for replica in range(self.replicas):
                yield ('stage',stage,replica,'all_cover_classes')
            if stage in (1,2,4):
                for replica in range(self.replicas):
                    yield ('idle',stage,replica,'all_cover_classes')
                    yield ('bridge',stage,replica,'all_cover_classes')
        for replica in range(self.replicas):
            yield ('terminal_exchange',replica,'all_cover_classes')
