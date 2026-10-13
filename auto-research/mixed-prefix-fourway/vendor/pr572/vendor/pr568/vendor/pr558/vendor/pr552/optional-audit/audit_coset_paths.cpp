#include <bits/stdc++.h>
#include <boost/multiprecision/cpp_int.hpp>
using namespace std;using boost::multiprecision::cpp_int;
struct D{cpp_int n=0;int e=0;D(){}D(long long x):n(x){}void norm(){if(n==0){e=0;return;}cpp_int a=n<0?-n:n;int k=min(e,(int)boost::multiprecision::lsb(a));n>>=k;e-=k;}D mul(long long a,long long b)const{assert(b>0&&(b&(b-1))==0);D x=*this;x.n*=a;x.e+=__builtin_ctzll((unsigned long long)b);x.norm();return x;}D operator+(const D&b)const{D c;c.e=max(e,b.e);c.n=(n<<(c.e-e))+(b.n<<(c.e-b.e));c.norm();return c;}D operator-(const D&b)const{return *this+b.mul(-1,1);}bool operator==(const D&b)const{return n==b.n&&e==b.e;}};
struct Op{int kind,t,s;long long a,b;};int N,V;using Mat=vector<vector<D>>;
Op readop(istream&in){Op e;in>>e.kind>>e.t>>e.s>>e.a>>e.b;return e;}
Mat ident(){Mat x(N,vector<D>(N));for(int i=0;i<N;i++)x[i][i]=D(1);return x;}
void apply_gate(Mat&x,const Op&e){for(int j=0;j<N;j++){if(e.kind)x[e.t][j]=x[e.t][j].mul(e.a,e.b);else if(x[e.s][j].n!=0)x[e.t][j]=x[e.t][j]+x[e.s][j].mul(e.a,e.b);}}
int main(int argc,char**argv){ifstream in(argv[1]);int K,PN;in>>N>>V>>K>>PN;set<int>P;for(int i=0,r;i<PN;i++){in>>r;P.insert(r);}vector<Mat> results;for(int v=0;v<2;v++){int m;in>>m;Mat x=ident();for(int j=0;j<m;j++)apply_gate(x,readop(in));results.push_back(move(x));}
long long oldcold=0,newcold=0,diffcold=0,protectedentries=0;for(int t=V;t<2*V;t++)for(int j=0;j<N;j++){if(P.count(j)){assert(results[0][t][j]==results[1][t][j]);protectedentries++;}else{oldcold+=results[0][t][j].n!=0;newcold+=results[1][t][j].n!=0;diffcold+=!(results[0][t][j]==results[1][t][j]);}}
int ac;in>>ac;vector<Op> A(ac);for(auto&e:A)e=readop(in);long long exacterrors=0;
for(int k=0;k<K;k++){int index,m;in>>index;Op change=readop(in);in>>m;vector<D>expected(N);for(int j=0,c;j<m;j++){long long a,b;in>>c>>a>>b;expected[c]=D(1).mul(a,b);}Mat x=ident();for(int j=0;j<index;j++)apply_gate(x,A[j]);Op old=A[index];assert(old.kind==0&&change.kind==0&&old.t==change.t);
 for(int j=0;j<N;j++){D error=x[change.s][j].mul(change.a,change.b)-x[old.s][j].mul(old.a,old.b);assert(error==expected[j]);if(P.count(j))assert(error.n==0);exacterrors++;}A[index]=change;}
assert(oldcold-newcold==624);ofstream out(argv[2]);out<<"{\"status\":\"PASS_INDEPENDENT_DYADIC_BOUNDARY_PATH_AND_VERSION_ERRORS\",\"initial_columns\":"<<N<<",\"target_rows\":"<<V<<",\"protected_columns_including_targets\":"<<PN<<",\"protected_entries_checked\":"<<protectedentries<<",\"old_cold_response_nnz\":"<<oldcold<<",\"new_cold_response_nnz\":"<<newcold<<",\"cold_response_nnz_saved\":"<<oldcold-newcold<<",\"changed_cold_entries\":"<<diffcold<<",\"version_witnesses\":"<<K<<",\"exact_error_coefficients_checked\":"<<exacterrors<<",\"arithmetic\":\"independent cpp_int dyadics, no imported gk implementation\"}\n";cout<<"PASS protected "<<protectedentries<<" old "<<oldcold<<" new "<<newcold<<" witnesses "<<K<<endl;
}
