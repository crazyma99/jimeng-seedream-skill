"""Optional Atlas Cloud provider for Seedream 4.5 image generation."""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List, Optional, Union
from urllib import error, request


ATLAS_API_BASE_URL = "https://api.atlascloud.ai"
ATLAS_CATALOG_URL = "https://api.atlascloud.ai/api/v1/models"
ATLAS_TEXT_MODEL = "bytedance/seedream-v4.5"
ATLAS_EDIT_MODEL = "bytedance/seedream-v4.5/edit"
ATLAS_SCHEMA_URL_TEMPLATE = "https://static.atlascloud.ai/model/schema/{slug}.json"
TERMINAL_STATUSES = {"completed", "failed"}
TRANSIENT_GET_ERRORS = {408, 429, 500, 502, 503, 504}


def _json_request(
    url: str,
    *,
    api_key: Optional[str] = None,
    method: str = "GET",
    payload: Optional[Dict[str, Any]] = None,
    timeout: float = 30,
) -> Any:
    headers = {
        "Accept": "application/json",
        "User-Agent": "jimeng-seedream-skill/1.0 (+https://github.com/crazyma99/jimeng-seedream-skill)",
    }
    data = None
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    req = request.Request(url, data=data, headers=headers, method=method)
    with request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _model_slug(model: str) -> str:
    return model.replace("/", "-")


def _response_data(payload: Any) -> Any:
    if isinstance(payload, dict) and isinstance(payload.get("data"), (dict, list)):
        return payload["data"]
    return payload


def _find_model(catalog: Any, model: str) -> Dict[str, Any]:
    catalog = _response_data(catalog)
    if isinstance(catalog, dict):
        models = catalog.get("models") or catalog.get("items") or []
    else:
        models = catalog
    for item in models:
        if isinstance(item, dict) and (item.get("model") == model or item.get("id") == model):
            if item.get("enabled") is False:
                raise RuntimeError(f"Atlas Cloud model is disabled: {model}")
            return item
    raise ValueError(f"Atlas Cloud model is not available: {model}")


def _api_paths(schema: Dict[str, Any]) -> tuple[str, str]:
    run_path = None
    result_path = None
    for path, operations in schema.get("paths", {}).items():
        if operations.get("x-api-name") == "model_run":
            run_path = path
        elif operations.get("x-api-name") == "model_result":
            result_path = path
    if not run_path or not result_path:
        raise ValueError("Atlas Cloud schema is missing model_run or model_result")
    return run_path, result_path


def _validate_payload(schema: Dict[str, Any], payload: Dict[str, Any]) -> None:
    input_schema = schema.get("components", {}).get("schemas", {}).get("Input", {})
    properties = input_schema.get("properties", {})
    unsupported = sorted(set(payload) - set(properties))
    if unsupported:
        raise ValueError(f"Unsupported Atlas Cloud input fields: {', '.join(unsupported)}")
    missing = [name for name in input_schema.get("required", []) if name not in payload]
    if missing:
        raise ValueError(f"Missing Atlas Cloud input fields: {', '.join(missing)}")
    for name, value in payload.items():
        enum = properties.get(name, {}).get("enum")
        if enum and value not in enum:
            raise ValueError(f"Invalid {name!r}; expected one of: {', '.join(map(str, enum))}")
    images = payload.get("images")
    image_schema = properties.get("images", {})
    if images is not None:
        if len(images) < image_schema.get("minItems", 0):
            raise ValueError("At least one reference image is required")
        if len(images) > image_schema.get("maxItems", len(images)):
            raise ValueError("Too many reference images")


def _discover(model: str, timeout: float) -> tuple[str, str, Dict[str, Any]]:
    catalog = _json_request(ATLAS_CATALOG_URL, timeout=timeout)
    model_info = _find_model(catalog, model)
    schema_url = model_info.get("schema") or ATLAS_SCHEMA_URL_TEMPLATE.format(slug=_model_slug(model))
    schema = _json_request(schema_url, timeout=timeout)
    run_path, result_path = _api_paths(schema)
    return run_path, result_path, schema


