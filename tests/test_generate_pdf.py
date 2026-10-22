import sys
import tempfile
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "python"))


def run_script_with_patched_path(script_name, original_path, new_path):
    src = Path(__file__).parent.parent / "scripts" / "python" / script_name
    code = src.read_text().replace(f'"{original_path}"', f'"{new_path}"')
    mod = types.ModuleType(f"{script_name}_test")
    exec(compile(code, str(src), "exec"), mod.__dict__)
    return mod


class TestGeneratePdf:
    def test_generates_pdf_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "color_test.pdf"
            run_script_with_patched_path(
                "generate_pdf.py",
                "/home/color_test_page_dated.pdf",
                str(output),
            )
            assert output.exists()
            assert output.stat().st_size > 0

    def test_pdf_is_valid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "color_test.pdf"
            run_script_with_patched_path(
                "generate_pdf.py",
                "/home/color_test_page_dated.pdf",
                str(output),
            )
            assert output.read_bytes()[:4] == b"%PDF"


class TestGenerateEmptyPdf:
    def test_generates_empty_pdf(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "empty.pdf"
            run_script_with_patched_path(
                "generate_empty_pdf.py",
                "/home/empty.pdf",
                str(output),
            )
            assert output.exists()
            assert output.read_bytes()[:4] == b"%PDF"
