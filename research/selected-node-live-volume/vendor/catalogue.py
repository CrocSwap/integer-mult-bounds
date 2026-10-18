"""Fixed selected request compilation, adapted from pinned PR2234 provider.py.

Only q, rational labels and low classes enter these compilation routines.
Runtime precision, high matrices, widths and coefficients remain on tapes.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction as F
from functools import cached_property, lru_cache
from hashlib import sha256
import importlib.util
import json

from binding import split_basis
from low_codes import LowCodes
import oracle
from plan import compile_plan
from sources import ROOT, Template, compile_specification, identity, product
from words import need


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"))


@dataclass(frozen=True)
class Base:
    kind: str
    data: tuple
    rank: int

    @cached_property
    def key(self):
        values=[[str(x) for x in row] for row in self.data] if self.kind=="local" else self.data
        return sha256(canonical([self.kind,self.rank,values]).encode()).hexdigest()

    @lru_cache(None)
    def matrix(self):
        out=[[F(0)]*64 for _ in range(64)]
        if self.kind=="local":
            for i,row in enumerate(self.data):out[i][:8]=row
        else:
            need(self.kind=="idle" and len(set(self.data))==self.rank,"fixed idle base")
            for i in self.data:out[i][i]=F(1)
        return tuple(map(tuple,out))

    @lru_cache(None)
    def basis(self,q):
        return split_basis(self.matrix(),self.rank,q)


@dataclass(frozen=True)
class Chart:
    kind: str
    port: int = -1
    stage: int = -1
    axes: tuple = ()

    @property
    def key(self):return (self.kind,self.port,self.stage,self.axes)


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
    source_chart: object = None

    def record(self):
        return [self.kind,self.stage,self.position,self.role,self.family,
                self.old_frame,self.new_frame,self.base.key,self.base.rank,
                self.chart.key,self.header_space,self.source_chart.key if self.source_chart else None]


class Catalogue:
    dimension=64
    replicas=32
    families=28416
    private=661
    replica_stride=888

    def __init__(self,q):
        self.q=q
        path=ROOT/"research/pr589-five-helper-hosting/verify.py"
        spec=importlib.util.spec_from_file_location("retained_selected_node_source",path)
        self.old=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.old)
        self.word,self.template,self.geometry=(self.old.read(p) for p in
                                               (self.old.WORD,self.old.HOST,self.old.GEO))
        rows=[self.old.projection([self.word["lines"][i] for i in frame]) for frame in self.word["frames"]]
        self.projectors=[p for p,_ in rows];self.dimensions=[r for _,r in rows]
        self.idles={event["idx"]:event for event in self.template["schedule"] if event["kind"]=="idle"}
        self.requests=[];self.bases={};self.charts=set();self.erase_guards=[]
        self._bind()
        self.codes=LowCodes(q,64,len(self.requests))
        self.identifiers={self.semantic_key(request):i for i,request in enumerate(self.requests)}
        need(len(self.identifiers)==len(self.requests),"unique full catalogue request identifiers")

    @staticmethod
    def semantic_key(request):
        return (request.kind,request.stage,request.role if request.kind=="IDLE" else request.position)

    def base(self,a,b):
        lo,hi=(a,b) if self.dimensions[a]<=self.dimensions[b] else (b,a)
        value=Base("local",self.old.sub(self.projectors[hi],self.projectors[lo]),
                   self.dimensions[hi]-self.dimensions[lo])
        return self.bases.setdefault(value.key,value)

    def pending(self,child):return tuple(self.old.pending_axes(self.idles[child]))

    def owner_chart(self,call,role):
        family,route=call["owners"][role]
        if route[0]=="data":return Chart("data",route[2],route[1])
        need(route[0]=="hosted","selected owner route kind")
        _,child,offset,width=route
        axes=self.pending(child)[offset:offset+width]
        need(len(axes)==8,"complete selected helper support")
        return Chart("host",family%111 if min(axes)<8 else -1,axes=axes)

    @lru_cache(None)
    def chart_matrix(self,chart):
        out=identity(64)
        if chart.kind=="identity":return tuple(map(tuple,out))
        if chart.kind=="data":
            if chart.stage==0:return tuple(map(tuple,out))
            axes=list(range(8))+list(range(8+7*(chart.stage-1),8+7*chart.stage))
            rho=self.geometry["ports"][chart.port]["rho15"]
            for i,a in enumerate(axes):
                for j,b in enumerate(axes):out[a][b]=F(rho[i][j])
            return tuple(map(tuple,out))
        if chart.kind=="family" or (chart.kind=="host" and chart.port>=0):
            port=self.geometry["ports"][chart.port]
            for i in range(8):out[i][:8]=[F(port["q"][i],2)]+list(map(F,port["complement_columns"][i]))
        if chart.kind=="host":
            domain,support=set(range(8)),set(chart.axes);permutation=list(range(64))
            for a,b in zip(sorted(domain-support),sorted(support-domain)):
                permutation[a],permutation[b]=b,a
            need(set(permutation[:8])==support,"selected owner support completion")
            out=[[row[permutation[j]] for j in range(64)] for row in out]
        else:need(chart.kind=="family","known fixed chart")
        return tuple(map(tuple,out))

    def _append(self,request):
        need(0<request.base.rank<=42,"positive selected paid residual")
        self.requests.append(request);self.charts.add(request.chart)
        if request.source_chart:self.charts.add(request.source_chart)

    def _bind(self):
        t=self.template
        need((t["m"],t["stages"],t["replicas"],t["live"])==(64,9,32,28416),"selected node dimensions")
        for stage in range(9):
            call=t["calls"][32*stage]
            for replica in range(32):
                other=t["calls"][32*stage+replica]
                need((other["stage"],other["replica"],other["orientation"],other["local_hash"])
                     ==(stage,replica,call["orientation"],call["local_hash"]),"replica literal binding")
                need(len(other["owners"])==len(call["owners"])==661 and
                     all(route==r0 and family==f0+888*replica
                         for (family,route),(f0,r0) in zip(other["owners"],call["owners"])),
                     "replica owner symmetry")
            opened=None
            for position,event in enumerate(t["local_programs"][call["orientation"]]):
                op,role=event[:2]
                if op==0:
                    _,_,a,b,rank,_=event;base=self.base(a,b)
                    need(base.rank==rank and opened is None,"positive MOVE outside private lifetime")
                    self._append(Request("MOVE",stage,position,role,call["owners"][role][0],a,b,
                                         base,self.owner_chart(call,role),"owner"))
                elif op==2:
                    _,_,temporary,a,b,rank,_=event;base=self.base(a,b)
                    need(temporary==661 and opened is None and base.rank==rank==7,"fresh selected COPY")
                    opened=Request("COPY",stage,position,role,t["live"],a,b,base,Chart("identity"),
                                   "common",self.owner_chart(call,role))
                    self._append(opened)
                elif op==3:
                    _,_,temporary,a,b,_,_=event
                    need(opened is not None and opened.role==role and temporary==661 and
                         opened.base==self.base(a,b),"transported ERASE source binding")
                    self.erase_guards.append((stage,position,opened.position,role,opened.base.key));opened=None
                else:need(op==1,"selected local opcode")
            need(opened is None,"closed local private lifetime")
        occupied=defaultdict(set)
        for child,copy,offset,width,_stage,_helper in t["hosting"]["slots"]:
            axes=self.pending(child)[offset:offset+width]
            need(not occupied[child,copy].intersection(axes),"disjoint selected hosted slots")
            occupied[child,copy].update(axes)
        for child,event in self.idles.items():
            pending=set(self.pending(child));histogram=Counter()
            for copy in range(222):
                axes=tuple(sorted(pending-occupied[child,copy]));rank=len(axes);histogram[rank]+=1
                if not rank:continue
                base=Base("idle",axes,rank);self.bases.setdefault(base.key,base)
                self._append(Request("IDLE",child,child,copy,event["pair"]*222+copy,
                                     event["source_level"],event["target_level"],base,
                                     Chart("family",copy%111),"owner"))
            if str(child) in t["hosting"]["remainders"]:
                need({str(rank):count for rank,count in histogram.items()}==t["hosting"]["remainders"][str(child)],
                     "actual idle remainder histogram")
            else:need(histogram==Counter({0:222}),"zero idle emits no residual")
        self.profile=Counter()
        for request in self.requests:self.profile[request.base.rank]+=32
        expected={int(k):v for k,v in self.old.read("research/e8-bit-p111-tuned/tune/EXPECTED.json")["nine"]["profile"].items()}
        need(dict(self.profile)==expected and sum(self.profile.values())==904896,"complete selected paid catalogue")
        need(self.receipt()["binding_sha256"]=="f5a4fb124709adc4b56376a3146e3609e91c0f4d3ed1931a61785a5d99bf8ee7",
             "exact ordered PR2234 request records")

    def receipt(self):
        digest=sha256()
        for request in self.requests:digest.update((canonical(request.record())+"\n").encode())
        return {"canonical_requests":len(self.requests),"replicas":32,"full_paid_requests":sum(self.profile.values()),
                "request_kinds":dict(Counter(request.kind for request in self.requests)),
                "base_labels":len(self.bases),"chart_labels":len(self.charts),
                "rank_histogram":dict(sorted(self.profile.items())),"canonical_ERASE_guards":len(self.erase_guards),
                "binding_sha256":digest.hexdigest()}

    @lru_cache(None)
    def template_for(self,request_id,common):
        request=self.requests[request_id]
        need(common or request.kind!="COPY","COPY uses a common header")
        chart=tuple(map(tuple,identity(64))) if common else self.chart_matrix(request.chart)
        basis=request.base.basis(self.q)
        preparation=basis if common else tuple(map(tuple,product(chart,basis)))
        record=tuple(request.record())+("common-after-route" if common else "native-owner",)
        return Template(self.q,request.base.rank,record,request.base.matrix(),chart,preparation)

    def identifier(self,kind,stage,position):return self.identifiers[kind,stage,position]

    def low_classes(self):
        for ordinal in range(self.codes.size):yield self.codes.unrank(ordinal)


class Specifications(dict):
    """Lazy fixed-q table, shared by current and frozen field codes."""
    def __init__(self,catalogue):
        super().__init__();self.catalogue=catalogue;self.plans={}

    def __contains__(self,code):
        codes=self.catalogue.codes
        if not isinstance(code,int) or not 0<=code<codes.limit:return False
        tag=code//codes.size
        return bool(tag&1) or self.catalogue.requests[tag//2].kind!="COPY"

    def __missing__(self,code):
        need(code in self,"admitted fixed source code")
        request,common,low=self.catalogue.codes.decode(code)
        result=compile_specification(code,self.catalogue.template_for(request,common),low)
        self[code]=result
        return result

    def bind(self,request_id,common,low):
        return self[self.catalogue.codes.encode(request_id,common,low)]

    def plan(self,code):
        if code in self.plans:return self.plans[code]
        spec=self[code];q=self.catalogue.q
        header=oracle.multiply(spec.low,oracle.reduce_rational(spec.template.preparation,q),q)
        projector=oracle.multiply([row[:spec.template.rank] for row in header],
                                  oracle.inverse(header,q)[:spec.template.rank],q)
        result=compile_plan(projector,spec.template.rank,q,spec.good)
        self.plans[code]=result
        return result
