"""Callable stage-private120-coordinate bank address template.

The caller supplies the freshly admitted actual helper role families and gauge
chart IDs. This module owns no paths, global frame registry or source loading.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from collections import Counter


class BankPlan:
    m, h, stages, replicas, v = 120, 24, 5, 60, 1760
    patterns = ((tuple([11]*8+[4]*8),360),
                (tuple([4]*30),4304),
                (tuple([6]*20),39),
                (tuple([12]*10),108),
                (tuple([24]*5),171696))

    active = ((0,1),(1,0),(0,1),(3,2),(2,3))

    def __init__(self, families, gauge_frames, helper_roles=None):
        self.families = {r:tuple(rows) for r,rows in families.items() if rows}
        assert {r:len(rows) for r,rows in self.families.items()} == {4:2200,6:13,11:48,12:18,24:14308}
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
        assert (self.banks_per_stage,self.data_families,self.live_families)==(176507,422400,1304935)
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

        frame=None denotes identity B=I24. The caller resolves other IDs in
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
        Boundary phases occur after all60 replicas of that stage finish.
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
