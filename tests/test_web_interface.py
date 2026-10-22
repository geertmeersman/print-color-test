import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "flask"))

with patch("pysnmp.hlapi.v3arch.asyncio.get_cmd"), patch("pysnmp.hlapi.v3arch.asyncio.next_cmd"), patch("os.makedirs"):
    import web_interface
    from web_interface import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestHealthEndpoint:
    def test_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.get_json()["status"] == "ok"


class TestIndexRoute:
    def test_returns_200(self, client):
        with (
            patch.object(web_interface, "read_version", return_value="1.0.0"),
            patch.object(web_interface, "get_cronjob_description", return_value="Every Friday"),
        ):
            response = client.get("/")
            assert response.status_code == 200


class TestUploadRoute:
    def test_rejects_non_pdf(self, client):
        data = {"file": (b"content", "test.txt")}
        response = client.post("/upload", data=data, content_type="multipart/form-data")
        assert response.status_code == 200
        assert response.get_json()["success"] is False

    def test_rejects_missing_file(self, client):
        response = client.post("/upload", data={}, content_type="multipart/form-data")
        assert response.status_code == 200
        assert response.get_json()["success"] is False


class TestPrintRoutes:
    def test_print_color_page_success(self, client):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            response = client.post("/print-color-page")
            assert response.status_code == 200
            assert response.get_json()["success"] is True

    def test_print_color_page_failure(self, client):
        import subprocess

        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "cmd", stderr="error")):
            response = client.post("/print-color-page")
            assert response.status_code == 200
            assert response.get_json()["success"] is False

    def test_print_empty_test_success(self, client):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            response = client.post("/print-empty-test")
            assert response.status_code == 200
            assert response.get_json()["success"] is True


class TestReadVersion:
    def test_reads_version_file(self, tmp_path):
        version_file = tmp_path / "VERSION"
        version_file.write_text("1.2.3")
        with patch("builtins.open", return_value=version_file.open()):
            result = web_interface.read_version()
        assert result == "1.2.3"

    def test_returns_unknown_on_error(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = web_interface.read_version()
        assert result == "Unknown"
