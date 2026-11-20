"""Address the compact436 fixed program by its source labels and residual cursor."""
from bisect import bisect_right
from functools import lru_cache


class RadixCounts:
    """Skip all smaller next residues using the retained constraint counts."""

    def before(self, state, reduced, count, places):
        total=count*self.q**places
        if state.inconsistent:
            return total
        _,rhs,pivot=reduced
        dim=len(state.rows)-len(state.basis)
        if pivot is not None:
            return total-count*self.q**(dim-1)
        return total-int(rhs<count)*self.q**dim

    def vector_rank(self,rows,vector):
        from low_codes import Constraints
        state=Constraints(rows,self.q)
        rank=0
        for column,value in enumerate(vector):
            reduced=state.next(column)
            rank+=self.before(state,reduced,value,self.dimension-column-1)
            state.choose(reduced,value)
        if not state.inconsistent:
            raise ValueError("dependent GL row")
        return rank

    def vector_unrank(self,rows,rank):
        from low_codes import Constraints
        state=Constraints(rows,self.q)
        vector=[]
        for column in range(self.dimension):
            reduced = state.next(column)
            _, rhs, pivot = reduced
            extent = self.q ** (self.dimension - column - 1)
            dimension = len(rows) - len(state.basis)
            if state.inconsistent:
                low, rank = divmod(rank, extent)
            elif pivot is not None:
                low, rank = divmod(rank, extent - self.q ** (dimension - 1))
            else:
                # Exactly the residue rhs has a smaller completion count.
                prefix = rhs * extent
                at_pivot = extent - self.q ** dimension
                if rank < prefix:
                    low, rank = divmod(rank, extent)
                elif rank < prefix + at_pivot:
                    low, rank = rhs, rank - prefix
                else:
                    skip, rank = divmod(rank - prefix - at_pivot, extent)
                    low = rhs + 1 + skip
            if not 0 <= low < self.q:
                raise ValueError("GL row ordinal exceeds its completion interval")
            state.choose(reduced,low)
            vector.append(low)
        if rank or not state.inconsistent:
            raise ValueError("GL row ordinal exceeds its exact completion count")
        return tuple(vector)


class BoundedSpecifications:
    """Hold four compiled low specifications and four associated source plans."""

    def __missing__(self, code):
        if len(self) >= 4:
            del self[next(iter(self))]
        return super().__missing__(code)

    def plan(self, code):
        if code not in self.plans and len(self.plans) >= 4:
            del self.plans[next(iter(self.plans))]
        return super().plan(code)


