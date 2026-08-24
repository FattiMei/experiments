#include <chrono>
#include <format>
#include <iostream>


#ifndef IntT
#define IntT int32_t
#endif


template <typename T>
std::pair<T,T>
__attribute__ ((noinline))
solution_strict(T val) {
	T x, y;

	int i = 0;
	while (true) {
		if (i % 2 == 0) {
			y = val;
			x = (2021*y + 2020) / 2020;

			if (2020*y > 2019*x) {
				break;
			} else {
				val = x;
			}
		} else {
			x = val;
			y = (2019*x + 2020) / 2020;

			if (2021*y < 2020*x) {
				break;
			} else {
				val = y;
			}
		}

		++i;
	}

	return std::make_pair(x,y);
}

int main() {
	const auto start_time = std::chrono::steady_clock::now();
	const auto [x, y] = solution_strict<IntT>(1);
	const auto end_time = std::chrono::steady_clock::now();
	const std::chrono::duration<double> solve_time = end_time - start_time;

	std::cout << std::format("x = [{}, {}]", x, y) << std::endl;
	std::cout << std::format("solve time = {}", solve_time.count()) << std::endl;

	return 0;
}
