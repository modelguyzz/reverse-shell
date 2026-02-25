import asyncio
import struct
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AsyncNetworkingEngine")


class AsyncNetworkingEngine:
    def __init__(self, host: str, port: int, max_reconnect_delay: int = 60):
        self.host = host
        self.port = port
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self._reconnect_delay = 1
        self.max_reconnect_delay = max_reconnect_delay
        self._connected = asyncio.Event()
        self._stop = False
        self._listen_task: Optional[asyncio.Task] = None

    async def connect(self):
        """Establishes a persistent TCP connection with automatic reconnection."""
        while not self._stop:
            try:
                logger.info(f"Attempting to connect to {self.host}:{self.port}")
                self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
                self._connected.set()
                logger.info("Connection established.")
                # Reset reconnect delay after successful connection
                self._reconnect_delay = 1
                # Start the listener coroutine
                if self._listen_task is None or self._listen_task.done():
                    self._listen_task = asyncio.create_task(self._listen())
                # Wait until connection is lost
                await self._connected.wait()
            except (ConnectionRefusedError, OSError) as e:
                logger.warning(f"Connection failed: {e}. Retrying in {self._reconnect_delay}s")
                await asyncio.sleep(self._reconnect_delay)
                self._reconnect_delay = min(self._reconnect_delay * 2, self.max_reconnect_delay)

    async def _listen(self):
        """Background coroutine that listens for incoming messages."""
        try:
            while not self._stop:
                # Read message length (4 bytes)
                header = await self.reader.readexactly(4)
                message_length = struct.unpack("!I", header)[0]
                # Read the message body
                data = await self.reader.readexactly(message_length)
                await self.message_queue.put(data)
        except (asyncio.IncompleteReadError, ConnectionResetError) as e:
            logger.warning(f"Connection lost: {e}")
            self._connected.clear()
            # Trigger reconnection
            await self._reconnect()

    async def _reconnect(self):
        """Handles reconnection logic."""
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception:
                pass
        self.reader = None
        self.writer = None
        self._connected.clear()
        # The main connect loop will attempt reconnection

    async def send_message(self, data: bytes):
        """Sends a length-prefixed message over the TCP connection."""
        if not self.writer or self.writer.is_closing():
            raise ConnectionError("Not connected to server.")
        # Prefix the message with its length (4 bytes, network byte order)
        message = struct.pack("!I", len(data)) + data
        self.writer.write(message)
        await self.writer.drain()

    async def receive_message(self) -> bytes:
        """Retrieves a single message from the queue."""
        return await self.message_queue.get()

    async def stop(self):
        """Stops the networking engine."""
        self._stop = True
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        self._connected.clear()
        logger.info("Networking engine stopped.")
