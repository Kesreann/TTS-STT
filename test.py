import asyncio
import time

import websockets
import json
from random import randrange


class VTubeStudioAPI:
    def __init__(self, host="localhost", port=8001):
        self.host = host
        self.port = port
        self.url = f"ws://{self.host}:{self.port}"
        self.websocket = None
        self.authentication_token = None
        self.request_id = "MyIDWithLessThan64Characters"

    async def connect(self):
        self.websocket = await websockets.connect(self.url)
        print(f"Connected to VTube Studio WebSocket at {self.url}")

    async def send_request(self, message):
        await self.websocket.send(json.dumps(message))
        response = await self.websocket.recv()
        return json.loads(response)

    def create_request(self, message_type, data=None):
        return {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": self.request_id,
            "messageType": message_type,
            "data": data or {}
        }

    async def authenticate(self):
        message = self.create_request("AuthenticationTokenRequest", data={
            "pluginName": "My Cool Plugin",
            "pluginDeveloper": "My Name"
        })
        response = await self.send_request(message)

        if response.get("messageType") == "AuthenticationTokenResponse":
            self.authentication_token = response["data"]["authenticationToken"]
            print(f"Authentication token received: {self.authentication_token}")

            auth_message = self.create_request(
                "AuthenticationRequest",
                data={
                    "pluginName": "My Cool Plugin",
                    "pluginDeveloper": "My Name",
                    "authenticationToken": self.authentication_token
                }
            )
            await self.send_request(auth_message)
            print("Authentication completed successfully.")
        else:
            raise ValueError("Failed to authenticate: " + response.get("data", {}).get("message", "Unknown error"))

    async def get_available_models(self):
        message = self.create_request("AvailableModelsRequest")
        response = await self.send_request(message)
        if "availableModels" not in response.get("data", {}):
            raise ValueError(f"Failed to retrieve models: {response.get('data', {}).get('message')}")
        return response

    async def load_model(self, model_id):
        message = self.create_request("ModelLoadRequest", data={"modelID": model_id})
        return await self.send_request(message)

    async def change_model(self, model_id):
        message = self.create_request("HotkeyTriggerRequest", data={"hotkeyID": model_id})
        return await self.send_request(message)

    async def get_hotkeys(self, model_id=None):
        data = {"modelID": model_id} if model_id else {}
        message = self.create_request("HotkeysInCurrentModelRequest", data=data)
        response = await self.send_request(message)
        return response

    async def trigger_hotkey(self, hotkey_id):
        message = self.create_request("HotkeyTriggerRequest", data={"hotkeyID": hotkey_id})
        return await self.send_request(message)

    async def move_and_spin_model(self, position_x, position_y, rotation, size, time_in_seconds=3):
        move_message = self.create_request(
            "MoveModelRequest",
            data={
                "timeInSeconds": time_in_seconds,
                "valuesAreRelativeToModel": False,
                "positionX": position_x,
                "positionY": position_y,
                "rotation": rotation,
                "size": size
            }
        )
        await self.send_request(move_message)
        await asyncio.sleep(time_in_seconds)
        spin_message = self.create_request(
            "MoveModelRequest",
            data={"timeInSeconds": 5.0, "valuesAreRelativeToModel": True, "rotation": 360}
        )
        await self.send_request(spin_message)

    async def close(self):
        await self.websocket.close()
        print("Connection closed.")


async def main():
    api = VTubeStudioAPI()
    await api.connect()

    try:
        await api.authenticate()
        available_models = await api.get_available_models()
        print("Available Models:", available_models)

        model_id = available_models["data"]["availableModels"][5]["modelID"]
        await api.load_model(model_id)
        await api.move_and_spin_model(position_x=0.1, position_y=-0.7, rotation=16.3, size=-22.5)

        hotkeys = await api.get_hotkeys(model_id)
        print("Hotkeys:", hotkeys)

        if hotkeys["data"]["availableHotkeys"]:
            first_hotkey = hotkeys["data"]["availableHotkeys"][0]["hotkeyID"]
            await api.trigger_hotkey(first_hotkey)
            print(f"Triggered hotkey: {first_hotkey}")
            # for hotkey in hotkeys["data"]["availableHotkeys"]:
            #     id = hotkey['hotkeyID']
            #     await api.trigger_hotkey(id)
            #     print(f"Triggered hotkey: {id}")
            #     time.sleep(5)

    except ValueError as e:
        print(f"Error: {e}")
    finally:
        await api.close()


if __name__ == "__main__":
    asyncio.run(main())
