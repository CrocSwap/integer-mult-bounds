"""Check the active-forest injection and the complete first-entry bit budget."""

from collections import Counter
import ast
from io import BytesIO
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

from staged_carriers import COMPLEX_LOG, RANK_LOGS, strong_precision_log


def source_proof(periodic):
    total = Counter()
    examples = (
        periodic.Rule(6, (2, 3), (1,)),
        periodic.Rule(7, (3, 4, 6), (1, 2)),
        periodic.Rule(9, (2, 4, 5, 8), (1, 1)),
        periodic.Rule(9, (4, 4, 6), (2, 3)),
    )
    for rule in examples:
        planner = periodic.make_planner(rule)
        for rank in (32, 76, 124, 252, 508, 764):
            active = rank - rank % 4
            if active // 4 < rule.ambient:
                continue
            plan = planner(rank)
            forest = plan.forest
            units = {path: {u.future: u for u in rows} for path, rows in forest.layers.items()}
            for path, rows in units.items():
                charged = []
                for future in rows:
                    cursor, label = path, future
                    while True:
                        kind, port = units[cursor][label].ports[0]
                        if kind == "source":
                            src_path, src_future, i, _ = forest.sources[port]
                            assert (src_path, src_future, i) == (cursor, label, 0)
                            charged.append(port)
                            break
                        assert kind == "parent" and cursor and port == (0,) + label
                        cursor, label = cursor[:-1], port
                assert len(set(charged)) == len(rows)
                assert len(rows) <= len(forest.sources) <= plan.owners_per_copy
                chain = sum(len(units[path[:j]]) for j in range(len(path) + 1))
                assert chain <= (forest.height + 1) * len(forest.sources)
                assert 15 * plan.copies * plan.owners_per_copy < 16 * plan.width
                total["unit_assignments"] += len(charged)
                total["path_slices"] += 1
            assert all(15 * planner(e).width <= plan.width for e in forest.exits.values())
            total["forests"] += 1
    return total


def physical_sites(package, previous, old):
    sources = (
        (
            package,
            "receiver direct_body same_order_body triangular_ordinary multiplier quotient_route limb_scale",
        ),
        (
            previous,
            "product_path spool stack_tapes complex_stage crt_tree compact_crt compact_columns "
            "positive stripe_route striped_tensor growing_binary raw_binary module_atoms raw48 binary_io ordinary",
        ),
        (old, "streaming_routes periodic powered"),
    )
    sizes, widths = set(), set()
    sites = 0
    for root, names in sources:
        for name in names.split():
            tree = ast.parse((root / (name + ".py")).read_text())
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                fn = node.func
                label = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", None)
                if label in {"TemporaryFile", "scratch", "snapshot", "work_tapes", "frames"}:
                    sites += 1
                if label == "work_tapes":
                    sizes.add(ast.literal_eval(node.args[0]))
                elif label == "frames":
                    widths.add(ast.literal_eval(node.args[-1]))
    assert sites < 1024 and max(sizes) <= 22 and max(widths) <= 3
    return {
        "data_modules": sum(len(n.split()) for _, n in sources),
        "sites": sites,
        "work_tape_max": max(sizes),
        "page_width_max": max(widths),
    }


