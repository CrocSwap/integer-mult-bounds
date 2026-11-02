/*
 *   Copyright (c) 2014-2017
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
#include <ctype.h>
#include <dirent.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include <stddef.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/apparmor.h>

#include "private.h"
#include "PMurHash.h"

#define FEATURES_FILE "/sys/kernel/security/apparmor/features"
#define CACHE_FEATURES_FILE ".features"

#define HASH_SIZE (8 + 1) /* 32 bits binary to hex + NUL terminator */
#define STRING_SIZE 8192

struct aa_features {
	unsigned int ref_count;
	char hash[HASH_SIZE];
	char string[STRING_SIZE];
};

struct features_struct {
	char *buffer;
	size_t size;
	char *pos;
};

struct component {
	const char *str;
	size_t len;
};

static int features_buffer_remaining(struct features_struct *fst,
				     size_t *remaining)
{
	ptrdiff_t offset = fst->pos - fst->buffer;

	if (offset < 0 || fst->size < (size_t)offset) {
		errno = EINVAL;
		PERROR("Invalid features buffer offset (%td)\n", offset);
		return -1;
	}

	*remaining = fst->size - offset;
	return 0;
}

static int features_snprintf(struct features_struct *fst, const char *fmt, ...)
{
	va_list args;
	int i;
	size_t remaining;

	if (features_buffer_remaining(fst, &remaining) == -1)
		return -1;

	va_start(args, fmt);
	i = vsnprintf(fst->pos, remaining, fmt, args);
	va_end(args);

	if (i < 0) {
		errno = EIO;
		PERROR("Failed to write to features buffer\n");
		return -1;
	} else if ((size_t)i >= remaining) {
		errno = ENOBUFS;
		PERROR("Feature buffer full.");
		return -1;
	}

	fst->pos += i;
	return 0;
}

/* load_features_file - reads a file into @buffer and then NUL-terminates @buffer
 * @file: file to read the features from
 * @buffer: the buffer to read the features file into (will be NUL-terminated on success)
 * @size: the size of @buffer
 *
 * Returns: The number of bytes copied into @buffer on success (not counting
 * the NUL-terminator), else -1 and errno is set. Note that @size must be
 * larger than the size of the file or -1 will be returned with errno set to
 * ENOBUFS indicating that @buffer was not large enough to contain all of the
 * file contents.
 */
static ssize_t load_features_file(int file, char *buffer, size_t size)
{
	char *pos = buffer;
	ssize_t len;

	/* Save room for a NUL-terminator at the end of @buffer */
	size--;

	do {
		len = read(file, pos, size);
		if (len > 0) {
			size -= len;
			pos += len;
		}
	} while (len > 0 && size);

	/**
	 * Possible error conditions:
	 *  - len == -1: read failed and errno is already set so return -1
	 *  - len  >  0: read() never returned 0 (EOF) meaning that @buffer was
	 *  		 too small to contain all of the file contents so set
	 *  		 errno to ENOBUFS and return -1
	 */
	if (len) {
		if (len > 0)
			errno = ENOBUFS;

		PDEBUG("Error reading features file: %m\n");
		return -1;
	}

	/* NUL-terminate @buffer */
	*pos = 0;

	return pos - buffer;
}

/* open_and_load_features_file - opens and reads a file into @buffer and then NUL-terminates @buffer
 * @dirfd: a directory file descriptory or AT_FDCWD (see openat(2))
 * @path: name of the file
 * @buffer: the buffer to read the features file into (will be NUL-terminated on success)
 * @size: the size of @buffer
 *
 * Returns: The number of bytes copied into @buffer on success (not counting
 * the NUL-terminator), else -1 and errno is set. Note that @size must be
 * larger than the size of the file or -1 will be returned with errno set to
 * ENOBUFS indicating that @buffer was not large enough to contain all of the
 * file contents.
 */
