#include<stdbool.h>
#include<stdio.h>

int x, y; 

int gcd(int a, int b){
	if(b == 0){
		return a; 
	}
	else{
		return gcd(b, a % b); 
	}
}

int main(int argc, char* argv[]){
	scanf("%d%d", &x, &y); 
	printf("%d\n", gcd(x, y)); 
}
