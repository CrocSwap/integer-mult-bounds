"""A private deterministic preview1 file system for a fixed setup flight."""

import posixpath
import struct
from collections import Counter


class FileService:
    def __init__(self, argv, env):
        self.strings = {"args": argv, "environ": env}
        self.maximum = Counter()
        self.files = {"/": None, "/tmp": None}
        self.ino = {k: i for i, k in enumerate(self.files, 1)}
        self.descriptors = {
            0: ["/stdin", 0, 0],
            1: ["/stdout", 0, 0],
            2: ["/stderr", 0, 0],
            3: ["/", 0, 0],
        }
        for name in ("/stdin", "/stdout", "/stderr"):
            self.create(name, bytearray())
        self.cursor = 4
        self.rng = 0
        self.calls = Counter()
        self.bytecount = 0

    def create(self, path, data):
        path = posixpath.normpath(path)
        if path in self.files:
            return
        parent = posixpath.dirname(path)
        if parent not in self.files:
            self.create(parent, None)
        self.files[path] = data
        self.meta("joined_path", len(path.encode()))
        self.meta("entries", len(self.files))
        if data is not None:
            self.meta("file", len(data))
        self.ino[path] = max(len(self.ino) + 1, getattr(self, "inode", 0) + 1)
        self.inode = self.ino[path]

    def meta(self, k, v):
        self.maximum[k] = max(self.maximum[k], v)
        assert (
            self.maximum[k]
            < {
                "path": 4096,
                "joined_path": 4096,
                "iov": 2**16,
                "io": 2**28,
                "entries": 2**16,
                "dirrows": 2**16,
                "file": 2**29,
                "fd": 2**20,
                "live_fds": 2**16,
            }[k]
        )

    def handler(self, name):
        def call(c, *args):
            try:
                return self.service(name, c, *args)
            except BaseException as e:
                print("failed syscall", name, args, repr(e), flush=True)
                raise

        return call

    def service(self, name, caller, *x):
        self.calls[name] += 1
        mem = caller["memory"]

        def get(p, n):
            assert 0 <= n < 2**29
            return mem.read(caller, p, p + n)

        def put(p, data):
            if data:
                mem.write(caller, bytes(data), p)

        def number(p, n, fmt="I"):
            put(p, struct.pack("<" + fmt, n))

        def path(fd, p, n):
            self.meta("path", n)
            raw = get(p, n).decode()
            parent = self.descriptors.get(fd, ("/badfd",))[0]
            full = posixpath.normpath(posixpath.join(parent, raw))
            self.meta("joined_path", len(full.encode()))
            return full

        def ftype(file):
            return 3 if self.files[file] is None else 4

        def filestat(file, p):
            if file not in self.files:
                return 44
            data = self.files[file]
            put(
                p,
                struct.pack(
                    "<QQB7xQQQQQ",
                    1,
                    self.ino[file],
                    ftype(file),
                    1,
                    len(data) if data is not None else 0,
                    0,
                    0,
                    0,
                ),
            )
            return 0

        if name.startswith(("args_", "environ_")):
            strings = [r.encode() + b"\0" for r in self.strings[name.split("_")[0]]]
            p, q = x
            if "sizes" in name:
                number(p, len(strings))
                number(q, sum(map(len, strings)))
            else:
                for s in strings:
                    number(p, q)
                    put(q, s)
                    q += len(s)
                    p += 4
            return 0
        if name.startswith("clock_"):
            number(x[-1], 1, "Q")
            return 0
        if name == "random_get":
            p, n = x
            self.meta("io", n)
            raw = bytearray()
            for _ in range(n):
                self.rng = (1664525 * self.rng + 1013904223) & 0xFFFFFFFF
                raw.append(self.rng >> 24)
            put(p, raw)
            return 0
        if name == "proc_exit":
            raise RuntimeError(f"WASI exit {x[0]}")
        if name in ("fd_prestat_get", "fd_prestat_dir_name"):
            if x[0] != 3:
                return 8
            put(x[1], struct.pack("<B3xI", 0, 1) if name.endswith("get") else b"/")
            return 0
        if name == "path_filestat_get":
            return filestat(path(x[0], x[2], x[3]), x[4])
        if name == "path_open":
            fd, _flags, p, n, op, _base, _inherit, options, dst = x
            file = path(fd, p, n)
            if file not in self.files:
                if not op & 1 or posixpath.dirname(file) not in self.files:
                    return 44
                self.create(file, bytearray())
            elif op & 1 and op & 4:
                return 20
            if op & 2 and self.files[file] is not None:
                return 54
            if op & 8 and self.files[file] is not None:
                self.files[file].clear()
            handle = self.cursor
            self.cursor += 1
            self.meta("fd", handle)
            self.descriptors[handle] = [file, 0, options]
            number(dst, handle)
            self.meta("live_fds", len(self.descriptors))
            return 0
        if name in (
            "path_create_directory",
            "path_remove_directory",
            "path_unlink_file",
            "path_readlink",
        ):
            file = path(x[0], x[1], x[2])
            if name == "path_create_directory":
                if file in self.files:
                    return 20
                self.create(file, None)
                self.meta("entries", len(self.files))
                return 0
            if name == "path_readlink":
                return 28 if file in self.files else 44
            if file not in self.files:
                return 44
            del self.files[file], self.ino[file]
            return 0
        if name.startswith("fd_"):
            fd = x[0]
            if fd not in self.descriptors:
                return 8
            desc = self.descriptors[fd]
            file, offset, options = desc
            if name == "fd_close":
                del self.descriptors[fd]
                return 0
            if name == "fd_fdstat_get":
                put(
                    x[1],
                    struct.pack(
                        "<BxH4xQQ",
                        2 if fd <= 2 else ftype(file),
                        options,
                        2**30 - 1,
                        2**30 - 1,
                    ),
                )
                return 0
            if name == "fd_filestat_get":
                return filestat(file, x[1])
            data = self.files[file]
            if name == "fd_readdir":
                fd, p, n, cookie, stored = x
                if data is not None:
                    return 54
                rows = sorted(
                    (posixpath.basename(k), k)
                    for k in self.files
                    if k != "/" and posixpath.dirname(k) == file
                )
                self.meta("dirrows", len(rows))
                raw = bytearray()
                for i, (short, k) in enumerate(rows[cookie:], cookie + 1):
                    nbytes = short.encode()
                    raw.extend(
                        struct.pack("<QQIB3x", i, self.ino[k], len(nbytes), ftype(k))
                        + nbytes
                    )
                    if len(raw) >= n:
                        break
                raw = raw[:n]
                put(p, raw)
                number(stored, len(raw))
                return 0
            if name in ("fd_seek", "fd_tell"):
                if name == "fd_seek":
                    delta, whence = x[1:3]
                    desc[1] = [0, offset, len(data)][whence] + delta
                number(x[-1], desc[1], "Q")
                return 0
            if name in ("fd_read", "fd_write", "fd_pread", "fd_pwrite"):
                writing = name.endswith("write")
                explicit = name.startswith("fd_p")
                if explicit:
                    offset = x[3]
                if data is None:
                    return 31
                self.meta("iov", x[2])
                nbytes = 0
                for i in range(x[2]):
                    p, n = struct.unpack("<II", get(x[1] + 8 * i, 8))
                    self.meta("io", n)
                    if writing:
                        if options & 1:
                            offset = len(data)
                        assert offset <= len(data)
                        data[offset : offset + n] = get(p, n)
                        self.meta("file", len(data))
                    else:
                        n = min(n, len(data) - offset)
                        put(p, data[offset : offset + n])
                    offset += n
                    nbytes += n
                if not explicit:
                    desc[1] = offset
                self.bytecount += nbytes
                number(x[-1], nbytes)
                return 0
            if name in ("fd_fdstat_set_flags", "fd_advise", "fd_sync", "fd_datasync"):
                return 0
        raise RuntimeError("unexpected call " + name + " " + repr(x))
