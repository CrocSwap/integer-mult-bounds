#!/usr/bin/env python3
"""Nonconstant multi-axis delivery controls, separate from actual Full replay.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
These small service fixtures are not relabelled as Full compiler outputs.
"""
from copy import copy
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace,ModuleType
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from physical_sources import need,opened
from verify_physical import actual,reject,floor_table,certify_table,certified_floors


def cases():
    from compiler import Hadamard,Diagonal
    from reference import FreshSemanticService
    first = (
        (((7,3),(0,0)),((9,-2),(-5,4)),((5,1),(8,-1))),
        (((-3,6),(8,0)),((1,2),(9,-4)),((0,0),(7,3))),
    )
    second = (
        (((6,-1),(-3,4)),((0,0),(7,2)),((8,1),(4,-2))),
        (((8,0),(3,-5)),((7,1),(2,6)),((5,2),(0,0))),
    )
    events = tuple(Diagonal(step,1,1,3,3,18,8,18,40,pages)
                   for step,pages in enumerate((first,second)))
    program = SimpleNamespace(array_bits=4,coarse_bits=1,axis_bits=1,axes=3,bits=3,
        data_width=18,factor_width=8,cache_width=18,temporary_width=40,incoming=3,
        radius_bits=5,stages=2,h_count=0,diagonal_count=2)
    program.validate = lambda: [event.validate() for event in events]
    program.events = lambda: iter(events)
    values = [(8*(i%5-2)+1,8*((3*i)%7-3)+2) for i in range(16)]
    oracle = FreshSemanticService()
    expected = list(values)
    for event in events:
        oracle.apply_diagonal(expected,event)
    need(oracle.stats['nonzero_roundings'] > 0,'nontrivial signed cache/data rounding fixture')
    base = dict(label='synthetic three-axis/two-label/two-diagonal service',program=program,
        values=values,expected=expected,event_types=(Hadamard,Diagonal),
        allocation=dict(records=16,axes=3,coarse_labels=2,F=3,W=18,stages=2),
        semantic_work=dict(global_diagonals=2),oracle_work=oracle.stats,
        root_error_squared_sha256='not applicable: explicit service fixture')
    mutants = {}
    for name,changed in (
        ('wrong_coarse_page', (replace(events[0],pages=(first[0],first[0])),events[1])),
        ('wrong_axis_order', (replace(events[0],pages=tuple(tuple(reversed(block)) for block in first)),events[1])),
        ('stale_stage_pages', (events[0],replace(events[1],pages=first))),
    ):
        wrong = list(values)
        service = FreshSemanticService()
        for event in changed:
            service.apply_diagonal(wrong,event)
        need(wrong != expected,'semantic mutant discriminates: '+name)
        altered = copy(program)
        altered.events = lambda changed=changed:iter(changed)
        altered.validate = lambda changed=changed:[event.validate() for event in changed]
        mutants[name] = dict(base,program=altered,label=name)
    rounding = copy(program)
    rounding.array_bits,rounding.coarse_bits,rounding.axes = 2,0,2
    rounding.data_width,rounding.factor_width,rounding.cache_width,rounding.temporary_width = 12,6,12,28
    rounding.radius_bits,rounding.stages,rounding.diagonal_count = 1,1,1
    rounding_event = Diagonal(0,0,1,2,3,12,6,12,28,
        ((((2,2),(8,0)),((3,3),(0,0))),))
    rounding.validate = rounding_event.validate
    rounding.events = lambda:iter((rounding_event,))
    rounding_values = [(8,0),(2,2),(0,0),(0,0)]
    rounding_expected = list(rounding_values)
    rounding_oracle = FreshSemanticService()
    rounding_oracle.apply_diagonal(rounding_expected,rounding_event)
    need(rounding_expected == [(0,1),(0,1),(0,0),(0,0)],'cache and data complete-numerator rounding witnesses')
    rounding_case = dict(base,program=rounding,label='separate cache/data premature-truncation witnesses',
        values=rounding_values,expected=rounding_expected,oracle_work=rounding_oracle.stats,
        allocation=dict(records=4,axes=2,coarse_labels=1,F=3,W=12,stages=1),
        semantic_work=dict(global_diagonals=1))
    for name in ('sources','compiler','reference'):
        sys.modules.pop(name,None)
    return base,mutants,rounding_case


