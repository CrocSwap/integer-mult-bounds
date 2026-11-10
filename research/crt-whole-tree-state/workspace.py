"""Fixed-node stable backing; source arithmetic and retirement are unchanged.
JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
"""
from types import SimpleNamespace


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Workspace:
    def __init__(self):
        self.backing = {}
        self.ports = {}
        self.geometry = None
        self.live = False
        self.used = set()
        self.setup_actions = 0

    def begin(self, geometry, source, dirty):
        need(not self.live, 'previous source borrow must retire')
        need(self.geometry is None or self.geometry[:2] == geometry[:2], 'fixed whole-tree shape')
        protected = [source.cells, *(p.cells for p in dirty)]
        need(len({id(p) for p in protected}) == 9, 'protected backing aliases')
        need(not {id(p) for p in protected} & {id(p) for p in self.backing.values()},
             'owned backing aliases protected source')
        self.geometry = geometry
        self.live = True
        self.used = set()

    def claim(self, role):
        need(self.live and role not in self.used, 'single live owner per role')
        self.used.add(role)

    def cells(self, role):
        self.claim(role)
        if role not in self.backing:
            self.backing[role] = ['_']
            self.setup_actions += 1  # Fresh physical cell remains positively charged.
        return self.backing[role]

    def port(self, role, w, entry):
        self.claim(role)
        if role not in self.ports:
            port = object.__new__(entry.Port)
            port.w, port.cells, port.head, port.meter = w, bytearray([w.BLANK]), 0, w.Meter()
            self.setup_actions += 1
            self.ports[role] = port
            self.backing[role] = port.cells
        else:
            port = self.ports[role]
            need(port.head == 1, 'numerical retirement head')
            port.step(-1)  # The retired port is at head one, not a fresh origin.
        need(port.read() == w.BLANK, 'blank numerical origin')
        port.write(w.LEFT)
        port.step(1)
        return port

    def entry_facade(self, w, entry):
        workspace = self
        inputs = iter(('numeric.guide', 'numeric.canonical_left', 'numeric.canonical_right'))
        roles = tuple('numeric.word.' + str(i) for i in range(8, 64))
        roles += ('numeric.template', 'numeric.padded_left', 'numeric.padded_right', 'numeric.output')

        class Entry(entry.Entry):
            def new_port(self):
                port = workspace.port(roles[len(self.owned)], w, entry)
                self.owned.append(port)
                self.control += 1
                return port

        return SimpleNamespace(Port=lambda words: workspace.port(next(inputs), words, entry), Entry=Entry)

    def end(self, active):
        need(self.live, 'single workspace retirement')
        need(len(self.used) == (118 if active else 0), 'complete actual constructor ownership')
        need(len({id(x) for x in self.backing.values()}) == len(self.backing), 'distinct role backing')
        self.live = False
