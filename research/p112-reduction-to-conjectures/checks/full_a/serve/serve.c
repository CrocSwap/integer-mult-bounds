// SERVE impl A (C): exact max served(E) over E = union of full label-flats N(V), V<=F2^9 of dim s_i, plus free lines.
// served(E)=#roots in E + #roots not in E having a minimal two-7-flat leftover (LEFT22 table) inside E + #D7 with leftover inside E.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128; typedef unsigned long long u64;
int lab[120],co[120][8],rootidx[120];
u128 *RM,*DM; // 120 x 9387, 1080 x 6021
#define NR 9387
#define NDm 6021
static inline int pc(u128 x){return __builtin_popcountll((u64)x)+__builtin_popcountll((u64)(x>>64));}
static int cmp(const void*a,const void*b){u128 x=*(u128*)a,y=*(u128*)b;return x<y?-1:x>y;}
static int served(u128 E){int n=0;
  for(int r=0;r<120;r++){ if((E>>rootidx[r])&1){n++;continue;} u128*m=RM+(long)r*NR; for(int i=0;i<NR;i++) if((m[i]&~E)==0){n++;break;} }
  for(int h=0;h<1080;h++){ u128*m=DM+(long)h*NDm; for(int i=0;i<NDm;i++) if((m[i]&~E)==0){n++;break;} }
  return n;}

typedef struct{int t; u128 R;} Ent; Ent*LST; long nl; 
static void buildlist(u128 F,int resmax){ LST=realloc(LST,sizeof(Ent)*(120L*NR+1080L*NDm)); nl=0;
  for(int r=0;r<120;r++){ u128*m=RM+(long)r*NR; for(int i=0;i<NR;i++){u128 R=m[i]&~F; if(pc(R)<=resmax){LST[nl].t=r;LST[nl].R=R;nl++;}}}
  for(int h=0;h<1080;h++){ u128*m=DM+(long)h*NDm; for(int i=0;i<NDm;i++){u128 R=m[i]&~F; if(pc(R)<=resmax){LST[nl].t=120+h;LST[nl].R=R;nl++;}}} }
static int served2(u128 E,u128 F){ // E=F u extra ; counts roots in E + other targets
  int n=pc(E); u128 X=E&~F; int last=-1;
  for(long i=0;i<nl;i++){ int t=LST[i].t; if(t==last)continue; if((LST[i].R&~X)==0){ if(t<120 && ((E>>rootidx[t])&1))continue; n++; last=t; } }
  return n; }

static void servedlist(u128 E){ printf("S"); 
  for(int r=0;r<120;r++){ int in=(E>>rootidx[r])&1; int hit=in; if(!hit){u128*m=RM+(long)r*NR; for(int i=0;i<NR;i++) if((m[i]&~E)==0){hit=1;break;}} if(hit) printf(" r%d",rootidx[r]); }
  for(int h=0;h<1080;h++){ u128*m=DM+(long)h*NDm; for(int i=0;i<NDm;i++) if((m[i]&~E)==0){printf(" d%d",h);break;} } printf("\n"); }
// enumerate all s-dim subspaces V of F2^9 (RREF), return deduped N(V) masks
u128* flats(int s,long*cnt){ long cap=1<<22,n=0; u128*A=malloc(cap*16);
  for(int P=0;P<512;P++){ if(__builtin_popcount(P)!=s)continue; int piv[9],k=0; for(int b=8;b>=0;b--) if((P>>b)&1) piv[k++]=b;
    int fb[20][2],nf=0; for(int i=0;i<s;i++) for(int c=0;c<piv[i];c++) if(!((P>>c)&1)){fb[nf][0]=i;fb[nf][1]=c;nf++;}
    for(long a=0;a<(1L<<nf);a++){ int row[9]; for(int i=0;i<s;i++) row[i]=1<<piv[i]; for(int j=0;j<nf;j++) if((a>>j)&1) row[fb[j][0]]|=1<<fb[j][1];
      u128 N=0; for(int t=0;t<120;t++){int x=lab[t]; for(int i=0;i<s;i++) if((x>>piv[i])&1) x^=row[i]; if(!x) N|=(u128)1<<t;}
      if(n==cap){cap*=2;A=realloc(A,cap*16);} A[n++]=N; } }
  qsort(A,n,16,cmp); long k=0; for(long i=0;i<n;i++) if(i==0||A[i]!=A[i-1]) A[k++]=A[i]; *cnt=k; return A; }
