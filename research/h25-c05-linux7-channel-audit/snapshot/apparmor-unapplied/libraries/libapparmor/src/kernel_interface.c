/*
 *   Copyright (c) 2014
 *   Canonical, Ltd. (All rights reserved)
 *
 *   This program is free software; you can redistribute it and/or
 *   modify it under the terms of version 2 of the GNU General Public
 *   License published by the Free Software Foundation.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program; if not, contact Novell, Inc. or Canonical
 *   Ltd.
 */

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/apparmor.h>

#include "private.h"

#define DEFAULT_APPARMORFS "/sys/kernel/security/apparmor"

struct aa_kernel_interface {
	unsigned int ref_count;
	bool supports_setload;
	int dirfd;
};

/**
 * find_iface_dir - find where the apparmor interface is located
 * @dir - RETURNs: stored location of interface director
 *
 * Returns: 0 on success, -1 with errno set if there is an error
 */
static int find_iface_dir(char **dir)
{
	if (aa_find_mountpoint(dir) == -1) {
		struct stat buf;
		if (stat(DEFAULT_APPARMORFS, &buf) == -1) {
			return -1;
		} else {
			*dir = strdup(DEFAULT_APPARMORFS);
			if (*dir == NULL)
				return -1;
		}
	}

	return 0;
}

/* bleah the kernel should just loop and do multiple load, but to support
 * older systems we need to do this
 */
#define PROFILE_HEADER_SIZE
static char header_version[] = "\x04\x08\x00version";

static const char *next_profile_buffer(const char *buffer, int size)
{
	const char *b = buffer;

	for (; size - sizeof(header_version); b++, size--) {
		if (memcmp(b, header_version, sizeof(header_version)) == 0) {
			return b;
		}
	}
	return NULL;
}

static int write_buffer(int fd, const char *buffer, int size)
{
	int wsize = write(fd, buffer, size);
	if (wsize < 0) {
		return -1;
	} else if (wsize < size) {
		errno = EPROTO;
		return -1;
	}
	return 0;
}

/**
 * write_policy_buffer - load compiled policy into the kernel
 * @fd: kernel interface to write to
 * @atomic: whether to load all policy in buffer atomically (true)
 * @buffer: buffer of policy to load
 * @size: the size of the data in the buffer
 *
 * Returns: 0 if the buffer loaded correctly
 *         -1 if the load failed with errno set to the error
 *
 * @atomic should only be set to true if the kernel supports atomic profile
 * set loads, otherwise only the 1st profile in the buffer will be loaded
 * (older kernels only support loading one profile at a time).
 */
static int write_policy_buffer(int fd, int atomic,
			       const char *buffer, size_t size)
{
	size_t bsize;
	int rc;

	if (atomic) {
		rc = write_buffer(fd, buffer, size);
	} else {
		const char *b, *next;

		rc = 0;	/* in case there are no profiles */
		for (b = buffer; b; b = next, size -= bsize) {
			next = next_profile_buffer(b + sizeof(header_version),
						   size);
			if (next)
				bsize = next - b;
			else
				bsize = size;
			if (write_buffer(fd, b, bsize) == -1)
				return -1;
		}
	}

	if (rc)
		return -1;

	return 0;
}

#define AA_IFACE_FILE_LOAD	".load"
#define AA_IFACE_FILE_REMOVE	".remove"
#define AA_IFACE_FILE_REPLACE	".replace"

static int write_policy_buffer_to_iface(aa_kernel_interface *kernel_interface,
					const char *iface_file,
					const char *buffer, size_t size)
{
	autoclose int fd = -1;

	fd = openat(kernel_interface->dirfd, iface_file, O_WRONLY | O_CLOEXEC);
	if (fd == -1)
		return -1;

	return write_policy_buffer(fd, kernel_interface->supports_setload,
				   buffer, size);
}

