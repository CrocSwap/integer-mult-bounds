#!/usr/bin/env python3
"""Joined producer -> scanner -> mask-driven key repair, replayed on the actual #4100 caller.

Host arrays below are VERIFICATION ORACLES and input/output adapters only:
 - the raw post-macro stream (the macro S itself is not executed on tapes),
 - the ideal-switch reference layout,
 - the bad-address set used to audit which addresses the key subroutine saw.
The tape program (bridge.py, plus the unchanged producer and scanner) never reads them.
The address -> key arithmetic (key_subroutine.py) is an explicit paid-elsewhere premise.
"""
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N_ADDRESS = 4096
PAYLOAD_BITS = 12


def need(ok, why):
    if not ok:
        raise ValueError(why)


def pin_ok(raw, row):
    return (sha256(raw).hexdigest() == row["sha256"]
            and __import__("hashlib").sha1(b"blob %d\0" % len(raw) + raw).hexdigest() == row["git_blob"])


def authenticate():
    rows = json.loads((HERE / "SOURCES.json").read_text())["files"]
    data = {}
    for row in rows:
        if row["usage"] != "input":
            continue
        raw = (ROOT / row["path"]).read_bytes()
        need(pin_ok(raw, row), "source SHA256/Git blob mismatch: " + row["path"])
        data[row["path"]] = raw
    phrases = {"research/unconditional-batched-crt/CRT.md":
               ["T(S^-1(x)), sort those holes by this full key on fixed tapes",
                "It does not sort the full input."],
               "research/pr4100-crt-repair-tariff/README.md":
               ["Compose the hole mask, key evaluator and repair into one fixed-tape",
                "program."],
               "research/crt-uniform-evaluator/PROOF.md": ["E(p, ell) = 2^{4 ell} (p+2)^{16}"]}
    for path, needed in phrases.items():
        text = data[path].decode()
        for phrase in needed:
            need(" ".join(phrase.split()) in " ".join(text.split()), "source phrase missing: " + phrase)
    return data


def load(name, path, data, aliases=()):
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / path)
    saved = {a: sys.modules.get(a) for a in aliases}
    sys.modules[name] = module
    for alias, target in aliases:
        sys.modules[alias] = target
    try:
        exec(compile(data[path], str(ROOT / path), "exec", dont_inherit=True), module.__dict__)
    finally:
        for alias, _ in aliases:
            sys.modules.pop(alias, None)
    return module


def own(name):
    path = HERE / (name + ".py")
    module = types.ModuleType("bridge_" + name)
    module.__file__ = str(path)
    sys.modules["bridge_" + name] = module
    exec(compile(path.read_bytes(), str(path), "exec", dont_inherit=True), module.__dict__)
    return module


class Env:
    def __init__(self):
        data = authenticate()
        self.data = data
        P = "research/crt-dense-guard-scan/machine.py"
        self.machine = load("pred_machine", P, data)
        self.producer = load("pred_producer", "research/crt-unary-stencil-producer/producer.py", data)
        self.original = load("pred_original", "research/unconditional-batched-crt/check_batched_crt.py", data)
        self.caller = load("pred_caller", "research/unconditional-batched-crt/check_compact_crt.py", data,
                           aliases=(("check_batched_crt", self.original),))
        self.kumagi = load("pred_4169", "research/crt-arbitrary-source-repair/verify.py", data)
        self.bridge = own("bridge")
        self.keysub = own("key_subroutine")
        machine = self.machine

        class BitTape(machine.Tape):
            """Unchanged Tape plus an observer bit meter: payload record 12, other symbol 1."""

            def __init__(self, cells=None):
                super().__init__(cells)
                self.bits = 0

            @staticmethod
            def weight(symbol):
                return PAYLOAD_BITS if type(symbol) is tuple and symbol[0] == "R" else 1

            def read(self):
                symbol = super().read()
                self.bits += self.weight(symbol)
                return symbol

            def write(self, symbol):
                self.bits += self.weight(symbol)
                super().write(symbol)

            def move(self, direction):
                self.bits += self.weight(self.cells[self.head])
                super().move(direction)

        self.BitTape = BitTape
        self.pool = []
        self.base = {}
        # The unchanged scanner bytes call Tape() for their counter and mask roles; route those
        # allocations through the verifier's physical-blank pool (observer wiring, not program text).
        machine.Tape = self.fresh

    # -- tape pool: recycled tapes must be physically blank with head at LEFT --------------
    def blank(self, tape):
        return (tape.head == 0 and tape.cells[0] == self.machine.LEFT
                and all(x == self.machine.BLANK for x in tape.cells[1:]))

    def fresh(self, check=True):
        if self.pool:
            tape = self.pool.pop()
            if check:
                need(self.blank(tape), "recycled tape not physically blank/head-returned")
        else:
            tape = self.BitTape()
        self.base[id(tape)] = (tape.actions, getattr(tape, "bits", 0))
        return tape

    def since(self, tapes):
        a = b = 0
        for t in tapes:
            ba, bb = self.base.get(id(t), (0, 0))
            a += t.actions - ba
            b += getattr(t, "bits", 0) - bb
        return a, b


