"""Exact row-service ABI for the current physical lifecycle controller.

All physical tapes are supplied once. Numerical/native stopping is a separate
local-machine service. The row implementation never uses CodedPort: J counts
actual physical bits, including every three-bit code and component delimiter.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import importlib.util
import sys


def programs():
    path=Path(__file__).resolve().parent/"row_programs.py"
    spec=importlib.util.spec_from_file_location("bound_row_programs",path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    exec(compile(path.read_bytes(),str(path),"exec"),module.__dict__)
    return module


r=programs()


class RowServices:
    """Prepare/install/collect for one fixed final-template width.

    work is a fixed tuple of 40 distinct, marked, blank payload ports, all
    included in the caller's continuation inventory. descriptor is one other
    raw-binary payload port. The externally supplied bridge/header use BASE5;
    all payload/work ports use LEFT2. Primitive bodies contain physical0/1,
    with physical BLANK6 at their actual frontier.

    sites is a fixed map from source finite tokens to event kinds. Only final
    rank-one ordinary PAID sites are ROW_CHILD. Matched compiler occurrences
    are static services on already established fields; their metadata stays.
    """
    def __init__(self,width,descriptor,work,sites,leaf_decider=None,
                 rank=None,remainder_service=None):
        r.need(type(width) is int and width>=1,"fixed positive template width")
        r.need(len(work)==r.FIRST_ROLE,"fixed row work inventory")
        r.need(len(set(map(id,(*work,descriptor))))==len(work)+1,"distinct row work/descriptor ports")
        self.width=width
        self.descriptor=descriptor
        self.work=tuple(work)
        self.sites=dict(sites)
        r.need(all(kind in (r.ROW_CHILD,r.MATCHED) for kind in self.sites.values()),"source event kinds")
        r.need(rank is not None or leaf_decider is not None,
               "structural-only mode declares its separate stopping predicate")
        r.need(rank is None or (type(rank) is int and rank>=2),"fixed compiled rank")
        r.need(rank is None or remainder_service is not None,
               "encoded numerical recursion requires its completed remainder service")
        self.rank=rank
        self.remainder_service=remainder_service
        self.leaf_decider=EncodedLeaf(rank) if leaf_decider is None else leaf_decider
        self.prepared=r.compile_prepare(width,rank=rank)
        self.root_prepared=None if rank is None else r.compile_prepare(width,rank=rank,root=True)
        self.split=r.compile_router(width)
        self.merge=r.compile_router(width,True)
        b=r.Builder()
        b.boundary(r.HEADER);b.boundary(r.CHILD_HEADER)
        b.copy(r.HEADER,r.CHILD_HEADER)
        self.copy=b.close()
        self.observed_steps=0

    def views(self):
        return [r.PhysicalPort(t,2) for t in self.work]

    def row_site(self,site):
        r.need(site in self.sites,"declared finite source site")
        r.need(self.sites[site]==r.ROW_CHILD,"matched-field event cannot consume row stock")

    def is_leaf(self,site):
        self.row_site(site)
        # This service has a separate explicit native/caller proof and invoice.
        return self.leaf_decider(site,self.descriptor,self.work)

    def prepare(self,site,child_header):
        self.row_site(site)
        ports=self.views()
        ports[r.HEADER]=r.PhysicalPort(self.descriptor,2)
        ports[r.CHILD_HEADER]=r.PhysicalPort(child_header,5)
        self.observed_steps+=r.run(self.prepared,ports)

    def prepare_root(self,root_header,child_header,root_marker=5):
        r.need(self.root_prepared is not None,"root geometry requires fixed compiled rank")
        ports=self.views()
        ports[r.HEADER]=r.PhysicalPort(root_header,root_marker)
        ports[r.CHILD_HEADER]=r.PhysicalPort(child_header,5)
        self.observed_steps+=r.run(self.root_prepared,ports)

    def install(self,bridge,child_header,public):
        r.need(len(public)==self.width,"actual fixed productive field list")
        ports=self.views()+[r.PhysicalPort(t,2) for t in public]
        ports[r.SOURCE]=r.PhysicalPort(bridge,5)
        ports[r.HEADER]=r.PhysicalPort(child_header,5)
        self.observed_steps+=r.run(self.split,ports)
        ports=self.views()
        ports[r.HEADER]=r.PhysicalPort(child_header,5)
        ports[r.CHILD_HEADER]=r.PhysicalPort(self.descriptor,2)
        self.observed_steps+=r.run(self.copy,ports)
        if self.rank is not None:
            r.need(self.remainder_service is not None,"completed elementary remainder service required")
            # At most N-1 elementary kernels, on every complete public field.
            # This service's semantic and physical invoice is retained separately.
            self.remainder_service(tuple(public),self.descriptor)

    def collect(self,public,bridge):
        r.need(len(public)==self.width,"all child public outputs returned")
        ports=self.views()+[r.PhysicalPort(t,2) for t in public]
        ports[r.OUTPUT]=r.PhysicalPort(bridge,5)
        ports[r.HEADER]=r.PhysicalPort(self.descriptor,2)
        self.observed_steps+=r.run(self.merge,ports)


class EncodedLeaf:
    """Source-compatible requested-child test f<=certified integer cutoff."""
    def __init__(self,rank):
        self.table=r.compile_leaf(rank)
        self.observed_steps=0

    def __call__(self,site,descriptor,work):
        ports=[r.PhysicalPort(t,2) for t in work]
        ports[r.HEADER]=r.PhysicalPort(descriptor,2)
        result,steps=r.run_choice(self.table,ports)
        self.observed_steps+=steps
        return result


class StockLeafFixture:
    """Physical fixture predicate stock==1; not the selected rank cutoff.

    This supplies a nontrivial finite-depth integration fixture. Production
    uses its retained encoded rank/stopping predicate with a separate invoice.
    """
    def __init__(self):
        b=r.Builder()
        fields=tuple(port for _,port in r.SCHEMA)
        for port in (r.HEADER,r.LENGTH,*fields):b.boundary(port)
        b.decode(r.HEADER,fields)
        b.canonical(r.STOCK,positive=True)
        maybe,leaf,internal=(b.fresh("stock_leaf") for _ in range(3))
        b.read(r.STOCK,{r.ONE:maybe,r.ZERO:internal})
        b.mark(maybe);b.move(r.STOCK,1)
        b.read(r.STOCK,{r.BLANK:leaf,r.ZERO:internal,r.ONE:internal})
        for label,value in ((leaf,True),(internal,False)):
            b.mark(label)
            for port in fields:b.clear(port)
            b.code.append(("result",value))
        self.table=b.close()
        self.observed_steps=0

    def __call__(self,site,descriptor,work):
        ports=[r.PhysicalPort(t,2) for t in work]
        ports[r.HEADER]=r.PhysicalPort(descriptor,2)
        result,steps=r.run_choice(self.table,ports)
        self.observed_steps+=steps
        return result
