#include <cblas.h>

int foo() {
	return (int) cblas_sdsdot(0, 0.0, NULL, 0, NULL, 0);
}
