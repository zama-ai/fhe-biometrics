import os
from uuid import uuid4

import concrete.numpy as cnp
from fastapi import BackgroundTasks, FastAPI, status

app = FastAPI()

FHE_SERVER_PATH = os.path.join(os.path.dirname(__file__), "fhe_server.zip")

fhe_server = cnp.Server.load(FHE_SERVER_PATH)

auth_results = {}


def run_auth(auth_id, public_args, evaluation_keys):
    auth_results[auth_id] = None
    public_result = fhe_server.run(public_args, evaluation_keys)
    auth_results[auth_id] = public_result


@app.post("/auth", status_code=status.HTTP_202_ACCEPTED)
def auth_route(background_tasks: BackgroundTasks, data: bytes, evaluation_keys: bytes):
    public_args = fhe_server.client_specs.unserialize_public_args(data)
    evaluation_keys_ = cnp.EvaluationKeys.unserialize(evaluation_keys)

    auth_id = uuid4()

    background_tasks.add_task(run_auth, auth_id, public_args, evaluation_keys_)
    queue_len = len(background_tasks.tasks)

    return {
        "message": (
            f"You request is being processed, you're {queue_len} in the queue,"
            f" check /auth/check/{auth_id} for results"
        )
    }


@app.get("/auth/check/{auth_id}")
def check_auth(auth_id):
    if result := auth_results.get(auth_id):
        return fhe_server.client_specs.serialize_public_result(result)
    else:
        return {"message": f"Still processing {auth_id} ..."}
