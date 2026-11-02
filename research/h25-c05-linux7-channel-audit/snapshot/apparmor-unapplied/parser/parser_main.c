/*
 *   Copyright (c) 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007
 *   NOVELL (All rights reserved)
 *
 *   Copyright (c) 2010 - 2018
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

#include <assert.h>
#include <ctype.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdarg.h>
#include <stddef.h>
#include <getopt.h>
#include <errno.h>
#include <fcntl.h>

/* enable the following line to get voluminous debug info */
/* #define DEBUG */

#include <unistd.h>
#include <limits.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>

#include <sys/apparmor.h>

#include "capability.h"
#include "lib.h"
#include "features.h"
#include "parser.h"
#include "parser_version.h"
#include "parser_include.h"
#include "common_optarg.h"
#include "policy_cache.h"
#include "libapparmor_re/apparmor_re.h"
#include "file_cache.h"

#define OLD_MODULE_NAME "subdomain"
#define PROC_MODULES "/proc/modules"
#define MATCH_FILE "/sys/kernel/security/" MODULE_NAME "/matching"
#define MOUNTED_FS "/proc/mounts"
#define AADFA "pattern=aadfa"

#define PRIVILEGED_OPS (kernel_load)
#define UNPRIVILEGED_OPS (!(PRIVILEGED_OPS))


const char *parser_title	= "AppArmor parser";
const char *parser_copyright	= "Copyright (C) 1999-2008 Novell Inc.\nCopyright 2009-2018 Canonical Ltd.";

int opt_force_complain = 0;
int binary_input = 0;
int dump_vars = 0;
int dump_expanded_vars = 0;
int show_cache = 0;
int skip_cache = 0;
int skip_read_cache = 0;
int write_cache = 0;
int cond_clear_cache = 1;		/* only applies if write is set */
int force_clear_cache = 0;		/* force clearing regargless of state */
int create_cache_dir = 0;		/* DEPRECATED in favor of write_cache */
int preprocess_only = 0;
int skip_mode_force = 0;
int abort_on_error = 0;			/* stop processing profiles if error */
int skip_bad_cache_rebuild = 0;
int mru_skip_cache = 1;

bool O_rule_merge = true;
bool D_rule_merge = false;

/* for jobs_max and jobs
 * LONG_MAX : no limit
 * LONG_MIN  : auto  = detect system processing cores
 * -n  : multiply by the number of CPUs to compile policy
 */
#define JOBS_AUTO LONG_MIN
#define DEFAULT_JOBS_MAX -8
#define DEFAULT_ESTIMATED_JOB_SIZE (50 * 1024 * 1024)
long estimated_job_size = DEFAULT_ESTIMATED_JOB_SIZE;
long jobs_max = DEFAULT_JOBS_MAX;	/* 8 * cpus */
long jobs = JOBS_AUTO;			/* default: number of processor cores */
long njobs = 0;
long jobs_scale = 0;			/* number of chance to resample online
					 * cpus. This allows jobs spawning to
					 * scale when scheduling policy is
					 * taking cpus off line, and brings
					 * them back with load
					 */
bool debug_jobs = false;

#define MAX_CACHE_LOCS 4

struct timespec cache_tstamp, mru_policy_tstamp;

static char *apparmorfs = NULL;
static const char *cacheloc[MAX_CACHE_LOCS];
static int cacheloc_n = 0;
static bool print_cache_dir = false;

aa_features *pinned_features = NULL;
aa_features *policy_features = NULL;
aa_features *override_features = NULL;
aa_features *kernel_features = NULL;

static const char *config_file = "/etc/apparmor/parser.conf";

#define ARG_SKIP_BAD_CACHE		129
#define ARG_PURGE_CACHE			130
#define ARG_CREATE_CACHE_DIR		131
#define ARG_SKIP_BAD_CACHE_REBUILD	132
#define ARG_DEBUG_CACHE			133
#define ARG_PRINT_CACHE_DIR		134
#define ARG_ABORT_ON_ERROR		135
#define ARG_WARN			136
#define ARG_MAX_JOBS			137
#define ARG_KERNEL_FEATURES		138
#define ARG_POLICY_FEATURES		139
#define ARG_PRINT_CONFIG_FILE		140
#define ARG_OVERRIDE_POLICY_ABI		141
#define EARLY_ARG_CONFIG_FILE		142
#define ARG_WERROR			143
#define ARG_ESTIMATED_COMPILE_SIZE	144

/* Make sure to update BOTH the short and long_options */
static const char *short_options = "ad::f:h::rRVvI:b:BCD:NSm:M:qQn:XKTWkL:O:po:j:";
struct option long_options[] = {
	{"add", 		0, 0, 'a'},
	{"binary",		0, 0, 'B'},
	{"base",		1, 0, 'b'},
	{"subdomainfs",		1, 0, 'f'},
	{"help",		2, 0, 'h'},
	{"replace",		0, 0, 'r'},
	{"reload",		0, 0, 'r'},	/* undocumented reload option == replace */
	{"version",		0, 0, 'V'},
	{"complain",		0, 0, 'C'},
	{"Complain",		0, 0, 'C'},	/* Erk, apparently documented as --Complain */
	{"Include",		1, 0, 'I'},
	{"remove",		0, 0, 'R'},
	{"names",		0, 0, 'N'},
	{"stdout",		0, 0, 'S'},
	{"ofile",		1, 0, 'o'},
	{"match-string",	1, 0, 'm'},
	{"features-file",	1, 0, 'M'},
	{"quiet",		0, 0, 'q'},
	{"skip-kernel-load",	0, 0, 'Q'},
	{"verbose",		0, 0, 'v'},
	{"namespace",		1, 0, 'n'},
	{"readimpliesX",	0, 0, 'X'},
	{"skip-cache",		0, 0, 'K'},
	{"skip-read-cache",	0, 0, 'T'},
	{"write-cache",		0, 0, 'W'},
	{"show-cache",		0, 0, 'k'},
	{"cache-loc",		1, 0, 'L'},
	{"debug",		2, 0, 'd'},
	{"dump",		1, 0, 'D'},
	{"Dump",		1, 0, 'D'},
	{"optimize",		1, 0, 'O'},
	{"Optimize",		1, 0, 'O'},
	{"preprocess",		0, 0, 'p'},
	{"jobs",		1, 0, 'j'},
	{"skip-bad-cache",	0, 0, ARG_SKIP_BAD_CACHE},/* no short option */
	{"purge-cache",		0, 0, ARG_PURGE_CACHE},	/* no short option */
	{"create-cache-dir",	0, 0, ARG_CREATE_CACHE_DIR},/* no short option */
	{"abort-on-error",	0, 0, ARG_ABORT_ON_ERROR},	/* no short option */
	{"skip-bad-cache-rebuild",	0, 0, ARG_SKIP_BAD_CACHE_REBUILD},/* no short option */
	{"warn",		1, 0, ARG_WARN},	/* no short option */
	{"Werror",		2, 0, ARG_WERROR},
	{"debug-cache",		0, 0, ARG_DEBUG_CACHE},	/* no short option */
	{"max-jobs",		1, 0, ARG_MAX_JOBS},	/* no short option */
	{"print-cache-dir",	0, 0, ARG_PRINT_CACHE_DIR},	/* no short option */
	{"kernel-features",	1, 0, ARG_KERNEL_FEATURES},	/* no short option */
	{"policy-features",	1, 0, ARG_POLICY_FEATURES},	/* no short option */
	{"compile-features",	1, 0, ARG_POLICY_FEATURES},	/* original name of policy-features */
	{"print-config-file",	0, 0, ARG_PRINT_CONFIG_FILE},	/* no short option */
	{"override-policy-abi",	1, 0, ARG_OVERRIDE_POLICY_ABI},	/* no short option */
	{"config-file",		1, 0, EARLY_ARG_CONFIG_FILE},	/* early option, no short option */
	{"estimated-compile-size", 1, 0, ARG_ESTIMATED_COMPILE_SIZE}, /* no short option, not in help */

