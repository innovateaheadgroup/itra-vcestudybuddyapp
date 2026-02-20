from __future__ import annotations

import subprocess
import tempfile
import textwrap
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CodeRunResult:
    passed: bool
    output: str
    failed_test: str | None = None


FORBIDDEN_SNIPPETS = ["import os", "import subprocess", "__import__", "open(", "socket.", "pathlib.Path("]


def _contains_forbidden(code: str) -> str | None:
    lowered = code.lower()
    for snippet in FORBIDDEN_SNIPPETS:
        if snippet in lowered:
            return snippet
    return None


def run_python_tests(code: str, tests: str | None, timeout_seconds: int = 3) -> CodeRunResult:
    forbidden = _contains_forbidden(code)
    if forbidden:
        return CodeRunResult(
            passed=False,
            output=f"Execution blocked: disallowed snippet detected ({forbidden}).",
            failed_test="security_guardrail",
        )

    test_block = tests or "assert True"
    runner = textwrap.dedent(
        f"""
        import resource

        # Set a soft execution boundary for sandbox placeholder.
        resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
        resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))

        namespace = {{}}
        submitted_code = {code!r}
        exec(submitted_code, namespace, namespace)

        try:
            {textwrap.indent(test_block, "    ")}
            print("__PASS__")
        except Exception as exc:
            print("__FAIL__")
            print(type(exc).__name__ + ": " + str(exc))
        """
    )

    with tempfile.TemporaryDirectory(prefix="vce_code_run_") as tmp_dir:
        path = Path(tmp_dir) / "runner.py"
        path.write_text(runner, encoding="utf-8")
        try:
            proc = subprocess.run(
                ["python", "-I", str(path)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return CodeRunResult(passed=False, output="Execution timed out.", failed_test="timeout")

    output = (proc.stdout + "\n" + proc.stderr).strip()
    if "__PASS__" in output:
        return CodeRunResult(passed=True, output=output.replace("__PASS__", "").strip() or "All tests passed.")
    failure = output.split("__FAIL__")[-1].strip() if "__FAIL__" in output else output
    return CodeRunResult(passed=False, output=output, failed_test=failure or "Test failure")
