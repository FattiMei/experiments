#include <math.h>
#include <stdio.h>


int cache[10];


void set_cache() {
	cache[0] = 0;

	for (int i = 1; i < 10; ++i) {
		cache[i] = pow(i,i);
	}
}


void print_cache() {
	for (int i = 0; i < 10; ++i) {
		printf("%d ", cache[i]);
	}

	printf("\n");
}


int is_munchhausen(const int number) {
	int n = number;
	int total = 0;

	while (n > 0) {
		const int digit = n % 10;
		total += cache[digit];

		if (total > n) {
			return 0;
		}

		n = n / 10;
	}

	return total == n;
}


#define NMAX 440000000


int main(void) {
	set_cache();
	print_cache();

	for (int i = 0; i < NMAX; ++i) {
		if (is_munchhausen(i)) {
			printf("%d\n", i);
		}
	}

	return 0;
}