	{NULL, 0, 0, 0},
};

static int debug = 0;

void display_version(void)
{
	printf("%s version " PARSER_VERSION "\n%s\n", parser_title,
	       parser_copyright);
}

static void display_usage(const char *command)
{
	display_version();
	printf("\nUsage: %s [options] [profile]\n\n"
	       "Options:\n"
	       "--------\n"
	       "-a, --add		Add apparmor definitions [default]\n"
	       "-r, --replace		Replace apparmor definitions\n"
	       "-R, --remove		Remove apparmor definitions\n"
	       "-C, --Complain		Force the profile into complain mode\n"
	       "-B, --binary		Input is precompiled profile\n"
	       "-N, --names		Dump names of profiles in input.\n"
	       "-S, --stdout		Dump compiled profile to stdout\n"
	       "-o n, --ofile n		Write output to file n\n"
	       "-b n, --base n		Set base dir and cwd\n"
	       "-I n, --Include n	Add n to the search path\n"
	       "-f n, --subdomainfs n	Set location of apparmor filesystem\n"
	       "-m n, --match-string n  Use only features n\n"
	       "-M n, --features-file n Set compile & kernel features to file n\n"
	       "--policy-features n     Policy features set in file n\n"
	       "--override-policy-abi n     As policy-features but override ABI rules\n"
	       "--kernel-features n     Kernel features set in file n\n"
	       "-n n, --namespace n	Set Namespace for the profile\n"
	       "-X, --readimpliesX	Map profile read permissions to mr\n"
	       "-k, --show-cache	Report cache hit/miss details\n"
	       "-K, --skip-cache	Do not attempt to load or save cached profiles\n"
	       "-T, --skip-read-cache	Do not attempt to load cached profiles\n"
	       "-W, --write-cache	Save cached profile (force with -T)\n"
	       "    --skip-bad-cache	Don't clear cache if out of sync\n"
	       "    --purge-cache	Clear cache regardless of its state\n"
	       "    --debug-cache       Debug cache file checks\n"
	       "    --print-cache-dir	Print the cache directory path\n"
	       "-L, --cache-loc n	Set the location of the profile caches\n"
	       "-q, --quiet		Don't emit warnings\n"
	       "-v, --verbose		Show profile names as they load\n"
	       "-Q, --skip-kernel-load	Do everything except loading into kernel\n"
	       "-V, --version		Display version info and exit\n"
	       "-d [n], --debug 	Debug apparmor definitions OR [n]\n"
	       "-p, --preprocess	Dump preprocessed profile\n"
	       "-D [n], --dump		Dump internal info for debugging\n"
	       "-O [n], --Optimize	Control dfa optimizations\n"
	       "-h [cmd], --help[=cmd]  Display this text or info about cmd\n"
	       "-j n, --jobs n		Set the number of compile threads\n"
	       "--max-jobs n		Hard cap on --jobs. Default 8*cpus\n"
	       "--abort-on-error	Abort processing of profiles on first error\n"
	       "--skip-bad-cache-rebuild Do not try rebuilding the cache if it is rejected by the kernel\n"
	       "--config-file n		Specify the parser config file location, processed early before other options.\n"
	       "--print-config		Print config file location\n"
	       "--warn n		Enable warnings (see --help=warn)\n"
	       "--Werror [n]		Convert warnings to errors. If n is specified turn warn n into an error\n"
	       ,command);
}

optflag_table_t warnflag_table[] = {
	{ 1, "rule-not-enforced", "warn if a rule is not enforced", WARN_RULE_NOT_ENFORCED },
	{ 1, "rule-downgraded", "warn if a rule is downgraded to a lesser but still enforcing rule", WARN_RULE_DOWNGRADED },
	{ 1, "abi", "warn if there are abi issues in the profile", WARN_ABI },
	{ 1, "deprecated", "warn if something in the profile is deprecated", WARN_DEPRECATED },
	{ 1, "config", "enable configuration warnings", WARN_CONFIG },
	{ 1, "cache", "enable regular cache warnings", WARN_CACHE },
	{ 1, "debug-cache", "enable warnings for debug cache file checks", WARN_DEBUG_CACHE },
	{ 1, "jobs", "enable job control warnings", WARN_JOBS },
	{ 1, "dangerous", "warn on dangerous policy", WARN_DANGEROUS },
	{ 1, "unexpected", "warn when an unexpected condition is found", WARN_UNEXPECTED },
	{ 1, "format", "warn on unnecessary or confusing formatting", WARN_FORMAT },
	{ 1, "missing", "warn when missing qualifier and a default is used", WARN_MISSING },
	{ 1, "override", "warn when overriding", WARN_OVERRIDE },
	{ 1, "dev", "turn on warnings that are useful for profile development", WARN_DEV },
	{ 1, "pound-include", "warn when #include is used", WARN_INCLUDE },
	{ 1, "all", "turn on all warnings", WARN_ALL},
	{ 0, NULL, NULL, 0 },
};


/* Parse comma separated cachelocations. Commas can be escaped by \, */
static int parse_cacheloc(const char *arg, const char **cacheloc, int max_size)
{
	const char *s = arg;
	const char *p = arg;
	int n = 0;

	while(*p) {
		if (*p == '\\') {
			if (*(p + 1) != 0)
				p++;
		} else if (*p == ',') {
			if (p != s) {
				char *tmp;
				if (n == max_size) {
					errno = E2BIG;
					return -1;
				}
				tmp = (char *) malloc(p - s + 1);
				if (tmp == NULL)
					return -1;
				memcpy(tmp, s, p - s);
				tmp[p - s] = 0;
				cacheloc[n] = tmp;
				n++;
			}
			p++;
			s = p;
		} else
			p++;
	}
	if (p != s) {
		char *tmp;
		if (n == max_size) {
			errno = E2BIG;
			return -1;
		}
		tmp = (char *) malloc(p - s + 1);
		if (tmp == NULL)
			return -1;
		memcpy(tmp, s, p - s);
		tmp[p - s] = 0;
		cacheloc[n] = tmp;
		n++;
	}

	return n;
}

