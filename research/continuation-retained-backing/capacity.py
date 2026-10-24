"""Source-specific retained extents of the physical continuation bank.

Checker arithmetic, not a physical allocator. Local peaks must include erased
interiors and delivered outputs. A virtual empty child counts push delimiters.
"""
from dataclasses import dataclass


def need(ok,message):
    if not ok:raise ValueError(message)


@dataclass(frozen=True)
class Cut:
    sizes: tuple
    heads: tuple
    descriptor: int
    child: object


@dataclass(frozen=True)
class Node:
    peaks: tuple
    descriptor_peak: int
    cuts: tuple = ()
    output: int = 0


def extents(root,k):
    """Return payload k-vector, control, descriptor and relay written extents."""
    payload=[0]*k;control=descriptor=relay=0
    def visit(node,offset,stack):
        nonlocal control,descriptor,relay
        need(len(node.peaks)==k and all(type(x) is int and x>=0 for x in node.peaks),'Local nonnegative role peaks')
        need(type(node.descriptor_peak) is int and node.descriptor_peak>=0,'Descriptor interior peak')
        need(type(node.output) is int and 0<=node.output<=max(node.peaks,default=0),'Output inside local peak')
        payload[:]=[max(old,start+peak) for old,start,peak in zip(payload,offset,node.peaks)]
        control=max(control,stack);descriptor=max(descriptor,node.descriptor_peak)
        for cut in node.cuts:
            need(len(cut.sizes)==len(cut.heads)==k,'Complete parked role vectors')
            need(all(type(s) is int and type(h) is int and 0<=h<=s<=a
                     for s,h,a in zip(cut.sizes,cut.heads,node.peaks)),'Parked extents and heads within local peaks')
            need(type(cut.descriptor) is int and 0<=cut.descriptor<=node.descriptor_peak,'Parked descriptor within local peak')
            following=tuple(o+s+1 for o,s in zip(offset,cut.sizes))
            frame=sum(cut.heads)+2*k+cut.descriptor+3
            visit(cut.child,following,stack+frame)
            relay=max(relay,cut.child.output)
    visit(root,(0,)*k,0)
    return tuple(payload)+(control,descriptor,relay)


def capacities(origins,entry,extra):
    need(len(origins)==len(entry)==len(extra),'All k+3 tape coordinates')
    need(all(type(b) is int and type(x) is int and b>=1 and x>=b for b,x in zip(origins,entry)),'Entry backing includes initial marker/prefix')
    need(all(type(x) is int and x>=0 for x in extra),'Nonnegative written extents')
    return tuple(max(old,base+growth) for base,old,growth in zip(origins,entry,extra))


def coarse_grant(k,entry_total,volume,depth,descriptor_path,descriptor_max,output_max):
    """Sufficient history envelope; volume includes each node's local peaks."""
    need(type(k) is int and k>=1,'Fixed positive role count')
    need(all(type(x) is int and x>=0 for x in (entry_total,volume,depth,descriptor_path,descriptor_max,output_max)),
         'Nonnegative historical envelopes')
    return entry_total+(k+1)*volume+(3*k+3)*depth+descriptor_path+descriptor_max+output_max


def compact_peak(address_bits,record_bits):
    need(type(address_bits) is int and address_bits>=0 and type(record_bits) is int and record_bits>=1,
         'Compact rectangle bit widths')
    return (1<<address_bits)*(address_bits+record_bits)
