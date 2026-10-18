#!/usr/bin/env python3
"""Exact return-cut census of named retained arrays; no heap/allocator claim."""
from pathlib import Path
import importlib.util
import json
import sys
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("backing_runtime", ROOT / "runtime.py")
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
need = runtime.require


def budget(N, F, K, D, Q, t, j, distinct):
    for v in (N, F, K, D, Q, t, j):
        need(type(v) is int, "integer domain, excluding bool")
    need(N > 0 and F > 0 and K >= N*F+1 and D > 0 and Q > 0,
         "positive complete packet and backing domain")
    need(t >= 0 and 0 <= j < N and type(distinct) is bool, "cut domain")
    later = t > 0 or j > 0
    payload = K + (N*F+1 if t else 0) + j*F+1
    if later:
        payload += (1+int(distinct))*(F+1)
    fields = D + (3 if later else 2)*Q
    return {"payload": payload, "records": fields, "total": payload+fields}


def unique_size(roles):
    return sum(len(x.cells) for x in {id(v): v for v in roles.values()}.values())


def erased(x):
    return x.head == 1 and all(a == 4 for a in x.cells[1:])


def body_tape(rt, body, padding=0):
    x = rt.records.Tape()
    x.cells.extend(body)
    if padding:
        x.cells.extend(bytes([4]) + bytes([0])*padding)
    return x


def scan_packet(rt, N, F, events_count, directory, field_count, first,
                ring, M, before, suffix, mode="sign", padding=0):
    import packet_engine
    original_reader, original_action = packet_engine.read_prefix, packet_engine.action
    payload = bytes(((i*i+3*i+1) % 7) % 2 for i in range(N*F))
    source = body_tape(rt, payload, padding)
    K, D, Q = len(source.cells), len(directory.cells), len(first.cells)
    prefixes = rt.counts.Count.literal(N)
    cuts = []

    def reader(d, count):
        fresh = original_reader(d, count)
        frame = sys._getframe(1).f_locals
        t, j = divmod(len(cuts), N)
        later = t > 0 or j > 0
        roles = {n: frame[n] for n in ("source", "current", "output")}
        need((roles["source"] is roles["current"]) == (t == 0), "packet alias boundary")
        need(len(roles["output"].cells) == 1+j*F, "partial output backing")
        if later:
            roles.update({n: frame[n] for n in ("local", "changed")})
            need(all(erased(roles[n]) and len(roles[n].cells) == F+1
                     for n in ("local", "changed")), "retained erased payload")
            need((roles["local"] is not roles["changed"]) == (mode != "alias"),
                 "changed result ownership")
        records = {"directory": d, "first": first, "fresh": fresh}
        if later:
            records["previous"] = frame["fields"]
            need(erased(records["previous"]), "retained erased previous prefix")
        need(len({id(v) for v in records.values()}) == len(records), "distinct record owners")
        need(not ({id(v) for v in roles.values()} & {id(v) for v in records.values()}),
             "disjoint payload/record owners")
        need(erased(first) and len(fresh.cells) == Q, "full fresh prefix and erased preflight")
        measured = {"payload": unique_size(roles), "records": unique_size(records)}
        measured["total"] = sum(measured.values())
        need(measured == budget(N,F,K,D,Q,t,j,mode != "alias"),
             "exact simultaneous backing census")
        if later:
            need(measured["payload"] > unique_size({k:v for k,v in roles.items()
                                                    if k not in ("local", "changed")}),
                 "erasure-as-deallocation control")
            need(measured["records"] != D+2*Q, "omitted previous prefix control")
        if t == 0:
            need(sum(len(v.cells) for v in roles.values()) > measured["payload"],
                 "source/current double count control")
        cuts.append({"t":t,"j":j,**measured,
                     "payload_arrays":len({id(v) for v in roles.values()}),
                     "record_arrays":len(records)})
        return fresh

    def extent(value):
        base=rt.counts.Count.literal(value)
        result=base.marginal();base.close()
        return result
    layout = NS(ring=ring,q=3,
                fibre=lambda:rt.counts.Count.literal(F),
                extents=lambda _:[extent(before),extent(suffix)])
    if mode == "alias":
        def action(source,*_):return source
    else:
        action = original_action
    try:
        packet_engine.read_prefix, packet_engine.action = reader, action
        output = packet_engine.run(source,(NS(kind="sign",first=None) for _ in range(events_count)),
                                   layout,directory,prefixes,field_count,lambda _:None)
        need(len(output.cells) == N*F+1 and output is not source, "complete distinct output packet")
        expected_payload = bytearray()
        for n in range(N):
            for b in range(before):
                for a in range(M):
                    old_a = a if mode == "alias" or events_count % 2 == 0 else (-a) % M
                    for s in range(suffix):
                        expected_payload.append(payload[n*F+(b*M+old_a)*suffix+s])
        need(bytes(output.cells[1:]) == bytes(expected_payload), "literal sign/alias output")
        need(bytes(source.cells[1:1+N*F]) == payload and len(source.cells) == K,
             "borrowed source and hidden backing preserved")
        need(len(cuts) == N*events_count, "complete return-cut coverage")
        output.clear(); source.clear()
    finally:
        packet_engine.read_prefix, packet_engine.action = original_reader, original_action
        prefixes.close()
    return {"N":N,"F":F,"K":K,"D":D,"Q":Q,"events":events_count,
            "mode":mode,"cuts":cuts}