/* Treat conf file like options passed on command line
 */
static int getopt_long_file(FILE *f, const struct option *longopts,
			    char **optarg, int *longindex)
{
	static char line[256];
	char *pos, *opt, *save;
	int i;

	for (;;) {
		if (!fgets(line, 256, f))
			return -1;
		pos = line;
		while (isblank(*pos))
			pos++;
		if (*pos == '#')
			continue;
		opt = strtok_r(pos, " \t\r\n=", &save);
		/* blank line */
		if (!opt)
			continue;

		for (i = 0; longopts[i].name &&
			     strcmp(longopts[i].name, opt) != 0; i++) ;
		if (!longopts[i].name) {
			PERROR("%s: unknown option (%s) in config file.\n",
			       progname, opt);
			/* skip it */
			continue;
		}
		break;
	}

	if (longindex)
		*longindex = i;

	if (*save) {
		int len;
		while(isblank(*save))
			save++;
		len = strlen(save) - 1;
		if (save[len] == '\n')
			save[len] = 0;
	}

	switch (longopts[i].has_arg) {
	case 0:
		*optarg = NULL;
		break;
	case 1:
		if (!strlen(save)) {
			*optarg = NULL;
			return '?';
		}
		*optarg = save;
		break;
	case 2:
		*optarg = save;
		break;
	default:
		PERROR("%s: internal error bad longopt value\n", progname);
		exit(1);
	}

	if (longopts[i].flag == NULL)
		return longopts[i].val;
	else
		*longopts[i].flag = longopts[i].val;
	return 0;
}

static long process_jobs_arg(const char *arg, const char *val) {
	char *end;
	long n;

	if (!val || strcmp(val, "auto") == 0)
		n = JOBS_AUTO;
	else if (strcmp(val, "max") == 0)
		n = LONG_MAX;
	else {
		bool multiple = false;
		if (*val == 'x') {
			multiple = true;
			val++;
		}
		n = strtol(val, &end, 0);
		if (!(*val && val != end && *end == '\0')) {
			PERROR("%s: Invalid option %s=%s%s\n", progname, arg, multiple ? "x" : "", val);
			exit(1);
		}
		if (multiple)
			n = -n;
	}

	return n;
}

static long str_to_size(const char *s)
{
	if (*s == '\0')
		return 1;
	else if (strcmp(s, "KB") == 0)
		return 1024;
	else if (strcmp(s, "MB") == 0)
		return 1024*1024;
	else if (strcmp(s, "GB") == 0)
		return 1024*1024*1024;
	return -1;
}

#define	EARLY_ARG   1
#define	LATE_ARG    2
#define	TWOPASS_ARG (EARLY_ARG | LATE_ARG)

int arg_pass(int c) {
	switch(c) {
	case EARLY_ARG_CONFIG_FILE:
		return EARLY_ARG;
		break;
	case ARG_WARN:
		return TWOPASS_ARG;
		break;
	case ARG_WERROR:
		return TWOPASS_ARG;
		break;
	}

	return LATE_ARG;
}

/* process a single argument from getopt_long
 * Returns: 1 if an action arg, else 0
 */
#define DUMP_HEADER "     variables      \tDump variables\n" \
	            "     expanded-variables\t Dump variables after expansion\n"