int gperm[8][120];
static u128 img(int g,u128 m){u128 o=0; while(m){int t=__builtin_ctzll((u64)m); if(!(u64)m){t=64+__builtin_ctzll((u64)(m>>64));} o|=(u128)1<<gperm[g][t]; m&=m-1;} return o;}
static long find(u128*A,long n,u128 x){long lo=0,hi=n-1;while(lo<=hi){long m=(lo+hi)/2; if(A[m]==x)return m; if(A[m]<x)lo=m+1; else hi=m-1;} return -1;}
long *uf; static long fnd(long x){while(uf[x]!=x){uf[x]=uf[uf[x]];x=uf[x];}return x;}
// orbit reps (indices) of set family under W(E8)
long* orbits(u128*A,long n,long*nrep,long*osz){ uf=malloc(n*sizeof(long)); for(long i=0;i<n;i++)uf[i]=i;
  for(long i=0;i<n;i++) for(int g=0;g<8;g++){ long j=find(A,n,img(g,A[i])); if(j<0){fprintf(stderr,"family not closed!\n");exit(1);} long a=fnd(i),b=fnd(j); if(a!=b) uf[a]=b; }
  long*reps=malloc(n*sizeof(long)); long k=0; for(long i=0;i<n;i++) if(fnd(i)==i){reps[k++]=i;}
  for(long j=0;j<k;j++) osz[j]=0; for(long i=0;i<n;i++){ long r=fnd(i); for(long j=0;j<k;j++) if(reps[j]==r){osz[j]++;break;} }
  *nrep=k; return reps; }
