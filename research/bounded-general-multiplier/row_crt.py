"""Use genuine ternary low packets for a row-local CRT in the direct multiplier."""

from io import BytesIO
from itertools import product

from streaming_routes import regular, right_route, type_route
from ternary_frames import covered_factors
from ternary_leaf import run_leaf, select_pivot

TRITS = tuple((i % 3, i // 3) for i in range(9))
LOW_COUNT = 48
BODY = 81
MATCHER = (("swap", 0, 1),)


def leaf_map(flat):
    """Compute the complete data permutation for the native first-coordinate line."""
    u,v = covered_factors(((1,0),(1,0)), (flat[:2],flat[2:]), 1)
    images = []
    for axis in range(4):
        z = [[int(i == axis)] for i in range(4)]
        out, _ = run_leaf(u,v,[(1,1)],z[:2],z[2:],1)
        images.append(tuple(row[0] for row in out))
    destinations = []
    for y in TRITS:
        for x in TRITS:
            d = x+y
            a,b,c,f = (sum(d[i]*images[i][j] for i in range(4)) % 3 for j in range(4))
            destinations.append(a+3*b+9*c+27*f)
    return destinations, bool(select_pivot(u,v))


def apply_map(block, positions):
    dest = bytearray(len(positions))
    for i,j in enumerate(positions):
        dest[j] = block[i]
    return dest


def reversed_exchange(source, groups, stats):
    """The second copy of the same native line needs its own right matcher."""
    for second in (False,True):
        if second:
            dest = BytesIO()
            right_route(BytesIO(source),dest,2,1,groups,BODY,MATCHER)
            source = dest.getvalue()
        major = BytesIO()
        type_route(BytesIO(source),major,groups,LOW_COUNT,BODY)
        major.seek(0)
        complete = BytesIO()
        for low in product(range(3),repeat=4):
            if regular(low,2):
                positions,bad = leaf_map(low)
                for _ in range(groups):
                    complete.write(apply_map(major.read(BODY),positions))
                stats["late_packets"] += int(bad)
                stats["low_packets"] += 1
        complete.seek(0)
        dest = BytesIO()
        type_route(complete,dest,groups,LOW_COUNT,BODY,inverse=True)
        source = dest.getvalue()
        if second:
            dest = BytesIO()
            right_route(BytesIO(source),dest,2,1,groups,BODY,MATCHER)
            source = dest.getvalue()
    return source


def ordinary_transpose(data, groups, stats):
    """Apply the two reversed calls and the three full ternary corrections."""
    for name in ("subtract","exchange","add","exchange","reverse_subtract"):
        if name == "exchange":
            data = reversed_exchange(data,groups,stats)
            continue
        move = []
        for y in TRITS:
            for x in TRITS:
                if name == "subtract":
                    dy = ((a-b)%3 for a,b in zip(y,x,strict=True))
                elif name == "add":
                    dy = ((a+b)%3 for a,b in zip(y,x,strict=True))
                else:
                    dy = ((b-a)%3 for a,b in zip(y,x,strict=True))
                c,d = dy
                move.append(x[0]+3*x[1]+9*c+27*d)
        data = b"".join(apply_map(data[i:i+BODY],move) for i in range(0,len(data),BODY))
    return data


def two_axis_crt(machine, field, reverse):
    """The bit planes of the actual signed records provide the independent low rows."""
    nx,ny = machine.widths
    scalar = isinstance(field[0],int)
    channels = 1 if scalar else 2
    bits = machine.grid.bits+4
    groups = (channels*bits+LOW_COUNT-1)//LOW_COUNT
    words = [0]*(BODY*channels)
    for y in range(ny):
        for x in range(nx):
            value = field[y*nx+x]
            for c,v in enumerate((value,) if scalar else value):
                if not -(1 << (bits-1)) <= v < 1 << (bits-1):
                    raise OverflowError("The fixed CRT payload format is too narrow")
                words[(9*y+x)*channels+c] = v
    planes = bytearray(groups*LOW_COUNT*BODY)
    for j in range(channels*bits):
        c,bit = divmod(j,bits)
        planes[j*BODY:(j+1)*BODY] = bytes((v >> bit) & 1 for v in words[c::channels])
    if not hasattr(machine,"row_stats"):
        machine.row_stats = {"late_packets":0,"low_packets":0,"crt_calls":0}
    stats = machine.row_stats
    stats["crt_calls"] += 1
    rows = bytearray(ordinary_transpose(planes,groups,stats))
    for x in range(nx):
        [(_,width,program)] = machine.router.offset_programs((x,0),1)
        order = range(2*width-1)
        for step in reversed(order) if reverse else order:
            bit,table = program[step]
            for y in range(ny):
                if not (y >> bit) & 1 and table[y]:
                    for base in range(9*x,len(rows),BODY):
                        a,b = base+y, base+y+(1 << bit)
                        rows[a],rows[b] = rows[b],rows[a]
    restored = ordinary_transpose(rows,groups,stats)
    if any(restored[channels*bits*BODY:]):
        raise ArithmeticError("A retired spare bit plane contains data")
    values = []
    for index in range(BODY):
        components = []
        for c in range(channels):
            v = sum(restored[(c*bits+bit)*BODY+index] << bit for bit in range(bits))
            components.append(v-(1 << bits) if v >> (bits-1) else v)
        if index % 9 < nx and index // 9 < ny:
            values.append(components[0] if scalar else tuple(components))
        elif any(components):
            raise ArithmeticError("A temporary physical hole contains data")
    return values
