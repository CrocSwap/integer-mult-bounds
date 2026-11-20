"""Fresh complete producer/consumer/terminal execution on one fixed graph."""
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
import json
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import integration as linked

need = linked.need


@contextmanager
def terminal_seal(w,e,entry):
    changes = [(w.Word,name) for name in ("read","write","step","rewind","erase","zero","msb","inspect")]
    changes += [(e.Port,name) for name in ("read","write","step","rewind","clear","retire")]
    old = [(cls,name,getattr(cls,name)) for cls,name in changes]
    calls = {"calls":0}
    def forbidden(*args,**kwargs):
        calls["calls"] += 1
        raise ValueError("RAW_TERMINAL_OR_HOST_MEMBERSHIP_UNAVAILABLE")
    parent = type(entry.arena)
    class TerminalArena(parent):
        @property
        def live(self):
            return forbidden()
        @property
        def available(self):
            return forbidden()
    entry.arena.__class__ = TerminalArena
    for cls,name,_ in old:
        setattr(cls,name,forbidden)
    try:
        yield calls
    finally:
        for cls,name,value in old:
            setattr(cls,name,value)
        entry.arena.__class__ = parent


def meters(entry,guide,guards,left,right):
    found = {id(t.meter):t.meter for t in (guide,*guards,left,right,*entry.owned)}
    found[id(entry.arena.meter)] = entry.arena.meter
    return sum(m.reads+m.writes+m.moves for m in found.values())


