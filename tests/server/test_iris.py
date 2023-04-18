import cv2
import numpy as np
from hypothesis import given, settings, strategies as st

from server import iris


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

    m = iris.IrisAuthenticator(input_shape=(4,), input_max_value=1)

    clear_result = iris.auth(x, y)

    tfhe_result = m.circuit.encrypt_run_decrypt(x, y)
    assert tfhe_result == clear_result


def read_ap_img(path, shape):
    ap = np.zeros(shape, dtype=np.uint8)

    with open(path, "r") as f:
        n_points = int(f.readline())
        for i in range(n_points):
            x, y = f.readline().split()
            x = int(x)
            y = int(y)
            ap[x][y] = 255

    return ap


DATA_DIR = "/home/mohammedi/workspace/tfhe-ubiris/data/Output"


def test_iris_auth_real_data():
    iris_code = cv2.imread(
        f"{DATA_DIR}/IrisCodes/0000_000_code.bmp", cv2.IMREAD_GRAYSCALE
    )
    mask = cv2.imread(
        f"{DATA_DIR}/NormalizedMasks/0000_000_mano.bmp", cv2.IMREAD_GRAYSCALE
    )

    iris_code2 = cv2.imread(
        f"{DATA_DIR}/IrisCodes/0000_001_code.bmp", cv2.IMREAD_GRAYSCALE
    )
    mask2 = cv2.imread(
        f"{DATA_DIR}/NormalizedMasks/0000_001_mano.bmp", cv2.IMREAD_GRAYSCALE
    )

    p = "notebooks/points.txt"

    ap = read_ap_img(p, (64, 512))

    total_mask = mask & mask2 & ap

    total_mask_big = np.array(total_mask.tolist() * 6)

    clear_result = iris.auth(iris_code, mask)

    print("clear result", clear_result)

    m = iris.IrisAuthenticator(input_shape=iris_code.shape, input_max_value=255)

    tfhe_result = m.circuit.encrypt_run_decrypt(iris_code, iris_code2, total_mask_big)

    assert clear_result == tfhe_result
