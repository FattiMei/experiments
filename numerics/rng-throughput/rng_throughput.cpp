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


struct DataPoint {
	int64_t n_iterations;
	double time_s;
};


template <class Distribution, class UniformRNG>
void profile_generation(
		const std::size_t nruns,
		DataPoint output_data[],
		const std::size_t trial_runs = 1000,
		const double target_time_per_run_s = 1.0) {

	Distribution dist;
	UniformRNG rng;

	int64_t target_iterations = trial_runs;
	double time_s = run(dist, rng, target_iterations);

	for (std::size_t i = 0; i < nruns; ++i) {
		// use the previously measured time to update the number of iterations
		target_iterations = static_cast<int64_t>(
				target_iterations * target_time_per_run_s / time_s);
		time_s = run(dist, rng, target_iterations);

		output_data[i] = {target_iterations, time_s};
	}
}


int main(int argc, char* argv[]) {
	std::size_t nruns = 1;

	if (argc == 2) {
		nruns = std::atoi(argv[1]);
	} else if (argc > 2) {
		std::cerr
			<< "Invalid number of arguments" << '\n'
			<< "Usage: gen [nruns: int = 1]" << std::endl;
		return 1;
	}

	DataPoint* output_data = new DataPoint[nruns];
	if (output_data == NULL) {
		std::cerr
			<< "Allocation of " << nruns << " data points failed"
			<< std::endl;
		return 1;
	}

	std::cout << "dist,rng,nit,time_s" << std::endl;

#define PROFILE_GENERATION(dist, rng) do {                                     \
	profile_generation<dist, rng>(nruns, output_data);                     \
	for (std::size_t i = 0; i < nruns; ++i) {                              \
		std::cout                                                      \
			<< #dist << ','                                        \
			<< #rng  << ','                                        \
			<< output_data[i].n_iterations << ','                  \
			<< output_data[i].time_s << std::endl;                 \
	}                                                                      \
} while (0)

	// we need to solve the problem of iterating over the cartesian product
	// of the distribution set and the rng set
	//
	// suggested solutions involved C++ features that I don't understand
	// instead of wrapping my mind around complications for such simple
	// task, I decided to write by hand the combinations.
	//
	// The writing cost is paid once, but it pays off the more you read it
	// This could been avoided in languages where:
	//   * types are first-class objects (zig)
	//   * there is JIT compilation (julia)
	using namespace std;
	PROFILE_GENERATION(normal_distribution<double>      , minstd_rand0 );
	PROFILE_GENERATION(normal_distribution<double>      , minstd_rand  );
	PROFILE_GENERATION(normal_distribution<double>      , mt19937      );
	PROFILE_GENERATION(normal_distribution<double>      , mt19937_64   );
	PROFILE_GENERATION(normal_distribution<double>      , ranlux24_base);
	PROFILE_GENERATION(normal_distribution<double>      , ranlux48_base);
	PROFILE_GENERATION(normal_distribution<double>      , ranlux24     );
	PROFILE_GENERATION(normal_distribution<double>      , ranlux48     );
	PROFILE_GENERATION(normal_distribution<double>      , knuth_b      );
	PROFILE_GENERATION(uniform_real_distribution<double>, minstd_rand0 );
	PROFILE_GENERATION(uniform_real_distribution<double>, minstd_rand  );
	PROFILE_GENERATION(uniform_real_distribution<double>, mt19937      );
	PROFILE_GENERATION(uniform_real_distribution<double>, mt19937_64   );
	PROFILE_GENERATION(uniform_real_distribution<double>, ranlux24_base);
	PROFILE_GENERATION(uniform_real_distribution<double>, ranlux48_base);
	PROFILE_GENERATION(uniform_real_distribution<double>, ranlux24     );
	PROFILE_GENERATION(uniform_real_distribution<double>, ranlux48     );
	PROFILE_GENERATION(uniform_real_distribution<double>, knuth_b      );

	delete[] output_data;

	return 0;
}
