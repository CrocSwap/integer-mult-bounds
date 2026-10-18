// Independent audit engine: (10,10) simple-20-cycle census at n = 7.
//
// Re-implements, from scratch, the exact census scope of
// research/universal-f7-singleton-l20-seed06704c39 (PR2634, head e2f30d93):
// restricted-growth restored words of length 20 over 7 singleton labels whose
// 20 prefix parity states are distinct (|P| = 20 forces the (10,10) split).
//
// Only proved-necessary prunes are applied:
//   1. multiplicity room: odd + 2*(n-used) <= L - i, and per-label count < L-2*(n-1);
//   2. self-avoidance of prefix states (justified by |P| = L = 20);
//   3. pair-representation collision budget e_ex + b_ex <= C(10,2)+C(10,2)-63 = 27
//      (full coverage needs all 63 nonzero even masks from E+E and O+O).
//
// Universality at a closed leaf: P + P = F2^7 over the 20 prefix states.
// Exact 128-bit integer masks; no floating point; no shared code with the
// audited package.  Cross-validation gate: reproduces the author's 11
// completed per-shard (nodes, leaves, hits) exactly before any new result.
//
// Usage:
//   cc -O2 -o f7_census f7_census.c
//   ./f7_census                 # all 15 shards (~165 s on Apple Silicon)
//   ./f7_census 0102 0123       # selected shards
//   ./f7_census 0123:5000000    # capped probe (aborts whole traversal, like
//                               # the reference engine's OverflowError at max_nodes)
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define N 7
#define L 20
#define BUDGET 27

static int prefix[8], preflen;
static uint64_t nodes, leaves, hits;
static int cnt[N];
static int qstate, coll, used, odd;
static unsigned __int128 seen, e_supp, o_supp;
static int E[L], O[L], e_len, o_len;
static int word[L];
static FILE *hitout;
static uint64_t node_cap; /* 0 = no cap; aborts whole traversal when exceeded (mirrors OverflowError) */
static int aborted;

static inline int pop128(unsigned __int128 x) {
    return __builtin_popcountll((uint64_t)x) + __builtin_popcountll((uint64_t)(x >> 64));
}

static void rec(int i) {
    nodes++;
    if (node_cap && nodes > node_cap) { aborted = 1; return; }
    if (i == L) {
        if (qstate != 0) return;
        leaves++;
        int pts[2 * L], m = 0;
        for (int a = 0; a < e_len; a++) pts[m++] = E[a];
        for (int a = 0; a < o_len; a++) pts[m++] = O[a];
        unsigned __int128 cov = 0;
        for (int a = 0; a < m; a++)
            for (int b = a; b < m; b++)
                cov |= (unsigned __int128)1 << (pts[a] ^ pts[b]);
        if (pop128(cov) == (1 << N)) {
            hits++;
            if (hitout) {
                for (int k = 0; k < L; k++) fprintf(hitout, "%d", word[k]);
                fprintf(hitout, "\n");
                fflush(hitout);
            }
        }
        return;
    }
    if (odd + 2 * (N - used) > L - i) return;
    const int room = L - 2 * (N - 1);
    const int limit = (used + 1 < N) ? used + 1 : N;
    for (int j = 0; j < limit; j++) {
        if (aborted) return;
        if (cnt[j] >= room) continue;
        if (i < preflen && j != prefix[i]) continue;
        int nq = qstate ^ (1 << j);
        int closing = (i == L - 1 && nq == 0);
        if (!closing && (seen >> nq) & 1) continue;
        unsigned __int128 add = 0;
        int newcoll = 0;
        if (!closing) {
            if (nq & 1) {
                for (int a = 0; a < o_len; a++) add |= (unsigned __int128)1 << (nq ^ O[a]);
                newcoll = pop128(add & o_supp);
            } else {
                for (int a = 0; a < e_len; a++) add |= (unsigned __int128)1 << (nq ^ E[a]);
                newcoll = pop128(add & e_supp);
            }
            if (coll + newcoll > BUDGET) continue;
        }
        /* save */
        unsigned __int128 s_seen = seen, s_es = e_supp, s_os = o_supp;
        int s_q = qstate, s_coll = coll, s_used = used, s_odd = odd, s_cnt = cnt[j];
        word[i] = j;
        cnt[j]++;
        odd += (cnt[j] & 1) ? 1 : -1;
        qstate = nq;
        coll += newcoll;
        if (!closing) {
            seen |= (unsigned __int128)1 << nq;
            if (nq & 1) { o_supp |= add; O[o_len++] = nq; }
            else        { e_supp |= add; E[e_len++] = nq; }
        }
        if (j == s_used) used++;
        rec(i + 1);
        /* restore */
        if (!closing) { if (nq & 1) o_len--; else e_len--; }
        seen = s_seen; e_supp = s_es; o_supp = s_os;
        qstate = s_q; coll = s_coll; used = s_used; odd = s_odd; cnt[j] = s_cnt;
    }
}

static void run_shard(const char *key) {
    preflen = 0;
    node_cap = 0;
    const char *colon = strchr(key, ':');
    char kbuf[16];
    if (colon) {
        size_t kl = (size_t)(colon - key);
        memcpy(kbuf, key, kl); kbuf[kl] = 0;
        node_cap = strtoull(colon + 1, NULL, 10);
        key = kbuf;
    }
    preflen = (int)strlen(key);
    for (int i = 0; i < preflen; i++) prefix[i] = key[i] - '0';
    nodes = leaves = hits = 0;
    aborted = 0;
    qstate = 0; seen = 1; e_supp = 0; o_supp = 0;
    coll = 0; used = 0; odd = 0;
    e_len = 1; E[0] = 0; o_len = 0;
    memset(cnt, 0, sizeof cnt);
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    rec(0);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double secs = (double)(t1.tv_sec - t0.tv_sec) + 1e-9 * (double)(t1.tv_nsec - t0.tv_nsec);
    printf("SHARD %s nodes=%llu leaves=%llu hits=%llu secs=%.1f\n",
           key, (unsigned long long)nodes, (unsigned long long)leaves,
           (unsigned long long)hits, secs);
    fflush(stdout);
}

int main(int argc, char **argv) {
    hitout = fopen("hits.txt", "w");
    if (argc > 1) {
        for (int a = 1; a < argc; a++) run_shard(argv[a]);
    } else {
        /* all 15 restricted-growth prefixes of depth 4 */
        const char *shards[] = {"0000","0001","0010","0011","0012",
                                "0100","0101","0102","0110","0111","0112",
                                "0120","0121","0122","0123"};
        for (int s = 0; s < 15; s++) run_shard(shards[s]);
    }
    if (hitout) fclose(hitout);
    return 0;
}