def premature(self,left,right,word_width,fractional,output_width,temporary_width,output,kind):
    from ring_words import truncate,difference,add,write_signed
    from router_metadata import owned
    with owned(self.arithmetic.multiply(left[0],right[0],word_width),
               self.arithmetic.multiply(left[1],right[1],word_width),
               self.arithmetic.multiply(left[0],right[1],word_width),
               self.arithmetic.multiply(left[1],right[0],word_width)) as raw:
        with owned(*(truncate(value,fractional) for value in raw)) as rounded:
            with owned(difference(rounded[0],rounded[1]),add(rounded[2],rounded[3])) as result:
                for value in result:
                    write_signed(value,output,output_width)
    self.note(kind)


def floor_controls():
    from cardinal_counts import Count
    import active_plan
    bases = (1,609,610)
    table = floor_table(bases)
    table[(997,1000,609)] += 1
    wrong = reject(lambda:certify_table(table,bases),'exact finite metadata floor certificate')
    def fallback(*args):
        raise ValueError('actual original-helper fallback reached')
    value = Count.literal(611)
    try:
        with patch.object(active_plan,'floor_power',fallback):
            with certified_floors(bases) as (_,_,misses):
                delegated = reject(lambda:active_plan.floor_power(value,997,1000),
                                   'actual original-helper fallback reached')
                need(misses == [[997,1000]],'declared out-of-domain delegation')
    finally:
        value.close()
    return dict(wrong_entry=wrong,out_of_domain=delegated,
                limitation='Sentinel proves delegation; this control does not execute the expensive original power.')


def main():
    base,mutants,rounding_case = cases()
    cold_aliases = {}
    def probe():
        with opened():
            raise ValueError('unexpected accepted cold alias')
    for name in ('word_product','ring_words','fft_arithmetic'):
        with patch.dict(sys.modules,{name:ModuleType(name)}):
            cold_aliases[name] = reject(probe,'one cold Full/word/H cohort per process')
    with opened():
        positive = actual(base,reuse=True)
        controls = {name:reject(lambda case=case:actual(case),
                               'actual complete physical Full endpoint equals independent oracle')
                    for name,case in mutants.items()}
        rounded = actual(rounding_case)
        from physical_engine import FullPhysical
        correct = FullPhysical.product
        for role in ('coefficient_products','data_products'):
            def altered(self,*args,role=role):
                return (premature if args[-1] == role else correct)(self,*args)
            with patch.object(FullPhysical,'product',altered):
                controls['premature_'+role] = reject(lambda:actual(rounding_case),
                    'actual complete physical Full endpoint equals independent oracle')
        invalid = dict(rounding_case,values=[(31,0)]*4)
        controls['actual_input_radius'] = reject(lambda:actual(invalid),
                                                'physical complete input Euclidean radius')
        unobserved = actual(rounding_case,diagnostics=False)
        need(unobserved['output_sha256'] == rounded['output_sha256']
             and unobserved['physical_tape_actions'] == rounded['physical_tape_actions'],
             'observer erasure preserves actual endpoint and literal tape actions')
        passive = unobserved['passive_state']
        need(passive['word_products'] == 0
             and all(value == 0 for value in passive['word_calls'].values())
             and all(value == 0 for value in passive['program_calls'].values())
             and all(value == 0 for value in passive['wrapper_calls'].values()),
             'production passive counters remain finite zero values')
        floors = floor_controls()
    result = dict(status='PASS_PHYSICAL_FULL_CONTROLS',positive=positive,
                  rounding_witnesses=rounded,executed_physical_endpoint_mutants=controls,
                  observer_erasure=unobserved,metadata_floor_controls=floors,
                  preloaded_scalar_module_controls=cold_aliases)
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__ == '__main__':
    main()