static int process_arg(int c, char *optarg)
{
	struct aa_features *tmp_features = NULL;
	int count = 0;

	switch (c) {
	case 0:
		PERROR("Assert, in getopt_long handling\n");
		exit(1);
		break;
	case 'a':
		count++;
		option = OPTION_ADD;
		break;
	case 'd':
		if (!optarg) {
			debug++;
			skip_read_cache = 1;
		} else if (strcmp(optarg, "jobs") == 0 ||
			   strcmp(optarg, "j") == 0) {
			debug_jobs = true;
		} else {
			PERROR("%s: Invalid --debug option '%s'\n",
			       progname, optarg);
			exit(1);
		}
		break;
	case 'h':
		if (!optarg) {
			display_usage(progname);
		} else if (strcmp(optarg, "Dump") == 0 ||
			   strcmp(optarg, "dump") == 0 ||
			   strcmp(optarg, "D") == 0) {
			flagtable_help("--dump=", DUMP_HEADER, progname,
				       dumpflag_table);
		} else if (strcmp(optarg, "Optimize") == 0 ||
			   strcmp(optarg, "optimize") == 0 ||
			   strcmp(optarg, "O") == 0) {
			flagtable_help("-O ", "", progname, dfaoptflag_table);
		} else if (strcmp(optarg, "warn") == 0) {
			flagtable_help("--warn=", "", progname, warnflag_table);
		} else if (strcmp(optarg, "Werror") == 0) {
			flagtable_help("--Werror=", "", progname, warnflag_table);
		} else {
			PERROR("%s: Invalid --help option %s\n",
			       progname, optarg);
			exit(1);
		}
		exit(0);
		break;
	case 'r':
		count++;
		option = OPTION_REPLACE;
		break;
	case 'R':
		count++;
		option = OPTION_REMOVE;
		skip_cache = 1;
		break;
	case 'V':
		display_version();
		exit(0);
		break;
	case 'I':
		add_search_dir(optarg);
		break;
	case 'b':
		set_base_dir(optarg);
		break;
	case 'B':
		binary_input = 1;
		skip_cache = 1;
		break;
	case 'C':
		opt_force_complain = 1;
		skip_cache = 1;
		break;
	case 'N':
		count++;
		names_only = 1;
		skip_cache = 1;
		kernel_load = 0;
		break;
	case 'S':
		count++;
		option = OPTION_STDOUT;
		skip_read_cache = 1;
		kernel_load = 0;
		break;
	case 'o':
		count++;
		option = OPTION_OFILE;
		skip_read_cache = 1;
		kernel_load = 0;
		ofile = fopen(optarg, "w");
		if (!ofile) {
			PERROR("%s: Could not open file %s\n",
			       progname, optarg);
			exit(1);
		}
		break;
	case 'f':
		apparmorfs = strndup(optarg, PATH_MAX);
		break;
	case 'D':
		skip_read_cache = 1;
		if (!optarg) {
			dump_vars = 1;
		} else if (strcmp(optarg, "show") == 0) {
			print_flags("dump", dumpflag_table, parseopts.dump);
		} else if (strcmp(optarg, "variables") == 0) {
			dump_vars = 1;
		} else if (strcmp(optarg, "expanded-variables") == 0) {
			dump_expanded_vars = 1;
		} else if (!handle_flag_table(dumpflag_table, optarg,
					      &parseopts.dump)) {
			PERROR("%s: Invalid --Dump option %s\n",
			       progname, optarg);
			exit(1);
		}
		break;
	case 'O':
		if (strcmp(optarg, "show") == 0) {
			print_flags("Optimize", dfaoptflag_table, parseopts.control);
		} else if (!handle_flag_table(dfaoptflag_table, optarg,
					      &parseopts.control)) {
			PERROR("%s: Invalid --Optimize option %s\n",
			       progname, optarg);
			exit(1);
		}
		break;
	case 'm':
		if (pinned_features)
			aa_features_unref(pinned_features);
		if (kernel_features)
			aa_features_unref(kernel_features);
		if (aa_features_new_from_string(&tmp_features,
						optarg, strlen(optarg))) {
			fprintf(stderr,
				"Failed to parse features string: %m\n");
			exit(1);
		}
		kernel_features = aa_features_ref(tmp_features);
		pinned_features = tmp_features;
		break;
	case 'M':
		if (pinned_features)
			aa_features_unref(pinned_features);
		if (kernel_features)
			aa_features_unref(kernel_features);
		if (aa_features_new(&tmp_features, AT_FDCWD, optarg)) {
			fprintf(stderr,
				"Failed to load features from '%s': %m\n",
				optarg);
			exit(1);
		}
		kernel_features = aa_features_ref(tmp_features);
		pinned_features = tmp_features;
		break;
	case ARG_KERNEL_FEATURES:
		if (kernel_features)
			aa_features_unref(kernel_features);
		if (aa_features_new(&kernel_features, AT_FDCWD, optarg)) {
			fprintf(stderr,
				"Failed to load kernel features from '%s': %m\n",
				optarg);
			exit(1);
		}
		break;
	case ARG_POLICY_FEATURES:
		if (pinned_features)
			aa_features_unref(pinned_features);
		if (strcmp(optarg, "<kernel>") == 0) {
			if (aa_features_new_from_kernel(&tmp_features)) {
				fprintf(stderr,
					"Failed to load kernel features into the policy-features abi: %m\n");
				exit(1);
			}
		} else if (aa_features_new(&tmp_features, AT_FDCWD, optarg)) {
			fprintf(stderr,
				"Failed to load policy-features from '%s': %m\n",
				optarg);
			exit(1);
		}
		pinned_features = tmp_features;
		break;
	case ARG_OVERRIDE_POLICY_ABI:
		if (override_features)
			aa_features_unref(override_features);
		if (strcmp(optarg, "<kernel>") == 0) {
			if (aa_features_new_from_kernel(&tmp_features)) {
				fprintf(stderr,
					"Failed to load kernel features into the policy-features abi: %m\n");
				exit(1);
			}
		} else if (aa_features_new(&tmp_features, AT_FDCWD, optarg)) {
			fprintf(stderr,
				"Failed to load policy-features from '%s': %m\n",
				optarg);
			exit(1);
		}
		override_features = tmp_features;
		break;
	case 'q':
		conf_verbose = 0;
		conf_quiet = 1;
		parseopts.warn = 0;
		break;
	case 'v':
		conf_verbose = 1;
		conf_quiet = 0;
		break;
	case 'n':
		profile_ns = strdup(optarg);
		break;
	case 'X':
		read_implies_exec = 1;
		break;
	case 'K':
		skip_cache = 1;
		break;
	case 'k':
		show_cache = 1;
		break;
	case 'W':
		write_cache = 1;
		break;
	case 'T':
		skip_read_cache = 1;
		break;
	case ARG_SKIP_BAD_CACHE:
		cond_clear_cache = 0;
		break;
	case ARG_PURGE_CACHE:
		force_clear_cache = 1;
		break;
	case ARG_CREATE_CACHE_DIR:
		create_cache_dir = 1;
		break;
	case ARG_ABORT_ON_ERROR:
		abort_on_error = 1;
		break;
	case ARG_SKIP_BAD_CACHE_REBUILD:
		skip_bad_cache_rebuild = 1;
		break;
	case 'L':
		cacheloc_n = parse_cacheloc(optarg, cacheloc, MAX_CACHE_LOCS);
		if (cacheloc_n == -1) {
			PERROR("%s: Invalid --cacheloc option '%s' %m\n", progname, optarg);
			exit(1);
		}
		break;
	case 'Q':
		kernel_load = 0;
		break;
	case 'p':
		count++;
		kernel_load = 0;
		skip_cache = 1;
		preprocess_only = 1;
		skip_mode_force = 1;
		break;
	case ARG_WARN:
		if (strcmp(optarg, "show") == 0) {
			print_flags("warn", warnflag_table, parseopts.warn);
		} else if (!handle_flag_table(warnflag_table, optarg,
				       &parseopts.warn)) {
			PERROR("%s: Invalid --warn option %s\n",
			       progname, optarg);
			exit(1);
		}
		break;
	case ARG_WERROR:
		if (!optarg) {
			parseopts.Werror = -1;
		} else if (strcmp(optarg, "show") == 0) {
			print_flags("Werror", warnflag_table, parseopts.Werror);
		} else if (optarg && !handle_flag_table(warnflag_table, optarg,
					      &parseopts.Werror)) {
			PERROR("%s: Invalid --Werror option %s\n",
			       progname, optarg);
			exit(1);
		}
		break;
	case ARG_DEBUG_CACHE:
		parseopts.warn |= WARN_DEBUG_CACHE;
		break;
	case 'j':
		jobs = process_jobs_arg("-j", optarg);
		if (jobs == 0)
			jobs_max = 0;
		else if (jobs != JOBS_AUTO && jobs < LONG_MAX)
			jobs_max = jobs;
		break;
	case ARG_MAX_JOBS:
		jobs_max = process_jobs_arg("max-jobs", optarg);
		break;
	case ARG_PRINT_CACHE_DIR:
		kernel_load = 0;
		print_cache_dir = true;
		break;
	case EARLY_ARG_CONFIG_FILE:
		config_file = strdup(optarg);
		if (!config_file) {
			PERROR("%s: %m", progname);
			exit(1);
		}
		break;
	case ARG_PRINT_CONFIG_FILE:
		printf("%s\n", config_file);
		break;
	case ARG_ESTIMATED_COMPILE_SIZE:
		/* used to auto tune parser on low resource systems */
		{
			char *end;
			long mult;
			long long tmp = strtoll(optarg, &end, 0);
			if (end == optarg ||
			    (errno == ERANGE && (tmp == LLONG_MIN || tmp == LLONG_MAX)) ||
			    (mult = str_to_size(end)) == -1) {
				PERROR("%s: --estimated-compile-size invalid size '%s'", progname, optarg);
				exit(1);
			}
			estimated_job_size = tmp * mult;
		}
		break;
	default:
		/* 'unrecognized option' error message gets printed by getopt_long() */
		exit(1);
		break;
	}

	return count;
}

static void process_early_args(int argc, char *argv[])
{
	int c, o;

	while ((c = getopt_long(argc, argv, short_options, long_options, &o)) != -1)
	{
		if (arg_pass(c) & EARLY_ARG)
			process_arg(c, optarg);
	}

	/* reset args, so we are ready for a second pass */
	optind = 1;
}