class CompactProgram:
    """An arbitrary-precision continuation label can skip an entire GL64 interval."""

    def __init__(self,topology,binding):
        from control import LocalState
        self.topology,self.binding=topology,binding
        self.m=binding.codes.dimension
        self.ngl=binding.codes.size
        self.skeletons={}
        self.max_block=4*(2*self.m)**2+4*(2*self.m)+8
        self.residual_size=3*self.max_block+2
        self.bounds=[1]
        self.staged_roles=0
        for event in topology.schedule:
            kind=event['kind']
            if kind=='local_cover_sweep':
                stage=event['stage']
                call=topology.call(stage,0)
                count=len(call.owners)
                self.staged_roles=max(self.staged_roles,count+1)
                skeleton=[('gather_owner',i) for i in range(count)]
                state=LocalState(call)
                for pos,item in enumerate(call.events):
                    op,role=state.accept(pos)
                    target=('stage',role)
                    if op==0:
                        skeleton.append(('residual',target,call.requests[pos],True))
                    elif op==1:
                        skeleton.append(('xor',target,('stage',item[2])))
                    elif op==2:
                        skeleton.extend((('copy',target,'copy_source'),('residual','copy_source',call.requests[pos],True),('move','copy_source',('stage',state.private))))
                    else:
                        skeleton.append(('clear',('stage',state.private)))
                state.finish()
                skeleton.extend(('scatter_owner',i) for i in range(count))
                skeleton.extend(('clear',('stage',i)) for i in range(count+1))
                starts=[0]
                for entry in skeleton:
                    starts.append(starts[-1]+(self.residual_size if entry[0]=='residual' else 1))
                self.skeletons[stage]=skeleton,starts
                extent=topology.replicas*self.ngl*starts[-1]
            elif kind=='idle':
                extent=topology.replicas*len(topology.idles[event['idx']])*self.ngl*(3+self.residual_size)
            elif kind=='bridge':
                if event['coefficient'] not in (-1,1):
                    raise ValueError('native Boolean bridge coefficient')
                extent=topology.replicas*topology.ports*2
            elif kind=='exchange':
                extent=topology.replicas*topology.pairs*topology.ports
            else:
                raise ValueError('unknown fixed source event')
            self.bounds.append(self.bounds[-1]+extent+1)
        self.extent=self.bounds[-1]+1
        self.low=lru_cache(2)(binding.codes.unrank)
        self.definition=lru_cache(2)(binding.residual)
        self.call=lru_cache(2)(topology.call)

    def residual(self,pc,sub,entry,low):
        from residual_blocks import Cursor
        _,role,identifier,common=entry
        job=self.definition(identifier,common,low,0)
        end=self.residual_size-1
        if sub==0:
            if job.axis is None and Cursor(job.plan).done:
                return ('residual_begin',role,job),pc+end
            return ('residual_begin',role,job),pc+1
        if sub==end:
            return ('residual_end',role,job),pc+1
        if job.axis is not None:
            if sub!=1:
                raise ValueError('invalid reduced-axis block label')
            return ('block',job,('axis',job.axis,0)),pc+end-sub
        pos,stage=divmod(sub-1,3)
        cursor=Cursor(job.plan,pos,stage)
        if cursor.bound>self.max_block:
            raise ValueError('fixed Gauss elimination command bound')
        block=cursor.take()
        nxt=end if cursor.done else 1+3*cursor.position+cursor.stage
        return ('block',job,block),pc+nxt-sub

    def step(self,pc):
        from driver import compile_owner
        topo=self.topology
        if not 0<=pc<self.extent:
            raise ValueError('invalid compact continuation')
        if pc==0:
            return ('node',),1
        if pc==self.extent-1:
            return ('return',),self.extent
        j=bisect_right(self.bounds,pc)-1
        at=pc-self.bounds[j]
        event=topo.schedule[j]
        kind=event['kind']
        if pc+1==self.bounds[j+1]:
            return ('checkpoint',kind,event.get('stage',event.get('idx',-1))),pc+1
        if kind=='local_cover_sweep':
            stage=event['stage']
            entries,starts=self.skeletons[stage]
            packet,inside=divmod(at,starts[-1])
            replica,ordinal=divmod(packet,self.ngl)
            slot=bisect_right(starts,inside)-1
            entry=entries[slot]
            if entry[0]=='residual':
                return self.residual(pc,inside-starts[slot],entry,self.low(ordinal))
            if entry[0] in ('gather_owner','scatter_owner'):
                low=self.low(ordinal)
                role=entry[1]
                owner=self.call(stage,replica).owners[role]
                chart=topo.matrix(owner.chart)
                # compile_owner's unbounded low-label cache is not source data.
                native,forward,backward=compile_owner.__wrapped__(chart,low,self.binding.codes)
                if entry[0]=='gather_owner':
                    return ('gather_route',('stage',role),owner.family,native,forward),pc+1
                return ('route_scatter',('stage',role),owner.family,native,backward),pc+1
            return entry,pc+1
        if kind=='idle':
            ids=topo.idles[event['idx']]
            packet,sub=divmod(at,self.residual_size+3)
            owner,ordinal=divmod(packet,self.ngl)
            replica,site=divmod(owner,len(ids))
            identifier=ids[site]
            low=self.low(ordinal)
            family=topo.idle_family(identifier,replica)
            if sub==0:
                return ('gather','idle',family,low),pc+1
            if sub<=self.residual_size:
                return self.residual(pc,sub-1,('residual','idle',identifier,False),low)
            if sub==self.residual_size+1:
                return ('scatter','idle',family,low),pc+1
            return ('clear','idle'),pc+1
        if kind=='bridge':
            row,side=divmod(at,2)
            replica,port=divmod(row,topo.ports)
            target,source=event['dst'],event['src']
            if side:
                target,source=source,target
            return ('family_xor',topo.family(replica,target,side,port),topo.family(replica,source,side,port)),pc+1
        temp,port=divmod(at,topo.ports)
        replica,pair=divmod(temp,topo.pairs)
        return ('exchange',topo.family(replica,pair,0,port),topo.family(replica,pair,1,port)),pc+1
