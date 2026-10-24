/* Incremental matching-capacity state.
 * Ali Romman, with substantial OpenAI Codex assistance; Apache-2.0.
 * The predecessor algorithm and notices follow without changes.
 */
/* Source-bound maintained-engine successor with opt-in prefix capacity.
 * JoyboyBrian, with substantial OpenAI Codex assistance; Apache-2.0.
 * PR5001 capacity theorem: Ali Romman; all predecessor credit follows.
 *
 * Corrected finite canonical restored-word census with a union-support budget.
 * Derived from Nicholas Stone's corrected_census.c (research/
 * f7-weight-parity-census-correction, sha256 265ead91...) and the L<=22 gate
 * extension recorded in PR #3731; preserves the restricted-growth word scope.
 * New implementation/review with substantial OpenAI Codex assistance.
 * (The preceding attribution line is retained verbatim from the pinned
 * predecessor. The union-budget port, the length-22 probes and their
 * verification were produced by Nick Petalas with AI assistance.)
 *
 * E and O ALWAYS mean Hamming-weight parity, never coordinate bit 0.
 * New DISTINCT states add pair representations; visits add none.
 * Even excess is (C(|E|,2)-|supp EE|)+(C(|O|,2)-|supp OO|).
 * Odd excess is |E||O|-|supp EO|. These are monotone, so their necessary
 * final bounds are sound at intermediate prefixes. Default enables both.
 *
 * UNION BUDGET (from research/f7-union-support-audit, PR #3005): let
 * U = supp EE union supp OO. A completion adds at most
 * C(S,2)+C(T,2)-C(e,2)-C(o,2) further same-parity pairs, each contributing
 * at most one new mask, so |U| + that quantity >= 2^(N-1)-1 is necessary.
 * Because |U| <= |supp EE|+|supp OO|, this dominates the even excess budget
 * above (the excess form charges an overlapping mask twice). Enabled by
 * default; --no-union-budget restores the predecessor's even-side test.
 *
 * candidate_restored_leaves counts only leaves surviving enabled budgets.
 * all_restored_leaves is exact only with --no-budgets and complete=true.
 * A capped run returns 2, complete=false; bad input or output I/O returns 1.
 * N in [1,7], positive even L<=22. See README.md for proof and commands.
 */
#ifndef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 200809L
#endif
#include <errno.h>
#include <inttypes.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifndef N
#define N 7
#endif
#ifndef L
#define L 20
#endif
#if N < 1 || N > 7 || L < 2 || L > 22 || L % 2
#error "Requires 1 <= N <= 7 and positive even 2 <= L <= 22"
#endif

