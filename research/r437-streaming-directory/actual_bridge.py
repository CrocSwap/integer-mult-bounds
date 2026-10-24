"""Actual64 calibration restriction of the same consumer code.

This visitor reads two already selected complete prefixes. It does NOT execute
or claim the complete 3**4096 production domain. The ordinary run uses visit.
JoyboyBrian; substantial OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
from types import FunctionType
import importlib.util
from cardinal_counts import Count,positive
from stream import Counter
from words import BLANK,Unsigned,need
import packet
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r437_stream_actual_body',HERE/'streaming.py')
body=importlib.util.module_from_spec(spec);spec.loader.exec_module(body)

def run(source,target,events,layout,prefixes,prefix_count,field_count,coefficient,context,old_count,observe=None):
    need(len({id(source),id(target),id(prefixes)})==3,'distinct streamed borrowed roles')
    positive(prefix_count);positive(old_count);positive(context.highs)
    total=Count.product(old_count,context.highs)
    try:need(total.equals(prefix_count),'complete calibration prefix product')
    finally:total.close()
    def selected(old,fields,count,code,ctx,consume):
        remaining=Counter(prefix_count)
        try:
            old.rewind()
            while not remaining.finished:
                prefix=packet.read_prefix(old,field_count)
                try:consume(prefix)
                finally:prefix.clear()
                remaining.decrement()
            need(old.read()==BLANK,'complete calibration selected directory')
            return Count(prefix_count)
        finally:old.rewind();remaining.close()
    one=field_count.arena.literal(1)
    previous,borrow=Unsigned(field_count.arena).subtract(field_count,one)
    field_count.arena.free(one)
    need(not borrow,'positive calibration field count')
    run_body=FunctionType(body.run.__code__,dict(body.run.__globals__,visit=selected),body.run.__name__,body.run.__defaults__)
    try:return run_body(source,target,events,layout,prefixes,previous,old_count,0,context,coefficient,observe)
    finally:field_count.arena.free(previous)