static void pr(u128 E){for(int t=0;t<120;t++) if((E>>t)&1) printf(" %d",t); printf("\n");}
int main(int argc,char**argv){
  FILE*f=fopen("lines.txt","r"); for(int t=0;t<120;t++){fscanf(f,"%d",&lab[t]);for(int k=0;k<8;k++)fscanf(f,"%d",&co[t][k]);} fclose(f);
  f=fopen("rootidx.txt","r"); for(int i=0;i<120;i++)fscanf(f,"%d",&rootidx[i]); fclose(f);
  RM=malloc(120L*NR*16); DM=malloc(1080L*NDm*16);
  f=fopen("roots.bin","rb"); u64*b=malloc(120L*NR*16); fread(b,16,120L*NR,f); fclose(f); for(long i=0;i<120L*NR;i++) RM[i]=((u128)b[2*i+1]<<64)|b[2*i]; free(b);
  f=fopen("d7.bin","rb"); b=malloc(1080L*NDm*16); fread(b,16,1080L*NDm,f); fclose(f); for(long i=0;i<1080L*NDm;i++) DM[i]=((u128)b[2*i+1]<<64)|b[2*i]; free(b);
  // simple-root reflections (doubled coords, Bourbaki)
  int S[8][8]={{1,-1,-1,-1,-1,-1,-1,1},{2,2,0,0,0,0,0,0},{-2,2,0,0,0,0,0,0},{0,-2,2,0,0,0,0,0},{0,0,-2,2,0,0,0,0},{0,0,0,-2,2,0,0,0},{0,0,0,0,-2,2,0,0},{0,0,0,0,0,-2,2,0}};
  for(int g=0;g<8;g++) for(int t=0;t<120;t++){ int d=0; for(int k=0;k<8;k++) d+=co[t][k]*S[g][k]; d/=4; int w[8]; for(int k=0;k<8;k++) w[k]=co[t][k]-d*S[g][k];
    int found=-1; for(int u=0;u<120&&found<0;u++){int p=1,m=1; for(int k=0;k<8;k++){ if(co[u][k]!=w[k])p=0; if(co[u][k]!=-w[k])m=0;} if(p||m)found=u;} if(found<0){fprintf(stderr,"refl fail\n");return 1;} gperm[g][t]=found; }
  // self-test: table sanity: served of empty / of one Q
  fprintf(stderr,"served(empty)=%d\n",served(0));
  int mode=atoi(argv[1]);
  if(mode==0){ // inventory: flats of rank s, sizes, orbits
    int s=atoi(argv[2]); long n; u128*A=flats(s,&n); long hist[130]={0}; for(long i=0;i<n;i++) hist[pc(A[i])]++;
    printf("rank %d: %ld distinct N sets; size hist:",s,n); for(int z=0;z<130;z++) if(hist[z]) printf(" %d:%ld",z,hist[z]); printf("\n");
    long nrep; long*osz=malloc(n*sizeof(long)); long*reps=orbits(A,n,&nrep,osz); printf("orbits %ld:",nrep); for(long j=0;j<nrep;j++) printf(" [size%d x%ld]",pc(A[reps[j]]),osz[j]); printf("\n"); return 0; }
  if(mode==1){ // F_s1 rep  U  all F_s2 : args s1 s2 [repstart repend]
    int s1=atoi(argv[2]),s2=atoi(argv[3]); long n1; u128*A=flats(s1,&n1); long nrep; long*osz=malloc(n1*sizeof(long)); long*reps=orbits(A,n1,&nrep,osz);
    long n2; u128*B=flats(s2,&n2); int r0=argc>4?atoi(argv[4]):0, r1=argc>5?atoi(argv[5]):nrep; fprintf(stderr,"reps %ld, F2 sets %ld\n",nrep,n2); int mx2=0; for(long i=0;i<n2;i++) if(pc(B[i])>mx2) mx2=pc(B[i]);
    for(int j=r0;j<r1&&j<nrep;j++){ int best=0; u128 bE=0; long hist[200]={0}; buildlist(A[reps[j]],mx2); fprintf(stderr,"list %ld\n",nl); for(long i=0;i<n2;i++){ u128 E=A[reps[j]]|B[i]; int v=served2(E,A[reps[j]]); hist[v]++; if(v>best){best=v;bE=E;} }
      printf("rep %d |F1|=%d orbit %ld |E|=%d max served %d at:",j,pc(A[reps[j]]),osz[j],pc(bE),best); pr(bE); fflush(stdout);} return 0; }
  if(mode==2){ // F_s rep U any k lines : args s k
    int s=atoi(argv[2]),k=atoi(argv[3]); long n1; u128*A=flats(s,&n1); long nrep; long*osz=malloc(n1*sizeof(long)); long*reps=orbits(A,n1,&nrep,osz); fprintf(stderr,"reps %ld\n",nrep);
    int r0=argc>4?atoi(argv[4]):0, r1=argc>5?atoi(argv[5]):nrep;
    for(int j=r0;j<r1&&j<nrep;j++){ int best=0; u128 bE=0; u128 F=A[reps[j]]; buildlist(F,k);
      if(k==3){ for(int a=0;a<120;a++)for(int b2=a+1;b2<120;b2++)for(int c=b2+1;c<120;c++){u128 E=F|((u128)1<<a)|((u128)1<<b2)|((u128)1<<c); int v=served2(E,F); if(v>best){best=v;bE=E;}} }
      else { for(int a=0;a<120;a++)for(int b2=a+1;b2<120;b2++){u128 E=F|((u128)1<<a)|((u128)1<<b2); int v=served2(E,F); if(v>best){best=v;bE=E;} if(argc>6&&v>=atoi(argv[6])){printf("HIT %d rep %d F:",v,j);pr(E);} } }
      printf("rep %d |F|=%d orbit %ld max served %d (|E|=%d) at:",j,pc(F),osz[j],best,pc(bE)); pr(bE); fflush(stdout);} return 0; }
  if(mode==4){ u128 E=0; int t; while(scanf("%d",&t)==1) E|=(u128)1<<t; servedlist(E); return 0; }
  if(mode==5){ u128 F=0; int t; while(scanf("%d",&t)==1) F|=(u128)1<<t; int thr=atoi(argv[2]); for(int a=0;a<120;a++)for(int b=a+1;b<120;b++){u128 E=F|((u128)1<<a)|((u128)1<<b); if(served(E)>=thr){printf("E %d %d ",a,b);servedlist(E);} } return 0; }
  if(mode==3){ // eval a given E (lines on stdin)
    u128 E=0; int t; while(scanf("%d",&t)==1) E|=(u128)1<<t; printf("%d\n",served(E)); return 0; }
}
