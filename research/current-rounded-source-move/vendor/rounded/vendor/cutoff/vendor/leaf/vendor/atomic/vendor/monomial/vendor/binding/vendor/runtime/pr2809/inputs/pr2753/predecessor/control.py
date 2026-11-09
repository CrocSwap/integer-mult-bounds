"""Finite literal-frame controller shared by execution and full-source checks."""
from words import need


class LocalState:
    def __init__(self,call):
        self.call=call
        self.private=len(call.owners)
        self.frames=list(call.start)+[-1]
        self.versions=[0]*(self.private+1)
        self.opened=None

    def accept(self,position):
        event=self.call.events[position]
        op,role=event[:2]
        private,frames,versions=self.private,self.frames,self.versions
        need(0<=role<private,"live local destination/source role")
        if op==0:
            _,_,old,new,_rank,flag=event
            need(self.opened is None and frames[role]==old and flag==int(self.call.reverse),
                 "MOVE frame and lifetime")
            need(self.call.requests[position] is not None,"source-bound MOVE request")
            frames[role]=new;versions[role]+=1
        elif op==1:
            _,_,source,coefficient,frame,flag=event
            need(coefficient in (-1,1) and flag==int(self.call.reverse) and role!=source and
                 0<=source<=private and frames[role]==frames[source]==frame and
                 (source!=private or self.opened is not None),"aligned framed local XOR")
            need(self.opened is None or role!=self.opened[0],"copied source remains unchanged")
            versions[role]+=1
        elif op==2:
            _,_,temporary,old,new,_rank,flag=event
            need(temporary==private and self.opened is None and frames[role]==old and
                 frames[private]==-1 and flag==int(self.call.reverse),"fresh transported COPY interval")
            need(self.call.requests[position] is not None,"source-bound COPY request")
            frames[private]=new;versions[private]+=1
            self.opened=(role,versions[role],versions[private],old,new,position)
        else:
            need(op==3 and self.opened is not None,"matching private ERASE")
            _,_,temporary,old,new,rank_field,flag=event
            need(temporary==private and flag==int(self.call.reverse) and
                 rank_field==(7 if self.call.reverse else 0) and
                 self.opened[:5]==(role,versions[role],versions[private],old,new) and
                 frames[role]==old and frames[private]==new,"transported source lifetime guard")
            frames[private]=-1;self.opened=None
        return op,role

    def finish(self):
        need(self.opened is None and tuple(self.frames[:-1])==self.call.end and self.frames[-1]==-1,
             "complete local endpoint and private closure")
