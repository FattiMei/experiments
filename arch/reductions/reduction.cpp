#include <cmath>
#include <chrono>
#include <random>
#include <vector>
#include <cassert>
#include <iostream>
#include <algorithm>


#define DTYPE int32_t


DTYPE reduce_xor(DTYPE *xs, std::size_t n) {
	DTYPE acc = 0;

	for (std::size_t i = 0; i < n; ++i) {
		acc = acc ^ xs[i];
	}

	return acc;
}


// This program assumes that the variables:
//   * NPOINTS (int)
//   * MIN_EXPONENT (int)
//   * MAX_EXPONENT (int)
//   * DISABLE_VECTORIZATION (int)
//   * SHUFFLE_ITERATIONS (int)
//
// have already been defined via preprocessor DEFINES


int main(void) {
	// first we fill the buffer size elements because we may need to shuffle it
	std::vector<std::size_t> buffer_size_bytes(NPOINTS);
	for (int i = 0; i < NPOINTS; ++i) {
		// this should implement a linspace
		const double exp =
			MIN_EXPONENT + i * (MAX_EXPONENT - MIN_EXPONENT) / (NPOINTS-1.0);

		assert(MIN_EXPONENT <= exp);
		assert(exp <= MAX_EXPONENT);

		const int bufsize = static_cast<int>(
			std::pow(2.0, exp)
		);

		const double padding = (sizeof(DTYPE) - (bufsize % sizeof(DTYPE))) % sizeof(DTYPE);

		buffer_size_bytes[i] = bufsize + padding;
		assert(buffer_size_bytes[i] % sizeof(DTYPE) == 0);
	}
	const auto max_buffer_size_bytes = buffer_size_bytes.back();
	const auto max_buffer_elements = max_buffer_size_bytes / sizeof(DTYPE);

	std::random_device rd;
	std::mt19937 mersenne_engine { rd() };

	if (SHUFFLE_ITERATIONS) {
		std::shuffle(buffer_size_bytes.begin(), buffer_size_bytes.end(), mersenne_engine);
	}

	// heap allocation of a buffer of suitable size
	std::vector<DTYPE> xs(max_buffer_elements);
	std::uniform_int_distribution<DTYPE> dist { 0, 1000 };
	auto gen = [&]() { return dist(mersenne_engine); };
	std::generate(xs.begin(), xs.end(), gen);

	std::cout << "# NPOINTS = "               << NPOINTS               << '\n'
	          << "# MIN_EXPONENT = "          << MIN_EXPONENT          << '\n'
	          << "# MAX_EXPONENT = "          << MAX_EXPONENT          << '\n'
	          << "# DISABLE_VECTORIZATION = " << DISABLE_VECTORIZATION << '\n'
	          << "# SHUFFLE_ITERATIONS = "    << SHUFFLE_ITERATIONS    << '\n'
	          << "buffer_size_bytes,runtime_s,res" << std::endl;

	for (const auto bufsize_bytes : buffer_size_bytes) {
		const auto n = bufsize_bytes / sizeof(DTYPE);
		assert(n > 0);
		assert(n <= max_buffer_elements);

		const auto start_time = std::chrono::steady_clock::now();
		const auto res = reduce_xor(xs.data(), n);
		const auto end_time = std::chrono::steady_clock::now();

		const std::chrono::duration<double> runtime = end_time - start_time;
		const double runtime_s = runtime.count();

		// we need to explicitly print res, otherwise the DCE will remove it
		std::cout << bufsize_bytes << ',' << runtime_s << ',' << res << std::endl;
	}

	return 0;
}

