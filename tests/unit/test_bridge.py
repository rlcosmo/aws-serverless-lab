import html
import json
import urllib.error
from io import BytesIO

import pytest

from automation import bridge


@pytest.mark.parametrize("endpoint", ["https://glpi.cosmotechsolutions.com.br.evil.invalid",
    "http://evil.invalid", "https://user:password@glpi.cosmotechsolutions.com.br",
    "https://glpi.cosmotechsolutions.com.br/private"])
def test_glpi_credential_endpoint_cannot_be_redirected_to_another_host(endpoint):
    with pytest.raises(ValueError):
        bridge.GLPIClient({"base_url": endpoint})


def test_http_errors_do_not_expose_secret_response_bodies(monkeypatch):
    class Opener:
        def open(self, *args, **kwargs):
            raise urllib.error.HTTPError("https://example.invalid", 401, "error", {},
                                         BytesIO(b"private-api-token"))

    monkeypatch.setattr(bridge.urllib.request, "build_opener", lambda *args: Opener())
    with pytest.raises(RuntimeError) as failure:
        bridge.request_json("https://example.invalid")
    assert "401" in str(failure.value)
    assert "private-api-token" not in str(failure.value)


def test_preformatted_state_is_parsed_without_reading_html_as_commands():
    parser = bridge.PreformattedRecords()
    payload = {"cosmotech_automation_state": {"state": "waiting_for_real_approvals", "run_id": 1}}
    parser.feed("<pre>" + html.escape(json.dumps(payload)) + "</pre><script>ignored()</script>")
    assert parser.records == [payload]


def test_unstructured_test_change_cannot_dispatch_any_workflow():
    class GLPI:
        def get_change(self, change_id):
            return {"content": "[COSMOTECH LAB TEST] no deployment requested"}

    class GitHub:
        def api(self, *args, **kwargs):
            pytest.fail("Invalid GMUD must be rejected before contacting GitHub")

    with pytest.raises(ValueError, match="structured change"):
        bridge.run_change(GLPI(), GitHub(), 1, "a" * 40, b"x" * 32)