def full_source(code,meta,joined,old):
    w,r,e,producer = old.modules()
    p = 7
    entry,guide,guards = old.eager(w,r,e,p)
    left,right = old.canonical(r,w,[(5,1)]),old.canonical(r,w,[(7,2)])
    # Explicit grants before the measured invocation; no source action may
    # silently grow a backing during this complete fixture.
    guide.cells.extend([w.BLANK])
    left.cells.extend([w.BLANK]*7)
    right.cells.extend([w.BLANK]*11)
    for port,capacity in zip((entry.left,entry.right,entry.output),(64,71,89)):
        port.cells.extend([w.BLANK]*(capacity-len(port.cells)))
    borrowed = [(id(t.cells),tuple(t.cells),t.head) for t in (guide,*guards,left,right)]
    audit = linked.Audit(old,p)
    machine = linked.Machine(code,meta,audit)
    bound,tracker = linked.bind_entry(joined,entry,machine,guide,left,right)
    phase_controls = []
    for private in ("A:ACQUIRE","L:INIT","A:RETIRE","L:CLOSE"):
        try:
            machine.run(bound.ports,private)
        except ValueError as exc:
            need(str(exc) == "predecessor setup/retirement entry is private", "private phase entry rejected")
            phase_controls.append("active-phase "+private+" rejected")
        else:
            raise ValueError("private initialization/retirement entry escaped")
    try:
        machine.run(tuple(list(bound.ports)),"L:TAKE")
    except ValueError as exc:
        need(str(exc) == "no service role rebinding", "fixed binding sentinel")
        phase_controls.append("replacement service-port tuple rejected")
    else:
        raise ValueError("service tuple rebinding escaped")
    before_native = meters(entry,guide,guards,left,right)
    with joined.forbid_old(w) as blocked:
        with linked.block_close(e) as close_blocked:
            with bound.install(w):
                with linked.retained_observation(w,r,e,tracker):
                    result = entry.invoke(producer,left,right)
                    lower = old.value(tuple(result["lower"].cells),p)
                    product = old.value(tuple(result["product"].cells),p)
                    records = old.decode_records(result["stream"],r,w,p)
                    # Independent CRT: 1 mod 5; the inverse of 5 mod 7 is 3.
                    need((lower,product,records,result["left_valid"]) == (1,5,[[3,5]],True), "independent complete CRT oracle")
                    entry.consume(result)
                prefix_instructions = machine.instructions
                prefix_calls = machine.calls
                before_terminal = meters(entry,guide,guards,left,right)
                with terminal_seal(w,e,entry) as terminal_blocked:
                    bound.close()
                terminal_native = meters(entry,guide,guards,left,right)-before_terminal
                need(blocked["calls"] == close_blocked["calls"] == terminal_blocked["calls"] == 0,
                     "no replaced provider or terminal fallback")
                need(machine.phase == "CLOSED" and entry.closed, "single terminal finite phase")
                # Positive sentinel controls follow the zero-call assertion.
                for function,expected in ((lambda:e.Entry.close(entry),"ORIGINAL_ENTRY_CLOSE_UNAVAILABLE"),
                                          (lambda:w.Arena.zero(entry.arena),"OLD_ARITHMETIC_OR_LIFECYCLE_UNAVAILABLE")):
                    try:
                        function()
                    except ValueError as exc:
                        need(str(exc) == expected,"active unavailable-provider sentinel")
                    else:
                        raise ValueError("old provider still callable")
    tracker.invariant()
    need(borrowed == [(id(t.cells),tuple(t.cells),t.head) for t in (guide,*guards,left,right)], "every borrowed history and head restored")
    need(all(t.head == 1 and set(t.cells) <= {w.BLANK} for t in entry.owned), "all original owned histories retired")
    native = meters(entry,guide,guards,left,right)-before_native
    literal_native = machine.arena_actions+machine.record_actions
    residual = native-literal_native
    retained = {k:v for k,v in tracker.actions.items() if not k.startswith("literal:")}
    need(residual == sum(retained.values()),"separate residual native invoice")
    need(terminal_native == 468 and machine.receipts[-1]["instructions"] == 2977,"terminal exact native/literal counts")
    need(len(audit.old.complete_prices) == len(bound.arithmetic_calls),"all arithmetic service invoices")
    for expected,actual in zip(audit.old.complete_prices,bound.arithmetic_calls):
        need(expected["kind"] == actual["kind"] and list(expected["slots"]) == actual["slots"]
             and expected["instructions"] == actual["complete_instructions"],"full reserve/setter/body cost")
    controls = phase_controls+["old Entry.close sentinel active","old Arena.zero sentinel active"]
    for action in (lambda:bound.close(), lambda:machine.run(bound.ports,"L:INIT"), lambda:machine.bind(bound.ports)):
        try:
            action()
        except ValueError:
            controls.append("post-terminal public service or rebinding rejected")
        else:
            raise ValueError("terminal phase escaped")
    role_kinds = ["protected" if i < 8 else "numerical" if i < 64 else "selector" if i < 68
                  else "template" if i == 68 else "stack" if i == 69 else "owned_record" if i < 73
                  else "guide" if i == 73 else "borrowed_record" for i in range(76)]
    by_kind = Counter()
    for key,count in retained.items():
        by_kind[key.split(":")[0]] += count
    return {"p":p,"left":[[5,1]],"right":[[7,2]],"lower":lower,"product":product,"records":records,
            "positive_fallback_calls":{"old_arithmetic_lifecycle":0,"original_entry_close":0,"raw_terminal_or_host_live":0},
            "literal_calls":machine.calls,"literal_instructions":machine.instructions,
            "prefix_calls":prefix_calls,"prefix_instructions":prefix_instructions,
            "terminal":machine.receipts[-1],"terminal_native_actions":terminal_native,
            "entry_counts":dict(sorted(machine.entries.items())),"entry_instruction_totals":dict(sorted(machine.entry_instructions.items())),
            "arithmetic_calls":dict(audit.old.arithmetic),
            "arithmetic_alias_calls":dict(Counter(x["kind"] for x in bound.arithmetic_calls if x["slots"][0] == x["slots"][1])),
            "complete_arithmetic_instructions":sum(x["complete_instructions"] for x in bound.arithmetic_calls),
            "maximum_observed_owned_live":audit.old.maximum_owned_live,
            "native_symbol_actions":native,"literal_native_symbol_actions":literal_native,
            "residual_native_symbol_actions":residual,"residual_native_by_kind":dict(by_kind),
            "residual_native_operations":dict(sorted(retained.items())),
            "retained_source_calls":dict(sorted(tracker.calls.items())),
            "controller_cost_scope":"Exact source-function call diagnostic, excluding backing/head accessors used by replay observation; not a physical controller tariff. Native R/W/M residual is separately exact. Pure higher control remains a premise.",
            "role_kinds":role_kinds,"physical_context_roles":76,"service_roles":73,
            "history_capacities":tracker.capacities,"touched_intervals":tracker.intervals,
            "physical_role_operations":[dict(sorted(x.items())) for x in tracker.actions_by_role],
            "history_cells":sum(tracker.capacities),"service_history_cells":sum(tracker.capacities[:73]),
            "final_phase":machine.phase,"controls":controls}


def main():
    started = time.monotonic()
    joined,old = linked.providers()
    code,meta = linked.compile_all(joined)
    compiled = time.monotonic()-started
    result = {"status":"PASS_COMPLETE_CRT_LITERAL_TERMINAL",
              "source_files":linked.authenticate(),"roles":73,"locations":len(code),
              "graph_sha256":joined.digest(code),"terminal_offset":meta["terminal_offset"],
              "source":full_source(code,meta,joined,old)}
    if "--record" not in sys.argv:
        need(json.loads(json.dumps(result)) == json.loads((HERE/"RESULT.json").read_text()),"deterministic complete receipt")
    print(json.dumps(result,indent=2,sort_keys=True))
    print(json.dumps({"compile_seconds":round(compiled,3),"total_seconds":round(time.monotonic()-started,3),
                      "peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}),file=sys.stderr)


if __name__ == "__main__":
    main()