static int write_policy_fd_to_iface(aa_kernel_interface *kernel_interface,
				    const char *iface_file, int fd)
{
	autofree char *buffer = NULL;
	int size = 0, asize = 0, rsize;
	int chunksize = 1 << 14;

	do {
		if (asize - size == 0) {
			char *tmp = realloc(buffer, chunksize);

			asize = chunksize;
			chunksize <<= 1;
			if (!tmp) {
				errno = ENOMEM;
				return -1;
			}
			buffer = tmp;
		}

		rsize = read(fd, buffer + size, asize - size);
		if (rsize)
			size += rsize;
	} while (rsize > 0);

	if (rsize == -1)
		return -1;

	return write_policy_buffer_to_iface(kernel_interface, iface_file,
					    buffer, size);
}

static int write_policy_file_to_iface(aa_kernel_interface *kernel_interface,
				      const char *iface_file,
				      int dirfd, const char *path)
{
	autoclose int fd;

	fd = openat(dirfd, path, O_RDONLY);
	if (fd == -1)
		return -1;

	return write_policy_fd_to_iface(kernel_interface, iface_file, fd);
}

/**
 * aa_kernel_interface_new - create a new aa_kernel_interface object from an optional path
 * @kernel_interface: will point to the address of an allocated and initialized
 *                    aa_kernel_interface object upon success
 * @kernel_features: features representing the currently running kernel (can be
 *                   NULL and the features of the currently running kernel will
 *                   be used)
 * @apparmorfs: path to the apparmor directory of the mounted securityfs (can
 *              be NULL and the path will be auto discovered)
 *
 * Returns: 0 on success, -1 on error with errno set and *@kernel_interface
 *          pointing to NULL
 */
int aa_kernel_interface_new(aa_kernel_interface **kernel_interface,
			    aa_features *kernel_features,
			    const char *apparmorfs)
{
	aa_kernel_interface *ki;
	autofree char *alloced_apparmorfs = NULL;
	char set_load[] = "policy/set_load";

	*kernel_interface = NULL;

	ki = calloc(1, sizeof(*ki));
	if (!ki) {
		errno = ENOMEM;
		return -1;
	}
	aa_kernel_interface_ref(ki);
	ki->dirfd = -1;

	if (kernel_features) {
		aa_features_ref(kernel_features);
	} else if (aa_features_new_from_kernel(&kernel_features) == -1) {
		aa_kernel_interface_unref(ki);
		return -1;
	}
	ki->supports_setload = aa_features_supports(kernel_features, set_load);
	aa_features_unref(kernel_features);

	if (!apparmorfs) {
		if (find_iface_dir(&alloced_apparmorfs) == -1) {
			alloced_apparmorfs = NULL;
			aa_kernel_interface_unref(ki);
			return -1;
		}
		/* alloced_apparmorfs will be autofree'ed */
		apparmorfs = alloced_apparmorfs;
	}

	ki->dirfd = open(apparmorfs, O_RDONLY | O_CLOEXEC | O_DIRECTORY);
	if (ki->dirfd < 0) {
		aa_kernel_interface_unref(ki);
		return -1;
	}

	*kernel_interface = ki;

	return 0;
}

/**
 * aa_kernel_interface_ref - increments the ref count of an aa_kernel_interface object
 * @kernel_interface: the kernel_interface
 *
 * Returns: the kernel_interface
 */
aa_kernel_interface *aa_kernel_interface_ref(aa_kernel_interface *kernel_interface)
{
	atomic_inc(&kernel_interface->ref_count);
	return kernel_interface;
}

/**
 * aa_kernel_interface_unref - decrements the ref count and frees the aa_kernel_interface object when 0
 * @kernel_interface: the kernel_interface (can be NULL)
 */
void aa_kernel_interface_unref(aa_kernel_interface *kernel_interface)
{
	int save = errno;

	if (kernel_interface &&
	    atomic_dec_and_test(&kernel_interface->ref_count)) {
		if (kernel_interface->dirfd >= 0)
			close(kernel_interface->dirfd);
		free(kernel_interface);
	}

	errno = save;
}

/**
 * aa_kernel_interface_load_policy - load a policy from a buffer into the kernel
 * @kernel_interface: valid aa_kernel_interface
 * @buffer: a buffer containing a policy
 * @size: the size of the buffer
 *
 * Returns: 0 on success, -1 on error with errno set
 */
