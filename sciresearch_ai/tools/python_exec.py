from __future__ import annotations
import contextlib, io, traceback

def run_user_code(code: str) -> str:
    # very lightweight sandbox (no imports filtering here; meant for local, trusted use only)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(code, {"__name__": "__main__"}, {})
    except Exception:
        buf.write("ERROR:\n" + traceback.format_exc())
    return buf.getvalue()
