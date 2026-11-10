"""Fixed chronological selected calls, owners and global frame boundaries."""
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256

from catalogue import canonical
from words import need


@dataclass(frozen=True)
class Owner:
    family: int
    chart: object


@dataclass(frozen=True)
class Call:
    stage: int
    replica: int
    owners: tuple
    start: tuple
    end: tuple
    events: tuple
    requests: tuple
    reverse: bool


class SelectedTopology:
    replicas=32
    pairs=4
    ports=111
    families=28416
    stride=888

    def __init__(self,catalogue):
        self.catalogue=catalogue
        self.schedule=tuple(catalogue.template["schedule"])
        self.idles={i:tuple(j for j,r in enumerate(catalogue.requests) if r.kind=="IDLE" and r.stage==i)
                    for i in range(10)}
        expected="Each recipe phase: replicas then all cover classes; finish every local invocation before the next."
        need(catalogue.template["loop_order"]==expected,"source-selected loop order")
        self._validate_global()

    def _validate_global(self):
        levels=[-1]*4
        for position,event in enumerate(self.schedule):
            kind=event["kind"]
            if kind=="local_cover_sweep":
                need(levels[event["pair"]]==event["stage"]-1,"local call enters its data level")
                levels[event["pair"]]=event["stage"]
            elif kind=="idle":
                need(levels[event["pair"]]==event["source_level"],"idle enters its native level")
                levels[event["pair"]]=event["target_level"]
                need(bool(self.idles[event["idx"]])==(event["rank"]>0),"zero idle source boundary")
            elif kind=="bridge":
                need(event["coefficient"] in (-1,1) and event["dst"]!=event["src"] and
                     levels[event["dst"]]==levels[event["src"]],"native bridge frame alignment")
            else:
                need(kind=="exchange" and position==len(self.schedule)-1 and levels==[8]*4,
                     "terminal exchange frame boundary")

    @lru_cache(None)
    def recipe(self,stage):
        source=self.catalogue.template["calls"][32*stage]
        reverse=source["orientation"]=="reverse"
        events=tuple(map(tuple,self.catalogue.template["local_programs"][source["orientation"]]))
        identifiers=tuple(self.catalogue.identifier("MOVE" if event[0]==0 else "COPY",stage,position)
                          if event[0] in (0,2) else None for position,event in enumerate(events))
        word=self.catalogue.word
        start=tuple(word["final"] if reverse else word["start"])
        end=tuple(word["start"] if reverse else word["final"])
        return events,identifiers,start,end,reverse

    @lru_cache(None)
    def call(self,stage,replica):
        source=self.catalogue.template["calls"][32*stage+replica]
        events,identifiers,start,end,reverse=self.recipe(stage)
        owners=tuple(Owner(family,self.catalogue.owner_chart(source,role))
                     for role,(family,_route) in enumerate(source["owners"]))
        need(len(owners)==len(start)==len(end)==661,"complete selected staged roles")
        return Call(stage,replica,owners,start,end,events,identifiers,reverse)

    def matrix(self,chart):return self.catalogue.chart_matrix(chart)

    def idle_family(self,request_id,replica):
        request=self.catalogue.requests[request_id]
        need(request.kind=="IDLE","native idle family")
        return request.family+self.stride*replica

    def family(self,replica,pair,side,port):
        return self.stride*replica+(2*pair+side)*self.ports+port