def unary(env, n):
    tape = env.BitTape([env.machine.LEFT] + ["1"] * n + [env.machine.END])
    env.base[id(tape)] = (0, 0)
    return tape


def schedule(env):
    original = env.original
    networks = [original.benes(original.rotation(8, 5, (2 * a) % 5 if a < 3 else 0)) for a in range(4)]
    layers = []
    for index in range(5):
        target = networks[0][index][0]
        need(all(net[index][0] == target for net in networks), "common schedule")
        table = [networks[a][index][1][b] for a in range(4) for b in range(8)]
        need(all(table[(((y >> 3) & 3) << 3) | (y & 7)] == table[((((y ^ (1 << target)) >> 3) & 3) << 3)
                                                                  | ((y ^ (1 << target)) & 7)]
                 for y in range(256)), "switch control omits its active target")
        layers.append((target, table))
    return layers


def pack(u, t, y):
    return (u << 10) | (t << 8) | y


def unpack(x):
    return x >> 10, (x >> 8) & 3, x & 255


def oracle_layer(env, values, target, table):
    """Host reference only: S-raw stream, ideal switch layout, bad-address set."""
    original = env.original
    fn = env.keysub.source_function(table)
    raw = [None] * N_ADDRESS
    ideal = [None] * N_ADDRESS
    for x in range(N_ADDRESS):
        u, t, y = unpack(x)

        out = pack(*original.compact(u, t, y, lambda yy: (fn(yy),), positions=(target,), ybits=8))
        need(raw[out] is None, "raw injection")
        raw[out] = values[x]
        dest = pack(u, t, y ^ (fn(y) << target))
        need(ideal[dest] is None, "ideal injection")
        ideal[dest] = values[x]
    bad = {q for q in range(N_ADDRESS)
           if not original.good(*unpack(q), bits=2, positions=(target,), guard=6)}
    return raw, ideal, bad


