#include<stdio.h>
void swap(int *m, int *n){
    int temp;
    temp = *m;
    *m = *n;
    *n = temp;
    printf("m=%d,n=%d\n",m,n);
    printf("m=%d,n=%d\n",*m,*n);
}
int main(){
    int a, b;
    a = 2;
    b = 3;
    printf("交换前：a=%d,b=%d\n",&a,&b);
    swap(&a, &b);
    printf("交换后：a=%d,b=%d\n",a,b);
    printf("交换后：a=%d,b=%d\n",&a,&b);
}