def packet_fixture(rt,N,w,before,suffix,events,mode,padding):
    M = 3**w
    arena=rt.words.Arena(M.bit_length()+1);mod=arena.input(M);ring=rt.words.Ring(mod)
    rec = bytes([0,5]) + bytes([0])*arena.bits + bytes([5,6])
    directory=body_tape(rt,rec*N)
    field_count=rt.counts.Count.literal(1)
    first=rt.packet.read_prefix(directory,field_count);first.clear();directory.rewind()
    row=scan_packet(rt,N,before*M*suffix,events,directory,field_count,first,
                    ring,M,before,suffix,mode,padding)
    directory.clear();field_count.close();ring.close();arena.free(mod)
    need(not arena.live,"packet numerical cleanup")
    return row


def consumer_fixture(rt):
    """Literal Consumer preflight plus native toy sign actions at run seam.

    Synthetic specifications and toy payload/layout replace selected GL64 work.
    This proves no catalogue or full selected payload admission.
    """
    import consumer, packet_engine, cardinal_counts
    arena=rt.words.Arena(3);mod=arena.input(3);ring=rt.words.Ring(mod)
    codes=NS(q=3,dimension=64,bits=6507,limit=2**6507)
    context=rt.directory.Context(ring,codes)
    index=rt.words.Arena(8);program=rt.records.Program.fixture(index,arena,64,1,[],6507)
    parent,depth=index.input(64),index.input(0)
    class Specs(dict):
        def bind(self,*args):return self[0]
        def plan(self,code):return NS(dimension=64,rank=1,good=True)
    specs=Specs({0:NS(code=0,good=True,template=NS(q=3,rank=1))})
    specs.catalogue=NS(requests=[NS(kind="MOVE")])
    source,old=rt.records.Tape(),rt.records.Tape();count=rt.counts.Count.literal(2)
    before,gap,suffix=[cardinal_counts.Count.literal(1) for _ in range(3)]
    baseR,baseI=set(arena.live),set(index.live);original=packet_engine.run;receipt={}
    def seam(source,events,layout,directory,prefixes,fields,coefficient,**kwargs):
        caller=sys._getframe(1).f_locals;first=caller["first"]
        need(caller["prefix"].tape is first and caller["frame"].fields.tape is first,
             "actual Consumer preflight references")
        events.close();packet_engine.run=original
        try:
            receipt.update(scan_packet(rt,2,3,2,directory,fields,first,ring,3,1,1))
        finally:
            packet_engine.run=seam
        return source
    packet_engine.run=seam
    try:
        c=consumer.Consumer(context,index,program,specs,parent,depth)
        need(c.apply(source,0,True,(),old,count,before,gap,suffix) is source,"Consumer seam return")
    finally:
        packet_engine.run=original
    need(set(arena.live)==baseR and set(index.live)==baseI,"Consumer numerical restoration")
    for x in (count,before,gap,suffix):x.close()
    program.tape.clear();index.free_many(parent,depth);context.close();ring.close();arena.free(mod)
    need(not arena.live and not index.live,"Consumer fixture cleanup")
    return receipt


def main():
    rt=runtime.load_runtime();rows=[]
    for N in (1,2,4):
        for w,b,s in ((1,1,1),(1,2,2),(2,1,1)):
            for mode in ("sign","alias"):
                rows.append(packet_fixture(rt,N,w,b,s,3,mode,5 if N==2 else 0))
    result={"status":"PASS_PACKET_RETAINED_BACKING","source_head":runtime.PIN,
            "fixtures":rows,"consumer":consumer_fixture(rt),
            "cuts":sum(len(x["cuts"]) for x in rows)+4,
            "no_new_kappa":True,"metric":"distinct named addressable backing entries including LEFT"}
    expected=ROOT/"RESULT.json"
    if expected.exists():runtime.check_receipt(json.loads(expected.read_text()),result)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":main()
