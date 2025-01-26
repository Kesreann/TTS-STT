import asyncio
import json
import websockets
import pyaudio
import numpy as np
import time

# VTuber Studio WebSocket settings
VTS_IP = "localhost"
VTS_PORT = 8001
VTS_URL = f"ws://{VTS_IP}:{VTS_PORT}"

# Local WebSocket Server (to communicate with client)
LOCAL_SERVER_PORT = 8765

ws = None
async def connect_vtuber_studio():
    """Connects to VTuber Studio WebSocket API and authenticates."""
    try:
        async with websockets.connect(VTS_URL) as ws:
            print("Connected to VTuber Studio API")
            # Authenticate with VTuber Studio
            auth_payload = {
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": "auth_request",
                "messageType": "AuthenticationRequest",
                "data": {"pluginName": "PythonVTSControl", "pluginDeveloper": "YourName"}
            }
            await ws.send(json.dumps(auth_payload))
            response = await ws.recv()
            print("Auth Response:", response)
            return ws
    except Exception as e:
        print(f"Error connecting to VTS: {e}")


def send_vts_command(ws, param, value):
    """Sends a parameter control command to VTuber Studio."""
    payload = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": "1.0",
        "requestID": "set_mouth",
        "messageType": "ParameterValueRequest",
        "data": {"parameterName": param, "parameterValue": value}
    }
    ws.send(json.dumps(payload))


def handle_client(websocket, path):
    global ws
    """Handles client requests to trigger speech animation."""
    # Connect to VTuber Studio (blocking)
    ws = connect_vtuber_studio()
    send_vts_command(ws, 'test', 'test')


async def start_vts_server():
    """Runs the WebSocket server."""
    print("Starting VTS server...")
    server = await websockets.serve(handle_client, "localhost", LOCAL_SERVER_PORT)
    print(f"Server started on ws://localhost:{LOCAL_SERVER_PORT}")

    await server.wait_closed()

def run_async_server():
    """Runs the asynchronous VTS server."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_vts_server())