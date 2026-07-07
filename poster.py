import requests

import config


def post_bundle(bundle: dict) -> requests.Response:
    resp = requests.post(
        config.ROUTINE_TRIGGER_URL,
        json=bundle,
        headers={"Authorization": f"Bearer {config.ROUTINE_API_TOKEN}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp
