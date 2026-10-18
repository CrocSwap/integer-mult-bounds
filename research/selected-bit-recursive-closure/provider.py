"""Bind selected literal residuals to full-ring preparation.

The image/kernel basis below is control arithmetic. It is never executed
as an address change, a row route or an extra normalization pass.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
import importlib.util
import json

import descriptor as d
import ring_algebra as ring
from controlled_normalizer import Arithmetic, prepare as coordinate_good_prepare
from fallback_program import Prefix, prepare as coordinate_fallback_prepare


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def rational_identity(n):
    return tuple(tuple(F(i == j) for j in range(n)) for i in range(n))


@dataclass(frozen=True)
class Base:
    kind: str
    data: tuple
    rank: int

    @property
    def key(self):
        values = [[str(x) for x in row] for row in self.data] if self.kind == "local" else self.data
        return sha256(canonical([self.kind, self.rank, values]).encode()).hexdigest()

    @lru_cache(None)
    def matrix(self, modulus):
        out = [[0]*64 for _ in range(64)]
        if self.kind == "local":
            need(len(self.data) == 8, "local projector dimension")
            for i, row in enumerate(self.data):
                need(len(row) == 8, "local projector row")
                for j, value in enumerate(row):
                    out[i][j] = value.numerator*pow(value.denominator,-1,modulus)%modulus
        else:
            need(self.kind == "idle" and len(set(self.data)) == self.rank, "idle projector label")
            for i in self.data:
                out[i][i] = 1
        return tuple(map(tuple,out))

    @lru_cache(None)
    def basis(self, q, width):
        matrix=[list(row) for row in self.matrix(q**width)]
        return tuple(map(tuple,ring.split_basis(matrix,self.rank,q,q**width)[2]))


@dataclass(frozen=True)
class Chart:
    kind: str
    port: int = -1
    stage: int = -1
    axes: tuple = ()

    @property
    def key(self):
        return (self.kind,self.port,self.stage,self.axes)


@dataclass(frozen=True)
class Request:
    kind: str
    stage: int
    position: int
    role: int
    family: int
    old_frame: int
    new_frame: int
    base: Base
    chart: Chart
    header_space: str
    source_chart: Chart | None = None

    def record(self):
        return [self.kind,self.stage,self.position,self.role,self.family,
                self.old_frame,self.new_frame,self.base.key,self.base.rank,
                self.chart.key,self.header_space,
                self.source_chart.key if self.source_chart else None]


class Catalogue:
    def __init__(self, root):
        path=root/"research/pr589-five-helper-hosting/verify.py"
        spec=importlib.util.spec_from_file_location("retained_pr1627_provider",path)
        self.old=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.old)
        self.word,self.template,self.geometry=(self.old.read(p) for p in
                                               (self.old.WORD,self.old.HOST,self.old.GEO))
        rows=[self.old.projection([self.word["lines"][i] for i in f]) for f in self.word["frames"]]
        self.projectors=[p for p,_ in rows];self.dimensions=[r for _,r in rows]
        self.idles={e["idx"]:e for e in self.template["schedule"] if e["kind"]=="idle"}
        self.requests=[];self.erase_guards=[];self.bases={};self.charts=set()
        self._bind()

    def base(self,a,b):
        lo,hi=(a,b) if self.dimensions[a] <= self.dimensions[b] else (b,a)
        value=Base("local",self.old.sub(self.projectors[hi],self.projectors[lo]),
                   self.dimensions[hi]-self.dimensions[lo])
        self.bases.setdefault(value.key,value)
        return self.bases[value.key]

    def pending(self,child):
        return tuple(self.old.pending_axes(self.idles[child]))

    def owner_chart(self,call,role):
        family,route=call["owners"][role]
        if route[0]=="data":
            _,stage,port=route
            return Chart("data",port,stage)
        need(route[0]=="hosted", "selected owner kind")
        _,child,offset,width=route
        axes=self.pending(child)[offset:offset+width]
        need(len(axes)==8,"complete helper block")
        return Chart("host",family%111 if min(axes)<8 else -1,axes=axes)

    @lru_cache(None)
    def chart_matrix(self,chart):
        out=[list(row) for row in rational_identity(64)]
        if chart.kind=="identity":
            return tuple(map(tuple,out))
        if chart.kind=="data":
            if chart.stage==0:
                return tuple(map(tuple,out))
            axes=list(range(8))+list(range(8+7*(chart.stage-1),8+7*chart.stage))
            rho=self.geometry["ports"][chart.port]["rho15"]
            for i,a in enumerate(axes):
                for j,b in enumerate(axes):
                    out[a][b]=F(rho[i][j])
            return tuple(map(tuple,out))
        if chart.kind=="family" or (chart.kind=="host" and chart.port>=0):
            port=self.geometry["ports"][chart.port]
            for i in range(8):
                out[i][:8]=[F(port["q"][i],2)]+list(map(F,port["complement_columns"][i]))
        if chart.kind=="host":
            domain=set(range(8));support=set(chart.axes);perm=list(range(64))
            for a,b in zip(sorted(domain-support),sorted(support-domain)):
                perm[a],perm[b]=b,a
            need(set(perm[:8])==support,"selected support completion")
            out=[[row[perm[j]] for j in range(64)] for row in out]
        else:
            need(chart.kind=="family","known chart type")
        return tuple(map(tuple,out))

    def _append(self,request):
        need(request.base.rank>0,"positive recursive residual")
        self.requests.append(request);self.charts.add(request.chart)
        if request.source_chart:
            self.charts.add(request.source_chart)

    def _bind(self):
        t=self.template
        need((t["m"],t["stages"],t["replicas"],t["live"])==(64,9,32,28416),"selected provider dimensions")
        for stage in range(9):
            call=t["calls"][stage*32]
            for rep in range(32):
                other=t["calls"][stage*32+rep]
                need((other["stage"],other["replica"],other["orientation"],other["local_hash"])
                     ==(stage,rep,call["orientation"],call["local_hash"]),"replica program binding")
                need(len(other["owners"])==len(call["owners"])==661,"replica owner inventory")
                need(all(route==r0 and family==f0+888*rep
                         for (family,route),(f0,r0) in zip(other["owners"],call["owners"])),
                     "replica owner symmetry")
            opened=None
            for pos,event in enumerate(t["local_programs"][call["orientation"]]):
                op,role=event[:2]
                if op==0:
                    _,_,a,b,rank,_=event
                    base=self.base(a,b)
                    need(base.rank==rank and opened is None,"MOVE binding and private interval")
                    self._append(Request("MOVE",stage,pos,role,call["owners"][role][0],a,b,
                                         base,self.owner_chart(call,role),"owner"))
                elif op==2:
                    _,_,temporary,a,b,rank,_=event
                    need(temporary==661 and opened is None,"fresh COPY role")
                    base=self.base(a,b)
                    need(base.rank==rank==7,"literal rank-seven COPY")
                    opened=Request("COPY",stage,pos,role,t["live"],a,b,base,
                                   Chart("identity"),"common",self.owner_chart(call,role))
                    self._append(opened)
                elif op==3:
                    _,_,temporary,a,b,_,_=event
                    need(opened is not None and opened.role==role and temporary==661 and
                         opened.base==self.base(a,b),"matching transported ERASE")
                    self.erase_guards.append((stage,pos,opened.position,role,opened.base.key))
                    opened=None
                else:
                    need(op==1,"known literal event")
            need(opened is None,"closed private temporary")
        occupied=defaultdict(set)
        for child,copy,offset,width,_stage,_helper in t["hosting"]["slots"]:
            axes=self.pending(child)[offset:offset+width]
            need(not occupied[child,copy].intersection(axes),"disjoint hosted slots")
            occupied[child,copy].update(axes)
        for child,event in self.idles.items():
            pending=set(self.pending(child));histogram=Counter()
            for copy in range(222):
                axes=tuple(sorted(pending-occupied[child,copy]));rank=len(axes)
                histogram[rank]+=1
                if not rank:
                    continue
                base=Base("idle",axes,rank);self.bases.setdefault(base.key,base)
                self._append(Request("IDLE",child,child,copy,event["pair"]*222+copy,
                    event["source_level"],event["target_level"],base,Chart("family",copy%111),"owner"))
            if str(child) in t["hosting"]["remainders"]:
                need({str(r):n for r,n in histogram.items()}==t["hosting"]["remainders"][str(child)],
                     "actual idle remainder binding")
            else:
                need(histogram==Counter({0:222}),"unlisted idle has zero residual")
        self.profile=Counter()
        for request in self.requests:
            self.profile[request.base.rank]+=32
        expected={int(k):v for k,v in self.old.read("research/e8-bit-p111-tuned/tune/EXPECTED.json")["nine"]["profile"].items()}
        need(dict(self.profile)==expected and sum(self.profile.values())==904896,"complete selected child provider")

    def receipt(self):
        binding=sha256()
        for request in self.requests:
            binding.update((canonical(request.record())+"\n").encode())
        return {"canonical_requests":len(self.requests),"replicas":32,
                "full_paid_requests":sum(self.profile.values()),
                "request_kinds":dict(Counter(r.kind for r in self.requests)),
                "base_labels":len(self.bases),"chart_labels":len(self.charts),
                "rank_histogram":dict(sorted(self.profile.items())),
                "canonical_ERASE_guards":len(self.erase_guards),
                "binding_sha256":binding.hexdigest()}


@dataclass(frozen=True)
class RawHeader:
    q: int
    width: int
    low: tuple
    high: tuple
    space: str

    def full(self,arithmetic,low_only=False):
        need(self.q>=3 and self.q%2 and self.width>=1,"odd prime-power header domain")
        need(len(self.low)==len(self.high)==64 and all(len(r)==64 for r in self.low+self.high),
             "physical header dimensions")
        cap=self.q**(self.width-1);out=[]
        for a,b in zip(self.low,self.high):
            row=[]
            for x,y in zip(a,b):
                need(0<=x<self.q and 0<=y<cap,"physical header digit range")
                arithmetic.prefix_cells+=2
                row.append(x+(0 if low_only else self.q*y))
            out.append(row)
        return out


@dataclass(frozen=True)
class GeneralHeader:
    raw: RawHeader
    request: Request
    catalogue: Catalogue

    @property
    def q(self): return self.raw.q
    @property
    def width(self): return self.raw.width
    @property
    def dimension(self): return 64
    @property
    def low(self): return self.raw.low
    @property
    def high(self): return self.raw.high
    @property
    def axes(self): return tuple(range(self.request.base.rank))

    def read(self,arithmetic,low_only=False):
        need(self.raw.space==self.request.header_space,"owner/common header convention")
        modulus=self.q**self.width
        physical=self.raw.full(arithmetic,low_only)
        sigma=ring.reduce_matrix(self.catalogue.chart_matrix(self.request.chart),modulus)
        basis=self.request.base.basis(self.q,self.width)
        arithmetic.counts["fixed_label_basis_preparations"]+=1
        # Only prepare the matrix consumed by the old coordinate normalizer.
        # No payload or row field is moved by these matrix multiplications.
        return ring.multiply(ring.multiply(physical,sigma,modulus),basis,modulus)

    def direct_projector(self):
        modulus=self.q**self.width;arithmetic=Arithmetic(modulus)
        g=self.raw.full(arithmetic)
        sigma=ring.reduce_matrix(self.catalogue.chart_matrix(self.request.chart),modulus)
        common=ring.multiply(g,sigma,modulus)
        return ring.conjugate(self.request.base.matrix(modulus),common,
                              ring.inverse(common,self.q,modulus),modulus)


@dataclass(frozen=True)
class WeightRecipe:
    q: int
    width: int
    root_size: int
    root_unit: int = 1
    ancestors: tuple = ()


def build_weights(recipe,low_only=False):
    modulus=recipe.q**recipe.width;arithmetic=Arithmetic(modulus)
    weights=d.Root(recipe.root_size,modulus,recipe.root_unit)
    for ancestor in recipe.ancestors:
        h=ancestor.header
        need((h.q,h.width)==(recipe.q,recipe.width),"one atom ring down the path")
        f=weights.size//64
        need(f>=1,"proper recursive ancestor width")
        p=d.projector(h.read(arithmetic,low_only),h.axes,modulus)
        if ancestor.kind=="good":
            weights=d.Good(weights,64,f,d.good_pivots(p,len(h.axes),modulus))
        elif ancestor.kind=="pair":
            plan=d.elimination(d.residual(p,modulus),modulus)
            weights=d.FallbackPair(weights,64,f,plan,ancestor.field,ancestor.reverse)
        else:
            raise ValueError("known generated ancestor kind")
    return weights,arithmetic


@dataclass
class GoodPrefix:
    header: GeneralHeader
    ancestor_weights: tuple
    atom_columns: int

    @property
    def q(self): return self.header.q
    @property
    def width(self): return self.header.width
    @property
    def low(self): return self.header.low
    @property
    def high(self): return self.header.high

    def full_matrix(self,arithmetic,low_only=False):
        return self.header.read(arithmetic,low_only)

    def weights(self,arithmetic):
        arithmetic.prefix_cells+=len(self.ancestor_weights)
        return list(self.ancestor_weights)


def prepare_good(recipe,header):
    need((recipe.q,recipe.width)==(header.q,header.width),"good call ring")
    weights,arithmetic=build_weights(recipe)
    f=weights.size//64
    need(f>=1,"internal good call")
    prefix=GoodPrefix(header,tuple(weights.value(i) for i in range(64*f)),f)
    result=coordinate_good_prepare(prefix,header.axes)
    result.arithmetic.counts.update(arithmetic.counts)
    result.arithmetic.prefix_cells+=arithmetic.prefix_cells
    need(result.projector==header.direct_projector(),"good full-frame projector binding")
    return result


def prepare_fallback(recipe,header):
    need((recipe.q,recipe.width)==(header.q,header.width),"fallback call ring")
    result=coordinate_fallback_prepare(Prefix(recipe.root_size,recipe.root_unit,recipe.ancestors,header))
    need(result.matrix==d.residual(header.direct_projector(),header.q**header.width),
         "fallback full-frame projector binding")
    return result


def raw_header(q,width,matrix,space):
    modulus=q**width
    return RawHeader(q,width,tuple(tuple(x%modulus%q for x in row) for row in matrix),
                     tuple(tuple((x%modulus)//q for x in row) for row in matrix),space)


def fixture_header(catalogue,request,q=3,width=2,bad=False,high=1):
    """A raw GL chart for the actual label; no payload basis change occurs."""
    modulus=q**width;r=request.base.rank
    h=ring.eye(64)
    if bad:
        h[0][0],h[0][r],h[r][0],h[r][r]=q,q-1,1,1+q*high
    else:
        c=q*high
        h[0][0],h[0][r],h[r][0],h[r][r]=1,1,c,1+c
    basis=request.base.basis(q,width)
    sigma=ring.reduce_matrix(catalogue.chart_matrix(request.chart),modulus)
    physical=ring.multiply(ring.multiply(h,ring.inverse(basis,q,modulus),modulus),
                           ring.inverse(sigma,q,modulus),modulus)
    return GeneralHeader(raw_header(q,width,physical,request.header_space),request,catalogue)
