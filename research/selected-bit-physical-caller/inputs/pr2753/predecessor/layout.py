"""Binary two-bank layout with an independent complete intervening gap."""
from cardinal_counts import Count, positive
from cardinality import multiply_atom_power
from words import need


class Layout:
    def __init__(self,geometry,parent_size,ring,q,before,gap,suffix,embedded=True):
        for value in (before,gap,suffix):positive(value)
        self.geometry,self.ring,self.q=geometry,ring,q
        self.before,self.gap,self.suffix=before,gap,suffix
        self.parent_size,self.embedded=parent_size,embedded
        self.core=geometry.raw.times_small(geometry.columns,geometry.plan.dimension)
        remaining=geometry.raw.subtract_exact(parent_size,self.core)
        self.extra=geometry.raw.times_small(remaining,2)
        geometry.index.free(remaining)
        self.total=geometry.raw.times_small(parent_size,2)

    def physical(self,position):
        if not self.embedded or self.geometry.raw.compare(position,self.core)<0:
            return self.geometry.index.copy(position)
        return self.geometry.plus(position,self.extra)

    def extents(self,first,second=None):
        g=self.geometry
        a=self.physical(first)
        b=self.physical(second) if second is not None else None
        if b is not None:need(g.raw.compare(a,b)<0,"ordered physical body atoms")
        last=a if b is None else b
        pre,tail=Count(self.before),Count(self.suffix)
        multiply_atom_power(pre,a,self.ring,self.q)
        after=g.raw.subtract_exact(self.total,last)
        count=g.raw.subtract_exact(after,g.one)
        multiply_atom_power(tail,count,self.ring,self.q)
        g.index.free_many(after,count)
        if g.raw.compare(a,self.parent_size)>=0:
            enlarged=Count.product(pre,self.gap);pre.close();pre=enlarged
        if g.raw.compare(last,self.parent_size)<0:
            enlarged=Count.product(tail,self.gap);tail.close();tail=enlarged
        values=[pre]
        if b is not None:
            distance=g.raw.subtract_exact(b,a)
            count=g.raw.subtract_exact(distance,g.one)
            middle=Count.literal(1)
            multiply_atom_power(middle,count,self.ring,self.q)
            if g.raw.compare(a,self.parent_size)<0 and g.raw.compare(b,self.parent_size)>=0:
                enlarged=Count.product(middle,self.gap);middle.close();middle=enlarged
            values.append(middle)
            g.index.free_many(distance,count,b)
        values.append(tail);g.index.free(a)
        result=[value.marginal() for value in values]
        for value in values:value.close()
        return result

    def fibre(self):
        value=Count.product(self.before,self.gap)
        multiply_atom_power(value,self.total,self.ring,self.q)
        result=Count.product(value,self.suffix)
        value.close()
        return result

    def close(self):
        self.geometry.index.free_many(self.core,self.extra,self.total)
