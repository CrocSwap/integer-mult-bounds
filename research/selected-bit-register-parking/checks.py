"""Independent endpoint, nesting and charge observations for the bank codec."""
from itertools import product
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import json

from codec import BankParking
from parking_machine import Machine, certify, TABLE
from words import Arena, BLANK, LEFT, RIGHT, need


def word_bytes(arena):
    return {slot: (arena.words[slot], bytes(arena.words[slot].cells), arena.words[slot].head)
            for slot in arena.live}


def check_words(arena, expected):
    need(arena.live == set(expected), "exact parent live-slot inventory")
    for slot, (identity, data, head) in expected.items():
        word = arena.words[slot]
        need(word is identity and bytes(word.cells) == data and word.head == head == 1,
             "exact parent alias, word bits and head")
    need(arena.template.head == 1, "restored numerical template head")
    for word in arena.words:
        if word.slot not in arena.live:
            need(word.head == 1 and word.cells[0] == LEFT and
                 all(bit == BLANK for bit in word.cells[1:]), "erased inactive physical word slot")


def observation(codec):
    return {"parking": dict(codec.machine.counts), "codec": dict(codec.codec_counts),
            "words": [{k: getattr(arena.meter, k) for k in ("reads", "writes", "moves")}
                      for arena in codec.arenas]}


def difference(after, before):
    out = {"parking": {}, "codec": {}, "words": []}
    for kind in ("parking", "codec"):
        out[kind] = {key: after[kind][key]-before[kind][key] for key in after[kind]}
    for a, b in zip(after["words"], before["words"]):
        out["words"].append({key: a[key]-b[key] for key in a})
    return out


def combine(parts):
    keys = ("reads", "writes", "moves")
    totals = {key: 0 for key in keys}
    parking = {key: 0 for key in ("steps", *keys)}
    finite = 0
    for part in parts:
        for key in keys:
            totals[key] += part["parking"][key]+part["codec"][key]+sum(row[key] for row in part["words"])
        for key in parking:
            parking[key] += part["parking"][key]
        finite += part["codec"]["slot_tests"]+part["codec"]["commands"]
    totals["actions"] = sum(totals.values())+finite
    return totals, parking


def measure(codec, action, parts):
    before = observation(codec)
    action()
    parts.append(difference(observation(codec), before))


def verify_bill(codec, parts, total_bits, word_bits, records, frames):
    totals, parking = combine(parts)
    expected = {"steps": 5*total_bits+7*records+3*frames,
                "reads": 10*total_bits+14*records+6*frames,
                "writes": 4*total_bits+4*records+2*frames,
                "moves": 8*total_bits+8*records+2*frames}
    need(parking == expected, "exact predecessor parking charge")
    capacity = sum(codec.capacities)
    exact = {"reads": 14*total_bits+10*word_bits+32*records+15*frames,
             "writes": 6*total_bits+3*word_bits+8*records+2*frames,
             "moves": 12*total_bits+10*word_bits+30*records+12*frames,
             "actions": 32*total_bits+23*word_bits+72*records+(capacity+31)*frames}
    need(totals == exact, "exact complete sequential API invoice")
    bounds = {"reads": 32*total_bits+40*records+(4*capacity+16)*frames,
              "writes": 12*total_bits+16*records+(4*capacity+8)*frames,
              "moves": 32*total_bits+40*records+(4*capacity+16)*frames,
              "actions": 96*total_bits+128*records+(16*capacity+64)*frames}
    need(all(totals[key] <= bounds[key] for key in totals), "complete codec, Word and table charge")
    return {"record_bits": total_bits, "word_bits": word_bits, "records": records, "frames": frames,
            "observed": totals, "upper_bounds": bounds, "parking": parking}


def clear_banks(arenas):
    for arena in arenas:
        for slot in tuple(arena.live):
            arena.free(arena.words[slot])


def flat_cases():
    cases, total_records = 0, 0
    maximum_actions = 0
    for a, b in product(range(8), range(8)):
        arenas = (Arena(3, 3), Arena(3, 5))
        left, right = arenas[0].input(a), arenas[1].input(b)
        state = tuple(word_bytes(arena) for arena in arenas)
        codec = BankParking(*arenas)
        parts = []
        measure(codec, codec.park, parts)
        need(all(not arena.live for arena in arenas), "parent banks released")
        # Reuse the same objects with different values while the parent waits.
        x, y = arenas[0].input(a ^ 7), arenas[1].input(b ^ 3)
        need(x is left and y is right, "child reuses the original physical slots")
        clear_banks(arenas)
        measure(codec, codec.restore, parts)
        for arena, expected in zip(arenas, state):
            check_words(arena, expected)
        need(codec.machine.tapes == [{}, {0: "^"}] and codec.machine.heads == [0, 1],
             "complete parking and port cleanup")
        bill = verify_bill(codec, parts, (1+2+3)+(1+3+3), 6, 2, 1)
        maximum_actions = max(maximum_actions, bill["observed"]["actions"])
        clear_banks(arenas)
        cases += 1
        total_records += 2
    return {"all_three_bit_pairs": cases, "records": total_records,
            "maximum_observed_actions": maximum_actions}


