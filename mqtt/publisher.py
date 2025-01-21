from mqtt.mqtt_common import host, port, connect_mqtt
from datetime import datetime
import time

topic = "530-citizen-test/mqtt-732435"


def publish(client, message):
    result = client.publish(topic, message)

    status = result[0]
    if status == 0:
        print(f"MQTT Successfully send to topic `{topic}`")
    else:
        print(f"Fails to send message to topic `{topic}`")


def run():
    client = connect_mqtt(host, port)

    for i in range(5):
        data = f"Message {i}"
        timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        message = f"{data},{timestamp}".encode("utf-8")

        publish(client, message)
        time.sleep(1)


if __name__ == "__main__":
    run()