def arena_positions(package, previous, old):
    from unittest.mock import patch

    sys.path.extend(str(p) for p in (package, previous, old))
    from raw_binary import Banks
    from spool import Arena as NumericArena
    from stack_tapes import Arena as Pages

    class History(BytesIO):
        peak = 0

        def write(self, buf):
            count = super().write(buf)
            self.peak = max(self.peak, self.tell())
            return count

    # The real numeric slots divide the extent at each nested height.
    tape = History()
    root = NumericArena(3, 1, tape)
    roots = [root.field() for _ in range(5)]
    for f in roots:
        f.clear()
    for _ in range(2):
        roots.pop().retire()
    assert (root.live, root.high) == (3, 5)
    with root.child(2) as c:
        assert c.start == 80
        a = [c.field() for _ in range(7)]
        for f in a:
            f.clear()
        for _ in range(6):
            a.pop().retire()
        with c.child(1) as g:
            assert g.start == 136
            b = [g.field() for _ in range(3)]
            for f in b:
                f.clear()
                f.retire()
        a.pop().retire()
    assert tape.peak == 148
    for _ in range(4):
        f = root.field()
        f.clear()
        roots.append(f)
    assert (root.live, root.high) == (7, 7)
    with root.child(2) as c:
        assert c.start == 112
        f = c.field()
        f.clear()
        f.retire()
    for f in roots:
        f.retire()
    root.close()
    assert tape.peak == 148

    # The ordinary owner bank writes each actual slot at its public index.
    source = History()
    bank = Banks(source, 1, 1, 1, 7, None)
    ids = [bank.zero() for _ in range(5)]
    for _ in range(2):
        bank.retire(ids.pop())
    ids.extend(bank.zero() for _ in range(4))
    assert bank.capacity == 7 and max(ids) == 6 and source.peak == 7 * bank.volume
    for owner in ids:
        bank.retire(owner)

    # A prior, larger child peak remains even after the actual slot shrinks.
    with patch("stack_tapes.TemporaryFile", History):
        arena = Pages()
        with arena.frames("compiler", 1) as (outer,):
            outer.write(bytes(30))
            with arena.frames("compiler", 1) as (child,):
                assert child.base == 30
                child.write(bytes(70))
            outer.seek(30)
            outer.write(bytes(20))
            with arena.frames("compiler", 1) as (child,):
                assert child.base == 50
                child.write(bytes(3))
        assert arena.head(("compiler", 0)).peak == 100
        arena.close()
    return {
        "numeric_historical_bytes": 148,
        "binary_owner_capacity": bank.capacity,
        "binary_page_historical_bytes": 100,
    }


def numeric():
    a = strong_precision_log()
    assert a % 2 == 0 and pow(2, a, 6) == 4
    s = a + 1
    logs = [64 + (v + 1).bit_length() + 28 * v for v in (264, 480)]
    raw = max(logs)
    forest_height_bits = max(RANK_LOGS + (COMPLEX_LOG,)).bit_length() + 1
    macro_log = 1 << 18
    # More than four times the unit log, depth, primitive scratch, and formatting.
    assert 4 * raw + 8 * forest_height_bits + 512 < macro_log
    complex_levels = (s + COMPLEX_LOG - 1) // COMPLEX_LOG + 2
    ordinary_levels = 6 * 9
    level_count = complex_levels + ordinary_levels + 32
    heads_log = 32 + 2 * (s + 128).bit_length()
    # Twice per level for input and returned child, plus every historical head.
    data_overhead = (2 * level_count + 4) * macro_log + heads_log + 16
    stripes_log = s // 2 - 2
    assert stripes_log - data_overhead > 1024
    # Every private control/meter has logarithmic size below log T - 64.
    log_k = (s + 1) ** 8
    private_log = 128 * (s + 130) * log_k
    assert (12 * (private_log + 64)).bit_length() <= a
    # CRT grouped-key guard and positive suffix guard.
    crt_guard_loss = 64 * (128 * s * s + s)
    assert (1200 * (crt_guard_loss + 2 * s + 128)).bit_length() <= a
    assert (s - 3) ** 2 >= s + 9
    return {
        "s": s,
        "raw_unit_log_bound": raw,
        "macro_log": macro_log,
        "complex_levels": complex_levels,
        "all_levels": level_count,
        "head_log": heads_log,
        "data_overhead_log": data_overhead,
        "stripe_log_lower": stripes_log,
        "stripe_margin_bits": stripes_log - data_overhead,
        "private_margin_check_bits": (12 * (private_log + 64)).bit_length(),
    }


if __name__ == "__main__":
    print(numeric())
    if len(sys.argv) in (2, 4):
        path = Path(sys.argv[1]) / "periodic.py"
        spec = spec_from_file_location("active_source_periodic", path)
        module = module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        print(dict(source_proof(module)))
        if len(sys.argv) == 4:
            print(physical_sites(Path(sys.argv[3]), Path(sys.argv[2]), path.parent))
            print(arena_positions(Path(sys.argv[3]), Path(sys.argv[2]), path.parent))
