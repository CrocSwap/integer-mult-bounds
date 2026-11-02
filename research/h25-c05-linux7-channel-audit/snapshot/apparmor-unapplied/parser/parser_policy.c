/*
 *   Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007
 *   NOVELL (All rights reserved)
 *
 *   Copyright (c) 2010 - 2012
 *   Canonical Ltd. (All rights reserved)
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
 *   along with this program; if not, contact Novell, Inc. or Canonical,
 *   Ltd.
 */

#include <algorithm>

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <search.h>
#include <string.h>
#include <errno.h>
#include <sys/apparmor.h>

#include "lib.h"
#include "parser.h"
#include "profile.h"
#include "parser_yacc.h"
#include "network.h"

/* #define DEBUG */
#ifdef DEBUG
#undef PDEBUG
#define PDEBUG(fmt, args...) fprintf(stderr, "Lexer: " fmt, ## args)
#else
#undef PDEBUG
#define PDEBUG(fmt, args...)	/* Do nothing */
#endif
#define NPDEBUG(fmt, args...)	/* Do nothing */


ProfileList policy_list;


void add_to_list(Profile *prof)
{
	pair<ProfileList::iterator, bool> res = policy_list.insert(prof);
	if (!res.second) {
		PERROR("Multiple definitions for profile %s exist,"
		       "bailing out.\n", prof->name);
		exit(1);
	}
}

void add_hat_to_policy(Profile *prof, Profile *hat)
{
	hat->parent = prof;

	pair<ProfileList::iterator, bool> res = prof->hat_table.insert(hat);
	if (!res.second) {
		PERROR("Multiple definitions for hat %s in profile %s exist,"
		       "bailing out.\n", hat->name, prof->name);
		exit(1);
	}
}

int load_policy_list(ProfileList &list, int option,
		     aa_kernel_interface *kernel_interface, int cache_fd)
{
	int res = 0;

	for (ProfileList::iterator i = list.begin(); i != list.end(); i++) {
		res = load_profile(option, kernel_interface, *i, cache_fd);
		if (res != 0)
			break;
	}

	return res;
}

int load_flattened_hats(Profile *prof, int option,
			aa_kernel_interface *kernel_interface, int cache_fd)
{
	return load_policy_list(prof->hat_table, option, kernel_interface,
				cache_fd);
}

int load_policy(int option, aa_kernel_interface *kernel_interface, int cache_fd)
{
	return load_policy_list(policy_list, option, kernel_interface, cache_fd);
}

int load_hats(std::ostringstream &buf, Profile *prof)
{
	for (ProfileList::iterator i = prof->hat_table.begin(); i != prof->hat_table.end(); i++) {
		sd_serialize_profile(buf, *i, 0);
	}

	return 0;
}


void dump_policy(void)
{
	policy_list.dump();
}

void dump_policy_names(void)
{
	policy_list.dump_profile_names(true);
}

/* merge_hats: merges hat_table into hat_table owned by prof */
static void merge_hats(Profile *prof, ProfileList &hats)
{
	for (ProfileList::iterator i = hats.begin(); i != hats.end(); ) {
		ProfileList::iterator cur = i++;
		add_hat_to_policy(prof, *cur);
		hats.erase(cur);
	}

}

Profile *merge_policy(Profile *a, Profile *b)
{
	Profile *ret = a;
	struct cod_entry *last;

	if (!a) {
		ret = b;
		goto out;
	}
	if (!b)
		goto out;

	if (a->name || b->name) {
                PERROR("ASSERT: policy merges shouldn't have names %s %s\n",
		       a->name ? a->name : "",
		       b->name ? b->name : "");
		exit(1);
	}

	if (a->entries) {
		list_last_entry(a->entries, last);
		last->next = b->entries;
	} else {
		a->entries = b->entries;
	}
	b->entries = NULL;

	if (merge_profile_mode(a->flags.mode, b->flags.mode) == MODE_CONFLICT) {
		PERROR("ASSERT: policy merge with different modes 0x%x != 0x%x\n",
		       a->flags.mode, b->flags.mode);
		exit(1);
	}

	a->flags.audit = a->flags.audit || b->flags.audit;

	a->caps.allow |= b->caps.allow;
	a->caps.audit |= b->caps.audit;
	a->caps.deny |= b->caps.deny;
	a->caps.quiet |= b->caps.quiet;

	if (a->net.allow) {
		size_t i;
		for (i = 0; i < get_af_max(); i++) {
			a->net.allow[i] |= b->net.allow[i];
			a->net.audit[i] |= b->net.audit[i];
			a->net.deny[i] |= b->net.deny[i];
			a->net.quiet[i] |= b->net.quiet[i];
		}
	}

	merge_hats(a, b->hat_table);
	delete b;
out:
	return ret;
}

int process_profile_rules(Profile *profile)
{
	int error;

	error = process_profile_regex(profile);
	if (error) {
		PERROR(_("ERROR processing regexs for profile %s, failed to load\n"), profile->name);
		exit(1);
		return error;
	}

	error = process_profile_policydb(profile);
	if (error) {
		PERROR(_("ERROR processing policydb rules for profile %s, failed to load\n"),
		       (profile)->name);
		exit(1);
		return error;
	}

	return 0;
}

int post_process_policy_list(ProfileList &list, int debug_only);
int post_process_profile(Profile *profile, int debug_only)
{
	int error = 0;

	profile->add_implied_rules();

	error = process_profile_variables(profile);
	if (error) {
		PERROR(_("ERROR expanding variables for profile %s, failed to load\n"), profile->name);
		exit(1);
		return error;
	}

	error = replace_profile_aliases(profile);
	if (error) {
		PERROR(_("ERROR replacing aliases for profile %s, failed to load\n"), profile->name);
		return error;
	}

	error = profile_merge_rules(profile);
	if (error) {
		PERROR(_("ERROR merging rules for profile %s, failed to load\n"), profile->name);
		exit(1);
		return error;
	}

	if (!debug_only) {
		error = process_profile_rules(profile);
		if (error)
			return error;
	}

	error = post_process_policy_list(profile->hat_table, debug_only);
	return error;
}

int post_process_policy_list(ProfileList &list, int debug_only)
{
	int error = 0;
	for (ProfileList::iterator i = list.begin(); i != list.end(); i++) {
		error = post_process_profile(*i, debug_only);
		if (error)
			break;
	}

	return error;
}

int post_process_policy(int debug_only)
{
	return post_process_policy_list(policy_list, debug_only);
}

void free_policies(void)
{
	policy_list.clear();
}
