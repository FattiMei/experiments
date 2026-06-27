STATIC_LIB = libfoo.a
HIDDEN_DEPENDENCY = -lblas

all: main

foo.o: foo.c
	gcc -c -o $@ $^

main.o: main.c
	gcc -c -o $@ $^

$(STATIC_LIB): foo.o
	ar --record-libdeps $(HIDDEN_DEPENDENCY) -rcs $@ $^

main: main.o $(STATIC_LIB)
	# here the linker should automatically find the dependency of foo
	gcc -o $@ $^ -L. -lfoo -Wl,-plugin,/usr/lib/arm-linux-gnueabihf/bfd-plugins/libdep.so

.PHONY: clean
clean:
	rm foo.o main.o $(STATIC_LIB)