def run_layer(env, values, target, table, mode="correct", flags=frozenset(), stencil_mutant=None,
              mask_hook=None, roles=None):
    machine, producer, bridge, keysub = env.machine, env.producer, env.bridge, env.keysub
    raw, ideal, bad_set = oracle_layer(env, values, target, table)
    inputs = [unary(env, n) for n in (2, 2, 6, 8, target, 0)]  # G,H,K,Y,J,B
    work, stencil = producer.produce(*inputs, env.fresh, **(stencil_mutant or {}))
    producer_tapes = inputs + list(work) + [stencil]
    prod_actions, prod_bits = env.since(producer_tapes)
    need(stencil_mutant is not None or prod_actions == 33 * 2 + 25 * 6 + 38 * 8 - 6 * 2 - target + 335,
         "unchanged producer exact invoice")
    need(all(env.blank(t) for t in work), "producer private work blank")
    stencil_before = stencil.actions
    counter, mask = machine.transduce(stencil)
    scan_actions = (stencil.actions - stencil_before) + env.since([counter, mask])[0]
    need(stencil_mutant is not None or scan_actions == 8 * N_ADDRESS * 12 + 15 * N_ADDRESS + 13 * 12 + 18,
         "unchanged scanner exact invoice")
    need(env.blank(counter) and mask.head == 0 and stencil.head == 0, "scanner returned/blanked")
    mask_cells = list(mask.cells)
    end = mask_cells.index(machine.END)  # recycled tapes may carry stale blank cells past END
    need(all(x == machine.BLANK for x in mask_cells[end + 1:]), "no stale data past the mask END")
    scanned = mask_cells[1:end]
    if stencil_mutant is not None:
        if len(scanned) != N_ADDRESS or {q for q, b in enumerate(scanned) if b == "1"} != bad_set:
            raise ValueError("mutated stencil mask differs from the source good predicate")
    need(len(scanned) == N_ADDRESS, "one mask bit per address")
    need({q for q, b in enumerate(scanned) if b == "1"} == bad_set, "scanner mask equals source good predicate")
    if mask_hook is not None:
        mask = mask_hook(mask, raw, ideal, bad_set)
    if roles is None:
        roles = (work[0], work[1], work[2], work[3])  # good, bad, b0, b1 recycled from producer
    good, bad, b0, b1 = roles
    data = env.BitTape([machine.LEFT] + [("R", v) for v in raw] + [machine.END])
    env.base[id(data)] = (0, 0)
    key = keysub.ReverseWordKey(target, table, mode)
    meter = {"calls": 0, "interface_actions": 0}
    repair_tapes = [data, stencil, mask, counter, good, bad, b0, b1]
    base = {id(t): (t.actions, getattr(t, "bits", 0)) for t in repair_tapes}
    phases = []

    def mark(name):
        total = sum(t.actions - base[id(t)][0] for t in repair_tapes)
        phases.append((name, total))

    bridge.repair(stencil, mask, counter, data, good, bad, b0, b1, key.key_of,
                  machine.increment_and_return, meter, flags, mark)
    repair_actions = sum(t.actions - base[id(t)][0] for t in repair_tapes)
    repair_bits = sum((t.bits - base[id(t)][1]) if hasattr(t, "bits") else (t.actions - base[id(t)][0])
                      for t in repair_tapes)  # scanner-created roles carry only 1-bit symbols
    phase_cost, last = {}, 0
    for name, total in phases:
        phase_cost[name] = total - last
        last = total
    final = [c[1] for c in data.cells[1:-1]]
    ownership = {
        "protected_payload_stream_kept_length": len(data.cells) == N_ADDRESS + 2,
        "all_roles_blank": all(env.blank(t) for t in (stencil, counter, good, bad, b0, b1)) and env.blank(mask),
        "all_heads_returned": all(t.head == 0 for t in repair_tapes),
        "good_addresses_evaluated": len(set(key.addresses) - bad_set),
        "hole_addresses_missed": len(bad_set - set(key.addresses)),
        "key_calls": meter["calls"],
        "distinct_key_addresses": len(set(key.addresses)),
    }
    return dict(final=final, ideal=ideal, raw=raw, bad=len(bad_set), repair_actions=repair_actions,
                repair_bits=repair_bits, phases=phase_cost, meter=meter, producer_actions=prod_actions,
                scanner_actions=scan_actions, ownership=ownership, tapes=repair_tapes + list(work),
                mask_cells_at_scanner_output=mask_cells, data=data, stencil=stencil, counter=counter,
                mask=mask, roles=(good, bad, b0, b1), key=key,
                producer_tapes=producer_tapes)


def recycle(env, result):
    seen = set()
    for t in result["tapes"] + result["producer_tapes"] + [result["mask"], result["counter"], result["stencil"]]:
        if id(t) in seen or t is result["data"] or t.cells[0] != env.machine.LEFT:
            continue
        seen.add(id(t))
        if env.blank(t) and hasattr(t, "bits"):
            env.pool.append(t)


def digest(values):
    return sha256(b"".join(v.to_bytes(4, "little") for v in values)).hexdigest()


