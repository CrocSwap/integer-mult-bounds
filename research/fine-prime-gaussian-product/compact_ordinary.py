"""Run the compact436 ordinary interchange on complete binary rectangles."""

from fractions import Fraction
from hashlib import sha256
from math import prod
import gzip
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


HERE=Path(__file__).resolve().parent
if __name__=="__main__":
    sys.path.insert(0,str(HERE))
Q=213*(1<<80)+1


def load_cohort():
    root=HERE.parent/"physical-ordinary-interchange"
    sys.path.insert(0,str(root))
    import source
    source.activate()


def matrix(size, entries):
    rows=[[Fraction(0)]*size for _ in range(size)]
    for i,j,v in entries:
        rows[i][j]=Fraction(v)
    return tuple(map(tuple,rows))


def open_source(path,q,*,check_only=False):
    from catalogue import Base, Catalogue, Chart, Request, Specifications
    from low_codes import LowCodes
    from topology import Call, Owner, SelectedTopology
    with gzip.open(path,"rb") as stream:
        raw=stream.read()
    if sha256(raw).hexdigest()!="b498336bba17cbcdf361447026350acebf8b066f0d64faeb9a11ee5c79d4f515":
        raise ValueError("compact436 coefficient source differs from the canonical producer")
    data=json.loads(raw)
    from compact_machine import RadixCounts, BoundedSpecifications, CompactProgram

    class FixedPrimeCodes(RadixCounts,LowCodes):
        def __init__(self, prime, requests):
            # Proth primality certificate for 213 times 2^80 plus one.
            if prime != Q or 213 >= 1<<80 or pow(7,(prime-1)//2,prime) != prime-1:
                raise ValueError("compact436 production prime")
            self.q,self.dimension,self.requests=prime,64,requests
            self.radices=tuple(prime**64-prime**i for i in range(64))
            self.size=prod(self.radices)
            self.limit=2*requests*self.size
            self.bits=max(1,(self.limit-1).bit_length())

    def chart(k):
        what,port,stage,axes=k
        return Chart(what,port,stage,tuple(axes))
    keys=tuple(map(chart,data["chart_keys"]))
    charts=dict(zip(keys,data["chart_matrices"],strict=True))
    bases=[Base(k,matrix(8,vals) if k=="local" else tuple(vals),r)
           for k,r,vals in data["bases"]]
    class BoundCatalogue(Catalogue):
        private=658

        def __init__(self):
            from collections import Counter
            self.q=q
            self.requests=[Request(*r[:7],bases[r[7]],keys[r[8]],r[9],
                                   None if r[10] is None else keys[r[10]])
                           for r in data["requests"]]
            self.profile=Counter()
            for item in self.requests:
                self.profile[item.base.rank]+=32
            self.bases={b.key:b for b in bases}
            self.charts=set(keys)
            self.erase_guards=data["erasures"]
            self.identifiers={self.semantic_key(r):i for i,r in enumerate(self.requests)}
            if (len(self.identifiers)!=28138 or data["request_digest"]!="09f5c631108ef0e17f82c595ae193ccafabe179b20565f71033890dd308c4e87"
                or self.receipt()["binding_sha256"]!=data["request_digest"]):
                raise ValueError("compact436 request order changed in transport")
            self.codes=FixedPrimeCodes(q,len(self.requests)) if q==Q else LowCodes(q,64,len(self.requests))
            self.template=dict(schedule=data["schedule"],loop_order=
                "Each recipe phase: replicas then all cover classes; finish every local invocation before the next.")

        def chart_matrix(self,key):
            return matrix(64,charts[key])

    class BoundTopology(SelectedTopology):
        def call(self,stage,replica):
            rev,owners,ids=data["stages"][stage]
            order=lambda r:(tuple(data["end"]),tuple(data["start"])) if r else (tuple(data["start"]),tuple(data["end"]))
            on,off=order(rev)
            events=data["programs"]["reverse" if rev else "forward"]
            physical=tuple(Owner(family+replica*self.stride,keys[label]) for family,label in owners)
            if len(physical)!=len(on) or len(off)!=658 or len(ids)!=len(events):
                raise ValueError("compact436 stage extent")
            return Call(stage,replica,physical,on,off,tuple(map(tuple,events)),tuple(ids),rev)
    catalogue=BoundCatalogue()
    topo=BoundTopology(catalogue)
    class FixedSpecifications(BoundedSpecifications,Specifications):
        pass

    specs=FixedSpecifications(catalogue)
    if check_only:
        return catalogue,topo,specs
    from binary import Binary
    from encoded import Profile
    from macro_binding import SelectedBinding
    from compact_execution import CompactOrdinary
    binding=SelectedBinding(specs)
    program=CompactProgram(topo,binding)
    native=CompactOrdinary(q,binding,topo,(program,),capacity=1<<24,
                    profile=Profile(numerator=1,denominator=574),fixture_index_floor=0)
    return Binary(native)


def source_at(path):
    subprocess.run([sys.executable,"-I","-B",str(HERE/"compact_source.py"),str(path)],check=True)


def worker():
    load_cohort()
    from cardinal_counts import Count
    from records import Tape
    from session import erase_marker
    from words import BLANK, RIGHT

    def encoded_count(value):
        tape = Tape()
        for i in range(max(1, value.bit_length())):
            tape.append((value >> i) & 1)
        tape.append(RIGHT)
        tape.rewind()
        result = Count(tape)
        tape.clear()
        erase_marker(tape)
        return result

    with TemporaryDirectory(prefix="compact436-product-") as temp:
        packet=Path(temp)/"source.gz"
        source_at(packet)
        engine=open_source(packet,Q)
        buf=sys.stdin.buffer
        fields=[int(token,16) for token in buf.readline().split()]
        width,prefix,gap,suffix=fields
        extent=prefix*gap*suffix << (2*width)
        original=Tape()
        for _ in range(extent):
            bit=buf.read(1)
            if bit not in (b"\x00",b"\x01"):
                raise ValueError("ordinary input bit")
            original.append(bit[0])
        original.rewind()
        values=[encoded_count(x) for x in fields]
        output=engine.run(original,*values)
        out=sys.stdout.buffer
        block=bytearray()
        for _ in range(extent):
            bit=output.read()
            if bit not in (0,1):
                raise ArithmeticError("ordinary output bit")
            block.append(bit)
            output.step(1)
            if len(block)==8192:
                out.write(block)
                block.clear()
        out.write(block)
        if output.read()!=BLANK:
            raise ArithmeticError("ordinary output extent")
        for tape in (original,output):
            tape.clear()
            erase_marker(tape)
        for v in values:
            v.close()
            erase_marker(v.tape)


def literal_transpose(field,width,prefixes,gap,suffix):
    from fine_ring import Tape
    n=1<<width
    for j in range(width):
        # In a rectangle, the two bit positions can include a nonbinary gap.
        buckets=[Tape(field.width,field.trace) for _ in range(4)]
        def selectors(swap):
            for _ in range(prefixes):
                for a in range(n):
                    first=(a>>j)&1
                    for _ in range(gap):
                        for b in range(n):
                            second=(b>>j)&1
                            k=2*second+first if swap else 2*first+second
                            for _ in range(suffix):
                                yield k
        field.home()
        for k in selectors(False):
            buckets[k].append(field.read())
        field.release()
        field=Tape(buckets[0].width,buckets[0].trace)
        for b in buckets:
            b.home()
        for k in selectors(True):
            field.append(buckets[k].read())
        for b in buckets:
            b.release()
    return field


def transpose(field,width,prefixes,gap,suffix):
    """Exchange two equal binary fields. Preserve both signed components."""
    from fine_ring import Tape
    count=len(field.cells)
    if min(prefixes,gap,suffix)<1 or width<0 or count!=prefixes*gap*suffix<<(2*width):
        raise ValueError("ordinary rectangle extent")
    if width<=64:
        return literal_transpose(field,width,prefixes,gap,suffix)
    component=field.width
    mask=(1<<component)-1
    header=" ".join(format(x,"x") for x in (width,prefixes,gap,2*component*suffix))+"\n"
    data=bytearray(header.encode("ascii"))
    field.home()
    for _ in range(count):
        for v in field.read():
            u=v & mask
            for i,byte in enumerate(u.to_bytes((component+7)//8,"little")):
                data.extend((byte>>j)&1 for j in range(min(8,component-8*i)))
    output=subprocess.run([sys.executable,"-I","-B",str(Path(__file__).resolve()),"--ordinary"],
                          input=data,stdout=subprocess.PIPE,check=True).stdout
    if len(output)!=2*component*count:
        raise ArithmeticError("ordinary rectangle return")
    out=Tape(component,field.trace)
    field.release()
    pos=0
    for _ in range(count):
        pair=[]
        for _ in range(2):
            bits=output[pos:pos+component]
            if any(bit>1 for bit in bits):
                raise ArithmeticError("invalid returned bit")
            packed=bytearray(sum(bit<<j for j,bit in enumerate(bits[i:i+8]))
                             for i in range(0,component,8))
            v=int.from_bytes(packed,"little")
            pair.append(v-(1<<component) if v>>(component-1) else v)
            pos+=component
        out.append(tuple(pair))
    return out


if __name__=="__main__" and sys.argv[1:]==["--ordinary"]:
    worker()
