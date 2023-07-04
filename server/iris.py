import numpy as np
import concrete.numpy as cnp
from functools import reduce
from pathlib import Path

from . import utils


N_SHIFTS = 2
PROJECT_ROOT = Path(__file__).parent.parent
APPLICATION_POINTS_PATH = PROJECT_ROOT / "data/OsirisParam/points.txt"
APPLICATION_POINTS_INDICES = utils.read_ap_indices(APPLICATION_POINTS_PATH)
DATA_DIR = PROJECT_ROOT / "data/Output"
# a list of irises and masks
DATABASE = utils.read_iris_database(DATA_DIR, APPLICATION_POINTS_INDICES)
# How much iris do we have
DATABASE_COUNT = len(DATABASE)


# Generate rotate_shift_left{x} and rotate_shift_right{x} functions to be used
# to compute the best shifted hamming distance of two arrays
# TODO: find a way to generate them locally in another function or class
utils.generate_all_rotate_shift_functions(N_SHIFTS, globals(), locals())


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


class IrisAuthenticator:
    def __init__(
        self, inputset=None, input_shape=None, input_max_value=None, database=None
    ) -> None:
        self.inputset = inputset or [
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

        self.database = database or self.inputset

        self.configuration = cnp.Configuration(
            enable_unsafe_features=True,
            use_insecure_key_cache=True,
            insecure_key_cache_location=".keys",
        )

        self.compiler = cnp.Compiler(
            self.auth, {"iris_code": "encrypted", "mask": "encrypted"}
        )
        self.circuit = self.compiler.compile(self.inputset, self.configuration)

    def auth(self, iris_code, mask):
        """Return the best score from comparing the provided iris and mask to the
        ones in the database, the user fo this function will need to define a threshold
        to decide weather the score means an identified iris or not

        We know this is suboptimal but this is the best we could came up with right now
        as we couldn't figure out a way to return an encrypted ID of the best match or
        a special ID if the score is too low, mainly because we can't compare FHE values
        """
        results = []

        for i in range(len(self.database)):
            (iris_code2, mask2) = self.database[i]
            combined_mask = mask & mask2
            ey1 = iris_code & combined_mask
            ey2 = iris_code2 & combined_mask
            score = best_shifted_hamming_distance(ey1, ey2)
            results.append(score)

        best_score = min_int_array(results)
        return best_score
