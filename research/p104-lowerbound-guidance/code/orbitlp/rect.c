/* ORBITLP rect.c (own code). Enumerate all maximal rectangles (D,S) of P104 up to Aut:
   D = L∩M (M label-closed, one rep per Aut orbit), S = L∩K^perp for every subspace K of M.
   For each: price = rank_F2 Q[D,S]; frame-activity counts per frame orbit (D∩T and S∩T nonempty);
   diag counts |D∩S∩P| per port orbit. Distinct profiles -> profiles.txt (with an example: rep id + K basis). */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
typedef unsigned __int128 u128;
int lab[104], NA, NF, perm[400][104], fr[800][8], fo[800], po[104];
u128 frm[800]; u128 hyp[512];
int NFO=20, NPO=3;
static int rankvecs(int *v,int k,int *basis){int piv[9]={0},r=0;
  for(int i=0;i<k;i++){int x=v[i];for(int h=8;h>=0;h--) if(x>>h&1){ if(piv[h]) x^=piv[h]; else {piv[h]=x;r++;break;}}}
  if(basis){int j=0;for(int h=8;h>=0;h--) if(piv[h]) basis[j++]=piv[h];} return r;}
static int dotb(int a,int b){return __builtin_parity(a&b);}
/* hash table of profiles */
#define PL 25
typedef struct {unsigned char p[PL]; long cnt; int rep; int kb[9]; int kd;} Ent;
Ent *H; long HS=1<<24, nent=0;
unsigned long hsh(unsigned char*p){unsigned long h=1469598103934665603UL; for(int i=0;i<PL;i++){h^=p[i]; h*=1099511628211UL;} return h;}
void add(unsigned char*p,int rep,int*kb,int kd){ unsigned long h=hsh(p)&(HS-1);
  while(H[h].cnt){ if(!memcmp(H[h].p,p,PL)){H[h].cnt++; return;} h=(h+1)&(HS-1);} 
  memcpy(H[h].p,p,PL); H[h].cnt=1; H[h].rep=rep; memcpy(H[h].kb,kb,sizeof(int)*9); H[h].kd=kd; nent++; if(nent>HS/2){fprintf(stderr,"hash full\n");exit(1);} }
int curM[9], md, currep; u128 curD; int Dlab[104], nD;
int Mbasis_full[9];
void doK(int *kb,int kd){ /* kb in F2^9 */
  u128 S=0; S=~S; S&=(((u128)1)<<104)-1;
  for(int i=0;i<kd;i++) S&=hyp[kb[i]];
  /* price: rank of Gram(Mbasis, Abasis) */
  int sl[104],ns=0; for(int t=0;t<104;t++) if(S>>t&1) sl[ns++]=lab[t];
  int Ab[9]; int ad=rankvecs(sl,ns,Ab);
  int rows[9]; for(int i=0;i<md;i++){int x=0; for(int j=0;j<ad;j++) if(dotb(curM[i],Ab[j])) x|=1<<j; rows[i]=x;}
  int price=rankvecs(rows,md,NULL);
  unsigned char p[PL]; memset(p,0,PL);
  for(int f=0;f<NF;f++) if((curD&frm[f]) && (S&frm[f])) p[fo[f]]++;
  u128 DS=curD&S; for(int t=0;t<104;t++) if(DS>>t&1) p[20+po[t]]++;
  p[23]=price; p[24]=0;
  add(p,currep,kb,kd);
}
/* enumerate subspaces of F2^md via RREF in coordinates, map to M */
int cb[9];
void rec(int d,int *piv,int idx){
  if(idx==d){ int kb[9]; for(int i=0;i<d;i++){int x=0; for(int j=0;j<md;j++) if(cb[i]>>j&1) x^=curM[j]; kb[i]=x;} doK(kb,d); return;}
  int fp[9],nf=0; for(int c=piv[idx]-1;c>=0;c--){int isp=0; for(int j=0;j<d;j++) if(piv[j]==c) isp=1; if(!isp) fp[nf++]=c;}
  for(int s=0;s<(1<<nf);s++){int x=1<<piv[idx]; for(int j=0;j<nf;j++) if(s>>j&1) x|=1<<fp[j]; cb[idx]=x; rec(d,piv,idx+1);} }