static ssize_t open_and_load_features_file(int dirfd, const char *path,
					   char *buffer, size_t size)
{
	autoclose int file = -1;
	ssize_t rc;

	file = openat(dirfd, path, O_RDONLY);
	if (file < 0) {
		PDEBUG("Could not open '%s': %m\n", path);
		return -1;
	}
	PDEBUG("Opened features '%s': %m\n", path);

	if (!size) {
		errno = ENOBUFS;
		return -1;
	}

	rc = load_features_file(file, buffer, size);
	if (rc == -1)
		PDEBUG("Error failed to load features file '%s': %m\n", path);
	return rc;
}

static int features_dir_cb(int dirfd, const char *name, struct stat *st,
			   void *data)
{
	struct features_struct *fst = (struct features_struct *) data;

	/* skip dot files and files with no name */
	if (*name == '.' || !strlen(name))
		return 0;

	if (features_snprintf(fst, "%s {", name) == -1)
		return -1;

	/* Handle symlink here. See _aa_dirat_for_each in private.c */

	if (S_ISREG(st->st_mode)) {
		ssize_t len;
		size_t remaining;

		if (features_buffer_remaining(fst, &remaining) == -1)
			return -1;

		len = open_and_load_features_file(dirfd, name, fst->pos, remaining);
		if (len < 0)
			return -1;

		fst->pos += len;
	} else if (S_ISDIR(st->st_mode)) {
		if (_aa_dirat_for_each(dirfd, name, fst, features_dir_cb))
			return -1;
	}

	if (features_snprintf(fst, "}\n") == -1)
		return -1;

	return 0;
}

static ssize_t load_features_dir(int dirfd, const char *path,
				 char *buffer, size_t size)
{
	struct features_struct fst = { buffer, size, buffer };

	if (_aa_dirat_for_each(dirfd, path, &fst, features_dir_cb)) {
		PDEBUG("Failed evaluating %s\n", path);
		return -1;
	}

	return 0;
}

static int init_features_hash(aa_features *features)
{
	const char *string = features->string;
	uint32_t seed = 5381;
	uint32_t hash = seed, carry = 0;
	size_t len = strlen(string);

	/* portable murmur3 hash
	 * https://github.com/aappleby/smhasher/wiki/MurmurHash3
	 */
	PMurHash32_Process(&hash, &carry, string, len);
	hash = PMurHash32_Result(hash, carry, len);

	if (snprintf(features->hash, HASH_SIZE,
		     "%08" PRIx32, hash) >= HASH_SIZE) {
		errno = ENOBUFS;
		PERROR("Hash buffer full.");
		return -1;
	}

	return 0;
}

static bool islbrace(int c)
{
	return c == '{';
}

static bool isrbrace(int c)
{
	return c == '}';
}

static bool isnul(int c)
{
	return c == '\0';
}

static bool isbrace(int c)
{
	return islbrace(c) || isrbrace(c);
}

static bool isbrace_or_nul(int c)
{
	return isbrace(c) || isnul(c);
}

static bool isbrace_space_or_nul(int c)
{
	return isbrace(c) || isspace(c) || isnul(c);
}

static size_t tokenize_path_components(const char *str,
				       struct component *components,
				       size_t max_components)
{
	size_t i = 0;

	memset(components, 0, sizeof(*components) * max_components);

	if (!str)
		return 0;

	while (*str && i < max_components) {
		const char *fwdslash = strchrnul(str, '/');

		/* Save the token if it is not "/" */
		if (fwdslash != str) {
			components[i].str = str;
			components[i].len = fwdslash - str;
			i++;
		}

		if (isnul(*fwdslash))
			break;

		str = fwdslash + 1;
	}

	return i;
}

