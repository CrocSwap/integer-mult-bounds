#include <boost/multiprecision/cpp_int.hpp>
#include <iostream>
using I=boost::multiprecision::cpp_int;using Q=boost::multiprecision::cpp_rational;
Q sum(Q x,int n){Q t(1),s(1);for(int i=1;i<=n;i++){t*=x/Q(i);s+=t;}return s;}
int main(){Q a=sum(Q(5),6),b=sum(Q(4),7);Q x=Q(7)/2,t(1);for(int i=1;i<=17;i++)t*=x/Q(i);Q c=sum(x,16)+t/(Q(1)-x/Q(18));Q d=(Q(200)/Q(199)),der=(Q(101)/Q(100))*(7*5+6*4)-18*(Q(7)/Q(2));bool pass=a>100&&b>50&&c<(Q(100)/Q(3))&&d<(Q(101)/Q(100))&&der==(Q(-341)/Q(100));std::cout<<"e5 lower "<<a<<" >100\ne4 lower "<<b<<" >50\ne3.5 upper "<<c<<" <100/3\ne.005 upper "<<d<<" <101/100\nuniform derivative upper "<<der<<"\n";if(!pass)return 1;I left=1;for(int i=0;i<18;i++)left*=3;I right=1;for(int i=0;i<5;i++)right*=100;right*=64;if(left>=right)return 2;std::cout<<"PASS all exact rational sufficient inequalities; 3^18="<<left<<" <64*100^5="<<right<<"\n";}
