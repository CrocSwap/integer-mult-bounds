// E6SLACK2 search: cover 84 labels by subspaces dims comp (+budget free points). DFS, waste bound, static rarest-point.
// usage: s labs budget seed nodelimit comp...   [env ROOT=a/b: only root-candidate index mod]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128; typedef unsigned long long u64;
int N,lab[128],idx[512]; u128 bit[128];
static inline int pc(u128 x){return __builtin_popcountll((u64)x)+__builtin_popcountll((u64)(x>>64));}
int g[8]={0,1,2,4,8,12,20,36};
typedef struct{u128*m;long n,cap;}L; L cand[8];
u128 *HT;char*HU;long HS=1L<<24;
void add(L*l,u128 m){u64 h=((u64)m*0x9E3779B97F4A7C15ULL)^((u64)(m>>64)*0xC2B2AE3D27D4EB4FULL);long i=(h>>16)&(HS-1);
 while(HU[i]){if(HT[i]==m)return;i=(i+1)&(HS-1);}HU[i]=1;HT[i]=m;
 if(l->n==l->cap){l->cap=l->cap?l->cap*2:1024;l->m=realloc(l->m,l->cap*sizeof(u128));}l->m[l->n++]=m;}
void enumw(int w,int thr){memset(HU,0,HS);
 for(int pm=0;pm<512;pm++){if(__builtin_popcount(pm)!=w)continue;int piv[9],k=0;for(int c=0;c<9;c++)if(pm>>c&1)piv[k++]=c;
  int sr[64],sc[64],ns=0;for(int i=0;i<w;i++)for(int c=0;c<piv[i];c++)if(!(pm>>c&1)){sr[ns]=i;sc[ns]=c;ns++;}
  for(u64 b=0;b<(1ULL<<ns);b++){int rows[9];for(int i=0;i<w;i++)rows[i]=1<<piv[i];
   for(int s=0;s<ns;s++)if(b>>s&1)rows[sr[s]]|=1<<sc[s];
   u128 m=0;int el[512];el[0]=0;for(int j=1;j<(1<<w);j++){int lb=__builtin_ctz(j);el[j]=el[j&(j-1)]^rows[lb];if(idx[el[j]]>=0)m|=bit[idx[el[j]]];}
   if(pc(m)>=thr)add(&cand[w],m);}}}
int slack,cntleft[8]; int types[8],nt; long nodes,lim; int budget0;
long *pl[8][128]; long pn[8][128]; // per type per point candidate lists
u128 sol[16];int nsol; int rootmod=1,rootres=0;
int P0=-1; char *ROOTOK[8];
int rec(u128 unc,int budget,int waste,int depth){nodes++;if(nodes>lim)return -1;
 if(!unc)return 1;
 int bestp=-1;long bestc=1L<<60;
 for(int p=0;p<N;p++)if((unc>>p)&1){long c=budget?1:0;for(int t=0;t<nt;t++)if(cntleft[types[t]])c+=pn[types[t]][p];if(c<bestc){bestc=c;bestp=p;}}
 int p=bestp; if(depth==0&&P0>=0)p=P0; else if(bestc==0)return 0;
 for(int t=0;t<nt;t++){int w=types[t];if(!cntleft[w])continue;L*l=&cand[w];long *lst=pl[w][p];
  cntleft[w]--;
  for(long k=0;k<pn[w][p];k++){ if(depth==0&&ROOTOK[w]&&!ROOTOK[w][lst[k]])continue; u128 m=l->m[lst[k]];int nc=pc(m&unc);int nw=waste+g[w]-nc;if(nw>slack)continue;
   sol[depth]=m;int r=rec(unc&~m,budget,nw,depth+1);if(r){cntleft[w]++;return r;}}
  cntleft[w]++;}
 if(budget>0){int r=rec(unc&~bit[p],budget-1,waste,depth);if(r)return r;}
 return 0;}
int main(int argc,char**argv){FILE*f=fopen(argv[1],"r");fscanf(f,"%d",&N);for(int i=0;i<N;i++)fscanf(f,"%d",&lab[i]);
 memset(idx,-1,sizeof idx);for(int i=0;i<N;i++){idx[lab[i]]=i;bit[i]=(u128)1<<i;}
 u128 FULL=0;for(int i=0;i<N;i++)FULL|=bit[i];
 HT=malloc(HS*16);HU=malloc(HS);
 int budget=atoi(argv[2]);srand(atoi(argv[3]));lim=atol(argv[4]);int cap=budget;
 for(int i=5;i<argc;i++){int w=atoi(argv[i]);cntleft[w]++;cap+=g[w];}
 slack=cap-N;printf("N=%d cap=%d slack=%d\n",N,cap,slack);if(slack<0){puts("NOTCOVERABLE cap");return 0;}
 if(getenv("ROOTMOD")){rootmod=atoi(getenv("ROOTMOD"));rootres=atoi(getenv("ROOTRES"));}
 for(int w=1;w<8;w++)if(cntleft[w]&&w>=3){types[nt++]=w;int thr=g[w]-slack;if(thr<1)thr=1;enumw(w,thr);
   printf("dim%d thr%d cands %ld\n",w,thr,cand[w].n);fflush(stdout);
   // shuffle
   if(getenv("SHUF"))for(long i=cand[w].n-1;i>0;i--){long j=rand()%(i+1);u128 t=cand[w].m[i];cand[w].m[i]=cand[w].m[j];cand[w].m[j]=t;}
   for(int p=0;p<N;p++){pn[w][p]=0;}
   for(long i=0;i<cand[w].n;i++)for(int p=0;p<N;p++)if((cand[w].m[i]>>p)&1)pn[w][p]++;
   for(int p=0;p<N;p++){pl[w][p]=malloc(sizeof(long)*(pn[w][p]+1));pn[w][p]=0;}
   for(long i=0;i<cand[w].n;i++)for(int p=0;p<N;p++)if((cand[w].m[i]>>p)&1)pl[w][p][pn[w][p]++]=i;}
 if(getenv("DUMP")){FILE*o=fopen(getenv("DUMP"),"w");for(int t=0;t<nt;t++){int w=types[t];for(long i=0;i<cand[w].n;i++)fprintf(o,"%d %llu %llu\n",w,(u64)(cand[w].m[i]>>64),(u64)cand[w].m[i]);}fclose(o);fprintf(stderr,"dumped\n");if(getenv("DUMPONLY"))return 0;}
 // small types w<=2 treated as budget
 for(int w=1;w<=2;w++)if(cntleft[w]){puts("use budget for w<=2");return 1;}
 if(getenv("ROOTFILE")){FILE*rf=fopen(getenv("ROOTFILE"),"r");int w;long i;fscanf(rf,"%d",&P0);for(int t=0;t<8;t++)if(cand[t].n)ROOTOK[t]=calloc(cand[t].n,1);while(fscanf(rf,"%d %ld",&w,&i)==2)ROOTOK[w][i]=1;}
 nodes=0;int r=rec(FULL,budget,0,0);
 printf("RESULT %s nodes=%ld\n",r==1?"COVERABLE":r==0?"NOT_COVERABLE(exhaustive)":"LIMIT",nodes);
 if(r==1){for(int i=0;i<16;i++)if(sol[i])printf("S %016llx %016llx\n",(u64)(sol[i]>>64),(u64)sol[i]);}
}
