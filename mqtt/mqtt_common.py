import paho.mqtt.client as mqtt

host = "broker.emqx.io"
port = 1883


def on_connect(client, userdata, flags, reason_code, properties):
    """
    接続時のコールバック関数
    """
    if reason_code == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", reason_code)


def on_message(client, userdata, msg):
    """
    サブスクライブ時のコールバック関数
    """
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")


def connect_mqtt(host: str, port: int):
    """
    ブローカーへの接続
    """
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    # コールバック関数を登録
    client.on_connect = on_connect
    client.on_message = on_message

    # ブローカーに接続
    client.connect(host, port, 60)
    return client
