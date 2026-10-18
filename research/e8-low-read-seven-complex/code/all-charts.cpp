// Exact projector charts derived from the actual candidate and baseline words.
// Prepared with substantial OpenAI Codex assistance; Apache-2.0.
#include <algorithm>
#include <cstddef>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>
#include <json.hpp>
#include <boost/multiprecision/cpp_int.hpp>
using namespace std;using J=nlohmann::json;using Q=boost::multiprecision::cpp_rational;using Z=boost::multiprecision::cpp_int;using M=vector<vector<Q>>;
J ld(string p){ifstream f(p);if(!f)throw runtime_error("missing "+p);J j;f>>j;return j;}
Q rat(J j){return j.is_string()?Q(j.get<string>()):Q(j.get<long long>());}M eye(int n){M a(n,vector<Q>(n));for(int i=0;i<n;i++)a[i][i]=1;return a;}M tr(M a){M b(a[0].size(),vector<Q>(a.size()));for(int i=0;i<a.size();i++)for(int j=0;j<a[0].size();j++)b[j][i]=a[i][j];return b;}M mul(M a,M b){M c(a.size(),vector<Q>(b[0].size()));for(int i=0;i<a.size();i++)for(int k=0;k<b.size();k++)if(a[i][k]!=0)for(int j=0;j<b[0].size();j++)c[i][j]+=a[i][k]*b[k][j];return c;}
Z maxnum=1,maxden=1;void admit(Q q){Z n=abs(numerator(q)),d=denominator(q);maxnum=max(maxnum,n);maxden=max(maxden,d);if(n>=(Z(1)<<80)||d>=(Z(1)<<80))throw runtime_error("finite prime guard exceeded");}
M inverse(M a,int &ops,Q &det){int n=a.size();M b=eye(n);det=1;ops=0;for(int k=0;k<n;k++){int t=k;while(t<n&&a[t][k]==0)t++;if(t==n)throw runtime_error("singular");if(t!=k){swap(a[k],a[t]);swap(b[k],b[t]);det=-det;ops++;}Q p=a[k][k];admit(p);det*=p;if(p!=1){ops++;for(int j=0;j<n;j++){a[k][j]/=p;b[k][j]/=p;admit(a[k][j]);admit(b[k][j]);}}for(int i=0;i<n;i++)if(i!=k&&a[i][k]!=0){ops++;Q c=a[i][k];admit(c);for(int j=0;j<n;j++){a[i][j]-=c*a[k][j];b[i][j]-=c*b[k][j];admit(a[i][j]);admit(b[i][j]);}}}if(a!=eye(n))throw runtime_error("inverse failure");return b;}
M nullspace(M a){int n=a[0].size(),row=0;vector<int>piv;for(int col=0;col<n&&row<a.size();col++){int t=row;while(t<a.size()&&a[t][col]==0)t++;if(t==a.size())continue;swap(a[row],a[t]);Q p=a[row][col];admit(p);for(auto &q:a[row]){q/=p;admit(q);}for(int i=0;i<a.size();i++)if(i!=row){Q c=a[i][col];for(int j=0;j<n;j++)a[i][j]-=c*a[row][j];}piv.push_back(col);row++;}if(row!=a.size())throw runtime_error("basis rank failure");M out;for(int free=0;free<n;free++)if(find(piv.begin(),piv.end(),free)==piv.end()){vector<Q>v(n);v[free]=1;for(int i=0;i<row;i++)v[piv[i]]=-a[i][free];out.push_back(v);}return out;}
J mj(M a){J out=J::array();for(auto r:a){J z=J::array();for(Q q:r)z.push_back(q.str());out.push_back(z);}return out;}

