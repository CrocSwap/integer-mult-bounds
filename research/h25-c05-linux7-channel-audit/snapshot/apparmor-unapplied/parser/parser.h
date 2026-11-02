/*
 *   Copyright (c) 1999, 2000, 2001, 2002, 2004, 2005, 2006, 2007
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
 *   along with this program; if not, contact Novell, Inc. or Canonical
 *   Ltd.
 */

#ifndef __AA_PARSER_H
#define __AA_PARSER_H


#include <endian.h>
#include <string.h>
#include <sys/resource.h>

#include <libintl.h>
#define _(s) gettext(s)

#include <sys/apparmor.h>

#include "file_cache.h"
#include "immunix.h"
#include "libapparmor_re/apparmor_re.h"
#include "libapparmor_re/aare_rules.h"
#include "rule.h"
#include "bignum.h"

#include <string>

using namespace std;

#include <set>


#define MODULE_NAME "apparmor"

/* Global variable to pass token to lexer.  Will be replaced by parameter
 * when lexer and parser are made reentrant
 */
extern int parser_token;


#define WARN_RULE_NOT_ENFORCED	0x1
#define WARN_RULE_DOWNGRADED	0x2
#define WARN_ABI		0x4
#define WARN_DEPRECATED		0x8
#define WARN_CONFIG		0x10
#define WARN_CACHE		0x20
#define WARN_DEBUG_CACHE	0x40
#define WARN_JOBS		0x80
#define WARN_DANGEROUS		0x100
#define WARN_UNEXPECTED		0x200
#define WARN_FORMAT		0x400
#define WARN_MISSING		0x800
#define WARN_OVERRIDE		0x1000
#define WARN_INCLUDE		0x2000

#define WARN_DEV (WARN_RULE_NOT_ENFORCED | WARN_RULE_DOWNGRADED | WARN_ABI | \
		  WARN_DEPRECATED | WARN_DANGEROUS | WARN_UNEXPECTED | \
		  WARN_FORMAT | WARN_MISSING | WARN_OVERRIDE | \
		  WARN_DEBUG_CACHE | WARN_INCLUDE)

#define DEFAULT_WARNINGS (WARN_CONFIG | WARN_CACHE | WARN_JOBS | \
			  WARN_UNEXPECTED | WARN_OVERRIDE)

#define WARN_ALL (WARN_RULE_NOT_ENFORCED | WARN_RULE_DOWNGRADED | WARN_ABI | \
		  WARN_DEPRECATED | WARN_CONFIG | WARN_CACHE | \
		  WARN_DEBUG_CACHE | WARN_JOBS | WARN_DANGEROUS | \
		  WARN_UNEXPECTED | WARN_FORMAT | WARN_MISSING | \
		  WARN_OVERRIDE | WARN_INCLUDE)


typedef enum pattern_t pattern_t;


struct cod_pattern {
	char *regex;		// posix regex
};

struct value_list {
	char *value;

	struct value_list *next;
};

int cmp_value_list(value_list *lhs, value_list *rhs);

struct cond_entry {
	char *name;
	int eq;			/* where equals was used in specifying list */
	struct value_list *vals;

	struct cond_entry *next;
};

struct cond_entry_list {
	char *name;

	struct cond_entry *list;
};

struct cod_entry {
	char *name;
	union {
		char *link_name;
		char *onexec;
	};
	char *nt_name;
	Profile *prof;		 	/* Special profile defined
					 * just for this executable */
	perms_t perms;			/* perms is 'or' of AA_* bits */
	audit_t audit;
	rule_mode_t rule_mode;

	bool alias_ignore;		/* ignore for alias processing */

	bool subset;

	pattern_t pattern_type;
	struct cod_pattern pat;

	struct cod_entry *next;
};

struct aa_rlimits {
	unsigned int specified;			/* limits that are set */
	rlim_t limits[RLIMIT_NLIMITS];
};

struct alt_name {
	char *name;
	struct alt_name *next;
};

struct sd_hat {
	char *hat_name;
	unsigned int hat_magic;
};

struct var_string {
	char *prefix;
	char *var;
	char *suffix;
};

