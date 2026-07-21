import numpy as np
from numpy.random import Generator, MT19937, SeedSequence
import mpmath
import matplotlib.pyplot as plt


def ctz_mantissa(x) -> int:
    """
    Counts trailing zeros of the mantissa of a floating point number.
    Supports `np.float32` and `np.float64` types.

    Assumes that the mantissa bits are the least significant ones.
    True as of IEEE 754
    """
    nmant = np.finfo(x.dtype).nmant
    int_dtype = f'u{x.itemsize}'
    raw_bits = x.view(int_dtype)

    count = 0
    for i in range(nmant):
        lsb = raw_bits % 2
        if lsb == 0:
            count = count + 1
            raw_bits = raw_bits // 2
        else:
            break

    return count


def sample_cancellation_errors(loc:   float,
                               scale: float,
                               seeds,
                               sample_sizes,
                               var_impl,
                               ref_impl):

    err = np.empty((len(seeds), len(sample_sizes)))
    zeros = np.empty_like(err)
    N = np.max(sample_sizes)

    for i, seed in enumerate(seeds):
        rg = Generator(MT19937(seed))
        sample = rg.normal(loc, scale, N)

        for j, n in enumerate(sample_sizes):
            sample_slice = sample[:n]

            variance = var_impl(sample_slice)
            reference = ref_impl(sample_slice)

            err[i,j] = np.abs(variance - reference) / reference
            zeros[i,j] = ctz_mantissa(variance)

    return relerr, zeros


def single_pass_naive_var(x: np.ndarray) -> np.float64:
    # can potentially be implemented in a single pass
    return np.mean(x*x) - np.mean(x)**2


def two_pass_var(x: np.ndarray) -> np.float64:
    # inspired by numpy
    return np.mean((x - np.mean(x))**2)


def welford_var(x: np.ndarray) -> np.float64:
    pass


def reference_var(x: np.ndarray, digits: int = 250) -> np.float64:
    """
    Computes the input variance with high precision.
    Uses the two pass method with the mpmath library

    This is not particularly fast, we may be forced to
    use more performant technologies
    """
    with mpmath.workprec(digits):
        mean = mpmath.fsum(x) / len(x)

        sum_sq_diffs = mpmath.fsum(
            map(lambda val: mean-val, x),
            squared=True
        )
        var = sum_sq_diffs / len(x)

    return np.float64(var)


if __name__ == '__main__':
    pass