def _poll_prediction(
    result_url: str,
    api_key: str,
    *,
    poll_interval: float,
    max_polls: int,
    timeout: float,
) -> Dict[str, Any]:
    for poll_index in range(max_polls):
        try:
            prediction = _response_data(_json_request(result_url, api_key=api_key, timeout=timeout))
        except error.HTTPError as exc:
            if exc.code not in TRANSIENT_GET_ERRORS or poll_index + 1 >= max_polls:
                raise
            time.sleep(min(poll_interval * (2**poll_index), 10.0))
            continue
        except (error.URLError, TimeoutError):
            if poll_index + 1 >= max_polls:
                raise
            time.sleep(min(poll_interval * (2**poll_index), 10.0))
            continue

        status = prediction.get("status")
        if status in TERMINAL_STATUSES:
            return prediction
        if poll_index + 1 < max_polls:
            time.sleep(min(poll_interval * (2**poll_index), 10.0))
    raise TimeoutError(f"Atlas Cloud prediction did not finish after {max_polls} polls")


def _generate_with_atlas(
    payload: Dict[str, Any],
    *,
    api_key: Optional[str],
    poll_interval: float,
    max_polls: int,
    timeout: float,
) -> Dict[str, Any]:
    resolved_key = api_key or os.getenv("ATLASCLOUD_API_KEY")
    if not resolved_key:
        raise ValueError("ATLASCLOUD_API_KEY must be configured for the Atlas Cloud provider")

    run_path, result_path, schema = _discover(payload["model"], timeout)
    _validate_payload(schema, payload)

    # This paid generation request is deliberately submitted exactly once.
    prediction = _response_data(
        _json_request(
            f"{ATLAS_API_BASE_URL}{run_path}",
            api_key=resolved_key,
            method="POST",
            payload=payload,
            timeout=timeout,
        )
    )
    request_id = prediction.get("id")
    if not request_id:
        raise RuntimeError("Atlas Cloud response did not include a prediction id")

    if prediction.get("status") not in TERMINAL_STATUSES:
        prediction = _poll_prediction(
            f"{ATLAS_API_BASE_URL}{result_path.replace('{request_id}', request_id)}",
            resolved_key,
            poll_interval=poll_interval,
            max_polls=max_polls,
            timeout=timeout,
        )
    if prediction.get("status") != "completed":
        raise RuntimeError(f"Atlas Cloud generation failed: {prediction}")

    outputs = prediction.get("outputs") or []
    return {
        "success": True,
        "images": [{"url": url, "size": payload.get("size")} for url in outputs],
        "usage": None,
        "prediction_id": request_id,
    }


def atlas_text_to_image(
    prompt: str,
    size: str = "2048*2048",
    *,
    api_key: Optional[str] = None,
    poll_interval: float = 1.0,
    max_polls: int = 12,
    timeout: float = 30,
) -> Dict[str, Any]:
    """Generate one image with Atlas Cloud while leaving Ark as the default provider."""
    return _generate_with_atlas(
        {"model": ATLAS_TEXT_MODEL, "prompt": prompt, "size": size},
        api_key=api_key,
        poll_interval=poll_interval,
        max_polls=max_polls,
        timeout=timeout,
    )


def atlas_image_to_image(
    prompt: str,
    image: Union[str, List[str]],
    size: str = "2048*2048",
    *,
    api_key: Optional[str] = None,
    poll_interval: float = 1.0,
    max_polls: int = 12,
    timeout: float = 30,
) -> Dict[str, Any]:
    """Edit one or more public image URLs with Atlas Cloud Seedream 4.5."""
    images = [image] if isinstance(image, str) else list(image)
    return _generate_with_atlas(
        {"model": ATLAS_EDIT_MODEL, "prompt": prompt, "images": images, "size": size},
        api_key=api_key,
        poll_interval=poll_interval,
        max_polls=max_polls,
        timeout=timeout,
    )


__all__ = [
    "ATLAS_EDIT_MODEL",
    "ATLAS_TEXT_MODEL",
    "atlas_image_to_image",
    "atlas_text_to_image",
]