#define COD_READ_CHAR 		'r'
#define COD_WRITE_CHAR 		'w'
#define COD_APPEND_CHAR		'a'
#define COD_EXEC_CHAR 		'x'
#define COD_LINK_CHAR 		'l'
#define COD_LOCK_CHAR		'k'
#define COD_MMAP_CHAR		'm'
#define COD_INHERIT_CHAR 	'i'
#define COD_UNCONFINED_CHAR	'U'
#define COD_UNSAFE_UNCONFINED_CHAR	'u'
#define COD_PROFILE_CHAR	'P'
#define COD_UNSAFE_PROFILE_CHAR	'p'
#define COD_LOCAL_CHAR		'C'
#define COD_UNSAFE_LOCAL_CHAR	'c'

#define OPTION_ADD      1
#define OPTION_REMOVE   2
#define OPTION_REPLACE  3
#define OPTION_STDOUT	4
#define OPTION_OFILE	5

#define BOOL int

extern int preprocess_only;

#define PATH_CHROOT_REL 0x1
#define PATH_NS_REL 0x2
#define PATH_CHROOT_NSATTACH 0x4
#define PATH_CHROOT_NO_ATTACH 0x8
#define PATH_MEDIATE_DELETED 0x10
#define PATH_DELEGATE_DELETED 0x20
#define PATH_ATTACH 0x40
#define PATH_NO_ATTACH 0x80