static int process_args(int argc, char *argv[])
{
	int c, o;
	int count = 0;
	option = OPTION_ADD;

	opterr = 1;
	while ((c = getopt_long(argc, argv, short_options, long_options, &o)) != -1)
	{
		if (arg_pass(c) & LATE_ARG)
			count += process_arg(c, optarg);
	}

	if (count > 1) {
		PERROR("%s: Too many actions given on the command line.\n",
		       progname);
		exit(1);
	}

	PDEBUG("optind = %d argc = %d\n", optind, argc);
	return optind;
}

static int process_config_file(const char *name)
{
	char *optarg;
	autofclose FILE *f = NULL;
	int c, o;

	f = fopen(name, "r");
	if (!f) {
		pwarn(WARN_CONFIG, "config file '%s' not found\n", name);
		return 0;
	}

	while ((c = getopt_long_file(f, long_options, &optarg, &o)) != -1)
		process_arg(c, optarg);
	return 1;
}

int have_enough_privilege(void)
{
	uid_t uid, euid;

	uid = getuid();
	euid = geteuid();

	if (uid != 0 && euid == 0) {
		PERROR(_("%s: Warning! You've set this program setuid root.\n"
			 "Anybody who can run this program can update "
			 "your AppArmor profiles.\n\n"), progname);
	}

	return 0;
}

int features_intersect(aa_features *a, aa_features *b, const char *str)
{
	return aa_features_supports(a, str) && aa_features_supports(b, str);
}

static bool set_features_by_match_file(struct aa_features **features)
{
	autofclose FILE *ms = fopen(MATCH_FILE, "r");
	if (ms) {
		autofree char *match_string = (char *) malloc(1000);
		if (!match_string)
			goto no_match;
		if (!fgets(match_string, 1000, ms))
			goto no_match;
		if (strstr(match_string, " perms=c"))
			return aa_features_new_from_string(features,
							   match_cn_abi,
							   strlen(match_cn_abi)) == 0;

		return aa_features_new_from_string(features, match_n_abi,
						   strlen(match_n_abi)) == 0;
	}
no_match:
	/* either extremely old kernel or a container without the interfaces
	 * mounted
	 */
	return aa_features_new_from_string(features, match_c_abi,
					  strlen(match_c_abi)) == 0;
}

void set_supported_features()
{
	assert(kernel_features != NULL);

	/* has process_args() already assigned a match string? */
	if (!policy_features) {
		policy_features = aa_features_ref(kernel_features);

	}

	/*
	 * TODO: intersect with actual kernel features to get proper
	 * rule down grades for a give kernel
	 */
	perms_create = 1;
	features_supports_network = features_intersect(kernel_features,
						       policy_features,
						       "network");
	features_supports_networkv8 = features_intersect(kernel_features,
							 policy_features,
							 "network_v8");
	features_supports_inet = features_intersect(kernel_features,
						    policy_features,
						    "network_v8/af_inet");
	features_supports_unix = features_intersect(kernel_features,
						    policy_features,
						    "network/af_unix");
	features_supports_mount = features_intersect(kernel_features,
						     policy_features,
						     "mount");
	features_supports_dbus = features_intersect(kernel_features,
						    policy_features, "dbus");
	features_supports_signal = features_intersect(kernel_features,
						      policy_features,
						      "signal");
	features_supports_ptrace = features_intersect(kernel_features,
						      policy_features,
						      "ptrace");
	features_supports_stacking = features_intersect(kernel_features,
							policy_features,
							"domain/stack");
	features_supports_domain_xattr = features_intersect(kernel_features,
							    policy_features,
							    "domain/attach_conditions/xattr");
	features_supports_userns = features_intersect(kernel_features,
						      policy_features,
						      "namespaces/mask/userns_create");
	features_supports_posix_mqueue = features_intersect(kernel_features,
						      policy_features,
						      "ipc/posix_mqueue");
	features_supports_sysv_mqueue = features_intersect(kernel_features,
						      policy_features,
						      "ipc/sysv_mqueue");
	features_supports_io_uring = features_intersect(kernel_features,
							policy_features,
							"io_uring");
	features_supports_flag_interruptible = features_intersect(kernel_features,
						policy_features,
						"policy/profile/interruptible");
	features_supports_flag_signal = features_intersect(kernel_features,
							   policy_features,
				      "policy/profile/kill.signal");
}

static bool do_print_cache_dir(aa_features *features, int dirfd, const char *path)
{
	autofree char *cache_dir = NULL;

	cache_dir = aa_policy_cache_dir_path_preview(features, dirfd, path);
	if (!cache_dir) {
		PERROR(_("Unable to print the cache directory: %m\n"));
		return false;
	}

	printf("%s\n", cache_dir);
	return true;
}

static bool do_print_cache_dirs(aa_features *features, const char **cacheloc,
				int cacheloc_n)
{
	int i;

	for (i = 0; i < cacheloc_n; i++) {
		if (!do_print_cache_dir(features, AT_FDCWD, cacheloc[i]))
			return false;
	}

	return true;
}

int process_binary(int option, aa_kernel_interface *kernel_interface,
		   const char *profilename)
{
	const char *printed_name;
	int retval;

	printed_name = profilename ? profilename : "stdin";

	if (kernel_load) {
		if (option == OPTION_ADD) {
			retval = profilename ?
				 aa_kernel_interface_load_policy_from_file(kernel_interface, AT_FDCWD, profilename) :
				 aa_kernel_interface_load_policy_from_fd(kernel_interface, 0);
			if (retval == -1) {
				retval = errno;
				PERROR(_("Error: Could not load profile %s: %s\n"),
				       printed_name, strerror(retval));
				return retval;
			}
		} else if (option == OPTION_REPLACE) {
			retval = profilename ?
				 aa_kernel_interface_replace_policy_from_file(kernel_interface, AT_FDCWD, profilename) :
				 aa_kernel_interface_replace_policy_from_fd(kernel_interface, 0);
			if (retval == -1) {
				retval = errno;
				PERROR(_("Error: Could not replace profile %s: %s\n"),
				       printed_name, strerror(retval));
				return retval;
			}
		} else {
			PERROR(_("Error: Invalid load option specified: %d\n"),
			       option);
			return EINVAL;
		}
	}

	if (conf_verbose) {
		switch (option) {
		case OPTION_ADD:
			printf(_("Cached load succeeded for \"%s\".\n"),
			       printed_name);
			break;
		case OPTION_REPLACE:
			printf(_("Cached reload succeeded for \"%s\".\n"),
			       printed_name);
			break;
		default:
			break;
		}
	}

	return 0;
}

void reset_parser(const char *filename)
{
	PDEBUG("Resetting parser for profile %s\n", filename);
	memset(&mru_policy_tstamp, 0, sizeof(mru_policy_tstamp));
	memset(&cache_tstamp, 0, sizeof(cache_tstamp));
	mru_skip_cache = 1;
	free_aliases();
	free_symtabs();
	free_policies();
	reset_include_stack(filename);
	aa_features_unref(policy_features);
	policy_features = NULL;
	clear_cap_flag(CAPFLAG_POLICY_FEATURE);
	delete g_includecache;
	g_includecache = new IncludeCache_t();
}

