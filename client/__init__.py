import os
import concrete.numpy as cnp
import requests

from server import utils, iris

FHE_CLIENT_PATH = os.path.join(os.path.dirname(__file__), "fhe_client.zip")

THRESHOLD = 100

fhe_client = cnp.Client.load(FHE_CLIENT_PATH)


url = "http://localhost:8000/uploaddata/"
data = b"\x01\x02\x03\x04\x05"


def send_auth_request():
    iris_code, mask = utils.read_iris_code_and_mask(iris.DATABASE, 0, 0)

    public_args = fhe_client.encrypt(iris_code, mask)

    serialized_public_args = fhe_client.specs.serialize_public_args(public_args)

    response = requests.post(
        url,
        data=serialized_public_args,
        headers={"Content-Type": "application/octet-stream"},
    )

    serialized_public_result = response.json()

    public_result = fhe_client.specs.unserialize_public_result(serialized_public_result)

    best_score = fhe_client.decrypt(public_result)

    if best_score > THRESHOLD:
        return "Authenticated"
    else:
        return "Iris not recognized"
