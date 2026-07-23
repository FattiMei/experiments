#include <cmath>
#include <chrono>
#include <random>
#include <iostream>


/*
 * Returns the time in seconds for `n` generations from `dist`
 * Designed to accept any combination of distribution + rng
 */
template <class Distribution, class UniformRNG>
double
run(Distribution& dist, UniformRNG& rng, int64_t n) {
	const auto t_start = std::chrono::steady_clock::now();
	for (; n; --n) {
		// this has side effects, so the compiler must keep it
		dist(rng);
	}
	const auto t_end = std::chrono::steady_clock::now();

	const std::chrono::duration<double> delta = t_end - t_start;
	return delta.count();
}


template <class Distribution, class UniformRNG>
void profile_generation(const std::size_t nruns, const double target_time_per_run_s = 1.0) {
	Distribution dist;
	UniformRNG rng;

	int64_t target_iterations = 100;
	double time_s = run(dist, rng, target_iterations);

	for (auto i = 0; i < nruns; ++i) {
		// use the previously measured time to update the number of iterations
		target_iterations = static_cast<int64_t>(std::ceil(target_time_per_run_s / time_s));
		time_s = run(dist, rng, target_iterations);
	}
}


int main(void) {
	std::cout << "dist,rng,nit,time_s" << std::endl;
	return 0;
}
