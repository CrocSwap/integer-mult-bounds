"""Finite selected chart words and their exact low/carry specialization."""
from fractions import Fraction as F
import stage_sources
_source, retained, data = stage_sources.activate()
from words import need


def matrix_key(matrix):
    return tuple(tuple(F(value) for value in row) for row in matrix)


def inverse_word(word):
    return tuple((kind, target, control, 1/value if kind == "scale" else -value if kind == "add" else value)
                 for kind, target, control, value in reversed(word))


def ordinary_count(word):
    return sum(1 if kind == "swap" else 2 if kind == "add" and control > target else 0
               for kind, target, control, _value in word)


class Registry:
    def __init__(self, dimension):
        self.dimension, self.words, self.compiled = dimension, {}, {}
        self.register(retained.identity(dimension), ())

    def register(self, matrix, word):
        word = tuple((kind, target, control, F(value)) for kind, target, control, value in word)
        key = matrix_key(matrix)
        need(matrix_key(retained.replay(word, self.dimension)) == key, "exact factor word endpoint")
        for kind, target, control, value in word:
            need(kind in ("swap", "scale", "add") and 0 <= target < self.dimension and
                 0 <= control < self.dimension, "fixed column-factor vocabulary")
            need(value in (F(-4), F(-2), F(-1), F(-1,2), F(-1,4),
                           F(1,4), F(1,2), F(1), F(2), F(4)), "selected dyadic coefficient alphabet")
        old = self.words.get(key)
        if old is None or (ordinary_count(word), len(word), repr(word)) < (ordinary_count(old), len(old), repr(old)):
            self.words[key] = word
            self.compiled.clear()

    def compile(self, route):
        if route in self.compiled:
            return self.compiled[route]
        need(route.dimension == self.dimension, "route dimension binding")
        word = self.words.get(matrix_key(route.chart))
        need(word is not None, "route has an authenticated factor word")
        low = [list(row) for row in route.low]
        operations = []
        def scale_steps(target, magnitude, inverse=False):
            need(magnitude in (1,2,4), "compiled dyadic magnitude")
            for _ in range({1:0, 2:1, 4:2}[magnitude]):
                operations.append(("half" if inverse else "double", target))
        for kind, target, control, coefficient in word:
            a, d = coefficient.numerator, coefficient.denominator
            inverse = pow(d, -1, route.q)
            for row in range(self.dimension):
                y, x = low[row][target], low[row][control]
                target_field, control_field = row*self.dimension+target, row*self.dimension+control
                if kind == "swap":
                    low[row][target], low[row][control] = x, y
                    operations.append(("swap", target_field, control_field))
                    continue
                value = d*y+a*x if kind == "add" else a*y
                following = value*inverse % route.q
                carry, remainder = divmod(value-d*following, route.q)
                need(remainder == 0 and abs(carry) <= 4, "exact bounded low carry")
                if kind == "add":
                    need(target != control, "distinct affine fields")
                    scale_steps(target_field, d)
                    operations.append(("add", target_field, control_field, a))
                else:
                    scale_steps(target_field, abs(a))
                    if a < 0:
                        operations.append(("negate", target_field))
                if carry:
                    operations.append(("translate", target_field, carry))
                scale_steps(target_field, d, True)
                low[row][target] = following
        need(tuple(map(tuple, low)) == route.target_low, "compiled complete target low class")
        self.compiled[route] = tuple(operations)
        return self.compiled[route]


def selected_registry(catalogue):
    names = (retained.GEOMETRY, retained.TEMPLATE, retained.GLOBAL, retained.WORD,
             retained.EXPECTED, retained.ASSEMBLY)
    routes, receipt = retained.compile_catalog({name:data[name] for name in names})
    registry, checks = Registry(64), 0
    for chart in sorted(catalogue.charts, key=lambda value: value.key):
        if chart.kind == "data":
            key = f"data:{chart.port}:{chart.stage}"
        elif chart.kind == "host":
            key = "host:" + ",".join(map(str, chart.axes)) + (f":{chart.port}" if chart.port >= 0 else "")
        else:
            continue
        word = tuple((kind, target, control, F(value)) for kind, target, control, value in routes[key]["word"])
        inverse = inverse_word(word)
        matrix = catalogue.chart_matrix(chart)
        registry.register(matrix, inverse)
        registry.register(retained.replay(word), word)
        checks += 1
    need(checks == 1123, "complete retained selected owner chart vocabulary")
    return registry, dict(source_types=checks, matrices=len(registry.words), retained=receipt)