def actual_caller(env):
    layers = schedule(env)
    values = list(range(N_ADDRESS))
    rows, checked = [], []
    forward_hash = None
    total = dict(producer=0, scanner=0, repair=0, repair_bits=0, calls=0, interface=0, holes=0)
    sequence = [(i, layers[i], "forward") for i in range(5)] + [(i, layers[i], "inverse") for i in reversed(range(5))]
    reused_tapes = 0
    for position, (index, (target, table), direction) in enumerate(sequence):
        pool_before = len(env.pool)
        result = run_layer(env, values, target, table)
        reused_tapes += pool_before > 0
        need(result["final"] == result["ideal"], "repaired layer equals ideal switch layer")
        own = result["ownership"]
        need(own["all_roles_blank"] and own["all_heads_returned"], "ownership/return")
        need(own["good_addresses_evaluated"] == 0 and own["hole_addresses_missed"] == 0
             and own["key_calls"] == result["bad"] == own["distinct_key_addresses"],
             "keys evaluated exactly at the marked holes")
        # Compare the key subroutine with the pinned table-based caller and #4169 Word on EVERY address.
        word = env.kumagi.Word(2, 2, 8, (target,), 6)
        source = lambda y, table=table: (table[(((y >> 3) & 3) << 3) | (y & 7)],)
        for q in range(N_ADDRESS):
            ref = word.pack(word.ideal(word.run(word.unpack(q), source, inverse=True), source))
            need(int(result["key"].__class__(target, table).key_of(format(q, "012b")), 2) == ref,
                 "reverse-word key equals #4169 T(S^-1(q))")
        source_fn = lambda y, table=table: (table[(((y >> 3) & 3) << 3) | (y & 7)],)
        table_final, table_count = env.caller.layer(values, target, source_fn)
        need(table_final == result["final"] and table_count == result["bad"],
             "agrees with the pinned table-based #4100 caller layer")
        values = result["final"]
        if position == 4:
            forward_hash = digest(values)
            need(values.index(780) == 777, "label 780 reaches address 777")
            expected = [None] * N_ADDRESS
            for x in range(N_ADDRESS):
                u, t, y = unpack(x)
                a, b = (y >> 3) & 3, y & 7
                nb = (b + 2 * a) % 5 if a < 3 and b < 5 else b
                expected[pack(u, t, (y & ~7) | nb)] = x
            need(values == expected, "five-layer endpoint equals padded CRT rotation")
        for key_, field in (("producer", "producer_actions"), ("scanner", "scanner_actions"),
                            ("repair", "repair_actions"), ("repair_bits", "repair_bits")):
            total[key_] += result[field]
        total["calls"] += result["meter"]["calls"]
        total["interface"] += result["meter"]["interface_actions"]
        total["holes"] += result["bad"]
        rows.append(dict(direction=direction, schedule_index=index, target=target, holes=result["bad"],
                         producer_actions=result["producer_actions"], scanner_actions=result["scanner_actions"],
                         repair_actions=result["repair_actions"], repair_bit_weighted=result["repair_bits"],
                         key_interface_actions=result["meter"]["interface_actions"], phases=result["phases"]))
        recycle(env, result)
    need(values == list(range(N_ADDRESS)), "inverse five layers restore all 4096 payloads")
    need(values[780] == 780, "label 780 returns to address 780")
    need(forward_hash is not None, "forward hash")
    return dict(layers=rows, forward_payload_sha256=forward_hash, inverse_payload_sha256=digest(values),
                label_780_forward_address=777, label_780_inverse_address=780,
                totals=total, tapes_recycled_pool_hits=reused_tapes,
                pool_size_after=len(env.pool))


def expect_detected(label, check, rows):
    need(check, "control not detected: " + label)
    rows.append(dict(control=label, detected=True))


def run_outcome(env, values, target, table, **kwargs):
    """Run one layer and classify; exception capture is separate from expect_detected."""
    try:
        result = run_layer(env, values, target, table, **kwargs)
    except ValueError as exc:
        env.pool.clear()
        return dict(kind="rejected", message=str(exc))
    wrong = sum(a != b for a, b in zip(result["final"], result["ideal"]))
    recycle(env, result)
    return dict(kind="misplaced" if wrong else "equivalent", wrong=wrong)


def keys_differ(env, target, table, mode, bad_set):
    """Observer: does ``mode`` change the key at some hole relative to the correct reverse-word key?"""
    right = env.keysub.ReverseWordKey(target, table, "correct")
    wrong = env.keysub.ReverseWordKey(target, table, mode)
    return any(right.key_of(format(q, "012b")) != wrong.key_of(format(q, "012b")) for q in sorted(bad_set))


