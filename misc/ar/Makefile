CC ?= gcc
STATIC_LIB = libfoo.a
HIDDEN_DEPENDENCY = -lblas
TARGET = main

all: $(TARGET)

foo.o: foo.c
	$(CC) -c -o $@ $^

main.o: main.c
	$(CC) -c -o $@ $^

$(STATIC_LIB): foo.o
	ar --record-libdeps $(HIDDEN_DEPENDENCY) -rcs $@ $^

$(TARGET): main.o $(STATIC_LIB)
	# here the linker should automatically find the dependency of foo
	$(CC) -o $@ $^ -Wl,-plugin,/usr/lib/arm-linux-gnueabihf/bfd-plugins/libdep.so

.PHONY: clean
clean:
	rm -f foo.o main.o $(STATIC_LIB) $(TARGET)
