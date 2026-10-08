// New RaD negative-basis complete source pair certificate.
// Exhaustive fallback structure credited to Rohan Arun PR40 e3bf3ab0cb1ec48588e279b31a97e7a49c72f99e.
// Apache-2.0; inherited credits PR34 James Chang, PR32/36 icekylinx, PR37/39 and prior authors.
// Complete both-I+J data-prefix witness. Each pair is replayed from scratch
// at a fallback prime if a primary modular pivot vanishes. Such a vanishing
// alone is never treated as a rational zero. Universal zeros are inherited.
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <vector>
using namespace std;
constexpr int a=23,b=25,d=a+b-1;
using Triple=array<int,3>;
struct Result {bool pass;int row,col,det;int64_t zeros;};
template<int q> int mul(int x,int y){return int(int64_t(x)*y%q);}
template<int q> int power(int x,int n){int z=1;for(;n;n>>=1,x=mul<q>(x,x))if(n&1)z=mul<q>(z,x);return z;}
bool prime(int q){if(q<2)return false;for(int i=2;int64_t(i)*i<=q;i++)if(q%i==0)return false;return true;}
vector<int> R,C,piv;
template<int q> Result replay(const Triple&T,const Triple&S){
 const int xa=mul<q>(a+3,power<q>(a-1,q-2)),xb=q-mul<q>(a+3,power<q>(2,q-2));
 const int ya=mul<q>(b+3,power<q>(b-1,q-2)),yb=q-mul<q>(b+3,power<q>(2,q-2));
 int xs[a],ys[b],M[d][d];bool available[d];
 for(int i=0;i<a;i++)xs[i]=(i==T[0]||i==T[1]||i==T[2])?xa:xb;
 for(int i=0;i<b;i++)ys[i]=(i==S[0]||i==S[1]||i==S[2])?ya:yb;
 for(int i=0;i<d;i++){available[i]=true;for(int j=0;j<d;j++){
  int64_t z=q-1;if(R[i]==C[j])z+=xs[R[i]];if(i%b==(a*b-d+j)%b)z+=ys[i%b];M[i][j]=int(z%q);
 }}
 int determinant=1;int64_t zeros=0;
 for(int i=0;i<d;i++){
  int c=piv[i],value=M[i][c];if(!available[c]||!value)return {false,i,c,0,zeros};
  for(int j=c+1;j<d;j++)if(available[j]){if(M[i][j]){cerr<<"Fatal ordered zero identity failed\n";exit(2);}zeros++;}
  determinant=mul<q>(determinant,value);available[c]=false;int inverse=power<q>(value,q-2);
  for(int r=i+1;r<d;r++)if(M[r][c]){
   int ratio=mul<q>(M[r][c],inverse);
   for(int j=0;j<d;j++)if(available[j]&&M[i][j]){int z=M[r][j]-mul<q>(ratio,M[i][j]);M[r][j]=z<0?z+q:z;}
   M[r][c]=0;
  }
 }
 return {true,-1,-1,determinant,zeros};
}
int main(){
 const array<int,3> primes={1000003,2147483647,1000000007};
 for(int p:primes){if(!prime(p))return 10;for(int den:{2,22,24,26,28})if(den%p==0)return 11;}
 for(int i=0;i<a;i++)R.push_back(i),C.push_back(i);R.push_back(a-1);C.push_back(0);
 for(int i=0;i<a;i++)R.push_back(i),C.push_back(i);
 piv.push_back(2*a);for(int i=1;i<a-1;i++)piv.push_back(i+a+1);
 for(int i=a-1;i<a+5;i++)piv.push_back(2*a-i);
 for(int i=a+5;i<2*a-1;i++)piv.push_back(i-a-3);piv.push_back(1);piv.push_back(0);
 vector<Triple> left,right;for(int i=0;i<a;i++)for(int j=i+1;j<a;j++)for(int k=j+1;k<a;k++)left.push_back({i,j,k});
 for(int i=0;i<b;i++)for(int j=i+1;j<b;j++)for(int k=j+1;k<b;k++)right.push_back({i,j,k});
 struct Fallback {Triple left,right;int index,row,col,prime;};vector<Fallback> fallbacks;
 int count=0;array<int,3> success={0,0,0};int64_t prefixes=0,zeros=0;vector<Fallback> failures;int64_t verified_first21=0;
 for(const auto&T:left)for(const auto&S:right){
  auto first=replay<1000003>(T,S);auto result=first;int chosen=0;
  if(!result.pass){result=replay<2147483647>(T,S);chosen=1;}
  if(!result.pass){result=replay<1000000007>(T,S);chosen=2;}
  if(!result.pass){failures.push_back({T,S,count,result.row,result.col,primes[chosen]});if(result.row>=22)verified_first21++;count++;continue;}
  if(chosen)fallbacks.push_back({T,S,count,first.row,first.col,primes[chosen]});
  count++;success[chosen]++;prefixes+=d;zeros+=result.zeros;
  if(count%230000==0)cerr<<"Completed "<<count<<" actual pairs, "<<fallbacks.size()<<" complete fallback replays\n";
 }
 if(count!=1771*2300||prefixes!=int64_t(count-failures.size())*d||zeros!=int64_t(count-failures.size())*346)return 12;
 cout<<"{\"status\":\"COMPLETE ACTUAL-PAIR EXPECTED-PROFILE CLASSIFICATION\",\"dimensions\":[23,25],\"primes\":[1000003,2147483647,1000000007],\"primality_trial_division\":true,\"denominators\":[2,22,24,26,28],\"left_triples\":"<<left.size()<<",\"right_triples\":"<<right.size()<<",\"pairs\":"<<count<<",\"nonzero_prefixes\":"<<prefixes<<",\"ordered_zero_checks\":"<<zeros<<",\"unresolved_failures\":"<<failures.size()<<",\"late_failures_with_verified21_block\":"<<verified_first21<<",\"primary_modular_failures\":"<<fallbacks.size()<<",\"successful_pairs_by_prime\":["<<success[0]<<","<<success[1]<<","<<success[2]<<"],\"fallbacks\":[";
 for(size_t i=0;i<fallbacks.size();i++){auto f=fallbacks[i];if(i)cout<<",";cout<<"{\"index\":"<<f.index<<",\"left\":["<<f.left[0]<<","<<f.left[1]<<","<<f.left[2]<<"],\"right\":["<<f.right[0]<<","<<f.right[1]<<","<<f.right[2]<<"],\"primary_zero\":["<<f.row<<","<<f.col<<"],\"successful_prime\":"<<f.prime<<"}";}
 cout<<"],\"failures\":[";for(size_t i=0;i<failures.size();i++){auto f=failures[i];if(i)cout<<",";cout<<"{\"index\":"<<f.index<<",\"left\":["<<f.left[0]<<","<<f.left[1]<<","<<f.left[2]<<"],\"right\":["<<f.right[0]<<","<<f.right[1]<<","<<f.right[2]<<"],\"failed_step\":["<<f.row<<","<<f.col<<"],\"witness_prime_for_earlier_prefixes\":"<<f.prime<<"}";}cout<<"]}\n";
}