def discriminating_fixture(env):
    """First callable source omitting target bit 0 for which the stale-source key differs at a hole.
    Deterministic candidate list; failing to find one is a verifier failure."""
    candidates = [("parity(y>>1)", lambda y: (y >> 1).bit_count() & 1),
                  ("(y>>1)&(y>>4)", lambda y: ((y >> 1) & (y >> 4)) & 1),
                  ("(y>>2)^(y>>5)&(y>>6)", lambda y: ((y >> 2) ^ ((y >> 5) & (y >> 6))) & 1)]
    for name, source in candidates:
        need(all(source(y) == source(y ^ 1) for y in range(256)), "candidate omits target bit 0")
        bad_set = oracle_layer(env, list(range(N_ADDRESS)), 0, source)[2]
        if keys_differ(env, 0, source, "stale_source", bad_set):
            return name, source
    raise ValueError("no discriminating stale-source fixture found")


def controls(env):
    rows = []
    layers = schedule(env)
    target, table = layers[2]  # middle Benes layer, target bit 2
    values = list(range(N_ADDRESS))
    base = run_layer(env, values, target, table)
    ideal = base["ideal"]
    need(any(a != b for a, b in zip(base["raw"], ideal)), "control layer must have records the repair moves")
    need(base["final"] == ideal, "control baseline correct")
    holes = base["bad"]
    recycle(env, base)
    # Wrong keys, fed through the real repair program. A mode is only a control where it actually
    # changes some hole key; at the actual layer a mode that never changes a key is recorded as an
    # equivalent (and its output is checked correct) instead of being counted as detected.
    discriminating = discriminating_fixture(env)
    fixtures = [("actual caller layer 2", target, table), ("callable source " + discriminating[0],
                                                           0, discriminating[1])]
    detected_somewhere = {}
    for name, f_target, f_table in fixtures:
        bad_set = oracle_layer(env, values, f_target, f_table)[2]
        for mode in env.keysub.MODES[1:]:
            differs = keys_differ(env, f_target, f_table, mode, bad_set)
            outcome = run_outcome(env, values, f_target, f_table, mode=mode)
            if outcome["kind"] == "rejected":
                need(differs, "key-identical mode cannot be rejected: " + mode)
                need("sorted key" in outcome["message"] or "keyed hole" in outcome["message"],
                     "wrong key rejected for an unexpected reason: " + outcome["message"])
                rows.append(dict(control="wrong key " + mode + " [" + name + "]: rejected by hole-key check",
                                 detected=True, hole_keys_changed=True))
                detected_somewhere[mode] = True
            elif differs:
                expect_detected("wrong key " + mode + " [" + name + "] misplaces %d records" % outcome["wrong"],
                                outcome["wrong"] > 0, rows)
                detected_somewhere[mode] = True
            else:
                need(outcome["wrong"] == 0, "key-identical mode changed the output: " + mode)
                rows.append(dict(control="wrong key " + mode + " [" + name + "]: key-identical to the correct "
                                 "key at every hole here, so equivalent (not counted as detected)",
                                 detected=False, equivalent=True))
    need(all(m in detected_somewhere for m in env.keysub.MODES[1:]),
         "every wrong-key mode must be discriminated on at least one fixture")
    # Missing / damaged masks consumed directly.
    def zero_mask(mask, raw, ideal, bad_set):
        for i in range(1, mask.cells.index(env.machine.END)):
            mask.cells[i] = "0"
        return mask

    result = run_layer(env, values, target, table, mask_hook=zero_mask)
    wrong = sum(a != b for a, b in zip(result["final"], ideal))
    expect_detected("missing mask (all good): %d wrong, 0 keys" % wrong,
                    wrong > 0 and result["meter"]["calls"] == 0, rows)
    recycle(env, result)

    def drop_hole(mask, raw, ideal, bad_set):
        q = min(q for q in bad_set if raw[q] != ideal[q])  # a hole whose record must move
        mask.cells[1 + q] = "0"
        return mask

    outcome = run_outcome(env, values, target, table, mask_hook=drop_hole)
    if outcome["kind"] == "rejected":
        need("stream" in outcome["message"] or "sorted key" in outcome["message"],
             "unmarked hole rejected for an unexpected reason: " + outcome["message"])
        rows.append(dict(control="one hole unmarked: rejected (" + outcome["message"] + ")", detected=True))
    else:
        expect_detected("one hole unmarked: %d wrong" % outcome["wrong"], outcome["wrong"] > 0, rows)

    def truncate_mask(mask, raw, ideal, bad_set):
        del mask.cells[mask.cells.index(env.machine.END) - 1]
        return mask

    try:
        run_layer(env, values, target, table, mask_hook=truncate_mask)
        need(False, "truncated mask accepted")
    except ValueError as exc:
        need("mask length" in str(exc) or "stream" in str(exc), "truncated mask failure: " + str(exc))
        rows.append(dict(control="truncated mask rejected", detected=True))
        env.pool.clear()

    def over_mark(mask, raw, ideal, bad_set):
        q = min(q for q in range(N_ADDRESS) if q not in bad_set)
        mask.cells[1 + q] = "1"
        return mask

    result = run_layer(env, values, target, table, mask_hook=over_mark)
    over = dict(control="good address over-marked: output still correct, one extra key paid",
                final_correct=result["final"] == ideal, extra_keys=result["meter"]["calls"] - holes,
                good_addresses_evaluated=result["ownership"]["good_addresses_evaluated"])
    need(over["final_correct"] and over["extra_keys"] == 1 and over["good_addresses_evaluated"] == 1,
         "over-marking is conservative but charged")
    rows.append(over)
    recycle(env, result)
    # Key evaluation on good addresses.
    result = run_layer(env, values, target, table, flags=frozenset({"eval_good"}))
    expect_detected("good-address key evaluation: %d good addresses evaluated" %
                    result["ownership"]["good_addresses_evaluated"],
                    result["ownership"]["good_addresses_evaluated"] == N_ADDRESS - holes
                    and result["meter"]["calls"] > holes, rows)
    recycle(env, result)
    # Sort skipped.
    outcome = run_outcome(env, values, target, table, flags=frozenset({"skip_sort"}))
    if outcome["kind"] == "rejected":
        need("sorted key" in outcome["message"], "skipped sort rejected for an unexpected reason: "
             + outcome["message"])
        rows.append(dict(control="skipped radix sort: rejected by hole-key check", detected=True))
    else:
        expect_detected("skipped radix sort: %d wrong" % outcome["wrong"], outcome["wrong"] > 0, rows)
    env.pool.clear()
    # Skipped clears and head return.
    for flag in ("keep_mask", "keep_stencil", "keep_good", "keep_bad", "keep_counter", "keep_buckets"):
        result = run_layer(env, values, target, table, flags=frozenset({flag}))
        need(result["final"] == ideal, "skipped clear does not change this layer's output")
        good, bad, b0, b1 = result["roles"]
        left = {"keep_mask": result["mask"], "keep_stencil": result["stencil"], "keep_good": good,
                "keep_bad": bad, "keep_counter": result["counter"], "keep_buckets": b1}[flag]
        expect_detected("skipped clear (%s) leaves nonblank role" % flag, not env.blank(left), rows)
        env.pool.clear()
    # A skipped clear is a physical-state/ownership defect: the recycled-role blank gate rejects
    # it. (Marker-driven reads would not otherwise notice stale cells beyond a rewritten END.)
    result = run_layer(env, values, target, table, flags=frozenset({"keep_good"}))
    dirty = result["roles"][0]
    need(not env.blank(dirty), "dirty role")
    env.pool.append(dirty)
    rejected = False
    try:
        env.fresh(check=True)
    except ValueError as exc:
        rejected = "not physically blank" in str(exc)
    need(rejected, "blank-reuse gate must reject an uncleared role")
    rows.append(dict(control="blank-reuse gate rejects uncleared good role", detected=True))
    env.pool.clear()
    result = run_layer(env, values, target, table, flags=frozenset({"omit_head_return"}))
    expect_detected("omitted data head return", result["data"].head != 0, rows)
    env.pool.clear()
    # Producer geometry faults reach the actual scanner mask and then the repair.
    for name in ("wrong_lower_pivot", "wrong_upper_pivot", "include_parity"):
        try:
            run_layer(env, values, target, table, stencil_mutant={name: True})
            need(False, "mutant mask matched source predicate")
        except ValueError as exc:
            need("mutated stencil mask" in str(exc), "producer mutant failure: " + str(exc))
            rows.append(dict(control="producer mutant " + name + ": scanner mask differs from source predicate",
                             detected=True))
        env.pool.clear()
    # Damaged source bytes reject before execution.
    with tempfile.TemporaryDirectory() as directory:
        row = next(r for r in json.loads((HERE / "SOURCES.json").read_text())["files"]
                   if r["path"].endswith("crt-dense-guard-scan/machine.py"))
        damaged = Path(directory) / "machine.py"
        original = (ROOT / row["path"]).read_bytes()
        need(pin_ok(original, row), "undamaged source passes its pin")
        damaged.write_bytes(original + b"\nraise RuntimeError('UNAUTHENTICATED')\n")
        need(not pin_ok(damaged.read_bytes(), row), "damaged source bytes must fail the pin before exec")
        rows.append(dict(control="damaged scanner bytes rejected by pin before execution", detected=True))
    return rows


