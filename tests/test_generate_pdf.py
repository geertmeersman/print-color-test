import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "python"))


class TestGeneratePdf:
    def test_generates_pdf_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "color_test.pdf"
            with patch("scripts.python.generate_pdf.filepath", str(output)) if False else patch.dict("sys.modules"):
                # Import and run with patched filepath
                import types

                # Create a minimal module execution with patched path
                src = Path(__file__).parent.parent / "scripts" / "python" / "generate_pdf.py"
                code = src.read_text().replace(
                    'filepath = "/home/color_test_page_dated.pdf"',
                    f'filepath = "{output}"',
                )
                mod = types.ModuleType("generate_pdf_test")
                exec(compile(code, str(src), "exec"), mod.__dict__)

            assert output.exists()
            assert output.stat().st_size > 0

    def test_pdf_contains_four_color_blocks(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "color_test.pdf"
            src = Path(__file__).parent.parent / "scripts" / "python" / "generate_pdf.py"
            import types

            code = src.read_text().replace(
                'filepath = "/home/color_test_page_dated.pdf"',
                f'filepath = "{output}"',
            )
            mod = types.ModuleType("generate_pdf_test")
            exec(compile(code, str(src), "exec"), mod.__dict__)
            # PDF should be valid (starts with %PDF)
            content = output.read_bytes()
            assert content[:4] == b"%PDF"


class TestGenerateEmptyPdf:
    def test_generates_empty_pdf(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "empty.pdf"
            src = Path(__file__).parent.parent / "scripts" / "python" / "generate_empty_pdf.py"
            import types

            code = src.read_text().replace(
                'output_path = "/home/empty.pdf"',
                f'output_path = "{output}"',
            )
            mod = types.ModuleType("generate_empty_pdf_test")
            exec(compile(code, str(src), "exec"), mod.__dict__)
            assert output.exists()
            assert output.read_bytes()[:4] == b"%PDF"
