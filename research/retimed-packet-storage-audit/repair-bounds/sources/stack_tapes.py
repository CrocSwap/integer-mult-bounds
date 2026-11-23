"""Keep same-stage frames in fixed tape files, with top-only pending and answer packets."""

from contextlib import ExitStack, contextmanager
from tempfile import TemporaryFile

from streaming_routes import CHUNK, read_exact, write_zeros


class FileHead:
    def __init__(self, file):
        self.file = file
        self.moves = 0
        self.peak = 0
        self.frames = []

    def at(self, position):
        self.moves += abs(self.file.tell() - position)
        self.file.seek(position)

    def get(self, position, size):
        self.at(position)
        data = read_exact(self.file, size)
        self.moves += size
        return data

    def put(self, position, data):
        self.at(position)
        self.file.write(data)
        self.moves += len(data)
        self.peak = max(self.peak, position + len(data))


class Page:
    def __init__(self, head):
        self.head = head
        self.base = head.frames[-1].base + head.frames[-1].size if head.frames else 0
        self.size = self.cursor = 0
        head.frames.append(self)

    def tell(self):
        return self.cursor

    def seek(self, offset, whence=0):
        start = (0, self.cursor, self.size)[whence]
        if not 0 <= start + offset <= self.size:
            raise ValueError("The tape head would leave its active frame")
        self.cursor = start + offset
        return self.cursor

    def read(self, size=-1):
        remaining = self.size - self.cursor
        size = remaining if size < 0 else min(size, remaining)
        data = self.head.get(self.base + self.cursor, size)
        self.cursor += size
        return data

    def write(self, data):
        if self.head.frames[-1] is not self:
            raise ValueError("An outer frame cannot write through a suspended tape")
        self.head.put(self.base + self.cursor, data)
        self.cursor += len(data)
        self.size = max(self.size, self.cursor)
        return len(data)

    def truncate(self):
        if self.head.frames[-1] is not self:
            raise ValueError("An outer frame cannot resize a suspended tape")
        self.size = self.cursor

    def release(self):
        if self.head.frames[-1] is not self:
            raise ValueError("A tape frame returned out of order")
        self.seek(0)
        write_zeros(self, self.size)
        self.head.frames.pop()


class PacketStack:
    def __init__(self, head):
        self.head = head
        self.top = 0

    def push_reverse(self, tape, size):
        end = tape.tell()
        remaining = size
        while remaining:
            chunk = min(CHUNK, remaining)
            tape.seek(end - chunk)
            self.head.put(self.top, read_exact(tape, chunk)[::-1])
            self.top += chunk
            end -= chunk
            remaining -= chunk

    def pop_forward(self, target, size):
        if size > self.top:
            raise ValueError("A low packet crossed its saved boundary")
        while size:
            chunk = min(size, CHUNK)
            self.top -= chunk
            target.write(self.head.get(self.top, chunk)[::-1])
            self.head.put(self.top, bytes(chunk))
            size -= chunk

    def append(self, source, size):
        while size:
            chunk = min(size, CHUNK)
            self.head.put(self.top, read_exact(source, chunk))
            self.top += chunk
            size -= chunk

    def take_answers(self, marker, target):
        position = marker
        while position < self.top:
            chunk = min(CHUNK, self.top - position)
            target.write(self.head.get(position, chunk))
            self.head.put(position, bytes(chunk))
            position += chunk
        self.top = marker


class Arena:
    def __init__(self):
        self.files = ExitStack()
        self.heads = {}
        self.pending = PacketStack(self.head(("pending", 0)))
        self.answers = PacketStack(self.head(("answers", 0)))

    def head(self, key):
        if key not in self.heads:
            self.heads[key] = FileHead(self.files.enter_context(TemporaryFile()))
        return self.heads[key]

    @contextmanager
    def frames(self, kind, count):
        pages = [Page(self.head((kind, i))) for i in range(count)]
        try:
            yield pages
        finally:
            for page in reversed(pages):
                page.release()

    def close(self):
        self.files.close()

    def counts(self):
        return (
            len(self.heads),
            sum(h.moves for h in self.heads.values()),
            sum(h.peak for h in self.heads.values()),
        )