int cmp128(const void*a,const void*b){u128 x=*(u128*)a,y=*(u128*)b; return x<y?-1:x>y;}
int main(){ FILE*f=fopen("geo.txt","r");
  for(int i=0;i<104;i++) fscanf(f,"%d",&lab[i]); fscanf(f,"%d",&NA);
  for(int a=0;a<NA;a++) for(int i=0;i<104;i++) fscanf(f,"%d",&perm[a][i]);
  fscanf(f,"%d",&NF); for(int i=0;i<NF;i++){ frm[i]=0; for(int j=0;j<8;j++){fscanf(f,"%d",&fr[i][j]); frm[i]|=((u128)1)<<fr[i][j];} fscanf(f,"%d",&fo[i]);}
  for(int i=0;i<104;i++) fscanf(f,"%d",&po[i]); fclose(f);
  for(int k=0;k<512;k++){hyp[k]=0; for(int t=0;t<104;t++) if(!dotb(k,lab[t])) hyp[k]|=((u128)1)<<t;}
  /* byte tables for perms */
  static u128 tab[400][13][256];
  for(int a=0;a<NA;a++) for(int b=0;b<13;b++) for(int v=0;v<256;v++){u128 x=0; for(int j=0;j<8;j++) if(v>>j&1){int t=b*8+j; if(t<104) x|=((u128)1)<<perm[a][t];} tab[a][b][v]=x;}
  FILE*g=fopen("lcs.bin","rb"); unsigned char d; uint64_t m0,m1; long nl=0; 
  u128 *reps=malloc(sizeof(u128)*5000000); long nr=0;
  while(fread(&d,1,1,g)==1){ fread(&m0,8,1,g); fread(&m1,8,1,g); u128 D=((u128)m1<<64)|m0; nl++;
    u128 best=D; for(int a=0;a<NA;a++){u128 x=0; for(int b=0;b<13;b++) x|=tab[a][b][(unsigned)((D>>(8*b))&255)]; if(x<best) best=x;}
    if(best==D) reps[nr++]=D; }
  fclose(g); fprintf(stderr,"label-closed %ld, orbit reps %ld\n",nl,nr);
  H=calloc(HS,sizeof(Ent));
  for(long r=0;r<nr;r++){ curD=reps[r]; currep=r; nD=0; for(int t=0;t<104;t++) if(curD>>t&1) Dlab[nD++]=lab[t];
    md=rankvecs(Dlab,nD,curM);
    int piv[9];
    for(int dd=0;dd<=md;dd++) for(int mask=0;mask<(1<<md);mask++){ if(__builtin_popcount(mask)!=dd) continue; int j=0; for(int c=md-1;c>=0;c--) if(mask>>c&1) piv[j++]=c; rec(dd,piv,0);} 
    if(r%2000==0) fprintf(stderr,"rep %ld/%ld profiles %ld\n",r,nr,nent);
  }
  FILE*o=fopen("profiles.txt","w"); FILE*rp=fopen("reps.txt","w");
  for(long r=0;r<nr;r++){ fprintf(rp,"%llu %llu\n",(unsigned long long)(reps[r]>>64),(unsigned long long)reps[r]); } fclose(rp);
  for(long h=0;h<HS;h++) if(H[h].cnt){ for(int i=0;i<24;i++) fprintf(o,"%d ",H[h].p[i]); fprintf(o,"| %ld %d %d",H[h].cnt,H[h].rep,H[h].kd); for(int i=0;i<H[h].kd;i++) fprintf(o," %d",H[h].kb[i]); fprintf(o,"\n"); }
  fclose(o); fprintf(stderr,"profiles %ld\n",nent); }