/**
 * walk_one - walk one component of a features string
 * @str: a pointer to the current position in a features string
 * @component: the component to walk
 * @is_top_level: true if component is a top-level component
 *
 * Imagine a features string such as:
 *
 *  "feat1 { subfeat1.1 subfeat1.2 } feat2 { subfeat2.1 { subfeat2.1.1 } }"
 *
 * You want to know if "feat2/subfeat2.1/subfeat2.8" is valid. It will take 3
 * invocations of this function to determine if that string is valid. On the
 * first call, *@str will point to the beginning of the features string,
 * component->str will be "feat2", and is_top_level will be true since feat2 is
 * a top level feature. The function will return true and *@str will now point
 * at the the left brace after "feat2" in the features string. You can call
 * this function again with component->str being equal to "subfeat2.1" and it
 * will return true and *@str will now point at the left brace after
 * "subfeat2.1" in the features string. A third call to the function, with
 * component->str equal to "subfeat2.8", will return false and *@str will not
 * be changed.
 *
 * Returns true if the walk was successful and false otherwise. If the walk was
 * successful, *@str will point to the first encountered brace after the walk.
 * If the walk was unsuccessful, *@str is not updated.
 */
static bool walk_one(const char **str, const struct component *component,
		     bool is_top_level)
{
	const char *cur;
	uint32_t brace_count = 0;
	size_t i = 0;

	/* NULL pointers and empty strings are not accepted */
	if (!str || !*str || !component || !component->str || !component->len)
		return false;

	cur = *str;

	/**
	 * If @component is not top-level, the first character in the string to
	 * search MUST be '{'
	 */
	if (!is_top_level) {
		if (!islbrace(*cur))
			return false;

		cur++;
	}

	/**
	 * This loop tries to find the @component in *@str. When this loops
	 * completes, cur will either point one character past the end of the
	 * matched @component or to the NUL terminator of *@str.
	 */
	while(!isnul(*cur) && i < component->len) {
		if (!isascii(*cur)) {
			/* Only ASCII is expected */
			return false;
		} else if (islbrace(*cur)) {
			/* There's a limit to the number of left braces */
			if (brace_count == UINT32_MAX)
				return false;

			brace_count++;
		} else if (isrbrace(*cur)) {
			/* Check for unexpected right braces */
			if (brace_count == 0)
				return false;

			brace_count--;
		}

		/**
		 * Move to the next character in @component if we're not inside
		 * of braces and we have a character match
		 */
		if (brace_count == 0 && *cur == component->str[i])
			i++;
		else
			i = 0;

		cur++;
	}

	/* Return false if a full match was not found */
	if (i != component->len) {
		return false;
	} else if (!isbrace_space_or_nul(*cur))
		return false;

	/**
	 * This loop eats up valid (ASCII) characters until a brace or NUL
	 * character is found so that *@str is properly set to call back into
	 * this function
	 */
	while (!isbrace_or_nul(*cur)) {
		if (!isascii(*cur))
			return false;

		cur++;
	}

	*str = cur;
	return true;
}

/**
 * aa_features_new - create a new aa_features object based on a path
 * @features: will point to the address of an allocated and initialized
 *            aa_features object upon success
 * @dirfd: directory file descriptor or AT_FDCWD (see openat(2))
 * @path: path to a features file or directory
 *
 * Returns: 0 on success, -1 on error with errno set and *@features pointing to
 *          NULL
 */
int aa_features_new(aa_features **features, int dirfd, const char *path)
{
	struct stat stat_file;
	aa_features *f;
	ssize_t retval;

	*features = NULL;

	if (fstatat(dirfd, path, &stat_file, 0) == -1)
		return -1;

	f = calloc(1, sizeof(*f));
	if (!f) {
		errno = ENOMEM;
		return -1;
	}
	aa_features_ref(f);

	retval = S_ISDIR(stat_file.st_mode) ?
		 load_features_dir(dirfd, path, f->string, STRING_SIZE) :
		 open_and_load_features_file(dirfd, path, f->string, STRING_SIZE);
	if (retval == -1) {
		aa_features_unref(f);
		return -1;
	}

	if (init_features_hash(f) == -1) {
		int save = errno;

		aa_features_unref(f);
		errno = save;
		return -1;
	}

	*features = f;

	return 0;
}

/**
 * aa_features_new_from_string - create a new aa_features object based on a string
 * @features: will point to the address of an allocated and initialized
 *            aa_features object upon success
 * @string: a NUL-terminated string representation of features
 * @size: the size of @string, not counting the NUL-terminator
 *
 * Returns: 0 on success, -1 on error with errno set and *@features pointing to
 *          NULL
 */
