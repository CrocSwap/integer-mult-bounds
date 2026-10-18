"""Peel the last n-m head atoms using original incoming weight offsets."""
from cardinal_counts import Count
from layout import Layout
from numeric import Geometry
import packet_engine
from plan import Plan, Request
from trace import primitive
from words import need


def events(geometry,parent_size):
    raw,index=geometry.raw,geometry.index
    coordinate=raw.times_small(geometry.columns,geometry.plan.dimension)
    total=raw.times_small(parent_size,2)
    last=raw.subtract_exact(total,geometry.one)
    index.free(total)
    try:
        while raw.compare(coordinate,parent_size)<0:
            right=raw.subtract_exact(last,coordinate)
            try:
                for stage in range(8):
                    a,b=index.copy(coordinate),index.copy(right)
                    if stage in (0,2,4,6):yield from primitive("atom_swap",a,b,None,geometry)
                    elif stage==7:
                        index.free(a);yield from primitive("sign",b,None,None,geometry)
                    else:
                        request=Request("incoming",index.copy(coordinate),negative_inverse=stage==3)
                        yield from primitive("add",b,a,request,geometry)
            finally:index.free(right)
            raw.increment_in_place(coordinate)
    finally:index.free_many(coordinate,last)


def run(source,context,indices,parent_size,depth,program,old_directory,old_count,
        fresh_rows,before,gap,suffix,incoming):
    columns=indices.literal(1)
    geometry=Geometry(Plan(context.dimension,1,True,()),indices,columns,depth,0,program)
    leading=Count.product(fresh_rows,before)
    layout=Layout(geometry,parent_size,context.ring,context.q,leading,gap,suffix,embedded=False)
    try:
        return packet_engine.run(source,events(geometry,parent_size),layout,old_directory,
                                 old_count,depth,incoming.coefficient)
    finally:
        layout.close();leading.close();geometry.close();indices.free(columns)