#ifdef DEBUG
#define PDEBUG(fmt, args...)				\
do {							\
	int pdebug_error = errno;			\
	fprintf(stderr, "parser: " fmt, ## args);	\
	errno = pdebug_error;				\
} while (0)
#else
#define PDEBUG(fmt, args...)	/* Do nothing */
#endif
#define NPDEBUG(fmt, args...)	/* Do nothing */

#define PERROR(fmt, args...)			\
do {						\
	int perror_error = errno;		\
	fprintf(stderr, fmt, ## args);		\
	errno = perror_error;			\
} while (0)

#ifndef TRUE
#define TRUE	(1)
#endif
#ifndef FALSE
#define FALSE	(0)
#endif

#define MIN_PORT 0
#define MAX_PORT 65535

#ifndef unused
#define unused __attribute__ ((unused))
#endif


#define list_first(LIST) (LIST)
#define list_for_each(LIST, ENTRY) \
	for ((ENTRY) = (LIST); (ENTRY); (ENTRY) = (ENTRY)->next)
#define list_for_each_safe(LIST, ENTRY, TMP) \
	for ((ENTRY) = (LIST), (TMP) = (LIST) ? (LIST)->next : NULL; (ENTRY); (ENTRY) = (TMP), (TMP) = (TMP) ? (TMP)->next : NULL)
#define list_last_entry(LIST, ENTRY) \
	for ((ENTRY) = (LIST); (ENTRY) && (ENTRY)->next; (ENTRY) = (ENTRY)->next)
#define list_append(LISTA, LISTB)		\
	do {					\
		typeof(LISTA) ___tmp;		\
		list_last_entry((LISTA), ___tmp);\
		___tmp->next = (LISTB);		\
	} while (0)

#define list_len(LIST)		\
({				\
	int len = 0;		\
	typeof(LIST) tmp;		\
	list_for_each((LIST), tmp)	\
		len++;		\
	len;			\
})

#define list_find_prev(LIST, ENTRY)	\
({					\
	typeof(ENTRY) tmp, prev = NULL;	\
	list_for_each((LIST), tmp) {	\
		if (tmp == (ENTRY))	\
			break;		\
		prev = tmp;		\
	}				\
	prev;				\
})

#define list_pop(LIST)				\
({						\
	typeof(LIST) _entry = (LIST);		\
	if (LIST) {				\
		(LIST) = (LIST)->next;		\
		_entry->next = NULL;		\
	}					\
	_entry;					\
})

#define list_remove_at(LIST, PREV, ENTRY)			\
	if (PREV)						\
		(PREV)->next = (ENTRY)->next;			\
	if ((ENTRY) == (LIST))					\
		(LIST) = (ENTRY)->next;				\
	(ENTRY)->next = NULL;					\

#define list_remove(LIST, ENTRY)				\
do {								\
	typeof(ENTRY) prev = list_find_prev((LIST), (ENTRY));	\
	list_remove_at((LIST), prev, (ENTRY));			\
} while (0)


#define DUP_STRING(orig, new, field, fail_target) \
	do {									\
		(new)->field = ((orig)->field) ? strdup((orig)->field) : NULL;	\
		if (((orig)->field) && !((new)->field))				\
				goto fail_target;				\
	} while (0)


#define u8  unsigned char
#define u16 uint16_t
#define u32 uint32_t
#define u64 uint64_t

#define cpu_to_le16(x) ((u16)(htole16 ((u16) x)))
#define cpu_to_le32(x) ((u32)(htole32 ((u32) x)))
#define cpu_to_le64(x) ((u64)(htole64 ((u64) x)))

/* The encoding for kernal abi > 5 is
 * 28-31: reserved
 * 20-27: policy version
 * 12-19: policy abi version
 * 11:    force complain flag
 * 10:    reserved
 * 0-9:   kernel abi version
 */
#define ENCODE_VERSION(C, P, PABI, KABI)		\
({							\
	u32 version = (KABI) & 0x3ff;			\
	if ((KABI) > 5) {				\
		version |= (C) ? 1 << 11 : 0;		\
		version |= ((PABI) & 0xff) << 12;	\
		version |= ((P) & 0xff) << 20;		\
	}						\
	version;					\
})

/* The parser fills this variable in automatically */
#define PROFILE_NAME_VARIABLE "profile_name"

/* from parser_common.c */
extern uint32_t policy_version;
extern uint32_t parser_abi_version;
extern uint32_t kernel_abi_version;

extern aa_features *pinned_features;
extern aa_features *policy_features;
extern aa_features *override_features;
extern aa_features *kernel_features;

extern int force_complain;
extern int perms_create;
extern int net_af_max_override;
extern int kernel_load;
extern int kernel_supports_setload;
extern int features_supports_network;
extern int features_supports_networkv8;
extern int features_supports_inet;
extern int kernel_supports_policydb;
extern int kernel_supports_diff_encode;
extern int features_supports_mount;
extern int features_supports_dbus;
extern int features_supports_signal;
extern int features_supports_ptrace;
extern int features_supports_unix;
extern int features_supports_stacking;
extern int features_supports_domain_xattr;
extern int features_supports_userns;
extern int features_supports_posix_mqueue;
extern int features_supports_sysv_mqueue;
extern int features_supports_io_uring;
extern int features_supports_flag_interruptible;
extern int features_supports_flag_signal;
extern int kernel_supports_oob;
extern int conf_verbose;
extern int conf_quiet;
extern int names_only;
extern int option;
extern int current_lineno;
extern const char *progname;
extern char *profilename;
extern char *profile_ns;
extern char *current_filename;
extern FILE *ofile;
extern int read_implies_exec;
extern IncludeCache_t *g_includecache;

extern void pwarnf(bool werr, const char *fmt, ...) __attribute__((__format__(__printf__, 2, 3)));
extern void common_warn_once(const char *name, const char *msg, const char **warned_name);

#define pwarn(F, args...) do { if (parseopts.warn & (F)) pwarnf((parseopts.Werror & (F)), ## args); } while (0)

/* from parser_main (cannot be used in tst builds) */
extern int force_complain;
extern void display_version(void);
extern int show_cache;
extern int skip_cache;
extern int skip_read_cache;
extern int write_cache;
extern int cond_clear_cache;
extern int force_clear_cache;
extern int create_cache_dir;
extern int preprocess_only;
extern int skip_mode_force;
extern int abort_on_error;
extern int skip_bad_cache_rebuild;
extern int mru_skip_cache;

/* provided by parser_lex.l (cannot be used in tst builds) */
extern FILE *yyin;
extern void yyrestart(FILE *fp);
extern int yyparse(void);
extern void yyerror(const char *msg, ...);
extern int yylex(void);

/* parser_include.c */
extern const char *basedir;

/* parser_regex.c */
#define default_match_pattern "[^\\000]*"
#define anyone_match_pattern "[^\\000]+"

#define glob_default	0
#define glob_null	1
extern pattern_t convert_aaregex_to_pcre(const char *aare, int anchor, int glob,
					 std::string& pcre, int *first_re_pos);
extern int build_list_val_expr(std::string& buffer, struct value_list *list);
extern int convert_entry(std::string& buffer, char *entry);
extern int clear_and_convert_entry(std::string& buffer, char *entry);
extern int convert_range(std::string& buffer, bignum start, bignum end);
extern int process_regex(Profile *prof);
extern int post_process_entry(struct cod_entry *entry);

extern int process_policydb(Profile *prof);

extern int process_policy_ents(Profile *prof);
extern void filter_slashes(char *path);

/* parser_variable.c */
int expand_entry_variables(char **name);
extern int process_variables(Profile *prof);
extern struct var_string *split_out_var(const char *string);
extern void free_var_string(struct var_string *var);

/* parser_misc.c */
extern void warn_uppercase(void);
extern int is_blacklisted(const char *name, const char *path);
extern struct value_list *new_value_list(char *value);
extern struct value_list *dup_value_list(struct value_list *list);
extern void free_value_list(struct value_list *list);
extern void print_value_list(struct value_list *list);
extern struct cond_entry *new_cond_entry(char *name, int eq, struct value_list *list);
extern void move_conditional_value(const char *rulename, char **dst_ptr,
				   struct cond_entry *cond_ent);
extern void free_cond_entry(struct cond_entry *ent);
extern void free_cond_list(struct cond_entry *ents);
extern void free_cond_entry_list(struct cond_entry_list &cond);
extern void print_cond_entry(struct cond_entry *ent);
extern char *processid(const char *string, int len);
extern char *processquoted(const char *string, int len);
extern char *processunquoted(const char *string, int len);
extern int get_keyword_token(const char *keyword);
extern int get_rlimit(const char *name);
extern char *process_var(const char *var);
extern perms_t parse_perms(const char *permstr);
extern int parse_X_perms(const char *X, int valid, const char *str_perms, perms_t *perms, int fail);
bool label_contains_ns(const char *label);
bool parse_label(bool *_stack, char **_ns, char **_name,
		 const char *label, bool yyerr);
extern struct cod_entry *new_entry(char *id, perms_t perms, char *link_id);

/* returns -1 if value != true or false, otherwise 0 == false, 1 == true */
extern int str_to_boolean(const char* str);
extern int null_strcmp(const char *s1, const char *s2);
extern bool strcomp (const char *lhs, const char *rhs);
extern struct cod_entry *copy_cod_entry(struct cod_entry *cod);
extern void free_cod_entries(struct cod_entry *list);
void debug_cod_entries(struct cod_entry *list);
bool check_x_qualifier(struct cod_entry *entry, const char *&error);
bool entry_add_prefix(struct cod_entry *entry, const prefixes &p, const char *&error);


#define SECONDS_P_MS (1000LL * 1000LL)
long long convert_time_units(long long value, long long base, const char *units);


/* parser_symtab.c */
struct set_value {
	char *val;
	struct set_value *next;
};
extern int add_boolean_var(const char *var, int boolean);
extern int get_boolean_var(const char *var);
extern int new_set_var(const char *var, const char *value);
extern int add_set_value(const char *var, const char *value);
extern struct set_value *get_set_var(const char *var);
extern char *get_next_set_value(struct set_value **context);
extern int delete_set_var(const char *var_name);
extern void dump_symtab(void);
extern void dump_expanded_symtab(void);
void free_symtabs(void);

/* parser_alias.c */
extern int new_alias(const char *from, const char *to);
extern int replace_profile_aliases(Profile *prof);
extern void free_aliases(void);

/* parser_merge.c */
extern int profile_merge_rules(Profile *prof);

/* parser_interface.c */
extern int load_profile(int option, aa_kernel_interface *kernel_interface,
			Profile *prof, int cache_fd);
extern void sd_serialize_profile(std::ostringstream &buf, Profile *prof,
				int flatten);
extern int sd_load_buffer(int option, char *buffer, int size);
extern int cache_fd;


/* parser_policy.c */
extern void add_to_list(Profile *profile);
extern void add_hat_to_policy(Profile *policy, Profile *hat);
extern int add_entry_to_x_table(Profile *prof, char *name);
extern void add_entry_to_policy(Profile *policy, struct cod_entry *entry);
extern int post_process_policy(int debug_only);
extern int process_profile_regex(Profile *prof);
extern int process_profile_variables(Profile *prof);
extern int process_profile_policydb(Profile *prof);
extern int post_merge_rules(void);
extern int merge_hat_rules(Profile *prof);
extern Profile *merge_policy(Profile *a, Profile *b);
extern int load_policy(int option, aa_kernel_interface *kernel_interface,
		       int cache_fd);
extern int load_hats(std::ostringstream &buf, Profile *prof);
extern int load_flattened_hats(Profile *prof, int option,
			       aa_kernel_interface *kernel_interface,
			       int cache_fd);
extern void dump_policy_hats(Profile *prof);
extern void dump_policy_names(void);
void dump_policy(void);

void free_policies(void);

/* parser_main.c */
extern void set_supported_features();

/* default_features.c */
extern const char *match_n_abi;
extern const char *match_c_abi;
extern const char *match_cn_abi;
extern const char *default_features_abi;

#endif /** __AA_PARSER_H */
