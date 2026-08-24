CXX = g++
STD = -std=c++20
OPT = -O2 -march=native

all: ilp_signed ilp_signed.s ilp_unsigned ilp_unsigned.s

ilp_signed: ilp.cpp
	$(CXX) -o $@ $^ $(OPT) $(STD) -DIntT=int32_t

ilp_signed.s: ilp_signed
	objdump -d $^ > $@

ilp_unsigned: ilp.cpp
	$(CXX) -o $@ $^ $(OPT) $(STD) -DIntT=uint32_t

ilp_unsigned.s: ilp_unsigned
	objdump -d $^ > $@