int test_for_dir_mode(const char *basename, const char *linkdir)
{
	int rc = 0;

	if (!skip_mode_force) {
		autofree char *target = NULL;
		if (asprintf(&target, "%s/%s/%s", basedir, linkdir, basename) < 0) {
			perror("asprintf");
			exit(1);
		}

		if (access(target, R_OK) == 0)
			rc = 1;
	}

	return rc;
}

int process_profile(int option, aa_kernel_interface *kernel_interface,
		    const char *profilename, aa_policy_cache *pc)
{
	int retval = 0;
	autofree const char *cachename = NULL;
	autofree const char *writecachename = NULL;
	autofree const char *cachetmpname = NULL;
	autoclose int cachetmp = -1;
	const char *basename = NULL;

	/* per-profile states */
	force_complain = opt_force_complain;

	if (profilename) {
		if ( !(yyin = fopen(profilename, "r")) ) {
			PERROR(_("Error: Could not read profile %s: %s.\n"),
			       profilename, strerror(errno));
			return errno;
		}
	} else {
		if (write_cache)
			pwarn(WARN_CACHE, "%s: cannot use or update cache, disable, or force-complain via stdin\n", progname);
		skip_cache = write_cache = 0;
	}

	reset_parser(profilename);

	if (profilename && option != OPTION_REMOVE) {
		/* make decisions about disabled or complain-mode profiles */
		basename = strrchr(profilename, '/');
		if (basename)
			basename++;
		else
			basename = profilename;

		if (test_for_dir_mode(basename, "disable")) {
 			if (!conf_quiet)
 				PERROR("Skipping profile in %s/disable: %s\n", basedir, basename);
			goto out;
		}

		if (test_for_dir_mode(basename, "force-complain")) {
			PERROR("Warning: found %s in %s/force-complain, forcing complain mode\n", basename, basedir);
 			force_complain = 1;
 		}

		/* setup cachename and tstamp */
		if (!force_complain && pc) {
			cachename = aa_policy_cache_filename(pc, basename);
			if (!cachename) {
				autoclose int fd = aa_policy_cache_open(pc,
								basename,
								O_RDONLY);
				if (fd != -1)
					pwarn(WARN_CACHE, _("Could not get cachename for '%s'\n"), basename);
			} else {
				valid_read_cache(cachename);
			}
		}

	}

	if (yyin) {
		yyrestart(yyin);
		update_mru_tstamp(yyin, profilename ? profilename : "stdin");
	}

	retval = yyparse();
	if (retval != 0)
		goto out;

	/* Test to see if profile is for another namespace, if so disable
	 * caching for now
	 * TODO: Add support for caching profiles in an alternate namespace
	 * TODO: Add support for embedded namespace defines if they aren't
	 *       removed from the language.
	 * TODO: test profile->ns NOT profile_ns (must be after parse)
	 */
	if (profile_ns)
		skip_cache = 1;

	if (cachename) {
		/* Load a binary cache if it exists and is newest */
		if (cache_hit(cachename)) {
			retval = process_binary(option, kernel_interface,
						cachename);
			if (!retval || skip_bad_cache_rebuild)
				goto out;
		}
	}

	if (show_cache)
		PERROR("Cache miss: %s\n", profilename ? profilename : "stdin");

	if (preprocess_only)
		goto out;

	if (names_only) {
		dump_policy_names();
		goto out;
	}

	if (dump_vars) {
		dump_symtab();
		goto out;
	}

	retval = post_process_policy(debug);
  	if (retval != 0) {
  		PERROR(_("%s: Errors found in file. Aborting.\n"), progname);
		goto out;
  	}

	if (dump_expanded_vars) {
		dump_expanded_symtab();
		goto out;
	}

	if (debug > 0) {
		printf("----- Debugging built structures -----\n");
		dump_policy();
		goto out;
	}

	if (pc && write_cache && !force_complain) {
		writecachename = cache_filename(pc, 0, basename);
		if (!writecachename) {
			pwarn(WARN_CACHE, "Cache write disabled: Cannot create cache file name '%s': %m\n", basename);
			write_cache = 0;
		}
		cachetmp = setup_cache_tmp(&cachetmpname, writecachename);
		if (cachetmp == -1) {
			pwarn(WARN_CACHE, "Cache write disabled: Cannot create setup tmp cache file '%s': %m\n", writecachename);
			write_cache = 0;
		}
	}
	/* cache file generated by load_policy */
	retval = load_policy(option, kernel_interface, cachetmp);
	if (retval == 0 && write_cache) {
		if (force_complain) {
			pwarn(WARN_CACHE, "Caching disabled for: '%s' due to force complain\n", basename);
		} else if (cachetmp == -1) {
			unlink(cachetmpname);
			pwarn(WARN_CACHE, "Failed to create cache: %s\n",
			       basename);
		} else {
			install_cache(cachetmpname, writecachename);
		}
	}
out:
	/* cleanup */
	reset_parser(profilename);
	return retval;
}

/* Do not call directly, this is a helper for work_sync, which can handle
 * single worker cases and cases were the work queue is optimized away
 *
 * call only if there are work children to wait on
 */
#define work_sync_one(RESULT)						\
do {									\
	int status;							\
	wait(&status);							\
	if (WIFEXITED(status))						\
		RESULT(WEXITSTATUS(status));				\
	else								\
		RESULT(ECHILD);						\
	/* TODO: do we need to handle traced */				\
	njobs--;							\
	if (debug_jobs)							\
		fprintf(stderr, "    JOBS SYNC ONE: result %d, jobs left %ld\n", status, njobs);							\
} while (0)

#define work_sync(RESULT)						\
do {									\
	if (debug_jobs)							\
		fprintf(stderr, "JOBS SYNC: jobs left %ld\n", njobs);	\
	while (njobs)							\
		work_sync_one(RESULT);					\
} while (0)

/* returns -1 if work_spawn fails, not a return value of any unit of work */
#define work_spawn(WORK, RESULT)					\
({									\
	int localrc = 0;						\
	do {								\
		if (jobs == 0) {					\
			/* no parallel work so avoid fork() overhead */	\
			RESULT(WORK);					\
			break;						\
		}							\
		if (jobs_scale) {					\
			long n = sysconf(_SC_NPROCESSORS_ONLN);		\
			if (n > jobs_max)				\
				n = jobs_max;				\
			if (n > jobs) {					\
				/* reset sample chances - potentially reduce to 0 */ \
				jobs_scale = jobs_max - n;		\
				jobs = n;				\
			} else						\
				/* reduce scaling chance by 1 */	\
				jobs_scale--;				\
		}							\
		if (njobs == jobs) {					\
			/* wait for a child */				\
			if (debug_jobs)					\
				fprintf(stderr, "    JOBS SPAWN: waiting (jobs %ld == max %ld) ...\n", njobs, jobs);					\
			work_sync_one(RESULT);				\
		}							\
									\
		pid_t child = fork();					\
		if (child == 0) {					\
			/* child - exit work unit with returned value */\
			exit(WORK);					\
		} else if (child > 0) {					\
			/* parent */					\
			njobs++;					\
			if (debug_jobs)					\
				fprintf(stderr, "    JOBS SPAWN: created %ld ...\n", njobs);								\
		} else {						\
			/* error */					\
			if (debug_jobs)	{				\
				int error = errno;			\
				fprintf(stderr, "    JOBS SPAWN: failed error: %d) ...\n", errno);	\
				errno = error;				\
			}						\
			RESULT(errno);					\
			localrc = -1;					\
		}							\
	} while (0);							\
	localrc;							\
})