int aa_features_new_from_string(aa_features **features,
				const char *string, size_t size)
{
	aa_features *f;

	*features = NULL;

	/* Require size to be less than STRING_SIZE so there's room for a NUL */
	if (size >= STRING_SIZE)
		return ENOBUFS;

	f = calloc(1, sizeof(*f));
	if (!f) {
		errno = ENOMEM;
		return -1;
	}
	aa_features_ref(f);

	memcpy(f->string, string, size);
	f->string[size] = '\0';

	if (init_features_hash(f) == -1) {
		int save = errno;

		aa_features_unref(f);
		errno = save;
		return -1;
	}

	*features = f;

	return 0;
}

/**
 * aa_features_new_from_file - create a new aa_features object based on an open file
 * @features: will point to the address of an allocated and initialized
 *            aa_features object upon success
 * @file: file to load features from
 *
 * Returns: 0 on success, -1 on error with errno set and *@features pointing to
 *          NULL
 */
int aa_features_new_from_file(aa_features **features, int file)
{
	aa_features *f;
	ssize_t retval;

	*features = NULL;

	f = calloc(1, sizeof(*f));
	if (!f) {
		errno = ENOMEM;
		return -1;
	}
	aa_features_ref(f);

	retval = load_features_file(file, f->string, STRING_SIZE);
	if (retval == -1) {
		aa_features_unref(f);
		return -1;
	}

	if (init_features_hash(f) == -1) {
		int save = errno;

		aa_features_unref(f);
		errno = save;
		return -1;
	}

	*features = f;

	return 0;
}

/**
 * aa_features_new_from_kernel - create a new aa_features object based on the current kernel
 * @features: will point to the address of an allocated and initialized
 *            aa_features object upon success
 *
 * Returns: 0 on success, -1 on error with errno set and *@features pointing to
 *          NULL
 */
int aa_features_new_from_kernel(aa_features **features)
{
	return aa_features_new(features, -1, FEATURES_FILE);
}

/**
 * aa_features_ref - increments the ref count of an aa_features object
 * @features: the features
 *
 * Returns: the features
 */
aa_features *aa_features_ref(aa_features *features)
{
	atomic_inc(&features->ref_count);
	return features;
}

/**
 * aa_features_unref - decrements the ref count and frees the aa_features object when 0
 * @features: the features (can be NULL)
 */
void aa_features_unref(aa_features *features)
{
	int save = errno;

	if (features && atomic_dec_and_test(&features->ref_count))
		free(features);

	errno = save;
}

/**
 * aa_features_write_to_fd - write a string representation of an aa_features object to an @fd
 * @features: the features
 * @fd: the file descriptor to write to
 *
 * Returns: 0 on success, -1 on error with errno set
 */
int aa_features_write_to_fd(aa_features *features, int fd)
{
	size_t size;
	ssize_t retval;
	char *string;

	string = features->string;
	size = strlen(string);
	do {
		retval = write(fd, string, size);
		if (retval == -1)
			return -1;

		size -= retval;
		string += retval;
	} while (size);

	return 0;
}

/**
 * aa_features_write_to_file - write a string representation of an aa_features object to a file
 * @features: the features
 * @dirfd: directory file descriptor or AT_FDCWD (see openat(2))
 * @path: the path to write to
 *
 * Returns: 0 on success, -1 on error with errno set
 */
int aa_features_write_to_file(aa_features *features,
			      int dirfd, const char *path)
{
	autoclose int fd = -1;

	fd = openat(dirfd, path,
		    O_WRONLY | O_CREAT | O_TRUNC | O_SYNC | O_CLOEXEC,
		    S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH);
	if (fd == -1)
		return -1;

	return aa_features_write_to_fd(features, fd);
}

/**
 * aa_features_is_equal - equality test for two aa_features objects
 * @features1: the first features (can be NULL)
 * @features2: the second features (can be NULL)
 *
 * Returns: true if they're equal, false if they're not or either are NULL
 */
