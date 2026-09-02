import io
import json
import unittest
from unittest import mock
from urllib import error

import atlas_provider


def response(payload):
    body = io.BytesIO(json.dumps(payload).encode("utf-8"))
    body.__enter__ = lambda self: self
    body.__exit__ = lambda *args: None
    return body


SCHEMA = {
    "paths": {
        "/run": {"x-api-name": "model_run"},
        "/result/{request_id}": {"x-api-name": "model_result"},
    },
    "components": {
        "schemas": {
            "Input": {
                "required": ["model", "prompt"],
                "properties": {
                    "model": {"type": "string"},
                    "prompt": {"type": "string"},
                    "size": {"enum": ["2048*2048"]},
                },
            }
        }
    },
}


class AtlasProviderTests(unittest.TestCase):
    def test_discovers_schema_submits_once_and_polls(self):
        replies = [
            response({"data": [{"model": atlas_provider.ATLAS_TEXT_MODEL, "enabled": True}]}),
            response(SCHEMA),
            response({"code": 200, "data": {"id": "pred-1", "status": "processing"}}),
            response({"code": 200, "data": {"id": "pred-1", "status": "completed", "outputs": ["https://example.com/a.png"]}}),
        ]
        with mock.patch("atlas_provider.request.urlopen", side_effect=replies) as open_url:
            result = atlas_provider.atlas_text_to_image("hello", api_key="test", poll_interval=0)

        self.assertEqual(result["images"][0]["url"], "https://example.com/a.png")
        methods = [call.args[0].method for call in open_url.call_args_list]
        self.assertEqual(methods.count("POST"), 1)
        self.assertEqual(methods.count("GET"), 3)

    def test_post_failure_is_not_retried(self):
        replies = [
            response({"data": [{"model": atlas_provider.ATLAS_TEXT_MODEL, "enabled": True}]}),
            response(SCHEMA),
            error.URLError("connection lost"),
        ]
        with mock.patch("atlas_provider.request.urlopen", side_effect=replies) as open_url:
            with self.assertRaises(error.URLError):
                atlas_provider.atlas_text_to_image("hello", api_key="test", poll_interval=0)
        self.assertEqual(len(open_url.call_args_list), 3)

    def test_retries_only_transient_result_get(self):
        transient = error.HTTPError("https://example.com", 503, "busy", {}, None)
        replies = [
            response({"data": [{"model": atlas_provider.ATLAS_TEXT_MODEL, "enabled": True}]}),
            response(SCHEMA),
            response({"code": 200, "data": {"id": "pred-2", "status": "processing"}}),
            transient,
            response({"code": 200, "data": {"id": "pred-2", "status": "completed", "outputs": ["https://example.com/b.png"]}}),
        ]
        with mock.patch("atlas_provider.request.urlopen", side_effect=replies), mock.patch("atlas_provider.time.sleep"):
            result = atlas_provider.atlas_text_to_image("hello", api_key="test", max_polls=2)
        self.assertEqual(result["prediction_id"], "pred-2")

    def test_rejects_size_before_paid_request(self):
        replies = [
            response({"data": [{"model": atlas_provider.ATLAS_TEXT_MODEL, "enabled": True}]}),
            response(SCHEMA),
        ]
        with mock.patch("atlas_provider.request.urlopen", side_effect=replies) as open_url:
            with self.assertRaisesRegex(ValueError, "Invalid 'size'"):
                atlas_provider.atlas_text_to_image("hello", size="2K", api_key="test")
        self.assertEqual(len(open_url.call_args_list), 2)


if __name__ == "__main__":
    unittest.main()