def guardrail():
    """Review aid, not a formal machine certificate: outside evaluate_key the tape program has
    no host arithmetic/indexing/length primitives and no observer-field reads."""
    path = HERE / "bridge.py"
    tree = ast.parse(path.read_text())
    forbidden = {"len", "range", "enumerate", "int", "str", "format", "sum", "min", "max", "pow",
                 "sorted", "list", "dict", "set", "tuple", "zip", "map", "abs", "bytes"}
    observers = ("head", "cells", "reads", "writes", "moves", "actions", "bits")
    checked = 0
    for fn in (n for n in tree.body if isinstance(n, ast.FunctionDef)):
        if fn.name == "evaluate_key":
            continue
        for node in ast.walk(fn):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                need(node.func.id not in forbidden, "host primitive outside key interface: " + node.func.id)
            if isinstance(node, ast.Attribute):
                need(node.attr not in observers, "observer read outside key interface: " + node.attr)
            if isinstance(node, ast.BinOp):
                need(False, "host arithmetic outside key interface in " + fn.name)
            if isinstance(node, ast.Subscript):
                need(fn.name == "is_record", "indexing outside record-tag test in " + fn.name)
        checked += 1
    return dict(status="PASS_AST_SCOPE_GUARDRAIL_NOT_A_FORMAL_MACHINE_CERTIFICATE", functions=checked)


