#include<stdbool.h>
#include<stdio.h>
const float pi = 3.14; 
const float e = 2.73; 

int x, y; 
char z[7]; 

int gcd(int* a, int* b){
	if(*b == 0){
		return *a; 
	}
	else{
		return gcd(&b, &(a % *b); 
	}
}

int main(int argc, char* argv[]){
	z[1] = 1; 
	scanf("%d%d", &x, &y); 
	printf("gcd(&x, &y): %d\n", gcd(&x, &y)); 
}
