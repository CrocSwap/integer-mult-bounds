"""Small exact sparse operations, retained from Ali Romman/CubeJerry. Apache-2.0."""
class L:
    @staticmethod
    def need(ok, why):
        if not ok: raise ValueError(why)
    @staticmethod
    def add(dst, src, q):
        for k,v in tuple(src.items()):
            value=dst.get(k,0)+q*v
            if value: dst[k]=value
            else: dst.pop(k,None)
    @staticmethod
    def span(basis):
        out={0}
        for v in basis:
            L.need(type(v) is int and 0<v<512 and v not in out,'Independent binary basis')
            out|={x^v for x in tuple(out)}
        return frozenset(out)
