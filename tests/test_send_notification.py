import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "python"))


def run_notification(status, message, env=None):
    src = Path(__file__).parent.parent / "scripts" / "python" / "send_notification.py"
    code = src.read_text()
    mod = types.ModuleType("send_notification_test")
    with patch.dict("os.environ", env or {}), patch("sys.argv", ["send_notification.py", status, message]):
        exec(compile(code, str(src), "exec"), mod.__dict__)


class TestSendNotification:
    def test_skips_email_when_smtp_not_configured(self, capsys):
        run_notification("SUCCESS", "Test message", {"SMTP_SERVER": ""})
        assert "Email" not in capsys.readouterr().out

    def test_sends_email_on_success(self, capsys):
        env = {
            "SMTP_SERVER": "smtp.example.com",
            "SMTP_PORT": "587",
            "EMAIL_FROM": "from@example.com",
            "EMAIL_TO": "to@example.com",
            "SMTP_USER": "user",
            "SMTP_PWD": "test-smtp-password",
            "PRINTER_NAME": "TestPrinter",
        }
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)
        with patch("smtplib.SMTP", return_value=mock_smtp):
            run_notification("SUCCESS", "Printed OK", env)
        assert "Email sent" in capsys.readouterr().out

    def test_handles_email_failure(self, capsys):
        env = {
            "SMTP_SERVER": "smtp.example.com",
            "SMTP_PORT": "587",
            "EMAIL_FROM": "from@example.com",
            "EMAIL_TO": "to@example.com",
            "SMTP_USER": "user",
            "SMTP_PWD": "test-smtp-password",
            "PRINTER_NAME": "TestPrinter",
        }
        with patch("smtplib.SMTP", side_effect=ConnectionRefusedError("refused")):
            run_notification("FAILURE", "Print failed", env)
        assert "Email failed" in capsys.readouterr().out

    def test_sends_telegram_on_success(self, capsys):
        env = {
            "TELEGRAM_BOT_ID": "123:ABC",
            "TELEGRAM_CHAT_ID": "456",
            "PRINTER_NAME": "TestPrinter",
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        with patch("requests.post", return_value=mock_response):
            run_notification("SUCCESS", "Printed OK", env)
        assert "Telegram message sent" in capsys.readouterr().out

    def test_handles_telegram_failure(self, capsys):
        env = {
            "TELEGRAM_BOT_ID": "123:ABC",
            "TELEGRAM_CHAT_ID": "456",
            "PRINTER_NAME": "TestPrinter",
        }
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        with patch("requests.post", return_value=mock_response):
            run_notification("FAILURE", "Print failed", env)
        assert "Telegram notification failed" in capsys.readouterr().out
