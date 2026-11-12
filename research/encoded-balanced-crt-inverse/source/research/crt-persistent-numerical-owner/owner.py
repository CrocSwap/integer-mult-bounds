"""One physical63-role owner for the unchanged numerical CRT RowEntry.
JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.
"""
from types import SimpleNamespace


class Bank:
    def __init__(self, words, entry, ports=None):
        self.w, self.entry = words, entry
        # Physical allocation belongs only to initial owner acquisition.
        if ports is None:
            ports = [entry.Port(words) for _ in range(63)]
            for port in ports:
                port.retire()
        words.need(len(ports) == 63 and len({id(p.cells) for p in ports}) == 63,
                   '63 distinct owned backing roles')
        self.ports = tuple(ports)
        self.busy = False
        self.cursor = 0

    def take(self, words):
        words.need(words is self.w and self.busy and self.cursor < 63,
                   'fixed live owner role')
        port = self.ports[self.cursor]
        self.cursor += 1
        words.need(port.head == 1 and port.read() == words.BLANK,
                   'retired role head and body')
        port.step(-1)
        words.need(port.read() == words.BLANK, 'retired marker')
        port.write(words.LEFT)
        port.step(1)
        return port

    def open(self, records, producer, bridge, source, dirty,
             widths, ell, level, start, row):
        self.w.need(not self.busy, 'previous result must retire first')
        self.w.need(not ({id(p.cells) for p in self.ports} &
                         {id(p.cells) for p in (source, *dirty)}),
                    'borrowed backing disjoint from owner')
        self.busy, self.cursor = True, 0
        bank = self

        class Reentry(self.entry.Entry):
            def new_port(self):
                port = bank.take(self.w)
                self.owned.append(port)
                self.control += 1
                return port

        adapter = SimpleNamespace(Port=self.take, Entry=Reentry)
        actual = bridge.RowEntry(self.w, records, adapter, producer, source,
                                 dirty, widths, ell, level, start, row)
        self.w.need(self.cursor == (63 if actual.active else 0),
                    'complete fixed role acquisition')
        return Lease(self, actual)

    def release(self):
        self.w.need(self.busy, 'live bank')
        # Fixed-role checks are paid local observations, never tail truncation.
        for port in self.ports[:self.cursor]:
            self.w.need(port.head == 1 and port.read() == self.w.BLANK,
                        'retired numerical body')
            port.step(-1)
            self.w.need(port.read() == self.w.BLANK, 'retired owned marker')
            port.step(1)
        self.busy = False


class Lease:
    def __init__(self, bank, actual):
        self.bank, self.actual, self.closed = bank, actual, False

    def close(self):
        self.bank.w.need(not self.closed, 'single row result retirement')
        self.actual.close()
        self.bank.release()
        self.closed = True
