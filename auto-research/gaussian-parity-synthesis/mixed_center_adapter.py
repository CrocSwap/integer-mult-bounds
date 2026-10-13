"""Bridge canonical Gaussian dyadics to the certified common-grid producer.

All producer ports must share the same scalar phase frame. grid_tag describes
the promised common input grid, not an inferred promise about raw dirty ports.
The complete producer guard is retained; its extra pass is paid reference work.
"""
from pi_exact import Gaussian
from verify_mixed_center_image import checked_fused_delta, numeric_roots


def producer_at_grid(graph, values, *, grid_tag):
    if len(values)!=graph['v']:
        raise ValueError('wrong source count')
    numerators=[z.aligned(grid_tag) for z in values]
    return [Gaussian(a,b,grid_tag) for a,b in numeric_roots(graph,numerators)]


def decode_at_grid(graph,before,after,roles,triples,h,d,*,grid_tag):
    if type(grid_tag) is not int or grid_tag<0:
        raise ValueError('nonnegative common pi grid required')
    old=[z.aligned(grid_tag) for z in before]
    new=[z.aligned(grid_tag) for z in after]
    result=checked_fused_delta(graph,old,new,roles,triples,h,d)
    return [Gaussian(a,b,grid_tag) for a,b in result]