typedef unsigned __int128 mask_t;
typedef struct { char key[L+1]; int length; uint64_t cap; } Shard;
typedef struct {
    uint64_t nodes, candidate_leaves, hits, even_prunes, odd_prunes, union_prunes, capacity_prunes;
    int aborted;
    double seconds;
} Result;
static int S,T, even_on=1,odd_on=1,union_on=1,even_budget,odd_budget,union_budget;
static int capacity_on,capacity_active;
static int word[L], counts[N], E[L+1],O[L+1],es=1,os=0;
static int q,used,odd_counts,even_excess,odd_excess;
static mask_t seen=1, ee,oo,eo;
static Result run;
static Shard *current;
static FILE *hitout;
static int io_error;
static int rem_even[L],rem_odd[L];
static inline int pop(mask_t x) {
    return __builtin_popcountll((uint64_t)x)+__builtin_popcountll((uint64_t)(x>>64));
}
static inline int parity(int x) { return __builtin_popcount((unsigned)x)&1; }
static inline mask_t bit(int x) { return (mask_t)1 << x; }
typedef struct { int size[2],stays[2],occupied_pairs[2]; } Capacity;
static Capacity capacity[L][N];
/* Each level owns its state. A sibling overwrites only the next level. */
static void extend_capacity(int depth,int point,int label,mask_t old_seen) {
    for(int omitted=0;omitted<N;omitted++) {
        Capacity *next=&capacity[depth+1][omitted];
        *next=capacity[depth][omitted];
        int mask=((1<<N)-1)^(1<<omitted),side=parity(point&mask);
        next->size[side]++;
        if(label==omitted) next->stays[side]++;
        if(old_seen&bit(point^(1<<omitted))) next->occupied_pairs[side]++;
    }
}
/* The caller supplies a simple path; each omitted functional uses actual splits. */
static uint32_t capacity_splits(int depth,int omitted) {
    int k=depth+1,r=L-k,mask=((1<<N)-1)^(1<<omitted);
    const Capacity *state=&capacity[depth][omitted];
    const int *size=state->size,*stays=state->stays;
    int cheap[2]={0},pairs[2],available[2];
    int crossing=depth-stays[0]-stays[1];
    if(!r) return __builtin_popcount((unsigned)q)==1 ? (uint32_t)1<<size[0] : 0;
    for(int side=0;side<2;side++) {
        available[side]=(1<<(N-1))-size[side];
        pairs[side]=(1<<N)/4-size[side]+state->occupied_pairs[side];
    }
    int endpoints[2]={0,q};
    for(int i=0;i<2;i++) {
        int endpoint=endpoints[i];
        if(!(seen&bit(endpoint^(1<<omitted)))) cheap[parity(endpoint&mask)]++;
    }
    uint32_t splits=0;
    for(int x=0;x<=r;x++) {
        int added[2]={x,r-x},low=crossing,high=crossing+r+1;
        if(x>available[0] || r-x>available[1]) continue;
        if(size[0]+x && size[1]+r-x && low<2) low=2;
        for(int side=0;side<2;side++) {
            int one=cheap[side]<added[side]?cheap[side]:added[side];
            int two=(added[side]-one)/2;
            if(two>pairs[side]) two=pairs[side];
            int total=size[side]+added[side];
            int floor=2*total-2*(stays[side]+one+two);
            int ceiling=2*total-2*stays[side];
            if(low<floor) low=floor;
            if(high>ceiling) high=ceiling;
        }
        low+=low&1;
        if(low<=high) splits|=(uint32_t)1<<(size[0]+x);
    }
    return splits;
}
static void rec(int i) {
    if (run.aborted || io_error) return;
    if (current->cap && run.nodes >= current->cap) { run.aborted=1; return; }
    run.nodes++;
    if (i==L) {
        if (q || used!=N || odd_counts || es!=S || os!=T) return;
        run.candidate_leaves++;
        if (pop(ee|oo|eo|1)==(1<<N)) {
            run.hits++;
            for (int k=0;k<L;k++) if (fputc('0'+word[k],hitout)==EOF) io_error=1;
            if (fputc('\n',hitout)==EOF || fflush(hitout)==EOF) io_error=1;
        }
        return;
    }
    if (odd_counts+2*(N-used)>L-i) return;
    if(capacity_active && i>0) {
        for(int omitted=0;omitted<N;omitted++) if(!capacity_splits(i,omitted)) {
            run.capacity_prunes++; return;
        }
    }
    int limit=used<N ? used+1 : N;
    for (int j=0;j<limit;j++) {
        if (run.aborted || io_error) return;
        if (counts[j]>=L-2*(N-1)) continue;
        if (i<current->length && j!=current->key[i]-'0') continue;
        int nq=q^(1<<j),last=(i==L-1);
        if (last && nq) continue; /* q_L is closure, never a prefix state. */
        int fresh=!last && !(seen&bit(nq));
        int p=parity(nq),ns=es+(fresh&&!p),nt=os+(fresh&&p);
        if (ns>S || nt>T || ns+rem_even[i]<S || nt+rem_odd[i]<T) continue;
        mask_t add_same=0,add_cross=0;
        int dc_even=0,dc_odd=0;
        if (fresh) {
            const int *same=p?O:E, *cross=p?E:O;
            int same_size=p?os:es,cross_size=p?es:os;
            for (int a=0;a<same_size;a++) add_same|=bit(nq^same[a]);
            for (int a=0;a<cross_size;a++) add_cross|=bit(nq^cross[a]);
            dc_even=pop(add_same&(p?oo:ee));
            dc_odd=pop(add_cross&eo);
            if (union_on) {
                mask_t nu=(p?oo:ee)|add_same, nc=(p?ee:oo);
                int future_same=S*(S-1)/2+T*(T-1)/2-ns*(ns-1)/2-nt*(nt-1)/2;
                if (pop(nu|nc)+future_same<(1<<(N-1))-1) { run.union_prunes++; continue; }
            }
            if (even_on && even_excess+dc_even>even_budget) { run.even_prunes++; continue; }
            if (odd_on && odd_excess+dc_odd>odd_budget) { run.odd_prunes++; continue; }
        }
        mask_t old_seen=seen,old_ee=ee,old_oo=oo,old_eo=eo;
        int old_q=q,old_used=used,old_odd=odd_counts;
        word[i]=j;
        counts[j]++;
        odd_counts+=(counts[j]&1)?1:-1;
        q=nq;
        if (j==old_used) used++;
        if(capacity_active && fresh) extend_capacity(i,nq,j,old_seen);
        if (fresh) {
            seen|=bit(nq);
            if (p) { O[os++]=nq; oo|=add_same; }
            else { E[es++]=nq; ee|=add_same; }
            eo|=add_cross;
            even_excess+=dc_even; odd_excess+=dc_odd;
        }
        rec(i+1);
        if (fresh) {
            if (p) os--; else es--;
            even_excess-=dc_even; odd_excess-=dc_odd;
        }
        seen=old_seen; ee=old_ee; oo=old_oo; eo=old_eo;
        counts[j]--; q=old_q; used=old_used; odd_counts=old_odd;
    }
}
static int parse_uint(const char *s,uint64_t *out) {
    if (!*s || *s<'0' || *s>'9') return 0;
    errno=0; char *end; unsigned long long n=strtoull(s,&end,10);
    if (errno || *end) return 0;
    *out=(uint64_t)n; return 1;
}
static int parse_split(const char *s) {
    const char *comma=strchr(s,',');
    if (!comma || comma==s || strchr(comma+1,',') || comma-s>3) return 0;
    char left[4]; memcpy(left,s,(size_t)(comma-s)); left[comma-s]=0;
    uint64_t a,b;
    if (!parse_uint(left,&a)||!parse_uint(comma+1,&b)||a<1||b<1||a>L/2||b>L/2||a>(1u<<(N-1))||b>(1u<<(N-1))) return 0;
    S=(int)a; T=(int)b; return 1;
}
static int parse_shard(const char *s,Shard *dst,uint64_t cap) {
    const char *colon=strchr(s,':');
    size_t len=colon?(size_t)(colon-s):strlen(s);
    if (len==1 && s[0]=='-') len=0;
    if (len>L || (colon && !parse_uint(colon+1,&cap))) return 0;
    int introduced=0;
    for (size_t k=0;k<len;k++) {
        int label=s[k]-'0';
        if (label<0 || label>=N || label>introduced) return 0;
        if (label==introduced) introduced++;
        dst->key[k]=s[k];
    }
    dst->key[len]=0; dst->length=(int)len; dst->cap=cap;
    return 1;
}
static void write_result(FILE *f,const char *prefix,Result *r,int comma) {
    fprintf(f,"    {\"prefix\":\"%s\",\"nodes\":%" PRIu64 ",\"candidate_restored_leaves\":%" PRIu64 ",\"all_restored_leaves\":",prefix,r->nodes,r->candidate_leaves);
    if (!even_on&&!odd_on&&!r->aborted) fprintf(f,"%" PRIu64,r->candidate_leaves); else fputs("null",f);
    fprintf(f,",\"hits\":%" PRIu64 ",\"even_budget_prunes\":%" PRIu64 ",\"odd_budget_prunes\":%" PRIu64 ",\"union_budget_prunes\":%" PRIu64 ",\"prefix_capacity_prunes\":%" PRIu64 ",\"aborted\":%s,\"complete\":%s,\"seconds\":%.6f}%s\n",r->hits,r->even_prunes,r->odd_prunes,r->union_prunes,r->capacity_prunes,r->aborted?"true":"false",(!r->aborted&&!io_error)?"true":"false",r->seconds,comma?",":"");
}
int main(int argc,char **argv) {
    Shard shards[128]; Result results[128]; int nshards=0;
    const char *hits_path=NULL,*json_path=NULL; uint64_t cap=0;
    if (argc<2||!parse_split(argv[1])) { fprintf(stderr,"usage: %s s,t --hits PATH [--json PATH] [--cap N] [--prefix-capacity] [--no-budgets|--no-even-budget|--no-odd-budget] [PREFIX[:CAP]...]\n",argv[0]); return 1; }
    for (int a=2;a<argc;a++) {
        const char *arg=argv[a];
        if (!strcmp(arg,"--prefix-capacity")) { capacity_on=1; continue; }
        if (!strcmp(arg,"--no-budgets")) { even_on=odd_on=union_on=0; continue; }
        if (!strcmp(arg,"--no-even-budget")) { even_on=0; continue; }
        if (!strcmp(arg,"--no-odd-budget")) { odd_on=0; continue; }
        if (!strcmp(arg,"--no-union-budget")) { union_on=0; continue; }
        if (!strcmp(arg,"--hits")||!strcmp(arg,"--json")||!strcmp(arg,"--cap")) {
            if (++a>=argc) { fprintf(stderr,"missing option argument\n"); return 1; }
            if (!strcmp(arg,"--hits")) { if(hits_path) return 1; hits_path=argv[a]; }
            else if (!strcmp(arg,"--json")) { if(json_path) return 1; json_path=argv[a]; }
            else if (!parse_uint(argv[a],&cap)) { fprintf(stderr,"invalid cap\n"); return 1; }
            continue;
        }
        if (nshards==128 || !parse_shard(arg,&shards[nshards],0)) { fprintf(stderr,"invalid shard: %s\n",arg); return 1; }
        nshards++;
    }
    if (!hits_path || (json_path&&!strcmp(hits_path,json_path))) { fprintf(stderr,"distinct explicit --hits PATH required\n"); return 1; }
    if (!nshards) { memset(&shards[0],0,sizeof shards[0]); nshards=1; }
    for(int a=0;a<nshards;a++) {
        if (!shards[a].cap) shards[a].cap=cap;
        for(int b=0;b<a;b++) {
            int common=shards[a].length<shards[b].length?shards[a].length:shards[b].length;
            if (!strncmp(shards[a].key,shards[b].key,(size_t)common)) { fprintf(stderr,"overlapping shards\n"); return 1; }
        }
    }
    capacity_active=capacity_on && N>=2 && L>=4 && L<=(1<<N) && S==L/2 && T==L/2;
    even_budget=S*(S-1)/2+T*(T-1)/2-((1<<(N-1))-1);
    odd_budget=S*T-(1<<(N-1));
    union_budget=S*(S-1)/2+T*(T-1)/2-((1<<(N-1))-1);
    for(int i=0;i<L;i++) for(int k=i+2;k<L;k++) if(k&1) rem_odd[i]++; else rem_even[i]++;
    hitout=fopen(hits_path,"wx");
    if(!hitout) { perror(hits_path); return 1; }
    FILE *jsonout=NULL;
    if(json_path) {
        jsonout=fopen(json_path,"wx");
        if(!jsonout) { perror(json_path); fclose(hitout); return 1; }
    }
    Result total={0}; int done=0;
    for(int a=0;a<nshards;a++) {
        memset(&run,0,sizeof run); memset(counts,0,sizeof counts);
        q=used=odd_counts=even_excess=odd_excess=0; es=1; os=0; E[0]=0;
        seen=1; ee=oo=eo=0; current=&shards[a];
        if(capacity_active) {
            memset(capacity,0,sizeof capacity);
            for(int omitted=0;omitted<N;omitted++) capacity[0][omitted].size[0]=1;
        }
        struct timespec start,end; clock_gettime(CLOCK_MONOTONIC,&start);
        /* Negative necessary budget proves no universal leaf: skip whole shard. */
        if (!(even_on&&even_budget<0) && !(odd_on&&odd_budget<0) && !(union_on&&union_budget<0)) rec(0);
        clock_gettime(CLOCK_MONOTONIC,&end);
        run.seconds=(double)(end.tv_sec-start.tv_sec)+1e-9*(double)(end.tv_nsec-start.tv_nsec);
        results[a]=run; done++;
        total.nodes+=run.nodes; total.candidate_leaves+=run.candidate_leaves; total.hits+=run.hits;
        total.even_prunes+=run.even_prunes; total.odd_prunes+=run.odd_prunes; total.union_prunes+=run.union_prunes; total.capacity_prunes+=run.capacity_prunes;
        total.aborted|=run.aborted; total.seconds+=run.seconds;
        printf("SHARD %s nodes=%" PRIu64 " candidate_restored_leaves=%" PRIu64 " hits=%" PRIu64 " complete=%s seconds=%.3f\n",current->length?current->key:"-",run.nodes,run.candidate_leaves,run.hits,(!run.aborted&&!io_error)?"true":"false",run.seconds); fflush(stdout);
        if (run.aborted||io_error) break;
    }
    printf("TOTAL N=%d L=%d split=%d,%d nodes=%" PRIu64 " candidate_restored_leaves=%" PRIu64 " hits=%" PRIu64 " complete=%s seconds=%.3f\n",N,L,S,T,total.nodes,total.candidate_leaves,total.hits,(!total.aborted&&!io_error)?"true":"false",total.seconds);
    if(jsonout) {
        fprintf(jsonout,"{\n  \"prefix_capacity_requested\":%s,\"prefix_capacity_enabled\":%s,\n",capacity_on?"true":"false",capacity_active?"true":"false");
        fprintf(jsonout,"  \"schema\":1,\"n\":%d,\"length\":%d,\"split\":[%d,%d],\"groups\":\"hamming_weight_parity\",\"even_budget\":%d,\"odd_budget\":%d,\"union_budget\":%d,\"even_budget_enabled\":%s,\"odd_budget_enabled\":%s,\"union_budget_enabled\":%s,\n  \"complete\":%s,\"aborted\":%s,\"requested_shards\":%d,\"completed_or_partial_shards\":%d,\n  \"shards\":[\n",N,L,S,T,even_budget,odd_budget,union_budget,even_on?"true":"false",odd_on?"true":"false",union_on?"true":"false",(!total.aborted&&!io_error)?"true":"false",total.aborted?"true":"false",nshards,done);
        for(int a=0;a<done;a++) write_result(jsonout,shards[a].key,&results[a],a+1<done);
        fputs("  ],\n  \"total\":[\n",jsonout); write_result(jsonout,"",&total,0); fputs("  ]\n}\n",jsonout);
        if(fclose(jsonout)) io_error=1;
    }
    if(fclose(hitout)) io_error=1;
    if(io_error) { fprintf(stderr,"output I/O failure; result not valid\n"); return 1; }
    return total.aborted?2:0;
}
