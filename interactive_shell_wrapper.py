import subprocess
import threading
import queue
import sys
import os
from typing import Optional


class InteractiveShellWrapper:
    def __init__(self):
        """Launch a persistent interactive shell process with redirected pipes."""
        # Determine the platform-specific default shell
        if os.name == "nt":  # Windows
            shell_cmd = ["cmd.exe"]
        else:  # Unix/Linux/macOS
            shell_cmd = ["/bin/bash"]

        # Start the shell process with stdin, stdout, stderr redirected
        self.process = subprocess.Popen(
            shell_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,  # unbuffered
            universal_newlines=True
        )

        # Queues to hold stdout and stderr lines
        self.stdout_queue: queue.Queue[str] = queue.Queue()
        self.stderr_queue: queue.Queue[str] = queue.Queue()

        # Start background threads for reading stdout and stderr
        self._stdout_thread = threading.Thread(target=self._read_stream, args=(self.process.stdout, self.stdout_queue), daemon=True)
        self._stderr_thread = threading.Thread(target=self._read_stream, args=(self.process.stderr, self.stderr_queue), daemon=True)
        self._stdout_thread.start()
        self._stderr_thread.start()

    def _read_stream(self, stream, output_queue: queue.Queue):
        """Continuously read lines from a stream and put them into a queue."""
        try:
            for line in iter(stream.readline, ""):
                output_queue.put(line.rstrip("\n"))
        finally:
            stream.close()

    def execute_command(self, command: str):
        """Send a command to the shell."""
        if self.process.stdin:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()

    def get_stdout(self, timeout: Optional[float] = None) -> str:
        """Retrieve a single line from stdout (non-blocking if timeout=0)."""
        try:
            return self.stdout_queue.get(timeout=timeout)
        except queue.Empty:
            return ""

    def get_stderr(self, timeout: Optional[float] = None) -> str:
        """Retrieve a single line from stderr (non-blocking if timeout=0)."""
        try:
            return self.stderr_queue.get(timeout=timeout)
        except queue.Empty:
            return ""

    def terminate(self):
        """Terminate the shell process cleanly."""
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
#code made by modelguyzz

# Example usage
if __name__ == "__main__":
    shell = InteractiveShellWrapper()
    
    # Send a command
    shell.execute_command("echo Hello World")
    
    # Read stdout
    import time
    time.sleep(0.1)  # give the background thread a moment
    while True:
        line = shell.get_stdout(timeout=0.1)
        if not line:
            break
        print(f"STDOUT: {line}")
    
    # Send another command
    shell.execute_command("invalidcommand")
    time.sleep(0.1)
    while True:
        line = shell.get_stderr(timeout=0.1)
        if not line:
            break
        print(f"STDERR: {line}")
    
    # Clean up
    shell.terminate()
