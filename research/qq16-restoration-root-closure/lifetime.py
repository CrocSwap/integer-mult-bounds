"""Nonretaining test observer for the literal restoration-generation invariant.

Weak references, host GC and graph introspection are checker mechanisms, not a
paid implementation or a bound on all Python objects/physical backing.
"""
from contextlib import contextmanager
import gc
import weakref


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Lifetime:
    def __init__(self, fault=None):
        self.generations = []
        self.dispatch_depth = 0
        self.peak = 0
        self.new_calls = self.restore_calls = self.dispatches = 0
        self.completed_replacement_dispatches = 0
        self.terminal_records = self.run_return_records = None
        self.fault = fault

    def live(self):
        return sum(reference() is not None for generation in self.generations for reference in generation)

    def fields(self, runtime, origin):
        context, program = runtime.context, runtime.program
        ring = context.ring
        values = (context,ring,context.raw,context.highs,program)
        ring_order = ('modulus','arena','raw','one') if origin=='new' else ('arena','raw','modulus','one')
        expected = [('ring','arena','raw','codes','q','dimension','cap','highs'),ring_order,
                    ('arena',),('tape',),('index_arena','residue_arena','code_bits','tape')]
        need(all(tuple(vars(value))==order for value,order in zip(values,expected)), 'Literal generation schemas')
        need(context.raw is ring.raw and context.arena is ring.arena is runtime.arena, 'Shared raw and residue arena')
        need(program.index_arena is runtime.indices and program.residue_arena is runtime.arena, 'Fixed program arenas')
        need(context.highs.tape is runtime.roles['highs'] and program.tape is runtime.roles['program'], 'Fixed Tape aliases')
        need(context.codes is runtime.binding.codes, 'Fixed codebook')
        need(len({id(value) for value in values})==5, 'Five distinct generation records')
        return tuple(weakref.ref(value) for value in values)

    def register(self, runtime, origin):
        generation = self.fields(runtime,origin)
        self.generations.append(generation)
        gc.collect()
        current = self.live()
        self.peak = max(self.peak,current)
        need(current<=10, 'At most old and new generation records')

    def stable(self):
        gc.collect()
        need(self.live()==5, 'Only the current generation at a closed dispatch')

    @contextmanager
    def instrument(self, cls):
        observer = self
        saved = {name:getattr(cls,name) for name in ('new_context','restore_context','dispatch','run')}
        def constructor(origin):
            original = saved[origin+'_context' if origin=='new' else 'restore_context']
            def wrapped(runtime,*args,**kwargs):
                need(runtime.observe is None, 'No retaining source observer in the closed algorithm')
                gc.collect()
                need(observer.live()<=5, 'One generation before replacement')
                if observer.fault in ('binding_history','boundary_backedge') and runtime.context is not None:
                    if observer.fault=='binding_history':
                        runtime.binding.history = runtime.context
                    else:
                        runtime.arena.history = runtime.context
                result = original(runtime,*args,**kwargs)
                if observer.fault=='program_backedge' and observer.generations:
                    runtime.program.previous = observer.generations[-1][-1]()
                if origin=='new':observer.new_calls+=1
                else:observer.restore_calls+=1
                observer.register(runtime,origin)
                return result
            return wrapped
        def dispatch(runtime,*args,**kwargs):
            need(observer.dispatch_depth==0, 'No suspended previous dispatcher')
            observer.dispatch_depth+=1
            before=len(observer.generations)
            try:
                action=saved['dispatch'](runtime,*args,**kwargs)
            finally:
                observer.dispatch_depth-=1
            observer.dispatches+=1
            if len(observer.generations)!=before:
                observer.completed_replacement_dispatches+=1
                observer.stable()
            if action=='done':
                observer.stable()
                observer.terminal_records=observer.live()
            return action
        def run(runtime,*args,**kwargs):
            result=saved['run'](runtime,*args,**kwargs)
            observer.stable()
            observer.run_return_records=observer.live()
            return result
        cls.new_context,cls.restore_context=constructor('new'),constructor('restore')
        cls.dispatch,cls.run=dispatch,run
        try:
            yield
        finally:
            for name,method in saved.items():setattr(cls,name,method)

    def result(self):
        return {'new_contexts':self.new_calls,'restorations':self.restore_calls,
                'dispatches':self.dispatches,'replacement_dispatches':self.completed_replacement_dispatches,
                'registered_generations':len(self.generations),'peak_live_generation_records':self.peak,
                'terminal_dispatch_records':self.terminal_records,'run_return_records':self.run_return_records,
                'observer_uses_weak_references':True}
