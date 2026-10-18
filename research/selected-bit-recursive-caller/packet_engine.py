"""Shared trace on complete prefixes, with the caller's full two-bank layout."""
from bitstream import copy_bits
from packet import read_prefix
from records import Tape
from stream import Counter
from stream_runner import action
from words import BLANK, need
from scheduler import Invocation, complete


def run_generator(source,events,layout,directory,prefix_count,field_count,coefficient,factory=Tape,observe=None,invoke=None):
    fibre=layout.fibre()
    current,active=source,None
    boundary_words=[]
    boundary_labels=None
    returned=False
    internal=invoked=False
    try:
        for event in events:
            if event.kind=="enter":
                need(active is None and event.parent_identity is layout.geometry.parent_identity,
                     "one whole-packet completed child")
                active=event
                boundary_labels=(event.child_kind,event.field,event.reverse,event.half,
                                 event.source_code,event.parent_identity)
                boundary_words=[layout.geometry.index.copy(getattr(event,name))
                                for name in ("first","second","width","depth")]
                internal=layout.geometry.raw.compare(event.width,layout.geometry.leaf_cutoff)>=0
                invoked=False
                if observe is not None:observe("enter")
                continue
            if event.kind=="return":
                need(active is not None and boundary_labels==
                     (event.child_kind,event.field,event.reverse,event.half,
                      event.source_code,event.parent_identity),
                     "same completed child returns")
                for saved,name in zip(boundary_words,("first","second","width","depth")):
                    need(layout.geometry.raw.compare(saved,getattr(event,name))==0,"restored child geometry")
                need(invoked==internal,"exactly one internal invocation before return")
                layout.geometry.index.free_many(*boundary_words);boundary_words=[]
                active=None
                boundary_labels=None
                if observe is not None:observe("return")
                continue
            if event.kind=="invoke":
                need(active is not None and internal and not invoked and invoke is not None,
                     "exactly one bound recursive child consumer")
                need(boundary_labels==(event.child_kind,event.field,event.reverse,event.half,
                                       event.source_code,event.parent_identity),
                     "invoke matches entered child")
                for saved,name in zip(boundary_words,("first","second","width","depth")):
                    need(layout.geometry.raw.compare(saved,getattr(event,name))==0,
                         "invoke has the entered child geometry")
                following=yield Invocation(invoke(current,event))
                need(following is not current,"recursive child returns its owned output")
                if current is not source:current.clear()
                current=following
                invoked=True
                continue
            need(active is None or not internal,"internal body is exclusively a whole-packet invocation")
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
        returned=True
        return current
    finally:
        # A deeper failure closes suspended parents with GeneratorExit. Owned
        # output must be erased on that path as well as ordinary ValueError.
        if not returned and current is not source:current.clear()
        fibre.close();directory.rewind();source.rewind()
        if boundary_words:layout.geometry.index.free_many(*boundary_words)
        events.close()


def run(*args,**kwargs):
    return complete(run_generator(*args,**kwargs))