M sub(M a,M b){for(int i=0;i<a.size();i++)for(int j=0;j<a[i].size();j++)a[i][j]-=b[i][j];return a;}
M independent_columns(M a){int m=a.size(),n=a[0].size(),row=0;vector<int> piv;M copy=a;for(int c=0;c<n&&row<m;c++){int k=row;while(k<m&&a[k][c]==0)k++;if(k==m)continue;swap(a[k],a[row]);Q p=a[row][c];for(int j=c;j<n;j++)a[row][j]/=p;for(int i=row+1;i<m;i++){Q b=a[i][c];for(int j=c;j<n;j++)a[i][j]-=b*a[row][j];}piv.push_back(c);row++;}M out(m);for(int i=0;i<m;i++)for(int c:piv)out[i].push_back(copy[i][c]);return out;}
M kernel_general(M a){int m=a.size(),n=a[0].size(),row=0;vector<int>piv;for(int col=0;col<n&&row<m;col++){int t=row;while(t<m&&a[t][col]==0)t++;if(t==m)continue;swap(a[row],a[t]);Q p=a[row][col];for(auto&q:a[row])q/=p;for(int i=0;i<m;i++)if(i!=row){Q c=a[i][col];for(int j=0;j<n;j++)a[i][j]-=c*a[row][j];}piv.push_back(col);row++;}M out;for(int free=0;free<n;free++)if(find(piv.begin(),piv.end(),free)==piv.end()){vector<Q>v(n);v[free]=1;for(int i=0;i<row;i++)v[piv[i]]=-a[i][free];out.push_back(v);}return out;}
// All E8 charts, not just changes against a paired-cube baseline. Derived from
// the Codex-assisted chart admission; E8 family/word: Jacob Sussman/Dylan Crow,
// with Anthropic Claude assistance. Geometry only, no signed decoder claim.
struct Ev {int op,a,b,c,r,z;};
int main(int argc,char**argv) {
 if(argc!=3)throw runtime_error("usage RECORD_DIR OUTPUT_DIR");
 string rd=argv[1],out=argv[2];J fs=ld(rd+"/frames.json")["frames"],st=ld(rd+"/249-states.json");
 int h=st["h"];if(h!=8)throw runtime_error("E8 dimension");M G=eye(h);for(int i=0;i<h;i++)G[i][i]=Q(1)/2;
 map<int,M>ps;int framecount=0;
 for(auto it=fs.begin();it!=fs.end();it++) {
  int f=stoi(it.key()),d=it.value()["dim"];M P;
  if(!d)P=M(h,vector<Q>(h));else if(d==h)P=eye(h);else {
   M B;for(auto row:it.value()["B"]){vector<Q>r;for(auto x:row)r.push_back(rat(x));B.push_back(r);}
   int ops;Q det;M BG=mul(B,G),GI=inverse(mul(BG,tr(B)),ops,det);P=mul(mul(tr(B),GI),BG);
  }
  Q trace=0;for(int i=0;i<h;i++)trace+=P[i][i];
  if(mul(P,P)!=P||mul(tr(P),G)!=mul(G,P)||trace!=d)throw runtime_error("frame projector");
  ps[f]=P;framecount++;
 }
 ifstream input(rd+"/249-records.bin",ios::binary|ios::ate);if(!input)throw runtime_error("raw");auto bytes=input.tellg();if(bytes%sizeof(Ev))throw runtime_error("raw shape");vector<Ev>events(bytes/sizeof(Ev));input.seekg(0);input.read((char*)events.data(),bytes);
 set<tuple<int,int,int>>pairs;long long occurrences=0;int nc=0;
 for(auto e:events){if(e.op==0&&e.r){pairs.insert({e.b,e.c,e.r});occurrences++;}else if(e.op==2){nc++;pairs.insert({st["ZERO"].get<int>(),e.c,e.z});}}
 J charts=J::array();int maximum=0,checked=0;
 for(auto [before,after,r]:pairs) {
  M E=sub(ps.at(after),ps.at(before));
  if(mul(ps.at(before),ps.at(after))!=ps.at(before)||mul(E,E)!=E)throw runtime_error("nested projector");
  M C=independent_columns(E);if(C[0].size()!=r)throw runtime_error("rank");M K=kernel_general(E);if(K.size()!=h-r)throw runtime_error("kernel");
  for(int i=0;i<h;i++)for(auto&v:K)C[i].push_back(v[i]);int ops;Q det;M CI=inverse(C,ops,det),D=eye(h);for(int i=r;i<h;i++)D[i][i]=0;
  if(mul(mul(CI,E),C)!=D||mul(C,CI)!=eye(h))throw runtime_error("chart");
  // The inverse complemented ledger uses (I-P_before)-(I-P_after), exactly E.
  if(sub(sub(eye(h),ps.at(before)),sub(eye(h),ps.at(after)))!=E)throw runtime_error("reflected gap");
  for(auto M0:{C,CI,E})for(auto row:M0)for(auto q:row)admit(q);
  maximum=max(maximum,ops);charts.push_back({{"before",before},{"after",after},{"rank",r},{"basis",mj(C)},{"inverse",mj(CI)},{"factors",ops},{"determinant",det.str()}});checked++;
 }
 // A zero entrance and full exit give the identity bank chart, independently
 // of the more expensive charts used for individual local MOVEs.
 for(int r=2*st["v"].get<int>();r<st["n"].get<int>();r++){
  int first=st["initial"][to_string(r)],last=st["final"][to_string(r)];
  if(ps.at(first)!=M(h,vector<Q>(h))||ps.at(last)!=eye(h))throw runtime_error("nonidentity bank chart");
 }
 J receipt={{"status","PASS_ALL_E8_MOVE_COPY_PROJECTORS_AND_REFLECTED_CHARTS"},{"all_frame_projectors",framecount},{"unique_move_copy_gaps",checked},{"positive_move_occurrences",occurrences},{"copies",nc},{"max_chart_factors",maximum},{"max_numerator",maxnum.str()},{"max_denominator",maxden.str()},{"helper_endpoint_chart","identity"},{"helper_endpoint_chart_factors",0},{"both_reflected_gaps_exact",true},{"scope","Actual rational chart identities and all intermediate finite bounds; scalar decoder and physical source lowering are separate."}};
 ofstream(out+"/ALL-CHARTS.json")<<charts.dump()<<endl;ofstream(out+"/CHART-RECEIPT.json")<<receipt.dump(2)<<endl;cout<<receipt.dump(2)<<endl;
}
