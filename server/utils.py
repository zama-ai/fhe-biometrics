import cv2
import numpy as np


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


def imread_black_and_white(path):
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    return np.where(image == 255, 1, image)


def read_ap_indices(path):
    points = []

    with open(path, "r") as f:
        n_points = int(f.readline())
        for i in range(n_points):
            x, y = f.readline().split()
            x = int(x)
            y = int(y)
            for i in range(1, 7):
                points.append([x * i, y])

    # Transform it in a way to be used for numpy arrays like this: x[ap_indices]
    points = tuple(np.array(points).T.tolist())

    return points


def read_iris_code_and_mask(database_dir, ap_indices, i, j):
    iris_code = imread_black_and_white(
        f"{database_dir}/IrisCodes/000{i}_00{j}_code.bmp"
    )
    mask = imread_black_and_white(
        f"{database_dir}/NormalizedMasks/000{i}_00{j}_mano.bmp"
    )
    mask = np.array(mask.tolist() * 6)

    iris_code = iris_code[ap_indices]
    mask = mask[ap_indices]

    return iris_code, mask


def read_iris_database(database_dir, ap_indices):
    database = []

    ij = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3)]

    for i, j in ij:
        iris_code, mask = read_iris_code_and_mask(database_dir, ap_indices, i, j)
        database.append((iris_code, mask))

    return database