def nested_case(depth, widths=(9, 602), capacities=(7, 9), translated=False):
    arenas = tuple(Arena(width, capacity) for width, capacity in zip(widths, capacities))
    machine = Machine(parking={-7: "1", -6: "R", -5: "0"},
                      packet={30: "^"}, heads=(11, 31)) if translated else Machine(packet={0: "^"}, heads=(0, 1))
    initial_tapes, initial_heads = deepcopy(machine.tapes), list(machine.heads)
    codec = BankParking(*arenas, machine=machine)
    expected_stack, parts = [], []  # Checker history, never read by the codec.
    total_bits = word_bits = records = 0
    for level in range(depth):
        for bank, arena in enumerate(arenas):
            # Empty frames, different inventories, holes and high-valued words.
            for index in range(level % 4):
                arena.input((1 << (widths[bank]-2)) + (level+index) % 64)
            if level % 4 == 3:
                arena.free(arena.words[1])
        state = tuple(word_bytes(arena) for arena in arenas)
        expected_stack.append(state)
        for bank, values in enumerate(state):
            records += len(values)
            total_bits += len(values)*(1+codec.slot_bits[bank]+widths[bank])
            word_bits += len(values)*widths[bank]
        measure(codec, codec.park, parts)
        need(all(not arena.live for arena in arenas), "numerical banks empty after each suspension")
    for state in reversed(expected_stack):
        measure(codec, codec.restore, parts)
        for arena, values in zip(arenas, state):
            check_words(arena, values)
        clear_banks(arenas)  # The returned child closes before its parent resumes.
    need(machine.tapes == initial_tapes and machine.heads == initial_heads,
         "nested opaque ancestors and translated heads preserved")
    bill = verify_bill(codec, parts, total_bits, word_bits, records, depth)
    need(all(len(arena.words) <= capacity for arena, capacity in zip(arenas, capacities)),
         "depth does not enlarge the physical bank inventory")
    return {"depth": depth, "word_widths": widths, "capacities": capacities,
            "allocated_slots": [len(arena.words) for arena in arenas], "translated": translated, "bill": bill}


def granted_arguments():
    arenas = (Arena(10, 8), Arena(12, 10))
    modulus, size, depth = arenas[0].input(729), arenas[1].input(256), arenas[1].input(3)
    parent = tuple(word_bytes(arena) for arena in arenas)
    # These copies model the modulus/size/depth grants at PR2753's Frame site.
    child_modulus = arenas[0].copy(modulus)
    child_size, child_depth = arenas[1].copy(size), arenas[1].copy(depth)
    granted = ({child_modulus.slot}, {child_size.slot, child_depth.slot})
    codec = BankParking(*arenas)
    parts = []
    measure(codec, lambda: codec.park(granted), parts)
    need((child_modulus.inspect(), child_size.inspect(), child_depth.inspect()) == (729, 256, 3),
         "separate child input grants survive parent suspension")
    need(arenas[0].live == granted[0] and arenas[1].live == granted[1], "only granted child inputs remain")
    clear_banks(arenas)
    measure(codec, codec.restore, parts)
    for arena, state in zip(arenas, parent):
        check_words(arena, state)
    bill = verify_bill(codec, parts, (1+3+10)+2*(1+4+12), 34, 3, 1)
    clear_banks(arenas)
    return bill


def wide_slot_labels():
    arenas = (Arena(2, 513), Arena(3, 65))
    for arena, value in zip(arenas, (3, 5)):
        for _ in range(arena.capacity):
            arena.input(value)
        for word in arena.words[:-1]:
            arena.free(word)
    parent = tuple(word_bytes(arena) for arena in arenas)
    codec = BankParking(*arenas)
    parts = []
    measure(codec, codec.park, parts)
    measure(codec, codec.restore, parts)
    for arena, expected in zip(arenas, parent):
        check_words(arena, expected)
    bill = verify_bill(codec, parts, (1+10+2)+(1+7+3), 5, 2, 1)
    clear_banks(arenas)
    return {"slots": [512, 64], "slot_bits": codec.slot_bits,
            "word_bits": [2, 3], "bill": bill}


def rejected(function, message):
    try:
        function()
    except (ValueError, KeyError):
        return message
    raise ValueError("missing failure control: " + message)


def controls():
    arenas = (Arena(5, 4), Arena(7, 4))
    codec = BankParking(*arenas)
    result = [rejected(lambda: codec.park(({0}, set())), "grant references an inactive slot")]
    word = arenas[0].input(19)
    original = word_bytes(arenas[0])
    codec.park()
    leak = arenas[0].input(3)
    result.append(rejected(codec.restore, "callee leaves a live numerical slot"))
    arenas[0].free(leak)
    codec.restore()
    check_words(arenas[0], original)
    clear_banks(arenas)
    result.append(rejected(codec.restore, "unmatched restore at the blank root"))

    local = (Arena(5, 4), Arena(7, 4))
    local[0].input(17)
    spare = local[0].input(3)
    local[0].free(spare)
    state = word_bytes(local[0])
    redirected = BankParking(*local)
    redirected.park()
    redirected.machine.tapes[0][3] = "1"  # Slot0 becomes valid, erased slot1.
    def wrong_slot():
        redirected.restore()
        need(sorted(word.inspect() for word in local[0].words if word.slot in local[0].live) == [17],
             "weak value-multiset check still passes")
        check_words(local[0], state)
    result.append(rejected(wrong_slot, "correct value restored into the wrong slot alias"))

    # Inject a table fault: POP returns each parked one bit as zero.
    for source_value in (31,):
        local = (Arena(5, 4), Arena(7, 4))
        local[0].input(source_value)
        state = word_bytes(local[0])
        table = dict(TABLE)
        nxt, _writes, moves = table["pop_copy", "1", "_"]
        table["pop_copy", "1", "_"] = (nxt, ("_", "0"), moves)
        changed = BankParking(*local, machine=Machine(packet={0: "^"}, heads=(0, 1), table=table))
        changed.park()
        def wrong_restore():
            changed.restore()
            check_words(local[0], state)
        result.append(rejected(wrong_restore, "physical parking bit mutation changes parent state"))

    local = (Arena(5, 4), Arena(7, 4))
    local[0].input(17)
    table = dict(TABLE)
    for bit in ("0", "1"):
        nxt, _writes, moves = table["pop_copy", bit, "_"]
        table["pop_copy", bit, "_"] = (nxt, (None, bit), moves)
    uncleared = BankParking(*local, machine=Machine(packet={0: "^"}, heads=(0, 1), table=table))
    uncleared.park()
    def lost_clear():
        uncleared.restore()
        need(uncleared.machine.tapes == [{}, {0: "^"}], "erase the consumed physical checkpoint")
    result.append(rejected(lost_clear, "parent values return but checkpoint cells remain occupied"))

    local = (Arena(5, 4), Arena(7, 4))
    saved_word = local[0].input(17)
    changed = BankParking(*local)
    changed.park()
    # A changed template extent must not silently truncate or pad a word.
    local[0].template.cells[-2] = RIGHT
    result.append(rejected(changed.restore, "word template extent changes across a parked frame"))
    need(saved_word.slot == 0, "control retains its original role identity")
    local = (Arena(5, 4), Arena(7, 4))
    fixed = BankParking(*local)
    fixed.park()
    local[0].capacity = 5
    result.append(rejected(fixed.restore, "bank inventory changes across a parked frame"))
    return result


def run():
    return {"finite_table_entries": certify(TABLE), "flat": flat_cases(),
            "nested": [nested_case(1), nested_case(17, translated=True), nested_case(1501, widths=(9, 11))],
            "granted_arguments": granted_arguments(), "wide_slot_labels": wide_slot_labels(),
            "controls": controls(),
            "integrity_controls": integrity_controls()}


def integrity_controls():
    import verify
    originals = Path.read_bytes, Path.read_text
    manifest = json.loads((verify.HERE / "SOURCES.json").read_text())
    result = []
    for entry in manifest["snapshots"]:
        target = verify.HERE / entry["path"]
        def changed_bytes(path, _target=target):
            data = originals[0](path)
            return data+b"\n" if path == _target else data
        with patch.object(Path, "read_bytes", changed_bytes):
            result.append(rejected(verify.authenticate, "pinned source mutation: " + entry["path"]))
    target = verify.HERE / "SOURCES.json"
    for duplicate in (False, True):
        changed = deepcopy(manifest)
        if duplicate:
            changed["snapshots"].append(changed["snapshots"][0])
        else:
            changed["snapshots"].pop()
        def changed_text(path, *args, _changed=changed, **kwargs):
            return json.dumps(_changed) if path == target else originals[1](path, *args, **kwargs)
        with patch.object(Path, "read_text", changed_text):
            result.append(rejected(verify.authenticate, "duplicate source entry" if duplicate else "missing source entry"))
    return result
