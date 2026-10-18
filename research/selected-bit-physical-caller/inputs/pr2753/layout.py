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

    def child_extents(self, first, second, width, *, before):
        """Return B', G', S' for two complete, disjoint child chunks.

        Source order is [U][B][head M^n][G][tail M^n][S]. U is returned
        separately to the caller and must not be absorbed in `before`.
        The projected order is [U][B'][chunk M^c][G'][chunk M^c][S'].
        """
        positive(before)
        g = self.geometry
        need(not width.zero(), "positive recursive child width")
        a, b = self.physical(first), self.physical(second)
        a_end, b_end = g.plus(a, width), g.plus(b, width)
        last_offset = g.raw.subtract_exact(width, g.one)
        first_last = g.plus(first, last_offset)
        second_last = g.plus(second, last_offset)
        mapped_first_last = self.physical(first_last)
        mapped_second_last = self.physical(second_last)
        expected_first_last = g.raw.subtract_exact(a_end, g.one)
        expected_second_last = g.raw.subtract_exact(b_end, g.one)
        words = (a,b,a_end,b_end,last_offset,first_last,second_last,
                 mapped_first_last,mapped_second_last,
                 expected_first_last,expected_second_last)
        values = []
        try:
            need(g.raw.compare(a,b)<0 and g.raw.compare(a_end,b)<=0,
                 "ordered disjoint recursive child chunks")
            need(g.raw.compare(b_end,self.total)<=0,
                 "recursive child lies in the complete body")
            need(g.raw.compare(mapped_first_last,expected_first_last)==0
                 and g.raw.compare(mapped_second_last,expected_second_last)==0,
                 "each recursive child chunk is physically contiguous")
            for start,end in ((a,a_end),(b,b_end)):
                need(g.raw.compare(start,self.parent_size)>=0
                     or g.raw.compare(end,self.parent_size)<=0,
                     "recursive chunk does not cross the original gap")

            pre, middle, tail = Count(before), Count.literal(1), Count(self.suffix)
            values = [pre,middle,tail]
            multiply_atom_power(pre,a,self.ring,self.q)
            between = g.raw.subtract_exact(b,a_end)
            after = g.raw.subtract_exact(self.total,b_end)
            try:
                multiply_atom_power(middle,between,self.ring,self.q)
                multiply_atom_power(tail,after,self.ring,self.q)
            finally:
                g.index.free_many(between,after)

            # Exactly one of these three complete spectator regions contains
            # the parent's external gap; it is multiplied in exactly once.
            gap_region = (0 if g.raw.compare(a,self.parent_size)>=0 else
                          2 if g.raw.compare(b_end,self.parent_size)<=0 else 1)
            enlarged = Count.product(values[gap_region],self.gap)
            values[gap_region].close()
            values[gap_region] = enlarged
            return [value.marginal() for value in values]
        finally:
            for value in values:
                value.close()
            g.index.free_many(*words)
