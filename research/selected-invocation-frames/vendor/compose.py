"""Compose real Compact adapters around an exact child and caller return.

The arithmetic/adapter/parking primitives are unchanged credited predecessors.
"""
from dataclasses import asdict
import pipeline as prior
import compact,monomial
from streams import copy,need
from arithmetic import c_axis

def layout(bits):
    return compact.Layout((('u',1),('t',1),('spectator',1))+
                          tuple(('v'+str(j),2) for j in range(4))+(('b',1),),2*bits)

def rows_adapter(source,lay,recipe,bits,outer,inverse=False,fault=None):
    size=lay.records*lay.record_bits
    need(len(source.data)==outer*size,'complete outer rows')
    source.rewind();out=prior.TrackingTape(source.meter)
    for _ in range(outer):
        row=prior.TrackingTape(source.meter);copy(source,row,size);row.rewind()
        old=monomial.execute
        if fault in ('omit_repair','wrong_inverse_key'):
            def changed(tape,layout,word):
                return old(tape,layout,word,omit_repair=fault=='omit_repair',wrong_inverse=fault=='wrong_inverse_key')
            monomial.execute=changed
        try:
            row=monomial.execute_monomial(row,lay,recipe,2,1,1,0,bits,inverse,
                                          omit_tensor_constant=fault=='single_constant_phase')
        finally: monomial.execute=old
        copy(row,out,size);row.finish();row.erase()
    source.finish();source.erase();out.rewind();return out

def child(source,recipe,grid,outer_rows,coefficients,inverse=False,round_child=False,fault=None):
    need(coefficients==1,'one Gaussian coefficient per complete record')
    lay=layout(grid.bits)
    first,last=('left','right') if inverse else ('right','left')
    source=rows_adapter(source,lay,recipe[first],grid.bits,outer_rows,inverse,fault)
    axes=[lay.position('v0',k) for k in range(2)]
    for axis in reversed(axes) if inverse else axes:
        source=c_axis(source,lay.bits,axis,1,grid,inverse,outer_rows)
    if round_child:
        values=prior.decode(source.data,grid.bits)
        values=[tuple((1 if x>=0 else -1)*(abs(x)//16)*16 for x in pair) for pair in values]
        changed=prior.TrackingTape(source.meter,prior.encode(values,grid.bits));source.erase();source=changed
    source=rows_adapter(source,lay,recipe[last],grid.bits,outer_rows,inverse,fault)
    need(not grid.workspace and source.head==0,'arithmetic and head returned')
    return source

def invoke(active,inactive,park,recipe,grid,outer,inverse=False,fault=None):
    # Reuse PR2483's literal parking/argument/return wrapper with our full child.
    old=prior.child
    def dispatch(tape,recipe,grid,outer_rows,coefficients,inverse=False,round_child=False):
        return child(tape,recipe,grid,outer_rows,coefficients,inverse,round_child,fault)
    prior.child=dispatch
    try: return prior.invoke(active,inactive,park,recipe,grid,outer,1,inverse)
    finally: prior.child=old

def report(meter,grid,park):
    return {'meter':asdict(meter),'arithmetic_bit_work':grid.arithmetic_steps,
            'exact_divisions':grid.exact_divisions,'peak_arithmetic_words':grid.peak_words,
            'peak_tape_bits':meter.peak,'parking_peak':park.peak,'parking_floor':park.floor}
