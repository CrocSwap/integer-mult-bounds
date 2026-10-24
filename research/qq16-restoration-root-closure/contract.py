"""Fail-closed source conformance checks for the written lifetime induction.

This is not a general Python escape analyser. The exact archive pin binds all
callee implementations; these structural obligations expose the proof's main
source dependencies and reject distinct invalidations before replay.
"""
import ast
from hashlib import sha256


def need(ok, message):
    if not ok:
        raise ValueError(message)


def methods(text, name):
    root=ast.parse(text)
    cls=next(n for n in root.body if isinstance(n,ast.ClassDef) and n.name==name)
    return {n.name:n for n in cls.body if isinstance(n,ast.FunctionDef)}


def targets(node):
    if isinstance(node,(ast.Tuple,ast.List)):
        return [n for value in node.elts for n in targets(value)]
    return [node]


def writes(function, receiver):
    result=[]
    for node in ast.walk(function):
        if isinstance(node,ast.Assign):
            values=node.targets
        elif isinstance(node,(ast.AnnAssign,ast.AugAssign)):
            values=[node.target]
        else:continue
        for target in values:
            for item in targets(target):
                if isinstance(item,ast.Attribute) and isinstance(item.value,ast.Name) and item.value.id==receiver:
                    result.append(item.attr)
    return result


def calls(function, receiver, member):
    return [n for n in ast.walk(function) if isinstance(n,ast.Call) and
            isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and
            (n.func.value.id,n.func.attr)==(receiver,member)]


def check(machine_text,binding_text,session_text):
    m=methods(machine_text,'Machine')
    sites={kind:{name:len(calls(fn,'self',kind)) for name,fn in m.items() if calls(fn,'self',kind)}
           for kind in ('new_context','restore_context','dispatch','run')}
    need(sites['new_context']=={'call':1,'load_root':1},'Closed new_context sites')
    need(sites['restore_context']=={'complete_return':1},'One literal restoration site')
    need(sites['dispatch']=={'run':1} and not sites['run'],'One iterative dispatcher and no recursive run')
    need(sum(isinstance(n,ast.While) for n in ast.walk(m['run']))==1,'One source dispatch loop')
    need(not any(isinstance(n,(ast.Yield,ast.YieldFrom,ast.Await)) for n in ast.walk(m['run'])),'No suspended run generator')
    allowed={'binding','topology','programs','arena','indices','roles','handoff','output','pool',
             'numerical','streams','header','context','program','size','depth','geometry_state',
             'pc','mode','root','closed','observe','counts'}
    need(set(a for fn in m.values() for a in writes(fn,'self'))<=allowed,'No unreviewed persistent Machine root')
    for field in ('context','program'):
        owners={name for name,fn in m.items() if field in writes(fn,'self')}
        need(owners=={'__init__','new_context','restore_context'},'Only the reviewed generation-root writers')
    need(set(writes(m['restore_context'],'context'))=={'ring','arena','raw','codes','q','dimension','cap','highs'},'Closed Context schema')
    need(set(writes(m['restore_context'],'ring'))=={'arena','raw','modulus','one'},'Closed Ring schema')
    returns=m['complete_return']
    body=returns.body[1:] if ast.get_docstring(returns) is not None else returns.body
    need(isinstance(body[0],ast.Expr) and ast.unparse(body[0].value)=='self.close_frame()',
         'Return closes the child frame first')
    need(len(calls(m['close_frame'],'self','close_geometry'))==1,'Close frame clears geometry')
    block=m['block']
    need(len(block.body)==4 and isinstance(block.body[1],ast.With) and isinstance(block.body[2],ast.If),
         'Block call occurs after its geometry scope')
    if_body=block.body[2].body
    need([ast.unparse(n.value) for n in if_body[:2]]==['self.close_geometry()','self.call(grants)'],
         'Block closes geometry before descent')
    need(any(isinstance(n,ast.Try) and any(calls(ast.Module(body=n.finalbody,type_ignores=[]),'trace','close'))
             for n in ast.walk(block)), 'Trace is closed before descent')
    root=ast.parse(binding_text)
    view=next(n for n in root.body if isinstance(n,ast.FunctionDef) and n.name=='view')
    need(writes(view,'result')==['code_bits','tape','index_arena','residue_arena'] or
         set(writes(view,'result'))=={'index_arena','residue_arena','code_bits','tape'} and len(writes(view,'result'))==4,
         'Program view has only fixed arena/code/Tape edges')
    need(isinstance(view.body[-1],ast.Return) and ast.unparse(view.body[-1].value)=='result','Program view returns its plain wrapper')
    for cls in ('SelectedBinding','ToyBinding'):
        for name,fn in methods(binding_text,cls).items():
            if name!='__init__':need(not writes(fn,'self'),'Binding does not retain dynamic runtime values')
    session=methods(session_text,'RootSession')
    need(not any(field in ('context','program') for fn in session.values() for field in writes(fn,'self')),
         'RootSession does not add generation aliases')
    for name in ('rearm','finish','erase_work'):
        need(name in session,'Complete root-reuse lifecycle')
    return {'replacement_sites':sites,'persistent_root_fields':sorted(allowed),
            'generation_writers':['__init__','new_context','restore_context'],
            'closed_binding_classes':['SelectedBinding','ToyBinding'],
            'root_session_adds_generation_roots':False,
            'source_methods_ast_sha256':{name:sha256(ast.dump(m[name],include_attributes=False).encode()).hexdigest()
                for name in ('run','dispatch','block','call','complete_return','new_context','restore_context','close_frame','erase_work')},
            'scope':'Exact pinned source plus exposed structural proof obligations, not general escape analysis.'}


def controls(machine,binding,session):
    mutants=[('retained_context_history',machine.replace('self.context = context','self.context = context\n        self.history = context',1),binding,session),
             ('recursive_run',machine.replace('action = self.dispatch(operation)','action = self.run()',1),binding,session),
             ('unclosed_return',machine.replace('        self.close_frame()\n        if self.root:', '        self.pool.empty()\n        if self.root:',1),binding,session),
             ('program_runtime_backedge',machine,binding.replace('    result.tape = tape','    result.tape = tape\n    result.runtime = runtime',1),session)]
    rejected={}
    for name,ma,bi,se in mutants:
        try:check(ma,bi,se)
        except ValueError as error:rejected[name]=str(error)
        else:raise ValueError('Invalid source contract accepted: '+name)
    return rejected
