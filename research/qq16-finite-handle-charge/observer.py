"""Read-only source encoder and observer for the actual inherited caller."""
import types
from kernel import need, validate, exchange

SKIP={'binding','catalogue','group','data','source','native_child','at_fence',
      'observe','codes','recipes','template','packet','core','events','word'}


def snapshot(protocol, Tape, handles):
    def handle(tape):
        need(isinstance(tape,Tape),'actual physical Tape')
        if id(tape) not in handles:handles[id(tape)]=len(handles)+1
        return handles[id(tape)]
    def graph(owner):
        seen={}; rows=[]; attributes=0
        def visit(value):
            nonlocal attributes
            key=id(value)
            if key in seen:return seen[key]
            index=len(rows);seen[key]=index;rows.append(None)
            if isinstance(value,Tape):
                rows[index]=[1,handle(value),[]];return index
            if isinstance(value,dict):children=list(value.values())
            elif isinstance(value,(tuple,list)):children=list(value)
            elif not isinstance(value,(type,types.ModuleType,types.FunctionType,types.MethodType)) and hasattr(value,'__dict__'):
                items=list(vars(value).items());attributes+=len(items)
                children=[v for k,v in items if k not in SKIP]
            else:children=[]
            rows[index]=[0,0,[visit(v) for v in children]]
            return index
        visit(owner)
        expected=[handle(t) for t in protocol.owned_tapes(owner)]
        # DFS node numbering puts first Tape encounters in source traversal order.
        need([r[1] for r in rows if r[0]]==expected,'complete source graph encoding')
        return dict(root=0,rows=rows,attributes=attributes)
    i=protocol.installation; storage=i.storage
    graphs=[graph(i.service),graph(i.native_child),graph(protocol.parent)]
    acquisition=storage.acquisition
    acquired=[] if acquisition is None else [*acquisition.packets,acquisition.output,*acquisition.pool.tapes]
    return dict(graphs=graphs,saved=[[handle(t) for t in r] for r in i.engine_roles],
                external=[handle(t) for t in storage.external_roles],
                auxiliary=[handle(t) for t in protocol.auxiliary],
                storage=[handle(t) for t in storage.roles],
                acquired=[handle(t) for t in acquired])


class Observer:
    def __init__(self,size):
        self.size=size;self.checks=[];self.exchanges=[];self.examples=[];self.handles={}

    def attach(self,adapter,Tape):
        original=adapter.ReturnProtocol.check_inventory
        original_exchange=adapter.ReturnProtocol.exchange
        def check(protocol):
            data=snapshot(protocol,Tape,self.handles)
            bill=validate(data,self.size)
            original(protocol)
            shapes=[dict(vertices=len(g['rows']),edges=sum(len(r[2]) for r in g['rows']),
                         attributes=g['attributes'],tapes=sum(r[0] for r in g['rows'])) for g in data['graphs']]
            self.checks.append(dict(shapes=shapes,bill=bill))
            if len(self.examples)<2 or shapes != self.checks[0]['shapes']:
                if len(self.examples)<3:self.examples.append(data)
        def exchanged(roles,old,new):
            ids=self.handles
            need(all(id(t) in ids for t in (*roles,old,new)), 'stable complete lifetime handles')
            encoded=[ids[id(t)] for t in roles]
            out,bill=exchange(encoded,ids[id(old)],ids[id(new)],self.size)
            result=original_exchange(roles,old,new)
            need(out==[ids[id(t)] for t in result],'exact original cache exchange')
            self.exchanges.append(bill)
            return result
        adapter.ReturnProtocol.check_inventory=check
        adapter.ReturnProtocol.exchange=staticmethod(exchanged)
