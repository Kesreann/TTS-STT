import websocket
import json


# Define the plugin name and developer
plugin_name = "test"  # Replace with your actual plugin name
developer_name = "tester"  # Replace with your actual developer name


# WebSocket event handlers
def on_message(ws, message):
    response = json.loads(message)
    print(f"Received: {response}")
    res1 = request_permission(ws)
    token = res1['data']['authenticationToken']
    request_auth_token(ws, token)
    move_model(ws, token)

    print(response)


def on_error(ws, error):
    print("Error:", error)


def on_close(ws, close_status_code, close_msg):
    print("Connection closed")


def on_open(ws):
    print("Connection established.")
    check_api_state(ws)


def check_api_state(ws):
    request = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": "1.0",
        "requestID": "StateCheck1",
        "messageType": "APIStateRequest"
    }
    ws.send(json.dumps(request))


def request_auth_token(ws):
    request = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": "1.0",
        "requestID": "AuthTokenRequest1",
        "messageType": "AuthenticationTokenRequest",
        "data": {
            "pluginName": plugin_name,
            "pluginDeveloper": developer_name,
            # Include other necessary fields here
        }
    }
    ws.send(json.dumps(request))  # Request the authentication token


def request_authentication(ws, token):
    request = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": "1.0",
        "requestID": "AuthRequest1",
        "messageType": "AuthenticationRequest",
        "data": {
            "token": token  # Include the received authentication token
        }
    }
    ws.send(json.dumps(request))  # Send the authentication request with token


def request_permission(ws, token):
    request = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": "1.0",
        "requestID": "PermissionRequest1",
        "messageType": "PermissionRequest",
        "data": {
            "requestedPermission": "LoadCustomImagesAsItems",
            "token": token
        }
    }
    ws.send(json.dumps(request))  # Request permission to load custom images


def move_model(ws, token):
    request = {
        "apiName": "VTubeStudioPublicAPI",
        "apiVersion": "1.0",
        "requestID": "MoveModel1",
        "messageType": "MoveModelRequest",
        "data": {
            "timeInSeconds": 0.2,
            "valuesAreRelativeToModel": False,
            "positionX": 0.1,
            "positionY": -0.7,
            "rotation": 16.3,
            "size": -22.5,
            "token": token
        }
    }
    ws.send(json.dumps(request))  # Send the model movement request


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8001",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
