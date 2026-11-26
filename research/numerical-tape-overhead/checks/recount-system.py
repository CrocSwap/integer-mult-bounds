"""Build one occupied CRT/short-Fourier/fixed-grid/full-carry integration fixture."""
from argparse import ArgumentParser
import json
from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location
from math import prod
from pathlib import Path
from random import Random
from subprocess import run
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
SPEC = spec_from_file_location("outer_integer_phases", HERE / "outer-phases.py")
PHASES = module_from_spec(SPEC)
SPEC.loader.exec_module(PHASES)


def inverse(gather):
    result = [-1] * len(gather)
    for i, j in enumerate(gather):
        assert 0 <= j < len(gather) and result[j] == -1
        result[j] = i
    return tuple(result)


def conjugate(z):
    return z[0], -z[1]


def reverse_op(op):
    kind, values = op
    if kind == "P":
        return kind, inverse(values)
    if kind == "D":
        return kind, tuple(map(conjugate, values))
    return kind, tuple((i, j, tag, conjugate(z)) for i, j, tag, z in values)


def adjoint(word):
    return tuple(reverse_op(op) for op in reversed(word))


class Fixture:
    def __init__(self, bits, p, phase_bits, volume):
        self.grid = PHASES.Grid(p)
        self.bits = bits
        self.p = p
        self.phase_bits = phase_bits
        self.volume = volume
        self.one = self.grid.q, 0
        self.phase_ids = {}
        self.gate_ids = {}
        self.gates = []

    def quantize(self, z):
        d = self.p - self.phase_bits
        assert d > 0
        return tuple((1 if h >= 0 else -1) * ((abs(h) + (1 << (d-1))) >> d)
                     for h in z)

    def phase_id(self, z):
        return self.phase_ids.setdefault(self.quantize(z), len(self.phase_ids))

    def gate_id(self, kind, fields=()):
        fields = tuple(fields)
        key = kind, fields
        if key not in self.gate_ids:
            self.gate_ids[key] = len(self.gates)
            self.gates.append(key)
        return self.gate_ids[key]

    def root(self, j, d):
        return PHASES.root(self.p, j, d)

    def raw(self, a):
        r = 1 << (2*a-2).bit_length()
        n = 2*r
        def diag(values):
            values = tuple(values)
            return "D", values + (self.one,) * (n-len(values))
        def pairs(values):
            return "E", tuple(values)
        bits = r.bit_length()-1
        rev = tuple(int(format(i, f"0{bits}b")[::-1], 2) for i in range(r))
        fft = [("P", rev + tuple(range(r, n)))]
        for stage in range(1, bits+1):
            step = 1 << stage
            half = step//2
            fft.append(diag(self.root(i % half, step) if i % step >= half else self.one
                            for i in range(r)))
            fft.append(pairs((i, i+half, "H", (0, 0))
                             for i in range(r) if i % step < half))
        lift = pairs((i, i+r, "L", self.grid.z(a, r, i)) for i in range(r))
        chirp = diag(self.root(j*j, 2*a) for j in range(a))
        v = (chirp, *fft, lift, *adjoint(fft), chirp)
        neg = -self.grid.q, 0
        first = diag((neg,)*a)
        second = diag((self.one,)*a + (neg,)*(n-a))
        amp = v + ((first,) + adjoint(v) + (second,) + v)*64
        left = diag(self.root(j*j+(a%2)*j, 2*a) for j in range(a))
        middle = diag(self.grid.d2(a,j) for j in range(a))
        right = diag(self.root(j*j-(a%2)*j, 2*a) for j in range(a))
        return (right, *amp, middle, *adjoint(amp), left), n

    @lru_cache(None)
    def pair_phases(self, tag, z):
        if tag == "H":
            return ((self.one, self.one),)*3
        if tag == "I":
            minus_i=(0, -self.grid.q)
            return ((self.one, minus_i), (self.root(1, 8), self.root(-1, 8)),
                    (self.one, minus_i))
        out, mid, inp = self.grid.pair(z)
        return inp, mid, out

    def lower(self, raw, tuples):
        kind, data = raw
        if kind == "P":
            p = list(range(self.volume))
            for dest in tuples:
                for i, j in enumerate(data):
                    p[dest[i]] = dest[j]
            inverse(p)
            return (self.gate_id("P", p),)
        if kind == "D":
            d = [self.phase_id(self.one)] * self.volume
            local = tuple(map(self.phase_id, data))
            for sites in tuples:
                for i, z in zip(sites, local):
                    d[i] = z
            return (self.gate_id("D", d),)

        edges = [(sites[i], sites[j], tag, z) for sites in tuples for i,j,tag,z in data]
        used = {i for a,b,_,_ in edges for i in (a,b)}
        assert len(used) == 2*len(edges)
        unused = [i for i in range(self.volume) if i not in used]
        edges.extend((i,j,"I",(0,0)) for i,j in zip(unused[::2], unused[1::2]))
        edges.sort(key=lambda entry: entry[0])
        p = tuple(i for a,b,_,_ in edges for i in (a,b))
        ip = inverse(p)
        ds = [[], [], []]
        for _,_,tag,z in edges:
            for d, pair in zip(ds,self.pair_phases(tag,z)):
                d.extend(map(self.phase_id,pair))
        p,ip=self.gate_id("P",p),self.gate_id("P",ip)
        di, mid, do = (self.gate_id("D",d) for d in ds)
        h = self.gate_id("W")
        return p,di,h,mid,h,do,h,ip

    def schedule(self, axes, sizes):
        seq=[]
        for d, a in enumerate(axes):
            stride=prod(sizes[:d]); step=stride*sizes[d]
            fibres=[tuple(start+offset+j*stride for j in range(sizes[d]))
                    for start in range(0,self.volume,step) for offset in range(stride)]
            assert len(fibres)>=8 and len(fibres)%8==0
            nactive=len(fibres)//8
            raw,n=self.raw(a)
            # Local bands repeat inside the 64 reflection pairs. Compile each unique band once.
            lookup={}
            local=[]
            for op in raw:
                if op not in lookup:
                    lookup[op]=len(lookup)
                local.append(lookup[op])
            for batch in range(8):
                begin=batch*nactive
                donors=[i for h,f in enumerate(fibres) if not begin<=h<begin+nactive for i in f]
                sites=[f[:a] + tuple(donors[j*(n-a):(j+1)*(n-a)])
                       for j,f in enumerate(fibres[begin:begin+nactive])]
                assert len({i for row in sites for i in row})==n*nactive
                translated=[self.lower(op, sites) for op in lookup]
                seq.extend(id for i in local for id in translated[i])
        return seq

    def inverse_seq(self, seq):
        phases=list(self.phase_ids)
        phase_inv=[self.phase_ids.setdefault(conjugate(z),len(self.phase_ids)) for z in phases]
        inv=[]
        for k, cells in self.gates[:]:
            if k=="P": inv.append(self.gate_id("P",inverse(cells)))
            elif k=="D": inv.append(self.gate_id("D", (phase_inv[j] for j in cells)))
            else: inv.append(self.gate_id("W"))
        return [inv[j] for j in reversed(seq)]


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--quick",action="store_true",help="use a 64-bit data grid")
    parser.add_argument("--directory",default=None,help="parent for reproducible temporary files")
    parser.add_argument("--inputs", choices=("reference", "boundaries"), default="reference",
                        help="select the original operand pair or three arithmetic edge cases")
    args=parser.parse_args()
    axes=(3,5,7,2)
    sizes=tuple(1<<(a-1).bit_length() for a in axes)
    modulus,volume=prod(axes),prod(sizes)
    k=(volume-1).bit_length()
    n=1000
    b=(n-1).bit_length()
    h=(n+b-1)//b
    assert (4*h-1).bit_length()==k and modulus>=2*h
    bits,phase_bits,p=(64,80,128) if args.quick else (72*k,80*k,2048*k)
    fixture=Fixture(bits,p,phase_bits,volume)
    forward=fixture.schedule(axes,sizes)
    backward=fixture.inverse_seq(forward)
    order=[]
    for rank in range(modulus):
        address=0
        for i,a in enumerate(axes):
            address+=((rank*pow(prod(axes[:i]),-1,a))%a)*prod(sizes[:i])
        order.append(address)
    assert len(set(order))==modulus
    rng=Random(0x8008)
    maximum = (1 << n) - 1
    reference = ("reference", maximum, rng.getrandbits(n-7) | (1 << (n-8)))
    cases = [reference] if args.inputs == "reference" else [
        ("maximal", maximum, maximum),
        ("zero", 0, maximum),
        ("single-pair", 1 << (27*b+2), 1 << (44*b+3)),
    ]
    with TemporaryDirectory(prefix="recount-system-",dir=args.directory) as temp:
        temp=Path(temp)
        spec=temp/"fixture"
        with spec.open("w") as f:
            def row(values):
                print(*values,file=f)
            row((n,k,bits,phase_bits,h,b,modulus,volume))
            row((len(fixture.phase_ids),))
            for z in fixture.phase_ids: row(z)
            row((len(fixture.gates),))
            for op, fields in fixture.gates: row((op,*fields))
            for word in (forward,backward):
                row((len(word),));row(word)
            row(order)
        print(f"Compiled {len(fixture.phase_ids)} phases, {len(fixture.gates)} gates "
              f"and {len(forward)} forward slots.",flush=True)
        binary=temp/"replay"
        gmp_version = json.loads((HERE.parent/"dependencies.json").read_text())["gmp"]
        run(["c++","-std=c++17","-O3",f'-DTAPE_EXPECTED_GMP="{gmp_version}"',HERE/"recount-system.cpp","-lgmpxx","-lgmp","-o",binary],check=True)
        with spec.open("r+") as f:
            f.seek(0, 2)
            operands_offset = f.tell()
            for label, x, y in cases:
                f.seek(operands_offset)
                print(x, y, file=f)
                f.truncate()
                f.flush()
                f.seek(0)
                result = run([binary], stdin=f, check=True, capture_output=True, text=True)
                receipt = json.loads(result.stdout)
                assert receipt["leading_output_zeros"] == 2*n - (x*y).bit_length()
                assert (receipt["wrong_without_inverse_crt"] > 0) == (x*y != 0)
                print(json.dumps({"inputs": label, **receipt}), flush=True)


if __name__=="__main__":
    main()
