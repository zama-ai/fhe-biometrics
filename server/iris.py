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


# a list of irises and masks
DATABASE = [
    (np.array([0, 0, 0, 0]), np.array([0, 0, 0, 0])),
    (np.array([1, 1, 1, 1]), np.array([1, 1, 1, 1])),
]

# How much iris do we have
DATABASE_COUNT = 2

ap = np.array([1, 1, 1, 1])


def auth(iris_code, mask):
    """Return the best score from comparing the provided iris and mask to the
    ones in the database, the user fo this function will need to define a threshold
    to decide weather the score means an identified iris or not

    We know this is suboptimal but this is the best we could came up with right now
    as we couldn't figure out a way to return an encrypted ID of the best match or
    a special ID if the score is too low, mainly because we can't compare FHE values
    """
    results = []

    for i in range(DATABASE_COUNT):
        (iris_code2, mask2) = DATABASE[i]
        combined_mask = mask & mask2 & ap
        ey1 = iris_code & combined_mask
        ey2 = iris_code2 & combined_mask
        bshd = best_shifted_hamming_distance(ey1, ey2)
        results.append(bshd)

    best_score = min_int_array(results)
    return best_score


class IrisAuthenticator:
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
            auth, {"iris_code": "encrypted", "mask": "encrypted"}
        )
        self.circuit = self.compiler.compile(self.inputset, self.configuration)
