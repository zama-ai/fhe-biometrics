import numpy as np
import concrete.numpy as cnp
from functools import reduce


N_SHIFTS = 2
INPUT_SHAPE = (2**2,)
INPUT_MAX_VALUE = 2**2


def generate_rotate_shift_right(shift, globals_=None, locals_=None):
    function_body = f"""def rotate_shift_right{shift}(a):
    return np.concatenate((a[-{shift}:], a[:-{shift}])).astype('int64')"""
    exec(function_body, globals_, locals_)


def generate_rotate_shift_left(shift, globals_=None, locals_=None):
    function_body = f"""def rotate_shift_left{shift}(a):
    return np.concatenate((a[{shift}:], a[:{shift}])).astype('int64')"""
    exec(function_body, globals_, locals_)


def generate_all_rotate_shift_functions(n_shifts, globals_=None, locals_=None):
    for shift in range(1, n_shifts + 1):
        generate_rotate_shift_left(shift, globals_, locals_)
        generate_rotate_shift_right(shift, globals_, locals_)


# Generate rotate_shift_left{x} and rotate_shift_right{x} functions to be used
# to compute the best shifted hamming distance of two arrays
# TODO: find a way to generate them locally in another function or class
generate_all_rotate_shift_functions(N_SHIFTS, globals(), locals())


def hamming_distance(x, y) -> int:
    return np.sum(x ^ y)


def min_int(x: int, y: int) -> int:
    """concrete-numpy doesn't yet support min, we have to implement one using
    only supported operations"""
    return (x + y - abs(x - y)) // 2


def min_int_array(a) -> int:
    """Return the minimum value of an array of ints using the `min_int` function"""
    return reduce(min_int, a)


def best_shifted_hamming_distance(x, y):
    h = hamming_distance(x, y)

    # Functions should be generated before
    l1 = rotate_shift_left1(x)
    l2 = rotate_shift_left2(x)

    # Functions should be generated before
    r1 = rotate_shift_right1(x)
    r2 = rotate_shift_right2(x)

    hl1 = hamming_distance(l1, y)
    hl2 = hamming_distance(l2, y)

    hr1 = hamming_distance(r1, y)
    hr2 = hamming_distance(r2, y)

    return min_int_array([h, hr1, hr2, hl1, hl2])


class IrisMatcher:
    def __init__(self, input_shape, input_max_value) -> None:
        self.inputset = [
            (
                np.random.randint(
                    0, input_max_value + 1, size=input_shape, dtype=np.int64
                ),
                np.random.randint(
                    0, input_max_value + 1, size=input_shape, dtype=np.int64
                ),
            )
            for _ in range(100)
        ]

        self.configuration = cnp.Configuration(
            enable_unsafe_features=True,
            use_insecure_key_cache=True,
            insecure_key_cache_location=".keys",
        )

        self.compiler = cnp.Compiler(
            best_shifted_hamming_distance, {"x": "encrypted", "y": "encrypted"}
        )
        self.circuit = self.compiler.compile(self.inputset, self.configuration)
