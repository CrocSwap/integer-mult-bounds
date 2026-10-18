"""Complete Boolean model with linear provenance attached by the checker."""
from collections import Counter, deque
from contextlib import contextmanager
from hashlib import sha256
import sys
from time import monotonic

import bitstream
import cardinality
from cardinal_counts import Count
from check_support import audit, bits, no_decode
import counts
from directory import Context
import driver
import fresh_rows
import model
import node
import packet
import packet_engine
from records import Tape
import stream
from words import Arena, BLANK, LEFT, ONE, Ring, ZERO, need


class Tracker:
    def __init__(self):
        self.last=None;self.recent=deque(maxlen=2);self.xor=False
        self.live=set();self.erased=0;state=self
        class Control(Tape):
            def __init__(self):
                super().__init__();state.live.add(self)

            def clear(self):
                super().clear()
                need(self.head==1 and not bits(self),"erased node control work")
                if self in state.live:state.live.remove(self);state.erased+=1

        class Payload(Tape):
            def __init__(self):
                super().__init__();self.origins={};state.live.add(self)

            def read(self):
                value=super().read()
                if self.head in self.origins:
                    state.last=self.origins[self.head];state.recent.append(state.last)
                return value

            def write(self,value):
                super().write(value)
                if value==BLANK:self.origins.pop(self.head,None)
                elif value in (ZERO,ONE):
                    if state.xor:
                        need(len(state.recent)==2,"two observed Boolean XOR operands")
                        self.origins[self.head]=state.recent[0]^state.recent[1]
                    elif state.last is not None:self.origins[self.head]=state.last

            def clear(self):
                super().clear()
                need(self.head==1 and not self.origins and not bits(self),"erased node payload work")
                if self in state.live:state.live.remove(self);state.erased+=1
        self.payload,self.control=Payload,Control

    def source(self,length,linear=True):
        tape=self.payload()
        for i in range(length):tape.append(((i*13)^(i>>3)^(i>>7)^0x53)&1)
        tape.origins={i+1:(1<<i if linear else i) for i in range(length)}
        tape.rewind();return tape

    @contextmanager
    def install(self,driver_type=None):
        originals=[]
        def set_attribute(module,name,value):
            originals.append((module,name,getattr(module,name)));setattr(module,name,value)
        for module in (driver,fresh_rows,bitstream):set_attribute(module,"Tape",self.payload)
        for module in (cardinality,counts,stream,packet):set_attribute(module,"Tape",self.control)
        for name in ("gather","scatter","route_packet"):
            original=getattr(driver,name)
            def wrapped(*args,_original=original,**kwargs):
                kwargs["factory"]=self.payload
                return _original(*args,**kwargs)
            set_attribute(driver,name,wrapped)
        original_run=packet_engine.run
        def run(*args,**kwargs):
            kwargs["factory"]=self.payload
            return original_run(*args,**kwargs)
        set_attribute(packet_engine,"run",run)
        for name in ("xor_packet","xor_family"):
            original=getattr(driver,name)
            def xor(*args,_original=original,_packet=name=="xor_packet",**kwargs):
                if _packet:kwargs["factory"]=self.payload
                previous=self.xor;self.xor=True
                try:return _original(*args,**kwargs)
                finally:self.xor=previous
            set_attribute(driver,name,xor)
        if driver_type is not None:set_attribute(node,"Driver",driver_type)
        try:yield
        finally:
            for module,name,value in reversed(originals):setattr(module,name,value)