/* sadly C forces us to do this with exit, long_jump or returning error
 * from work_spawn and work_sync. We could throw a C++ exception, is it
 * worth doing it to avoid the exit here.
 *
 * atm not all resources may be cleaned up at exit
 */
int last_error = 0;
void handle_work_result(int retval)
{
	if (retval) {
		last_error = retval;
		if (abort_on_error) {
			/* already in abort mode we don't need subsequent
			 * syncs to do this too
			 */
			abort_on_error = 0;
			work_sync(handle_work_result);
			exit(last_error);

		}
	}
}

static long compute_jobs(long n, long j)
{
	if (j == JOBS_AUTO)
		j = n;
	else if (j < 0)
		j = n * j * -1;
	return j;
}

static void setup_parallel_compile(long ncpus, long maxcpus)
{
	/* jobs and parallel_max set by default, config or args */
	if (jobs < 0 || jobs == JOBS_AUTO)
		jobs_scale = 1;
	jobs = compute_jobs(ncpus, jobs);
	jobs_max = compute_jobs(maxcpus, jobs_max);

	if (jobs > jobs_max) {
		pwarn(WARN_JOBS, "%s: Capping number of jobs to %ld * # of cpus == '%ld'",
		      progname, jobs_max, jobs);
		jobs = jobs_max;
	} else if (jobs_scale && jobs < jobs_max)
		/* the bigger the difference the more sample chances given */
		jobs_scale = jobs_max + 1 - ncpus;

	njobs = 0;
	if (debug_jobs)
		fprintf(stderr, "jobs: %ld\n", jobs);
}


/*
 * Tune parameters to adjust the parser to adapt to low memory, low power
 * systems.
 * with a profile compile taking up to 10s of MB, launching a lot of
 * parallel compiles is a bad idea on lauch 16 parallel compiles with
 * only 50 MB free.
 *
 */
#define PREFIX_TOTAL	"MemTotal:"
#define PREFIX_FREE	"MemFree:"
#define PREFIX_CACHE	"Cached:"

static bool get_memstat(long long &mem_total, long long &mem_free,
			long long &mem_cache)
{
	char *line, buf[256];
	autofclose FILE *f = NULL;

	mem_total = mem_free = mem_cache = -1;

	/* parse /proc/meminfo to get a rough idea of available mem,
	   look into libstatgrab as alternative */
	f = fopen("/proc/meminfo", "r");
	if (f == NULL) {
		PDEBUG("Failed to open /proc/meminfo");
		return false;
	}

	while ((line = fgets(buf, sizeof(buf), f)) != NULL) {
		long long value;
		if (sscanf(buf, "%*s %lld kB", &value) != 1)
			continue;

		if (strncmp(buf, PREFIX_FREE, strlen(PREFIX_FREE)) == 0)
			mem_free = value * 1024;
		else if (strncmp(buf, PREFIX_TOTAL, strlen(PREFIX_TOTAL)) == 0)
			mem_total = value * 1024;
		else if (strncmp(buf, PREFIX_CACHE, strlen(PREFIX_CACHE)) == 0)
			mem_cache = value * 1024;
	}

	if (mem_free == -1 || mem_total == -1 || mem_cache == -1) {
		PDEBUG("Failed to parse mem value");
		return false;
	}
	mem_free += mem_cache;

	return true;
}

static void auto_tune_parameters(void)
{
	long long mem_total, mem_free, mem_cache;
	long ncpus = sysconf(_SC_NPROCESSORS_ONLN);
	long maxcpus = sysconf(_SC_NPROCESSORS_CONF);
	if (ncpus == -1) {
		PDEBUG("Unable to determine number of processors, default to 1");
		ncpus = 1;
	}
	if (maxcpus == -1) {
		PDEBUG("Unable to determine number of processors, default to 1");
		maxcpus = 1;
	}
	/* only override if config or param hasn't overridden */
	if (get_memstat(mem_total, mem_free, mem_cache) == true &&
	    jobs == JOBS_AUTO) {
		long estimated_jobs = (long) (mem_free / estimated_job_size);

		if (mem_free < 2) {
			/* -j0 - no workers */
			jobs = jobs_max = 0;
			PDEBUG("Auto tune: --jobs=0");
		} else if (estimated_jobs < ncpus) {
			/* --jobs=estimate_jobs */
			jobs = estimated_jobs;
			PDEBUG("Auto tune: --jobs=%ld", estimated_jobs);
		} else {
			long long n = estimated_jobs / ncpus;

			if (n < -DEFAULT_JOBS_MAX) {
				/* --jobs=cpus*n */
				jobs = -n;
				PDEBUG("Auto tune: --jobs=%ld", jobs);
			}
		}
	} else {
		PDEBUG("Unable to get meminfo, using defaults");
	}

	setup_parallel_compile(ncpus, maxcpus);
}

struct dir_cb_data {
	aa_kernel_interface *kernel_interface;
	const char *dirname;	/* name of the parent dir */
	aa_policy_cache *policy_cache;	/* policy_cache to use */
};

/* data - pointer to a dir_cb_data */
static int profile_dir_cb(int dirfd unused, const char *name, struct stat *st,
			  void *data)
{
	int rc = 0;

	/* Handle symlink here. See _aa_dirat_for_each in private.c */

	if (!S_ISDIR(st->st_mode) && !is_blacklisted(name, NULL)) {
		struct dir_cb_data *cb_data = (struct dir_cb_data *)data;
		autofree char *path = NULL;
		if (asprintf(&path, "%s/%s", cb_data->dirname, name) < 0) {
			PERROR(_("Out of memory"));
			handle_work_result(errno);
			return -1;
		}
		rc = work_spawn(process_profile(option,
						cb_data->kernel_interface,
						path, cb_data->policy_cache),
				handle_work_result);
	}
	return rc;
}

/* data - pointer to a dir_cb_data */
static int binary_dir_cb(int dirfd unused, const char *name, struct stat *st,
			 void *data)
{
	int rc = 0;

	/* Handle symlink here. See _aa_dirat_for_each in private.c */

	if (!S_ISDIR(st->st_mode) && !is_blacklisted(name, NULL)) {
		struct dir_cb_data *cb_data = (struct dir_cb_data *)data;
		autofree char *path = NULL;
		if (asprintf(&path, "%s/%s", cb_data->dirname, name) < 0) {
			PERROR(_("Out of memory"));
			handle_work_result(errno);
			return -1;
		}
		rc = work_spawn(process_binary(option,
					       cb_data->kernel_interface,
					       path),
				handle_work_result);
	}
	return rc;
}

