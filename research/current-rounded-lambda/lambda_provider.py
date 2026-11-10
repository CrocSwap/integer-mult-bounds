"""Actual Q² monomial, private descriptor and one-rounded Gaussian join."""
from pathlib import Path
from types import SimpleNamespace
import sys
from source_binding import ROOT,authenticate,need,vendor,lambda_sites
from gaussian_table import compile_stage,COMMIT
M=vendor('lambda_retained_machine','vendor/machine.py')
authenticate();sys.path.insert(0,str(ROOT/'vendor/serial'))
from column_view import SerialProvider,S,literal
R=S.rows;ROLES=dict(R.SCHEMA);HEADER=R.HEADER;VIEW=R.CHILD_HEADER
PRIVATE=tuple(i for i in range(40) if i!=HEADER);FIELDS=tuple(p for _,p in R.SCHEMA)

def compile_view(rank):
    b=R.Builder()
    for p in (HEADER,*PRIVATE):b.boundary(p)
    for p in PRIVATE:b.empty(p)
    b.decode(HEADER,FIELDS);b.canonical(ROLES['f'],positive=True)
    b.clear(ROLES['remainder']);literal(b,ROLES['remainder'],0)
    b.clear(ROLES['selected_axes']);b.copy(ROLES['f'],ROLES['selected_axes'])
    for _ in range(rank-1):
        b.add(ROLES['selected_axes'],ROLES['f'],R.CONSTANT)
        b.clear(ROLES['selected_axes']);b.copy(R.CONSTANT,ROLES['selected_axes']);b.clear(R.CONSTANT)
    b.encode(FIELDS,VIEW);return b.close()

def release_view():
    b=R.Builder()
    for p in PRIVATE:b.clear(p)
    b.rewind(HEADER);return b.close()
RELEASE=release_view()

class HeaderView:
    port_count=len(PRIVATE)
    def __init__(self,rank):self.table=compile_view(rank);self.active=False;self.ports=None
    def bind(self,work,context):
        need(len(work)==self.port_count,'private descriptor inventory')
        self.ports={HEADER:R.PhysicalPort(context.tape)}
        self.ports.update({r:R.PhysicalPort(t) for r,t in zip(PRIVATE,work)})
    @property
    def context(self):return S.abi.BinaryContextPort(self.ports[VIEW].tape)
    def prepare(self):self.active=True;R.run(self.table,self.ports)
    def release(self):
        try:R.run(RELEASE,self.ports)
        finally:self.active=False

def translation_recipe(q,rank=9):
    need(type(rank)is int and 1<=rank<=9 and type(q)is int and 0<q<1<<rank,'fixed translation recipe')
    return dict(matrix_rows=tuple(1<<i for i in range(rank)),offset=q,linear_Z4=(0,)*rank,quadratic_rows=(0,)*rank,phase=0)

class LambdaProvider:
    """Fixed source sign/direction. rank<9 is for reduced mechanism fixtures only.

    Runtime consumes physical field/context and the bound fixed inventory.
    Q² is pure translation, so its phases never negate signed components.
    """
    def __init__(self,q,sign,native_factory,*,rank=9):
        need(type(rank)is int and 1<=rank<=9 and type(q)is int and 0<q<1<<rank,'fixed translation recipe')
        need(type(sign)is int and sign in (-1,1),'fixed source Lambda sign')
        self.q,self.sign,self.rank=q,sign,rank
        recipe=translation_recipe(q,rank)
        self.translation=SerialProvider(recipe,native_factory)
        self.view=HeaderView(rank);self.stage_table=compile_stage(sign);self.commit_table=COMMIT
        self.work=self.field=self.context=None;self.calls=0
    @property
    def port_count(self):return 3+self.view.port_count+self.translation.port_count
    def bind(self,work,field,context):
        need(len(work)==self.port_count and len(set(map(id,work)))==len(work),'complete distinct fixed inventory')
        need(field.tape is not context.tape and all(t is not field.tape and t is not context.tape for t in work),'distinct public/context/work segments')
        self.work=tuple(work);self.field=field;self.context=context
        self.stage=work[0];self.nums=work[1:3];stop=3+self.view.port_count
        self.view.bind(work[3:stop],context)
        self.translation.bind(work[stop:],S.abi.CodedPort(self.stage),self.view.context)
        self.control=SimpleNamespace(payloads=(field.tape,self.stage,*self.nums,context.tape),primitive_work=(2,3),primitive_context=(4,),services={('lambda-stage',self.sign):self.stage_table,('lambda-commit',):self.commit_table})
    def run(self):
        need(self.work is not None,'bound Lambda inventory')
        try:
            for t in self.work:M.retire(t)
            M.transfer(self.field.tape,self.stage)
            self.view.prepare();self.translation.run()
            M.Controller.primitive(self.control,('lambda-stage',self.sign),(0,1))
            M.Controller.primitive(self.control,('lambda-commit',),(0,1))
            self.calls+=1
        finally:
            if self.view.active:self.view.release()
            for t in self.work:M.retire(t)
            M.origin(self.field.tape);M.origin(self.context.tape)

def construct_source(site,port,native_factory):
    need(type(site)is int and type(port)is int,'exact typed source occurrence/port')
    rows=[r for r in lambda_sites() if r['site']==site and r['port']==port]
    need(len(rows)==1,'exact current Lambda source occurrence and port')
    r=rows[0];return LambdaProvider(r['q'],r['sign'],native_factory),r