def destination(address,n,modulus,weights,gap=1,suffix=1,active=None):
    """Independent mixed-radix F_A; preserve outer, gap and suffix coordinates."""
    address,s=divmod(address,suffix)
    address,tail=divmod(address,modulus**n)
    address,g=divmod(address,gap)
    outer,head=divmod(address,modulus**n)
    h,d=[0]*n,[0]*n
    for i in range(n-1,-1,-1):head,h[i]=divmod(head,modulus);tail,d[i]=divmod(tail,modulus)
    new_h,new_d=list(h),list(d)
    for i in range(n) if active is None else active:
        a=weights[i]
        new_h[i]=a*d[n-1-i]%modulus
        new_d[n-1-i]=pow(a,-1,modulus)*h[i]%modulus
    head=tail=0
    for a,b in zip(new_h,new_d):head=modulus*head+a;tail=modulus*tail+b
    return ((((outer*modulus**n+head)*gap+g)*modulus**n+tail)*suffix+s)


def complete_node(gap_size=2):
    started=monotonic()
    catalogue=model.Catalogue();topology=model.Topology(catalogue)
    arena,indices=Arena(3),Arena(8)
    mod=arena.input(3);ring=Ring(mod);context=Context(ring,catalogue.codes)
    size,depth=indices.input(2),indices.input(0)
    program=object();weights=(2,1)
    incoming=model.Incoming(context,indices,weights)
    consumer=model.Consumer(context,indices,program,size,depth,catalogue,incoming)
    evaluator=node.Node(context,indices,program,size,depth,topology,consumer,incoming)
    old=Tape();old_count=Count.literal(1);row_count=Count.literal(4*48)
    before,gap,suffix=Count.literal(1),Count.literal(gap_size),Count.literal(1)
    tracker=Tracker();body=81*gap_size;family_size=48*body
    source=tracker.source(4*family_size);original=bytes(source.cells)
    observations=Counter();checkpoints=[];active={}
    base_driver=driver.Driver
    class ObservedDriver(base_driver):
        def global_word(self,families):
            active["families"]=families
            return super().global_word(families)
    def observe(kind,*labels):
        observations[kind]+=1
        if kind=="global_return":
            event,stage=labels
            if event=="local_cover_sweep" and stage in (0,1):
                tape=active["families"][0]
                for low in range(48):
                    for address in range(body):
                        target=destination(address,2,3,weights,gap_size) if stage==0 else address
                        old_index=low*body+address;new_index=low*body+target
                        need(tape.origins.get(new_index+1)==1<<old_index,
                             "first-sweep endpoint prevents cancellation masking")
                checkpoints.append(stage)
            print("model global return",event,stage,round(monotonic()-started,3),file=sys.stderr,flush=True)
    with tracker.install(ObservedDriver),no_decode():
        output=evaluator.run(source,old,old_count,row_count,before,gap,suffix,observe)
    for row in range(4*48):
        for address in range(body):
            target=destination(address,2,3,weights,gap_size)
            old_index=row*body+address;new_index=row*body+target
            need(output.origins.get(new_index+1)==1<<old_index and output.cells[new_index+1]==original[old_index+1],
                 "complete node Boolean column endpoint")
    need(checkpoints==[0,1] and tracker.live=={source,output} and
         bytes(source.cells)==original and source.head==output.head==old.head==1,
         "complete node scratch/input/row return")
    need(consumer.calls=={"MOVE":192,"COPY":96,"IDLE":384} and
         consumer.children["enter"]==consumer.children["return"],"complete model residual/child census")
    result={"dimension":2,"width":1,"bank_atoms":2,"families":4,"low_classes":48,"gap":gap_size,
            "input_columns":4*family_size,"first_sweep_checkpoints":checkpoints,
            "residuals":dict(consumer.calls),"children":dict(consumer.children),
            "events":dict(observations),"erased_tapes":tracker.erased,
            "payload_sha256":sha256(bits(output)).hexdigest()}
    source.clear();output.clear();old.clear();incoming.close()
    for count in (old_count,row_count,before,gap,suffix):count.close()
    context.close();ring.close();arena.free(mod);indices.free_many(size,depth);audit(arena);audit(indices)
    print("complete model node",round(monotonic()-started,3),file=sys.stderr,flush=True)
    return result