static bool get_kernel_features(struct aa_features **features)
{
	/* Gracefully handle AppArmor kernel without compatibility patch */
	if (!kernel_features && aa_features_new_from_kernel(features) == -1) {
		PERROR("Cache read/write disabled: interface file missing. "
			"(Kernel needs AppArmor 2.4 compatibility patch.)\n");
		write_cache = 0;
		skip_read_cache = 1;

		/* Fall back to older match file */
		if (!set_features_by_match_file(features))
			return false;
	}

	/* At this point we have features, extra commonly used values  */
	kernel_supports_policydb = aa_features_supports(*features, "file");
	kernel_supports_setload = aa_features_supports(*features,
						       "policy/set_load");
	kernel_supports_diff_encode = aa_features_supports(*features,
							   "policy/diff_encode");
	kernel_supports_oob = aa_features_supports(*features,
						   "policy/outofband");

	if (aa_features_supports(*features, "policy/versions/v7"))
		kernel_abi_version = 7;
	else if (aa_features_supports(*features, "policy/versions/v6"))
		kernel_abi_version = 6;

	if (!kernel_supports_diff_encode)
		/* clear diff_encode because it is not supported */
		parseopts.control &= ~CONTROL_DFA_DIFF_ENCODE;

	return true;
}

int main(int argc, char *argv[])
{
	aa_kernel_interface *kernel_interface = NULL;
	aa_policy_cache *policy_cache = NULL;
	int retval;
	int i;
	int optind;

	/* name of executable, for error reporting and usage display */
	progname = argv[0];

	init_base_dir();
	capabilities_init();

	process_early_args(argc, argv);
	process_config_file(config_file);
	optind = process_args(argc, argv);

	auto_tune_parameters();

	setlocale(LC_MESSAGES, "");
	bindtextdomain(PACKAGE, LOCALEDIR);
	textdomain(PACKAGE);

	/* Check to see if we have superuser rights, if we're not
	 * debugging */
	if (!(UNPRIVILEGED_OPS) && ((retval = have_enough_privilege()))) {
		return retval;
	}

	if (!binary_input) parse_default_paths();

	if (!get_kernel_features(&kernel_features)) {
		PERROR(_("Kernel features abi not found"));
		return 1;
	}
	if (!add_cap_feature_mask(kernel_features, CAPFLAG_KERNEL_FEATURE)) {
		PERROR(_("Failed to add kernel capabilities to known capabilities set"));
		return 1;
	}

	if (!(UNPRIVILEGED_OPS) &&
	    aa_kernel_interface_new(&kernel_interface, kernel_features, apparmorfs) == -1) {
		PERROR(_("Warning: unable to find a suitable fs in %s, is it "
		       "mounted?\nUse --subdomainfs to override.\n"),
		       MOUNTED_FS);
		return 1;
	}

	if ((!skip_cache && (write_cache || !skip_read_cache)) ||
	    print_cache_dir || force_clear_cache) {
		uint16_t max_caches = write_cache && cond_clear_cache ? (uint16_t) (-1) : 0;

		if (!cacheloc[0]) {
			cacheloc[0] = "/var/cache/apparmor";
			cacheloc_n = 1;
		}
		if (print_cache_dir)
			return do_print_cache_dirs(kernel_features, cacheloc,
						   cacheloc_n) ? 0 : 1;

		if (force_clear_cache) {
			/* only ever write to the first cacheloc location */
			if (aa_policy_cache_remove(AT_FDCWD, cacheloc[0])) {
				PERROR(_("Failed to clear cache files (%s): %s\n"),
				       cacheloc[0], strerror(errno));
				return 1;
			}

			return 0;
		}

		if (create_cache_dir)
			pwarn(WARN_DEPRECATED, _("The --create-cache-dir option is deprecated. Please use --write-cache.\n"));
		retval = aa_policy_cache_new(&policy_cache, kernel_features,
					     AT_FDCWD, cacheloc[0], max_caches);
		if (retval) {
			if (errno != ENOENT && errno != EEXIST && errno != EROFS) {
				PERROR(_("Failed setting up policy cache (%s): %s\n"),
				       cacheloc[0], strerror(errno));
				return 1;
			}

			if (show_cache) {
				if (max_caches > 0)
					PERROR("Cache write disabled: Cannot create cache '%s': %m\n",
					       cacheloc[0]);
				else
					PERROR("Cache read/write disabled: Policy cache is invalid: %m\n");
			}

			write_cache = 0;
		} else {
			if (show_cache)
				PERROR("Cache: added primary location '%s'\n", cacheloc[0]);
			for (i = 1; i < cacheloc_n; i++) {
				if (aa_policy_cache_add_ro_dir(policy_cache, AT_FDCWD,
							       cacheloc[i])) {
					pwarn(WARN_CACHE, "Cache: failed to add read only location '%s', does not contain valid cache directory for the specified feature set\n", cacheloc[i]);
				} else if (show_cache)
					pwarn(WARN_CACHE, "Cache: added readonly location '%s'\n", cacheloc[i]);
			}
		}
	}

	retval = last_error = 0;
	for (i = optind; i <= argc; i++) {
		struct stat stat_file;

		if (i < argc && !(profilename = strdup(argv[i]))) {
			perror("strdup");
			last_error = ENOMEM;
			if (abort_on_error)
				break;
			continue;
		}
		/* skip stdin if we've seen other command line arguments */
		if (i == argc && optind != argc)
			goto cleanup;

		if (profilename && stat(profilename, &stat_file) == -1) {
			last_error = errno;
			PERROR("File %s not found, skipping...\n", profilename);
			if (abort_on_error)
				break;
			goto cleanup;
		}

		if (profilename && S_ISDIR(stat_file.st_mode)) {
			int (*cb)(int dirfd, const char *name, struct stat *st,
				  void *data);
			struct dir_cb_data cb_data;

			memset(&cb_data, 0, sizeof(struct dir_cb_data));
			cb_data.dirname = profilename;
			cb_data.policy_cache = policy_cache;
			cb_data.kernel_interface = kernel_interface;
			cb = binary_input ? binary_dir_cb : profile_dir_cb;
			if ((retval = dirat_for_each(AT_FDCWD, profilename,
						     &cb_data, cb))) {
				last_error = errno;
				PERROR("There was an error while loading profiles from %s\n",
				       profilename);
				if (abort_on_error)
					break;
			}
		} else if (binary_input) {
			/* ignore return as error is handled in work_spawn */
			work_spawn(process_binary(option, kernel_interface,
						  profilename),
				   handle_work_result);
		} else {
			/* ignore return as error is handled in work_spawn */
			work_spawn(process_profile(option, kernel_interface,
						   profilename, policy_cache),
				   handle_work_result);
		}

	cleanup:
		if (profilename)
			free(profilename);
		profilename = NULL;
	}
	work_sync(handle_work_result);

	if (ofile)
		fclose(ofile);
	aa_policy_cache_unref(policy_cache);
	aa_kernel_interface_unref(kernel_interface);

	return last_error;
}
