"""Exact occupied-cell representation for the pinned T37 checker. Apache-2.0."""
import ast
import hashlib
import inspect


def patch(source):
    changes = [
        ("    helpers, families, used = defaultdict(set), defaultdict(set), defaultdict(set)\n",
         "    helpers, families, used = defaultdict(set), defaultdict(set), defaultdict(int)\n"),
        ("        cells = set(range(offset, offset + width))\n"
         "        bin_key = (owner, child, port)\n"
         "        require(offset >= 0 and offset + width <= c['rank'][child] and not used[bin_key] & cells, 'overlapping or out-of-capacity slice')\n"
         "        used[bin_key].update(cells)\n",
         "        span = range(offset, offset + width)\n"
         "        bin_key = (owner, child, port)\n"
         "        require(offset >= 0 and offset + width <= c['rank'][child], 'overlapping or out-of-capacity slice')\n"
         "        cells = ((1 << len(span)) - 1) << span.start\n"
         "        require(not used[bin_key] & cells, 'overlapping or out-of-capacity slice')\n"
         "        used[bin_key] |= cells\n"),
        ("            cells = used[owner, child, port]\n"
         "            require(cells == set(range(len(cells))), 'gap in pending prefix')\n"
         "            left = c['rank'][child] - len(cells)\n",
         "            cells = used[owner, child, port]\n"
         "            count = cells.bit_count()\n"
         "            require(cells == (1 << count) - 1, 'gap in pending prefix')\n"
         "            left = c['rank'][child] - count\n")]
    for old, new in changes:
        if source.count(old) != 1:
            raise ValueError("pinned occupied-cell block changed")
        source = source.replace(old, new)
    return source


def install(module):
    original = inspect.getsource(module.check_roles)
    tree = ast.parse(original)
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef) or tree.body[0].name != "check_roles":
        raise ValueError("unexpected checker function")
    adapted = patch(original)
    # The unchanged function body shares its original globals, including the
    # T37 constants installed later by the unchanged official wrapper.
    exec(compile(adapted, "<t37-exact-occupancy-bitmaps>", "exec"), module.__dict__)
    return {"original_function_sha256": hashlib.sha256(original.encode()).hexdigest(),
            "adapted_function_sha256": hashlib.sha256(adapted.encode()).hexdigest(),
            "changed_blocks": 3}
