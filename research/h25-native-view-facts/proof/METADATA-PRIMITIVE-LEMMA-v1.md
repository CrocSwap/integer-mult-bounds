L12 — Mount-write mediation for ordinary metadata primitives

Hypotheses: use the selected exact Linux `v6.12` VFS semantics; the actual successful constructor has the final copied namespace with all ordinary mounts read-only except the exact artifact parent and usage clones; old regular-file, directory and mount references are retired; self/ancestor proc-reference closure is established as in L2/L3; no unreviewed delegated filesystem or administrative topology interposition is introduced. This lemma concerns ordinary namespace file objects. The explicitly admitted stdout/stderr pipe endpoints are a separate internal-filesystem channel and are not falsely described as read-only mounts.

Conclusion: allowing `chmod`, ownership, timestamp and xattr syscall families does not let an ordinary final-view path or an O_RDONLY/O_PATH file reference mutate a read-only external file. These syscalls perform a VFS mount-write check before their inode metadata operation. They remain available on the artifact/usage exceptions, subject to normal permission and operation-specific checks. Thus the proof need not claim that Landlock can filter metadata, and it need not exempt a compiler from confinement.

The exact primitive proof is:

| Primitive family | Exact retained source and physical lines | Required step before mutation |
|---|---|---|
| `chmod`, `fchmod`, `fchmodat`, `fchmodat2` | `primary/open.c`, `chmod_common` 636–664 and `vfs_fchmod` 666–670; syscall wrappers route to that common operation | `mnt_want_write(path->mnt)` precedes the LSM/`notify_change` operation. The FD form uses the actual `file->f_path`. |
| `chown`, `lchown`, `fchownat` | `primary/open.c`, 811–850 | Path resolution is followed by `mnt_want_write(path.mnt)` before `chown_common`. |
| `fchown` | `primary/open.c`, 853–863 | `mnt_want_write_file(file)` precedes the ownership operation. |
| `utime`, `utimes`, `utimensat`, FD timestamp forms | `primary/utimes.c`, `vfs_utimes` 20–77 and `do_utimes_fd` 109–123 | After validating the times, `mnt_want_write(path->mnt)` precedes `notify_change`. The FD form passes its actual `f_path`; world-write permission or an O_RDONLY FD is not an exemption. A no-change/error fast path is not a mutation. |
| `setxattr`, `lsetxattr` | `primary/xattr.c`, 633–683, particularly 652–660 | The resolved path must obtain mount-write access before `do_setxattr`. |
| `fsetxattr` | `primary/xattr.c`, 686–715 | The actual file must obtain mount-write access before the xattr operation. |
| `removexattr`, `lremovexattr`, `fremovexattr` | `primary/xattr.c`, 910–974 | Both path and FD variants obtain mount-write access before removal. |

`primary/namespace.c`, `__mnt_is_readonly` 381–384, tests the mount or superblock read-only state. `mnt_get_write_access`, 453–498, checks that state with the writer-transition synchronization and returns `-EROFS` on a read-only mount. The ordinary wrappers above use the corresponding mount-write API. Existing writer FDs require their separate reference-closure argument: merely changing a different copied mount would not revoke an old writable-mount reference. That is why closing old descriptors and replacing stdin's original devnull reference are substantive source steps.

The `/dev/null` character sink illustrates the distinction. Opening a character device for data output can be legitimate even through a read-only mount; the exact admitted sink still has its ordinary null behavior. Its inode metadata operations nevertheless follow the mount-write checks above. Reopening stdin through the final view removes the old writable-mount timestamp route without changing the underlying null sink. The final ioctl whitelist supplies the separate device-operation restriction.

The two inherited anonymous pipe endpoints should be stated as an admitted channel exception, not silently included in the ordinary read-only-file theorem. Their payload and FD-local effects remain subject to the exact relay/guardian lifetime and bounded-capture owner. An internal pipe inode is not a pathname alias to a retained regular capture or source file. The complete proof should not make the stronger unsupported assertion that every possible metadata bit of every anonymous kernel object is immutable. This refinement does not relax a required capture/source/retention oracle.

For compatibility, original required metadata operations on science output must remain within the writable artifact tree and use the same actual IDs, requested mode, umask and selected filesystem semantics. L7 addresses the selected LSM creation-label branch; the original metadata association and remaining proof must retain ACL/default-ACL, copied-attribute and retention-refusal consequences. This lemma is about the confinement check, not a universal metadata-equality claim.

Primary upstream files: [open.c](https://github.com/torvalds/linux/blob/v6.12/fs/open.c), [utimes.c](https://github.com/torvalds/linux/blob/v6.12/fs/utimes.c), [xattr.c](https://github.com/torvalds/linux/blob/v6.12/fs/xattr.c), and [namespace.c](https://github.com/torvalds/linux/blob/v6.12/fs/namespace.c). Complete Git blob and SHA256 pins are in `primary/INDEX-v6.json`, SHA256 `e1bd43774de853703ff8d6ea53b263609afecaa192a897d143cb68424cc8c2cb`, and `primary/SOURCE-SHA256SUMS-v5.txt`, SHA256 `98650e2ae84416fc655c890323a701f07a0a4f2a014a2796244b7d9ef7a15ef9`.

This is source reasoning only. No metadata syscall, kernel/host probe, implementation, compiler/native execution, test or archive operation was performed.
