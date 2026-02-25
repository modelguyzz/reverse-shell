import sys
import io
from typing import Optional, Dict


def execute_in_memory(script_code: str, injected_globals: Optional[Dict] = None) -> str:

    # Prepare isolated global and local scopes
    globals_dict = {"__builtins__": __builtins__}
    locals_dict = {}
    if injected_globals:
        globals_dict.update(injected_globals)

    # Capture stdout and stderr
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = stdout_buffer
    sys.stderr = stderr_buffer
# made by modelguyzz
    try:
        # Execute the code
        exec(script_code, globals_dict, locals_dict)
    except Exception as e:
        # Capture exceptions in stderr
        print(f"Exception: {e}", file=sys.stderr)
    finally:
        # Restore original stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr
#made by modelguyzz
    # Combine stdout and stderr outputs
    output = stdout_buffer.getvalue() + stderr_buffer.getvalue()
    return output
