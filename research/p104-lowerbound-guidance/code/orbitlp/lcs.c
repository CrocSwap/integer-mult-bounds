/* ORBITLP lcs.c (own code): enumerate all subspaces of F2^9 (as 512-bit member sets via RREF bases),
   keep label-closed ones (span(L∩X)=X). Output: dim, 104-bit mask (two uint64) per subspace to lcs.bin */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
int lab[104]; int nl=0;
static int span_dim(int *v,int k,int *basis){ int piv[9]; memset(piv,0,sizeof piv); int r=0;
  for(int i=0;i<k;i++){int x=v[i]; for(int h=8;h>=0;h--) if(x>>h&1){ if(piv[h]) x^=piv[h]; else {piv[h]=x;r++;break;} } }
  if(basis){int j=0; for(int h=8;h>=0;h--) if(piv[h]) basis[j++]=piv[h];} return r; }
FILE *out; long cnt_all=0,cnt_lc=0; long bydim[10],lcbydim[10];
/* enumerate subspaces via reduced row echelon: choose pivot set, free entries */
void emit(int *B,int d){ cnt_all++; bydim[d]++;
  /* member set */ static unsigned char mem[512]; memset(mem,0,512);
  for(int s=0;s<(1<<d);s++){int x=0; for(int j=0;j<d;j++) if(s>>j&1) x^=B[j]; mem[x]=1;}
  uint64_t m0=0,m1=0; int in[104],k=0;
  for(int i=0;i<104;i++) if(mem[lab[i]]){ in[k++]=lab[i]; if(i<64) m0|=1ULL<<i; else m1|=1ULL<<(i-64);} 
  if(span_dim(in,k,NULL)==d){ cnt_lc++; lcbydim[d]++; unsigned char dd=d; fwrite(&dd,1,1,out); fwrite(&m0,8,1,out); fwrite(&m1,8,1,out);} }
void rec(int d,int *piv,int idx,int *B){ /* fill free bits of row idx */
  if(idx==d){ emit(B,d); return; }
  /* free positions: columns (bit positions) < piv[idx] that are not pivots */
  int freepos[9],nf=0; for(int c=piv[idx]-1;c>=0;c--){ int isp=0; for(int j=0;j<d;j++) if(piv[j]==c) isp=1; if(!isp) freepos[nf++]=c; }
  for(int s=0;s<(1<<nf);s++){ int x=1<<piv[idx]; for(int j=0;j<nf;j++) if(s>>j&1) x|=1<<freepos[j]; B[idx]=x; rec(d,piv,idx+1,B);} }
int main(){ FILE*f=fopen("<research-tree>/cards/WILD/LUNCH/exchange/d56dir/mod4/labels.txt","r");
  while(fscanf(f,"%d",&lab[nl])==1) nl++; fclose(f); out=fopen("lcs.bin","wb");
  int B[9],piv[9];
  for(int d=0; d<=9; d++){ /* choose pivot positions descending */
    for(int mask=0;mask<512;mask++){ if(__builtin_popcount(mask)!=d) continue; int j=0; for(int c=8;c>=0;c--) if(mask>>c&1) piv[j++]=c; rec(d,piv,0,B);} }
  fclose(out); printf("all %ld lc %ld\n",cnt_all,cnt_lc); for(int d=0;d<=9;d++) printf("d%d all %ld lc %ld\n",d,bydim[d],lcbydim[d]); }
