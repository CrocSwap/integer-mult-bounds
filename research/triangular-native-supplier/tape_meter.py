"""Count the occupied extents and every move of an instrumented verification tape."""

from collections import Counter
from io import BytesIO
from tempfile import TemporaryFile


class Motion:
    def __init__(self):
        self.live = self.peak = 0
        self.bytes = Counter()

    def tape(self, data=None):
        return Track(
            self,
            TemporaryFile() if data is None else BytesIO(data),
            0 if data is None else len(data),
        )


class Track:
    def __init__(self, motion, stream, length):
        self.motion = motion
        self.stream = stream
        self.length = 0
        self.resize(length)

    def resize(self, length):
        self.motion.live += length - self.length
        self.length = length
        self.motion.peak = max(self.motion.peak, self.motion.live)

    def tell(self):
        return self.stream.tell()

    def seek(self, offset, whence=0):
        before = self.tell()
        after = self.stream.seek(offset, whence)
        self.motion.bytes["seek"] += abs(after - before)
        return after

    def read(self, count=-1):
        data = self.stream.read(count)
        self.motion.bytes["read"] += len(data)
        return data

    def write(self, data):
        result = self.stream.write(data)
        self.resize(max(self.length, self.tell()))
        self.motion.bytes["write"] += result
        return result

    def truncate(self):
        self.resize(self.tell())
        return self.stream.truncate()

    def __enter__(self):
        return self

    def close(self):
        self.stream.close()
        self.resize(0)

    def __exit__(self, *args):
        self.close()