bool aa_features_is_equal(aa_features *features1, aa_features *features2)
{
	return features1 && features2 &&
	       strcmp(features1->string, features2->string) == 0;
}

/**
 * aa_features_check - check if features from a directory matches an aa_features object
 * @dirfd: a directory file descriptory or AT_FDCWD (see openat(2))
 * @path: the path containing the features
 * @features: features to be matched against
 *
 * Returns: 0 on success, -1 on failure. errno is set to EEXIST when there's not a match
 */
int aa_features_check(int dirfd, const char *path,
		      aa_features *features)
{
	aa_features *local_features = NULL;
	autofree char *name = NULL;
	bool rc;
	int len;

	len = asprintf(&name, "%s/%s", path, CACHE_FEATURES_FILE);
	if (len == -1) {
		errno = ENOMEM;
		return -1;
	}

	/* verify that path dir .features matches */
	if (aa_features_new(&local_features, dirfd, name)) {
		PDEBUG("could not setup new features object for dirfd '%d' '%s'\n", dirfd, name);
		return -1;
	}

	rc = aa_features_is_equal(local_features, features);
	aa_features_unref(local_features);
	if (!rc) {
		errno = EEXIST;
		return -1;
	}

	return 0;
}

static const char *features_lookup(aa_features *features, const char *str)
{
	const char *features_string = features->string;
	struct component components[32];
	size_t i, num_components;

	/* Empty strings are not accepted. Neither are leading '/' chars. */
	if (!str || str[0] == '/')
		return NULL;

	/**
	 * Break @str into an array of components. For example,
	 * "mount/mask/mount" would turn into { "mount", 5 } as the first
	 * component, { "mask", 4 } as the second, and { "mount", 5 } as the
	 * third
	 */
	num_components = tokenize_path_components(str, components,
				sizeof(components) / sizeof(*components));

	/* At least one valid token is required */
	if (!num_components)
		return NULL;

	/* Ensure that all components are valid and found */
	for (i = 0; i < num_components; i++) {
		if (!walk_one(&features_string, &components[i], i == 0))
			return NULL;
	}

	return features_string;
}

/**
 * aa_features_supports - provides aa_features object support status
 * @features: the features
 * @str: the string representation of a feature to check
 *
 * Example @str values are "dbus/mask/send", "caps/mask/audit_read", and
 * "policy/versions/v7".
 *
 * Returns: a bool specifying the support status of @str feature
 */
bool aa_features_supports(aa_features *features, const char *str)
{
	const char *value = features_lookup(features, str);

	if (!value)
		return false;

	return true;
}

/**
 * aa_features_value - lookup the value for a give feature
 * @features: the features
 * @str: the feature to look up the value for
 * @len: return: if set length of returned str on success
 *
 * Returns: null terminated string or NULL on error with errno set to
 * ENOENT - @str not found
 * EISDIR - @str is not a leaf node in the feature tree
 */

char *aa_features_value(aa_features *features, const char *str, size_t *len)
{
	const char *start, *cur = features_lookup(features, str);

	errno = ENOENT;
	if (!cur)
		return NULL;

	if (!islbrace(*cur))
		return NULL;
	cur++;
	start = cur;

	while (!isbrace_or_nul(*cur)) {
		if (!isascii(*cur))
			return NULL;
		if (islbrace(*cur)) {
			/* component is not leaf */
			errno = EISDIR;
			return NULL;
		}
		cur++;
	}

	errno = 0;
	if (len)
		*len = cur - start;
	return strndup(start, cur - start);
}

/**
 * aa_features_id - provides unique identifier for an aa_features object
 * @features: the features
 *
 * Allocates and returns a string representation of an identifier that can
 * be used to uniquely identify an aa_features object. The mechanism for
 * generating the string representation is internal to libapparmor and
 * subject to change but an example implementation is applying a hash
 * function to the features string.
 *
 * Returns: a string identifying @features which must be freed by the
 * caller or NULL, with errno set, upon error
 */
char *aa_features_id(aa_features *features)
{
	return strdup(features->hash);
}