def probe():
    """One forward layer: producer -> scanner -> repair, no 10-layer caller, no controls."""
    import time
    start = time.time()
    env = Env()
    target, table = schedule(env)[0]
    result = run_layer(env, list(range(N_ADDRESS)), target, table)
    need(result["final"] == result["ideal"], "probe layer equals ideal switch layer")
    own = result["ownership"]
    need(own["all_roles_blank"] and own["all_heads_returned"] and own["good_addresses_evaluated"] == 0,
         "probe ownership")
    print(json.dumps(dict(target=target, holes=result["bad"], producer_actions=result["producer_actions"],
                          scanner_actions=result["scanner_actions"], repair_actions=result["repair_actions"],
                          repair_bits=result["repair_bits"], phases=result["phases"], meter=result["meter"],
                          ownership=own, seconds=round(time.time() - start, 1)), indent=2, sort_keys=True))
    return "PROBE_OK"


def run(part):
    env = Env()
    out = dict(status="PASS_CRT_MASK_REPAIR_BRIDGE_ONE_TARGET_KEY_PREMISE:" + part,
               geometry=dict(u_bits=2, t_bits=2, y_bits=8, guard_K=6, digit_bits_G=2, address_bits_L=12,
                             addresses=N_ADDRESS),
               key_arithmetic_on_tape=False,
               scope="One target per layer; macro S and inter-layer raw streams are host-built input "
                     "adapters; address->key arithmetic is the explicit paid-elsewhere premise; no kappa")
    if part == "caller":
        out["actual_caller"] = actual_caller(env)
    else:
        out["controls"] = controls(env)
        out["guardrail"] = guardrail()
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--part", choices=("caller", "controls"))
    parser.add_argument("--probe", action="store_true")
    args = parser.parse_args()
    if args.probe:
        print(probe())
        return
    need(args.part is not None, "choose --part caller|controls (or --probe)")
    result = run(args.part)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    receipt = HERE / ("RESULT-" + args.part + ".json")
    if args.write:
        receipt.write_text(text)
    elif receipt.exists():
        need(json.loads(text) == json.loads(receipt.read_text()), "stored receipt differs from replay")
    print(result["status"])


if __name__ == "__main__":
    main()
