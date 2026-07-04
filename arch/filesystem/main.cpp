#include <chrono>
#include <cstdio>
#include <iomanip>
#include <iostream>


// this replicates `padded_string::load` from simdjson/simdjson
long get_file_size_bytes(std::FILE* fp) {
	const long cur { std::ftell(fp) };
	std::fseek(fp, 0, SEEK_END);
	const long size_bytes { std::ftell(fp) };
	std::fseek(fp, 0, cur);

	return size_bytes;
}


inline char compute_checksum(const std::size_t n, const char buf[]) {
	char acc { 0 };

	for (std::size_t i { 0 }; i < n; ++i) {
		acc ^= buf[i];
	}

	return acc;
}


#define TIME_STMT(stmt) [&]() { \
	const auto start_time = std::chrono::high_resolution_clock::now(); \
	const auto result = stmt;                                          \
	const auto end_time = std::chrono::high_resolution_clock::now();   \
                                                                           \
        const std::chrono::duration<double> delta = end_time-start_time;   \
	return std::make_pair(delta, result);                              \
}()


int main(int argc, char* argv[]) {
	using DeltaT = std::chrono::duration<double>;

	if (argc != 3) {
		std::cout << "Invalid command line arguments" << std::endl;
		std::cout << "Usage: program file batchsize_kb (<= 0 if no batching)" << std::endl;
		return 1;
	}

	const char* filename { argv[1] };
	const auto requested_batch_size_kb = std::atoi(argv[2]);

	auto [time_fopen, fp] = TIME_STMT(std::fopen(filename, "rb"));
	if (fp == NULL) {
		std::cerr << "Could not open `" << filename << "`\n";
		return 1;
	}

	const auto batch_size {
		requested_batch_size_kb > 0 ? (1024*requested_batch_size_kb) : get_file_size_bytes(fp)
	};

	auto [time_malloc, buf] = TIME_STMT(new char[batch_size]);
	if (buf == NULL) {
		std::cerr << "Malloc of size " << batch_size << " failed\n";
		return 1;
	}

	std::size_t size_bytes { 0 };
	char checksum { 0 };

	DeltaT time_fread{};
	DeltaT time_sweep{};
	while (true) {
		const auto [time_fread_contrib, bytes_read] = TIME_STMT(
			std::fread(buf, 1, batch_size, fp)
		);

		if (bytes_read > 0) {
			// if it has read something, it's considered a valid read
			time_fread += time_fread_contrib;

			const auto [time_sweep_contrib, _] = TIME_STMT(
				compute_checksum(bytes_read, buf)
			);

			size_bytes += bytes_read;
			time_sweep += time_sweep_contrib;
		} else {
			break;
		}
	}

	delete[] buf;
	const int checksum_int { checksum };

	std::cout << std::fixed << std::setprecision(9);

	std::cout
		<< "file_name,size_bytes,checksum,batch_size,time_malloc_s,time_fopen_s,time_fread_s,time_sweep_s\n"
		<< filename            << ','
		<< size_bytes          << ','
		<< checksum_int        << ','
		<< batch_size          << ','
		<< time_malloc.count() << ','
		<< time_fopen.count()  << ','
		<< time_fread.count()  << ','
		<< time_sweep.count()  << std::endl;

	return 0;
}
