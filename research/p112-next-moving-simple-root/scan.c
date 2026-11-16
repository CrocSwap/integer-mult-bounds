/* Exhaustive half-split of one 112-bit, dimension-36 binary basis.
 *
 * Each generator is a 112-bit integer, written as 28 lowercase hex digits.
 * A split s lists the span of the first s generators and the span of the
 * rest by doubling. Every codeword is the XOR of exactly one pair. The
 * integer popcount is the Hamming weight. This file does not implement the
 * bit-lane iterator.
 *
 * The doubling method is the one used for the unreflected P112 frame in
 * PR #7007 and for the first reflected frame in PR #7017. This scanner
 * reads only the basis of the next moving simple root.
 *
 * Apache-2.0. Prepared by unpaidmoon with substantial Cursor Grok assistance.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>

enum { DIM = 36, WIDTH = 112, MAX_LOW = 64 };

typedef struct { uint64_t lo, hi; } Word;

static Word basis[DIM];
static Word *low_words;
static Word *high_words;
static size_t n_low;
static size_t n_high;
static pthread_mutex_t low_mu = PTHREAD_MUTEX_INITIALIZER;
static Word low_found[MAX_LOW];
static int n_low_found;
static int overflow;

typedef struct {
    size_t begin, end;
    uint64_t hist[WIDTH + 1];
    uint64_t seen;
} Job;

static Word wxor(Word a, Word b) {
    Word c;
    c.lo = a.lo ^ b.lo;
    c.hi = a.hi ^ b.hi;
    return c;
}

static int weight(uint64_t lo, uint64_t hi) {
    return __builtin_popcountll(lo) + __builtin_popcountll(hi);
}

static int hex_value(char ch) {
    if (ch >= '0' && ch <= '9') return ch - '0';
    if (ch >= 'a' && ch <= 'f') return ch - 'a' + 10;
    return -1;
}

static int load_basis(const char *path) {
    FILE *fp = fopen(path, "r");
    char hex[80];
    if (!fp) return 0;
    for (int i = 0; i < DIM; i++) {
        uint64_t lo = 0, hi = 0;
        if (fscanf(fp, "%79s", hex) != 1 || strlen(hex) != 28) {
            fclose(fp);
            return 0;
        }
        for (int k = 0; k < 28; k++) {
            int v = hex_value(hex[k]);
            if (v < 0) {
                fclose(fp);
                return 0;
            }
            hi = (hi << 4) | (lo >> 60);
            lo = (lo << 4) | (unsigned)v;
        }
        if (hi >> 48) {
            fclose(fp);
            return 0;
        }
        basis[i].lo = lo;
        basis[i].hi = hi;
    }
    if (fscanf(fp, "%79s", hex) == 1) {
        fclose(fp);
        return 0;
    }
    fclose(fp);
    return 1;
}

static void span(Word *out, int start, int count, size_t expected) {
    size_t len = 1;
    out[0].lo = 0;
    out[0].hi = 0;
    for (int i = 0; i < count; i++) {
        Word g = basis[start + i];
        for (size_t j = 0; j < len; j++) out[len + j] = wxor(out[j], g);
        len <<= 1;
    }
    if (len != expected) {
        fprintf(stderr, "span length mismatch\n");
        exit(1);
    }
}

static void *worker(void *arg) {
    Job *job = arg;
    memset(job->hist, 0, sizeof job->hist);
    job->seen = 0;
    for (size_t i = job->begin; i < job->end; i++) {
        uint64_t hlo = high_words[i].lo;
        uint64_t hhi = high_words[i].hi;
        for (size_t j = 0; j < n_low; j++) {
            uint64_t lo = hlo ^ low_words[j].lo;
            uint64_t hi = hhi ^ low_words[j].hi;
            int wt = weight(lo, hi);
            job->hist[wt]++;
            job->seen++;
            if (wt > 0 && wt <= 16) {
                pthread_mutex_lock(&low_mu);
                if (n_low_found >= MAX_LOW) overflow = 1;
                else {
                    low_found[n_low_found].lo = lo;
                    low_found[n_low_found].hi = hi;
                    n_low_found++;
                }
                pthread_mutex_unlock(&low_mu);
            }
        }
    }
    return NULL;
}

int main(int argc, char **argv) {
    int split, threads;
    long cpus;
    Job *jobs;
    pthread_t *ids;
    uint64_t hist[WIDTH + 1];
    uint64_t seen = 0;
    if (argc != 3) {
        fprintf(stderr, "usage: scan BASIS SPLIT\n");
        return 2;
    }
    split = atoi(argv[2]);
    if (split < 1 || split >= DIM || !load_basis(argv[1])) {
        fprintf(stderr, "bad basis or split\n");
        return 2;
    }
    n_low = (size_t)1 << split;
    n_high = (size_t)1 << (DIM - split);
    low_words = calloc(n_low, sizeof(Word));
    high_words = calloc(n_high, sizeof(Word));
    if (!low_words || !high_words) return 1;
    span(low_words, 0, split, n_low);
    span(high_words, split, DIM - split, n_high);
    cpus = sysconf(_SC_NPROCESSORS_ONLN);
    if (cpus < 1) cpus = 1;
    if (cpus > 4) cpus = 4;
    threads = (int)cpus;
    jobs = calloc((size_t)threads, sizeof(Job));
    ids = calloc((size_t)threads, sizeof(pthread_t));
    if (!jobs || !ids) return 1;
    for (int t = 0; t < threads; t++) {
        size_t chunk = n_high / (size_t)threads;
        jobs[t].begin = (size_t)t * chunk;
        jobs[t].end = (t + 1 == threads) ? n_high : ((size_t)t + 1) * chunk;
        if (pthread_create(&ids[t], NULL, worker, &jobs[t]) != 0) return 1;
    }
    memset(hist, 0, sizeof hist);
    for (int t = 0; t < threads; t++) {
        pthread_join(ids[t], NULL);
        seen += jobs[t].seen;
        for (int w = 0; w <= WIDTH; w++) hist[w] += jobs[t].hist[w];
    }
    if (overflow) {
        fprintf(stderr, "more than %d words of weight 1..16\n", MAX_LOW);
        return 1;
    }
    printf("SPLIT %d\n", split);
    printf("SEEN %llu\n", (unsigned long long)seen);
    printf("THREADS %d\n", threads);
    for (int w = 0; w <= WIDTH; w++) {
        if (hist[w]) printf("HIST %d %llu\n", w, (unsigned long long)hist[w]);
    }
    for (int i = 0; i < n_low_found; i++) {
        printf("LOW %012llx%016llx\n",
               (unsigned long long)low_found[i].hi,
               (unsigned long long)low_found[i].lo);
    }
    free(jobs);
    free(ids);
    free(low_words);
    free(high_words);
    return 0;
}
