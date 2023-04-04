import numpy as np
from hypothesis import given, settings, strategies as st

from server import iris_matcher


@given(x=st.integers(), y=st.integers())
def test_min_int(x, y):
    assert iris_matcher.min_int(x, y) == min(x, y)


@given(a=st.lists(st.integers(), min_size=1))
def test_min_int_array(a):
    assert iris_matcher.min_int_array(a) == min(a)


@given(
    x=st.lists(st.integers(min_value=0, max_value=1), min_size=4, max_size=4),
    y=st.lists(st.integers(min_value=0, max_value=1), min_size=4, max_size=4),
)
@settings(max_examples=5, deadline=None)
def test_iris_matcher(x, y):
    x = np.array(x)
    y = np.array(y)

    m = iris_matcher.IrisMatcher(input_shape=(4,), input_max_value=1)

    tfhe_result = m.circuit.encrypt_run_decrypt(x, y)
    clear_result = iris_matcher.best_shifted_hamming_distance(x, y)

    assert tfhe_result == clear_result
