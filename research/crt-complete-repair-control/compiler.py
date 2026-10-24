"""Static AST lowering of the retained finite-control source, not a runtime evaluator.

JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
No runtime Python function, AST, numeric loop bound or source callable survives.
"""
import ast

C=lambda x:('c',x)
R=lambda x:('r',x)

class Compiler:
    def __init__(self,sources,key):
        self.functions={}
        for ns,text in sources.items():
            tree=ast.parse(text)
            self.functions[ns]={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
        self.code=[];self.serial=0;self.roles=[];self.key=key;self.calls=[];self.key_sites=[]
        self.globals={'LEFT':C('<'),'END':C('>'),'BLANK':C('_'),'SKIP':C(('S',False,False,'0','0'))}
    def fresh(self):self.serial+=1;return 'v'+str(self.serial)
    def emit(self,*a):self.code.append(a);return len(self.code)-1
    def patch(self,i,*a):self.code[i]=a
    def value(self,expr,env,ns):
        if isinstance(expr,ast.Constant):return C(expr.value)
        if isinstance(expr,ast.Name):return env.get(expr.id,self.globals.get(expr.id)) or self.fail(expr)
        if isinstance(expr,ast.Tuple):return ('tuple',tuple(self.value(x,env,ns) for x in expr.elts))
        if isinstance(expr,ast.UnaryOp):
            a=self.value(expr.operand,env,ns)
            if isinstance(expr.op,ast.USub) and a[0]=='c':return C(-a[1])
            if isinstance(expr.op,ast.Not):
                if a[0]=='c':return C(not a[1])
                z=R(self.fresh());self.emit('not',a,z[1]);return z
        if isinstance(expr,ast.Compare):
            if len(expr.ops)!=1:raise ValueError('chained compare')
            a=self.value(expr.left,env,ns);b=self.value(expr.comparators[0],env,ns)
            op={ast.Eq:'eq',ast.NotEq:'ne',ast.Is:'eq',ast.IsNot:'ne',ast.In:'in',ast.NotIn:'notin'}[type(expr.ops[0])]
            if a[0]=='c' and b[0]=='c':return C(self.compare(op,a[1],b[1]))
            z=R(self.fresh());self.emit(op,a,b,z[1]);return z
        if isinstance(expr,ast.BoolOp):
            z=R(self.fresh());ends=[]
            for i,x in enumerate(expr.values):
                a=self.value(x,env,ns);self.emit('copy',a,z[1])
                if i+1<len(expr.values):
                    j=self.emit('branch',z,None,None);ends.append(j)
                    self.patch(j,'branch',z,len(self.code) if isinstance(expr.op,ast.And) else None,None if isinstance(expr.op,ast.And) else len(self.code))
            end=len(self.code)
            for j in ends:
                op,a,t,f=self.code[j];self.patch(j,op,a,end if t is None else t,end if f is None else f)
            return z
        if isinstance(expr,ast.IfExp):
            test=self.value(expr.test,env,ns)
            if test[0]=='c':return self.value(expr.body if test[1] else expr.orelse,env,ns)
            z=R(self.fresh());j=self.emit('branch',test,None,None);start=len(self.code)
            a=self.value(expr.body,env,ns);self.emit('copy',a,z[1]);end=self.emit('jump',None);other=len(self.code)
            b=self.value(expr.orelse,env,ns);self.emit('copy',b,z[1]);self.patch(j,'branch',test,start,other);self.patch(end,'jump',len(self.code));return z
        if isinstance(expr,ast.Subscript):
            a=self.value(expr.value,env,ns);i=ast.literal_eval(expr.slice)
            if not isinstance(i,int) or i<0:raise ValueError('fixed field projection only')
            if a[0]=='tuple':return a[1][i]
            z=R(self.fresh());self.emit('field',a,i,z[1]);return z
        if isinstance(expr,ast.Call):
            if isinstance(expr.func,ast.Attribute):
                role=self.value(expr.func.value,env,ns);op=expr.func.attr
                if expr.keywords or len(expr.args)!=(0 if op=='read' else 1):raise ValueError('method arity')
                if op=='read':
                    z=R(self.fresh());self.emit('read',role,z[1]);return z
                if op in ('write','move'):
                    a=self.value(expr.args[0],env,ns)
                    if op=='move' and (a[0]!='c' or a[1] not in (-1,1)):raise ValueError('unit move only')
                    self.emit(op,role,a);return C(None)
                raise ValueError('unsupported method '+op)
            name=expr.func.id
            if name in ('Tape','frozenset') and (expr.args or expr.keywords):raise ValueError('nonempty constructor')
            if name=='Tape':
                role='work'+str(len(self.roles));self.roles.append(role);return C(role)
            if name=='frozenset':return C(frozenset())
            args=[self.value(x,env,ns) for x in expr.args]
            if name=='is_record':
                z=R(self.fresh());self.emit('record',args[0],z[1]);return z
            if name=='key_port':
                self.inline_key(args[0],args[1]);return C(None)
            if name=='increment':return self.call('scanner','increment_and_return',args,{})
            if name=='evaluate_key':self.inline_key(args[0],args[1]);return C(None)
            if name=='mark':return C(None)
            return self.call(ns,name,args,{k.arg:self.value(k.value,env,ns) for k in expr.keywords})
        return self.fail(expr)
    @staticmethod
    def compare(op,a,b):
        if op=='eq':return a==b
        if op=='ne':return a!=b
        if op=='in':return a in b
        if op=='notin':return a not in b
        raise ValueError(op)
    def fail(self,n):raise ValueError('unsupported AST '+ast.dump(n))
    def assign(self,target,v,env):
        if isinstance(target,ast.Tuple):
            if v[0]!='tuple':
                for i,t in enumerate(target.elts):
                    z=R(self.fresh());self.emit('field',v,i,z[1]);self.assign(t,z,env)
            else:
                for t,a in zip(target.elts,v[1],strict=True):self.assign(t,a,env)
            return
        if not isinstance(target,ast.Name):return self.fail(target)
        # Static aggregates contain only a fixed finite number of values/roles.
        if v[0]=='tuple':env[target.id]=v;return
        if target.id not in env or env[target.id][0]!='r':env[target.id]=R(self.fresh())
        self.emit('copy',v,env[target.id][1])
    def block(self,body,env,ns,returns,breaks,handler):
        for n in body:
            if isinstance(n,ast.Expr):
                if not isinstance(n.value,ast.Constant):self.value(n.value,env,ns)
            elif isinstance(n,ast.Assign):
                v=self.value(n.value,env,ns)
                for t in n.targets:self.assign(t,v,env)
            elif isinstance(n,ast.If):
                t=self.value(n.test,env,ns)
                if t[0]=='c':self.block(n.body if t[1] else n.orelse,env,ns,returns,breaks,handler);continue
                j=self.emit('branch',t,None,None);a=len(self.code);self.block(n.body,env,ns,returns,breaks,handler);end=self.emit('jump',None);b=len(self.code);self.block(n.orelse,env,ns,returns,breaks,handler);self.patch(j,'branch',t,a,b);self.patch(end,'jump',len(self.code))
            elif isinstance(n,ast.While):
                if n.orelse:raise ValueError('while else unsupported')
                start=len(self.code);t=self.value(n.test,env,ns);j=self.emit('branch',t,None,None);a=len(self.code);local=[];self.block(n.body,env,ns,returns,local,handler);self.emit('jump',start);end=len(self.code);self.patch(j,'branch',t,a,end)
                for k in local:self.patch(k,'jump',end)
            elif isinstance(n,ast.For):
                if n.orelse or not isinstance(n.target,ast.Name):raise ValueError('for else/target unsupported')
                seq=self.value(n.iter,env,ns)
                if seq[0]!='tuple':raise ValueError('only static finite for tuple')
                for v in seq[1]:
                    env[n.target.id]=v;self.block(n.body,env,ns,returns,breaks,handler)
            elif isinstance(n,ast.Break):breaks.append(self.emit('jump',None))
            elif isinstance(n,ast.Return):
                val=C(None) if n.value is None else self.value(n.value,env,ns)
                self.emit('copy',val,returns[0]);returns[1].append(self.emit('jump',None))
            elif isinstance(n,ast.Raise):self.emit('halt','reject')
            elif isinstance(n,ast.Try):
                if n.orelse or n.finalbody:raise ValueError('try else/finally unsupported')
                if any(not isinstance(h.type,ast.Name) or h.type.id!='ValueError' or h.name for h in n.handlers):raise ValueError('exception handler unsupported')
                # Valid-domain theorem only; reject paths explicitly do not roll back.
                self.block(n.body,env,ns,returns,breaks,handler)
            else:self.fail(n)
    def call(self,ns,name,args,kwargs):
        if (ns,name) in self.calls:raise ValueError('recursive source not admitted')
        fn=self.functions[ns][name];env={};params=[a.arg for a in fn.args.args]
        if fn.decorator_list or fn.args.vararg or fn.args.kwarg or fn.args.kwonlyargs or fn.args.posonlyargs:raise ValueError('function signature unsupported')
        if len(args)>len(params) or any(k not in params or k in params[:len(args)] for k in kwargs):raise ValueError('call arguments unsupported')
        defaults=dict(zip(params[len(params)-len(fn.args.defaults):],fn.args.defaults))
        for i,p in enumerate(params):
            if i<len(args):env[p]=args[i]
            elif p in kwargs:env[p]=kwargs[p]
            elif p in defaults:env[p]=self.value(defaults[p],env,ns)
            else:raise ValueError('missing static parameter '+p)
        # Preallocate mutable locals before compiling either arm or a loop condition.
        # Without this, the first condition could refer to an old argument register.
        assigned={n.id for n in ast.walk(fn) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Store)}
        for p in sorted(assigned):
            if p in env:
                v=env[p];env[p]=R(self.fresh());self.emit('copy',v,env[p][1])
            else:env[p]=R(self.fresh())
        out=self.fresh();returns=(out,[]);self.calls.append((ns,name));self.block(fn.body,env,ns,returns,[],None);self.calls.pop()
        for j in returns[1]:self.patch(j,'jump',len(self.code))
        return R(out)
    def inline_key(self,counter,stream):
        start=len(self.code);key=self.key;self.key_sites.append((start,start+len(key)))
        mapping={'counter':counter,'stream':stream,'rom':C('rom')}
        for role in ('h','s','offset','target','out','count','col','row','limit','u','t','y'):mapping[role]=C('key_'+role)
        end=start+len(key)
        for op,*a in key:
            reg=lambda x:R('keyreg_'+x)
            if op=='read':self.emit('read',mapping[a[0]],reg(a[1])[1])
            elif op=='write':self.emit('write',mapping[a[0]],C(a[1]))
            elif op=='write_reg':self.emit('write',mapping[a[0]],reg(a[1]))
            elif op=='move':self.emit('move',mapping[a[0]],C(a[1]))
            elif op=='set':self.emit('copy',C(a[1]),reg(a[0])[1])
            elif op=='copy':self.emit('copy',reg(a[0]),reg(a[1])[1])
            elif op=='eq':self.emit('eq',reg(a[0]),C(a[1]),reg(a[2])[1])
            elif op=='eq_reg':self.emit('eq',reg(a[0]),reg(a[1]),reg(a[2])[1])
            elif op in ('xorbit','andbit','orbit'):self.emit(op,reg(a[0]),reg(a[1]),reg(a[2])[1])
            elif op=='branch':self.emit('branch',reg(a[0]),start+a[1],start+a[2])
            elif op=='jump':self.emit('jump',start+a[0])
            elif op=='halt':self.emit('jump',end) if a[0]=='accept' else self.emit('halt','reject')
            else:raise ValueError('unlowered key opcode '+op)
