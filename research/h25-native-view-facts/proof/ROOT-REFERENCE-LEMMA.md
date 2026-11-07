# The entry's own proc root names the protected copied mount

This is a constructive source lemma for the actual native entry, SHA256 `60af72915efea62f46ea376e2ba7ed0c616f99b09ca1beec0f4b0d8173609410`, from the closed native-dispatch predecessor. It resolves the proposed self-proc-root escape for that implementation. It neither executes a namespace operation nor changes the C source.

## Statement and hypotheses

Let `t` be the fresh, single-threaded entry task. Let `r_old` denote the root path in `t->fs` before the successful `unshare(CLONE_NEWNS)`, and let `r_new` denote the corresponding copied path afterwards. Assume the selected Linux v6.12 semantics, successful setup through the entry's recursive read-only `mount_setattr`, and the existing setup interval in which only the authenticated entry performs namespace operations. These are hypotheses about the indicated mechanism and trace, not a supplied compatibility flag or a claim about the installed host.

**Conclusion:** after that successful operation, the mount component of the root path returned by the task's own `/proc/self/root` has the newly installed read-only attribute. Following this magic link, opening it with `O_PATH`, resolving a relative path through such a descriptor, or passing its resolved path to a metadata syscall does not recover `r_old.mnt`. No additional `chroot` is required for this root-reference property. Writable artifact and usage mounts remain the two explicitly installed exceptions below that root; they do not replace the root path.

## The actual implementation changes attributes in place

The C source calls `unshare(CLONE_NEWNS)` in `enter_namespaces` at lines 355–369. In `make_view` at lines 466–493 it creates detached clones of the artifact parent and usage file only. It then opens `/` and adds recursive `RDONLY | NOSUID` attributes to that opened mount. The only subsequent `move_mount` calls attach those two writable clones to their exact existing artifact and usage paths.

In particular, this implementation does **not** attach a second root tree over `/`. The root reference cannot become stale merely because of a hypothetical root overmount that this code never performs. The subsequent cwd and stdin replacement closes their distinct pre-view reference issues; the root proof below follows the actual root path itself.

## Derivation of the root's ownership lineage

1. In Linux v6.12, `ksys_unshare` adds `CLONE_FS` when `CLONE_NEWNS` is requested. Its `unshare_fs` step provides a private `fs_struct` if sharing requires one. If the existing structure is already private, the absence of a newly allocated structure does not skip root remapping.
2. `unshare_nsproxy_namespaces` calls `create_new_namespaces` with the actual target filesystem structure: the newly allocated one when present, otherwise `current->fs`. `create_new_namespaces` passes that same structure to `copy_mnt_ns`. This closes the null-argument ambiguity in the unshare call chain. See [fork.c](https://github.com/torvalds/linux/blob/v6.12/kernel/fork.c) and [nsproxy.c](https://github.com/torvalds/linux/blob/v6.12/kernel/nsproxy.c).
3. `copy_mnt_ns` first copies the mount topology. In its second traversal, when an old mount matches the supplied filesystem structure's root mount, it replaces that root mount reference with the corresponding new mount reference. It similarly remaps the cwd mount. The old references are put after the traversal. Thus the task's root and cwd are not left on the parent's writable mount objects. The retained primary source is `review/proof/primary/namespace.c`, SHA256 `4e6809884d475aeb6b65a35897d55ffe7c11dd6f06d74b5784b84f3d0dc978e6`, with this function at lines 3916–3993.
4. The initial successful user-namespace creation also rules out silently starting from an unrelated chroot root in the selected source. `create_user_ns` rejects `current_chrooted()`. That predicate compares the task's root with its namespace root after following root mount stacking. This is a derived property of successful setup, rather than a new user request to alter the root. See [user_namespace.c](https://github.com/torvalds/linux/blob/v6.12/kernel/user_namespace.c) and `current_chrooted` in [namespace.c](https://github.com/torvalds/linux/blob/v6.12/fs/namespace.c).

The copied mount keeps the corresponding backing superblock and root dentry. This explains why original device/inode and pathname observations can remain genuine even though mount ownership and mount attributes have changed. It is not an assertion of equality between unrelated fresh output inodes.

## The root FD and the attribute update refer to that copied root

The entry opens `/` after namespace copying. In the selected namei implementation, an absolute path starts from the task's filesystem root. An `O_PATH` open uses the ordinary path lookup; a slash-only path has no filename component that can identify an unrelated mount. `mount_setattr` then resolves the empty pathname from that actual FD. No string prefix is used as mount authority.

`do_mount_setattr` operates on the resolved mount, and `mount_setattr_commit` writes the recalculated attributes into the mount objects themselves. With recursive operation it also visits their subordinate mounts. It does not allocate a replacement root path or leave an earlier writable copy in `t->fs`. After successful return, `r_new.mnt` itself therefore has `MNT_READONLY`. Existing stricter attributes are not cleared by the entry's zero `attr_clr`.

The relevant primary sources are `path_init`, `nd_jump_root`, `do_o_path` and the slash-only path handling in [namei.c](https://github.com/torvalds/linux/blob/v6.12/fs/namei.c), together with `do_mount_setattr` and `mount_setattr_commit` in [namespace.c](https://github.com/torvalds/linux/blob/v6.12/fs/namespace.c). The retained namespace file places `mount_setattr_commit` at line 4573 and its mount-attribute write at line 4582.

## Following `/proc/self/root` preserves the protected reference

The proc implementation obtains this link's target through `proc_root_link`, which calls `get_task_root`; that operation reads the task's **current** filesystem root. `proc_pid_get_link` passes the acquired path to `nd_jump_link`. The latter installs the supplied path in the lookup state; it does not reconstruct a path from the ancestor namespace or recover a discarded parent mount reference. See [proc/base.c](https://github.com/torvalds/linux/blob/v6.12/fs/proc/base.c) and [namei.c](https://github.com/torvalds/linux/blob/v6.12/fs/namei.c).

This argument deliberately does not depend on denying the task access to its own proc link. Self access may succeed. The returned mount is already the protected copied mount. A subsequent `openat` from an `O_PATH` descriptor uses that descriptor's actual path, so it likewise starts on the protected mount. A metadata operation that follows the magic link reaches the same copied mount and its mount-write checks. Crossing into the artifact or usage mount reaches the already declared writable exception; crossing to another ordinary copied mount reaches one covered by the recursive update.

The ancestor-task proc argument remains separate: it uses the namespace-sensitive ptrace/capability checks and the no-prior-descendant/inherited-policy invariant. It must not be substituted for this self-reference proof.

## Consequence for source correction and original observations

There is no established self-root escape in the actual in-place construction, and this proof step demands no C correction. Adding `chroot("/")` would introduce another setup operation and failure edge without repairing a demonstrated defect here. If a successor changes the mechanism to overmount a new root, this lemma must be reassessed; matching backing inode alone would not prove mount-reference equality.

The conclusion preserves the original root pathname and backing identity, original cwd pathname after its explicit reset, genuine proc visibility and PID namespace, and process/session/group relationships. It does not claim universal filesystem/LSM compatibility or equality of arbitrary runtime diagnostics. The independent filesystem and native-effect lemmas still supply the VFS consequences for each reached metadata operation, and the complete caller theorem still supplies the finite original-consumer projection. No runtime, kernel feature, resource-fit or execution admission is issued by this source lemma.
