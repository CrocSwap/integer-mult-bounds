"""Shared trace on complete prefixes, with the caller's full two-bank layout."""
from bitstream import copy_bits
from packet import read_prefix
from records import Tape
from stream import Counter
from stream_runner import action
from words import BLANK, need


def run(source,events,layout,directory,prefix_count,field_count,coefficient,factory=Tape,observe=None):
    fibre=layout.fibre()
    current,active=source,None
    try:
        for event in events:
            if event.kind=="enter":
                need(active is None and event.parent_identity is layout.geometry.parent_identity,
                     "one whole-packet completed child")
                active=event
                if observe is not None:observe("enter")
                continue
            if event.kind=="return":
                need(active is not None and active.parent_identity is event.parent_identity and
                     (active.child_kind,active.field,active.reverse,active.half,active.source_code)==
                     (event.child_kind,event.field,event.reverse,event.half,event.source_code),
                     "same completed child returns")
                for a,b in ((active.first,event.first),(active.second,event.second),
                            (active.width,event.width),(active.depth,event.depth)):
                    need(layout.geometry.raw.compare(a,b)==0,"restored child geometry")
                active=None
                if observe is not None:observe("return")
                continue
            output,prefixes=factory(),Counter(prefix_count)
            directory.rewind()
            try:
                need(not prefixes.finished,"nonempty complete prefix packet")
                while not prefixes.finished:
                    fields=read_prefix(directory,field_count)
                    local,changed=factory(),None
                    try:
                        copy_bits(current,local,fibre);local.rewind()
                        changed=action(local,event,layout,lambda request:coefficient(fields,request),factory)
                        copy_bits(changed,output,fibre)
                        need(changed.read()==BLANK,"complete changed prefix fibre")
                    finally:
                        if changed is not None and changed is not local:changed.clear()
                        local.clear();fields.clear()
                    prefixes.decrement()
                need(current.read()==directory.read()==BLANK,"complete shared packet and directory")
                current.rewind();directory.rewind()
                if current is not source:current.clear()
                output.rewind();current=output
            except ValueError:
                output.clear()
                raise
            finally:prefixes.close()
        need(active is None,"complete child lifetime")
        return current
    except ValueError:
        if current is not source:current.clear()
        raise
    finally:
        fibre.close();directory.rewind();source.rewind()
        events.close()
