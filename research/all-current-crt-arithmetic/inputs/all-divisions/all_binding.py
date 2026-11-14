"""Every raw division of the exact current producer uses the frozen core.

Finite64-slot metadata, source control and grant services remain retained.
Counters and optional observations are verifier instrumentation. Apache2.0;
prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
"""
from contextlib import contextmanager

def make_binding(base_binding):
    class AllBinding(base_binding.Binding):
        @contextmanager
        def install(self,m):
            base_binding.need(self.iterator is not None,'current source and explicit descriptor grants')
            old_raw=m.w.Unsigned.divmod
            producers=(m.numeric,m.subtractive)
            old_produce=tuple(module.produce for module in producers)
            owner=self;owner.active_arena=None
            def raw(obj,n,d):
                owner.raw_calls+=1;owner.finite_control_invoice+=16
                base_binding.need(owner.active and obj.arena is owner.active_arena,
                                  'raw division must belong to the active exact current producer')
                return owner.divide(obj,n,d)
            def wrap(original):
                def produce(arena,left,right,words,records,**kwargs):
                    base_binding.need(not owner.active,'one current producer at a time')
                    owner.finite_control_invoice+=32;owner.invocations+=1
                    owner.active=True;owner.active_arena=arena
                    if owner.observer:owner.observer('producer_before',owner,arena,left,right,None)
                    try:
                        result=original(arena,left,right,words,records,**kwargs)
                        if owner.observer:owner.observer('producer_after',owner,arena,left,right,result)
                        return result
                    finally:owner.active=False;owner.active_arena=None
                return produce
            m.w.Unsigned.divmod=raw
            for module,original in zip(producers,old_produce):module.produce=wrap(original)
            try:yield self
            finally:
                m.w.Unsigned.divmod=old_raw
                for module,original in zip(producers,old_produce):module.produce=original
    return AllBinding