int aa_kernel_interface_load_policy(aa_kernel_interface *kernel_interface,
				    const char *buffer, size_t size)
{
	return write_policy_buffer_to_iface(kernel_interface,
					    AA_IFACE_FILE_LOAD, buffer, size);
}

/**
 * aa_kernel_interface_load_policy_from_file - load a policy from a file into the kernel
 * @kernel_interface: valid aa_kernel_interface
 * @path: path to a policy binary
 *
 * Returns: 0 on success, -1 on error with errno set
 */
int aa_kernel_interface_load_policy_from_file(aa_kernel_interface *kernel_interface,
					      int dirfd, const char *path)
{
	return write_policy_file_to_iface(kernel_interface, AA_IFACE_FILE_LOAD,
					  dirfd, path);
}

/**
 * aa_kernel_interface_load_policy_from_fd - load a policy from a file descriptor into the kernel
 * @kernel_interface: valid aa_kernel_interface
 * @fd: a pre-opened, readable file descriptor at the correct offset
 *
 * Returns: 0 on success, -1 on error with errno set
 */
int aa_kernel_interface_load_policy_from_fd(aa_kernel_interface *kernel_interface,
					    int fd)
{
	return write_policy_fd_to_iface(kernel_interface, AA_IFACE_FILE_LOAD,
					fd);
}

/**
 * aa_kernel_interface_replace_policy - replace a policy in the kernel with a policy from a buffer
 * @kernel_interface: valid aa_kernel_interface
 * @buffer: a buffer containing a policy
 * @size: the size of the buffer
 *
 * Returns: 0 on success, -1 on error with errno set
 */
int aa_kernel_interface_replace_policy(aa_kernel_interface *kernel_interface,
				       const char *buffer, size_t size)
{
	return write_policy_buffer_to_iface(kernel_interface,
					    AA_IFACE_FILE_REPLACE,
					    buffer, size);
}

/**
 * aa_kernel_interface_replace_policy_from_file - replace a policy in the kernel with a policy from a file
 * @kernel_interface: valid aa_kernel_interface
 * @path: path to a policy binary
 *
 * Returns: 0 on success, -1 on error with errno set
 */
int aa_kernel_interface_replace_policy_from_file(aa_kernel_interface *kernel_interface,
						 int dirfd, const char *path)
{
	return write_policy_file_to_iface(kernel_interface,
					  AA_IFACE_FILE_REPLACE, dirfd, path);
}

/**
 * aa_kernel_interface_replace_policy_from_fd - replace a policy in the kernel with a policy from a file descriptor
 * @kernel_interface: valid aa_kernel_interface
 * @fd: a pre-opened, readable file descriptor at the correct offset
 *
 * Returns: 0 on success, -1 on error with errno set
 */
int aa_kernel_interface_replace_policy_from_fd(aa_kernel_interface *kernel_interface,
					       int fd)
{
	return write_policy_fd_to_iface(kernel_interface, AA_IFACE_FILE_REPLACE,
					fd);
}

/**
 * aa_kernel_interface_remove_policy - remove a policy from the kernel
 * @kernel_interface: valid aa_kernel_interface
 * @fqname: nul-terminated fully qualified name of the policy to remove
 *
 * Returns: 0 on success, -1 on error with errno set
 */
int aa_kernel_interface_remove_policy(aa_kernel_interface *kernel_interface,
				      const char *fqname)
{
	return write_policy_buffer_to_iface(kernel_interface,
					    AA_IFACE_FILE_REMOVE,
					    fqname, strlen(fqname) + 1);
}

/**
 * aa_kernel_interface_write_policy - write a policy to a file descriptor
 * @fd: a pre-opened, writeable file descriptor at the correct offset
 * @buffer: a buffer containing a policy
 * @size: the size of the buffer
 *
 * Returns: 0 on success, -1 on error with errno set
 */
int aa_kernel_interface_write_policy(int fd, const char *buffer, size_t size)
{
	return write_policy_buffer(fd, 1, buffer, size);
}
