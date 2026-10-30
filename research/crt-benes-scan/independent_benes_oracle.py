"""Independent levelwise Beneš oracle; semantic arrays are not a tape model.

No primary implementation is imported. FIFO component coloring and bottom-up
table assembly deliberately avoid the retained source's recursive DFS order.
"""
from collections import deque
from itertools import permutations
import hashlib
import json
from random import Random


def compile_levelwise(permutation):
    permutation = tuple(permutation)
    size = len(permutation)
    if size < 2 or size & (size - 1) or sorted(permutation) != list(range(size)):
        raise ValueError("dyadic permutation required")
    pending = deque([((), permutation)])
    nodes = {}
    order = []
    while pending:
        path, images = pending.popleft()
        order.append(path)
        n = len(images)
        if n == 2:
            nodes[path] = {"layers": ((0, (images[0], images[0])),)}
            continue
        inverse = {image: x for x, image in enumerate(images)}
        color = [-1] * n
        for seed in range(n):
            if color[seed] != -1:
                continue
            color[seed] = 0
            component = deque([seed])
            while component:
                x = component.popleft()
                for neighbor in (inverse[images[x] ^ 1], x ^ 1):
                    wanted = color[x] ^ 1
                    if color[neighbor] == -1:
                        color[neighbor] = wanted
                        component.append(neighbor)
                    elif color[neighbor] != wanted:
                        raise ValueError("alternating-pair graph is not bipartite")
        first = tuple(color[x] ^ (x & 1) for x in range(n))
        last = tuple(color[inverse[y]] ^ (y & 1) for y in range(n))
        nodes[path] = {"first": first, "last": last}
        for c in (0, 1):
            child = [None] * (n // 2)
            for x in range(n):
                if color[x] == c:
                    child[x // 2] = images[x] // 2
            pending.append((path + (c,), tuple(child)))
    for path in reversed(order):
        node = nodes[path]
        if "layers" in node:
            continue
        left, right = [nodes[path + (c,)]["layers"] for c in (0, 1)]
        n = len(node["first"])
        layers = [(0, node["first"])]
        for layer in range(len(left)):
            if left[layer][0] != right[layer][0]:
                raise ValueError("children have different bit schedules")
            table = tuple((left, right)[x & 1][layer][1][x // 2] for x in range(n))
            layers.append((1 + left[layer][0], table))
        layers.append((0, node["last"]))
        node["layers"] = tuple(layers)
    return nodes[()]["layers"]


def endpoint(layers, value):
    for target, table in layers:
        value ^= table[value] << target
    return value


def check(permutation, digest):
    size = len(permutation)
    h = size.bit_length() - 1
    layers = compile_levelwise(permutation)
    if tuple(bit for bit, _ in layers) != tuple(range(h)) + tuple(range(h - 2, -1, -1)):
        raise ValueError("wrong universal target-bit schedule")
    for target, table in layers:
        for x in range(size):
            if table[x] != table[x ^ (1 << target)]:
                raise ValueError("control reads its own target")
    for x, expected in enumerate(permutation):
        actual = endpoint(layers, x)
        if actual != expected or endpoint(tuple(reversed(layers)), actual) != x:
            raise ValueError("forward/inverse permutation endpoint mismatch")
    digest.update(bytes(endpoint(layers, x) for x in range(size)))
    return len(layers) * size


def mutation_witness():
    for permutation in permutations(range(4)):
        layers = compile_levelwise(permutation)
        # A child table is indexed by x//2, while x&1 chooses its child.
        # Swapping these child selectors is a genuine port-orientation bug.
        target, table = layers[1]
        broken = (layers[0], (target, tuple(table[x ^ 1] for x in range(4))), layers[-1])
        for x, expected in enumerate(permutation):
            actual = endpoint(broken, x)
            if actual != expected:
                return {"permutation": list(permutation), "input": x,
                        "expected": expected, "wrong": actual,
                        "mutation": "interchange the child selector parity"}
    raise ValueError("child-selector negative control was not detected")


def main():
    digest = hashlib.sha256()
    cases = columns = control_columns = 0
    for size in (2, 4, 8):
        for permutation in permutations(range(size)):
            control_columns += check(permutation, digest)
            cases += 1
            columns += size
    rng = Random(4174)
    for size in (16, 32, 64):
        for _ in range(16):
            permutation = list(range(size))
            rng.shuffle(permutation)
            control_columns += check(permutation, digest)
            cases += 1
            columns += size
    print(json.dumps({"status": "PASS_INDEPENDENT_BENES_SEMANTICS",
                      "permutations": cases, "endpoint_columns": columns,
                      "control_columns": control_columns,
                      "endpoint_sha256": digest.hexdigest(),
                      "negative_control": mutation_witness(),
                      "scope": "separate levelwise FIFO semantic oracle; host arrays and queues do not certify fixed-tape costs"},
                     sort_keys=True))


if __name__ == "__main__":
    main()
