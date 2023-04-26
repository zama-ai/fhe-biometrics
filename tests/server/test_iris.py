import numpy as np
from hypothesis import given, settings, strategies as st

from server import iris, utils


@given(x=st.integers(), y=st.integers())
def test_min_int(x, y):
    assert iris.min_int(x, y) == min(x, y)


@given(a=st.lists(st.integers(), min_size=1))
def test_min_int_array(a):
    assert iris.min_int_array(a) == min(a)


@given(
    x=st.lists(st.integers(min_value=0, max_value=1), min_size=4, max_size=4),
    y=st.lists(st.integers(min_value=0, max_value=1), min_size=4, max_size=4),
)
@settings(max_examples=1, deadline=None)
def test_iris_auth(x, y):
    x = np.array(x)
    y = np.array(y)

    database = [
        (np.array([0, 0, 0, 0]), np.array([0, 0, 0, 0])),
        (np.array([1, 1, 1, 1]), np.array([1, 1, 1, 1])),
    ]

    m = iris.IrisAuthenticator(input_shape=(4,), input_max_value=1, database=database)

    clear_result = m.auth(x, y)
    tfhe_result = m.circuit.encrypt_run_decrypt(x, y)

    assert tfhe_result == clear_result


def test_iris_auth_real_data():
    iris_code, mask = utils.read_iris_code_and_mask(
        iris.DATA_DIR, iris.APPLICATION_POINTS_INDICES, 0, 0
    )

    m = iris.IrisAuthenticator(inputset=iris.DATABASE)

    clear_result = m.auth(iris_code, mask)
    tfhe_result = m.circuit.encrypt_run_decrypt(iris_code, mask)

    assert clear_result == tfhe_result
