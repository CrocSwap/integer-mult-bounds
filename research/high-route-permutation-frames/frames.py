"""Offline column-frame scheduling; no runtime logical-wire renaming.

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction


def need(condition, message):
    if not condition:
        raise ValueError(message)


def price(word):
    """Number of complete B1 calls per row at positive high width."""
    return sum(1 if k == "swap" else 2 if k == "add" and c > t else 0
               for k, t, c, _ in word)


def setup_coefficient(dimension):
    """PR3301 conditional setup coefficient; its proof is pinned separately."""
    return 3*(716+1866*(dimension*dimension).bit_length())+36


def paid_price(word, dimension):
    """V coefficient of swap adapters plus the varying setup term, per row."""
    return 100000*price(word)+setup_coefficient(dimension)*sum(k == "swap" for k,t,c,v in word)


def defer(word, dimension):
    """Return an exact word with ordered ADDs and a paid terminal frame."""
    need(type(dimension) is int and dimension > 0, "positive dimension")
    location = list(range(dimension))
    occupant = list(range(dimension))
    output = []

    def physical_swap(a, b):
        need(a != b, "distinct physical fields")
        output.append(("swap", a, b, Fraction(1)))
        x, y = occupant[a], occupant[b]
        occupant[a], occupant[b] = y, x
        location[x], location[y] = b, a

    for kind, target, control, value in word:
        need(kind in ("add", "swap", "scale"), "closed factor vocabulary")
        need(type(target) is int and type(control) is int and
             0 <= target < dimension and 0 <= control < dimension,
             "field index")
        value = Fraction(value)
        if kind == "swap":
            need(target != control and value == 1, "canonical swap")
            a, b = location[target], location[control]
            location[target], location[control] = b, a
            occupant[a], occupant[b] = control, target
        elif kind == "add":
            need(target != control, "distinct ADD fields")
            if location[control] > location[target]:
                physical_swap(location[target], location[control])
            output.append((kind, location[target], location[control], value))
        else:
            need(value != 0, "invertible scale")
            output.append((kind, location[target], location[target], value))
    for target in range(dimension):
        if location[target] != target:
            physical_swap(location[target], target)
    need(location == list(range(dimension)), "canonical terminal frame")
    return tuple(output)


def schedule(word, dimension):
    """Keep the original unless native calls fall and the paid bound does not rise.

    A native-call tie keeps the original. The second guard retains the full
    PR3301 setup/adapter coefficient, conditional on that stated source bound.
    This does not assert optimality or compare actual native execution times.
    """
    original = tuple((k, t, c, Fraction(v)) for k, t, c, v in word)
    forward = defer(original, dimension)
    backward = inverse(defer(inverse(original), dimension))
    candidate = min((forward, backward), key=lambda w: (price(w), len(w), repr(w)))
    return candidate if (price(candidate) < price(original) and
                         paid_price(candidate, dimension) <= paid_price(original, dimension)) else original


def inverse(word):
    return tuple((k,t,c, -F if k == "add" else 1/F if k == "scale" else F)
                 for k,t,c,v in reversed(word) for F in (Fraction(v),))


def scheduled_registry(base_class):
    """Opt-in PR2915 Registry class; source code and runtime stay unchanged."""
    class FrameRegistry(base_class):
        def register(self, matrix, word):
            # Authenticate the caller's original word before transforming it.
            word = tuple(word)
            base_class.register(self, matrix, word)
            base_class.register(self, matrix, schedule(word, self.dimension))
    return FrameRegistry


def optimize_registry(registry):
    """Schedule the baseline registry's actual winning words, preserving keys."""
    result = type(registry)(registry.dimension)
    for matrix, word in registry.words.items():
        result.register(matrix, schedule(word, registry.dimension))
    need(result.words.keys() == registry.words.keys(), "same compiled chart domain")
    return result
