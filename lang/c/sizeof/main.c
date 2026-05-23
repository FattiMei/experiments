#include <stdio.h>
#include <stddef.h>
#include <stdint.h>


#define PRINT_SIZE(t) printf("%12s: %d\n", #t, sizeof(t))


int main(void) {
	PRINT_SIZE(char);
	PRINT_SIZE(short);
	PRINT_SIZE(int);
	PRINT_SIZE(long);
	PRINT_SIZE(long long);
	PRINT_SIZE(size_t);

	printf("\n");

	PRINT_SIZE(float);
	PRINT_SIZE(double);
	PRINT_SIZE(long double);

	printf("\n");

	PRINT_SIZE(int8_t);
	PRINT_SIZE(int16_t);
	PRINT_SIZE(int32_t);
	PRINT_SIZE(int64_t);

	return 0;
}
