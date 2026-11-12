#include <vector>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
using namespace std;
static const int NF=2025, NW=(NF+63)/64, NL=120;
static int tid[NF][NL]; static uint64_t pk[NL][NL][NW]; // frames killed by pair
static long long nodes=0; static int KMAX;
static int D[16]; 
typedef struct {uint64_t w[NW];} BS;
static bool dfs(int sz, const BS&killed){
  nodes++;
  int f=-1; for(int i=0;i<NW&&f<0;i++){ uint64_t u=~killed.w[i]; if(i==NW-1) u&=(NF%64? ((1ULL<<(NF%64))-1):~0ULL); if(u) f=i*64+__builtin_ctzll(u); }
  if(f<0){ printf("BAD D:"); for(int i=0;i<sz;i++)printf(" %d",D[i]); printf("\n"); fflush(stdout); return true; }
  if(sz>=KMAX) return false;
  // singles
  for(int i=0;i<sz;i++){ int x=D[i]; if(tid[f][x]>=200) continue; int T=tid[f][x];
    for(int y=0;y<NL;y++){ if(tid[f][y]!=T) continue; bool in=false; for(int j=0;j<sz;j++) if(D[j]==y) in=true; if(in) continue;
      BS nk=killed; for(int j=0;j<sz;j++) for(int w=0;w<NW;w++) nk.w[w]|=pk[y][D[j]][w];
      D[sz]=y; if(dfs(sz+1,nk)) return true; } }
  if(sz+2<=KMAX){
    for(int y1=0;y1<NL;y1++){ if(tid[f][y1]>=200) continue; bool in=false; for(int j=0;j<sz;j++) if(D[j]==y1) in=true; if(in) continue;
      for(int y2=y1+1;y2<NL;y2++){ if(tid[f][y2]!=tid[f][y1]) continue; in=false; for(int j=0;j<sz;j++) if(D[j]==y2) in=true; if(in) continue;
        BS nk=killed; D[sz]=y1; D[sz+1]=y2;
        for(int j=0;j<sz+1;j++) for(int w=0;w<NW;w++) nk.w[w]|=pk[y2][D[j]][w];
        for(int j=0;j<sz;j++) for(int w=0;w<NW;w++) nk.w[w]|=pk[y1][D[j]][w];
        if(dfs(sz+2,nk)) return true; } } }
  return false;
}
int main(int argc,char**argv){
  KMAX=atoi(argv[1]); FILE*fh=fopen("tid.txt","r"); for(int f=0;f<NF;f++) for(int l=0;l<NL;l++) if(fscanf(fh,"%d",&tid[f][l])!=1) return 1; fclose(fh);
  memset(pk,0,sizeof pk);
  for(int f=0;f<NF;f++) for(int a=0;a<NL;a++) for(int b=a+1;b<NL;b++) if(tid[f][a]<200&&tid[f][a]==tid[f][b]){ pk[a][b][f/64]|=1ULL<<(f%64); pk[b][a][f/64]|=1ULL<<(f%64); }
  for(int r=2;r+1<argc;r+=2){ int a=atoi(argv[r]), b=atoi(argv[r+1]); D[0]=a; D[1]=b; BS k; memcpy(k.w,pk[a][b],sizeof k.w); nodes=0;
    bool res=dfs(2,k); fprintf(stderr,"root %d %d: %s nodes %lld\n",a,b,res?"BAD FOUND":"no bad D",nodes); }
}
