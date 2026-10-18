import numpy as np


PRIME1 = np.uint32(0x9E3779B1)
PRIME2 = np.uint32(0x85EBCA77)
PRIME3 = np.uint32(0xC2B2AE3D)
PRIME4 = np.uint32(0x27D4EB2F)
PRIME5 = np.uint32(0x165667B1)


def rol(x, p):
    """
    This implementation has been designed to work with
    both numpy scalars and array inputs
    """
    return np.bitwise_left_shift(x, p) | np.bitwise_right_shift(x, 32-p)


def xxhash(x: np.array, seed: np.uint32 = np.uint32(0)) -> np.uint32:
    # this is just wrapper code for supporting strings
    if isinstance(x, str):
        buffer = bytes(x, encoding='utf-8')
        x = np.frombuffer(buffer, dtype=np.int8)

    x = x.view(np.uint8).reshape(-1)
    n = x.shape[0]
    h32 = np.uint32(n)

    # the input is partitioned into 3 sections:
    #   1. blocks of 16 bytes
    #   2. the remainder in blocks of 4 bytes
    #   3. the remainder in blocks of 1 bytes
    n1 = n - n%16
    n2 = n - n%4

    blocks_of_16 = x[0:n1].view(np.uint32).reshape(-1,4)
    blocks_of_4  = x[n1:n2].view(np.uint32)
    blocks_of_1  = x[n2:]

    if blocks_of_16.size == 0:
        h32 += seed + PRIME5
    else:
        v = np.array([
            seed + PRIME1 + PRIME2,
            seed + PRIME2,
            seed,
            seed - PRIME1
        ], dtype=np.uint32)

        for line in blocks_of_16:
            v = v + line * PRIME2
            v = rol(v, 13)
            v = v * PRIME1

        h32 += rol(v[0], 1) + rol(v[1], 7) + rol(v[2], 12) + rol(v[3], 18)

    for i32 in blocks_of_4:
        h32 += i32 * PRIME3
        h32 = rol(h32, 17) * PRIME4

    for i8 in blocks_of_1:
        h32 += np.uint32(i8) * PRIME5
        h32 = rol(h32, 11) * PRIME1

    h32 ^= np.right_shift(h32, 15)
    h32 *= PRIME2
    h32 ^= np.right_shift(h32, 13)
    h32 *= PRIME3
    h32 ^= np.right_shift(h32, 16)

    return h32


# only for debugging purposes
def compute_chunk_cos(chunk_number: int, CHUNK_SIZE: int):
    offset = chunk_number * CHUNK_SIZE
    integer_range = np.arange(offset, offset+CHUNK_SIZE, dtype=np.uint32)
    transmuted_range = integer_range.view(np.float32)

    return np.cos(transmuted_range)


def compute_chunk_hash(chunk_number: int, CHUNK_SIZE: int):
    offset = chunk_number * CHUNK_SIZE
    integer_range = np.arange(offset, offset+CHUNK_SIZE, dtype=np.uint32)
    transmuted_range = integer_range.view(np.float32)

    return xxhash(np.cos(transmuted_range))


CHUNK_SIZE = 2**10
CHUNK_NUMBER = 2**32 // CHUNK_SIZE


if __name__ == '__main__':
    print(f'# {CHUNK_SIZE = }')
    for i in range(CHUNK_NUMBER):
        hash = compute_chunk_hash(i, CHUNK_SIZE)
        print(f'{i},{hex(hash)}')
