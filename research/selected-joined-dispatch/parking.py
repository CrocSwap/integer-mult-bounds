"""One marked payload stack; pop visits only the current frame's suffix.

Host indices represent tape-head positions. The charged lowering walks from
the current top to its own marker; it does not scan older frames.
"""
from array import array
from dataclasses import dataclass

from algebra import need
from streams import Tape


@dataclass(frozen=True)
class Frame:
    start: int
    records: int


class Parking:
    marker = 1 << 32

    def __init__(self, meter):
        self.meter = meter
        self.records = array("Q")
        self.frames = []

    def push(self, source):
        need(source.head == 0, "park at a completed local boundary")
        n = len(source.records)
        frame = Frame(len(self.records), n)
        self.records.append(self.marker)
        self.records.extend(iter(source.records))
        self.frames.append(frame)
        self.meter["parking_pushes"] += 1
        self.meter["parking_read_bits"] += 32 * n
        self.meter["parking_write_bits"] += 64 * (n + 1)
        self.meter["parking_head_bits"] += 32 * n + 64 * (n + 1)
        self.meter["parking_max_depth"] = max(self.meter["parking_max_depth"], len(self.frames))
        self.meter["parking_peak_records"] = max(self.meter["parking_peak_records"], len(self.records))
        source.head = n
        source.erase()
        return frame

    def pop(self, frame):
        need(self.frames and self.frames[-1] == frame, "restore only the active frame")
        need(len(self.records) == frame.start + frame.records + 1 and
             self.records[frame.start] == self.marker, "current parking delimiter")
        n = frame.records
        result = Tape(self.meter, self.records[frame.start + 1:])
        self.meter["parking_read_bits"] += 64 * n
        self.meter["parking_write_bits"] += 32 * n
        self.meter["parking_erased_bits"] += 64 * (n + 1)
        self.meter["parking_head_bits"] += 192 * (n + 1) + 64 * n
        del self.records[frame.start:]
        self.frames.pop()
        self.meter["parking_pops"] += 1
        return result

    def closed(self):
        return not self.records and not self.frames
