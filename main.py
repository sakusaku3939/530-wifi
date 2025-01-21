import hashlib

import pywifi
import subprocess
import platform
import time
from datetime import datetime

from gps.gps import GPS
from mqtt.mqtt_common import connect_mqtt, host, port
from mqtt.publisher import publish


def scan_wifi_networks(interface):
    """
    指定されたインターフェースでWi-Fiネットワークをスキャンし、結果を返す。
    """
    try:
        if platform.system().lower() == 'linux':
            # Linuxの場合はwpa_supplicantでWi-Fiスキャンをトリガーしておく
            subprocess.run(["sudo", "wpa_cli", "scan"], check=True)
            time.sleep(0.5)
        else:
            # Windowsなどの場合はPyWiFiのscan()メソッドを使う
            interface.scan()
    except Exception as e:
        print(f"Error while starting scan: {e}")
        return []

    networks = []
    results = interface.scan_results()

    if not results:
        print(f"{datetime.now().isoformat(sep=' ', timespec='milliseconds')}: No networks found yet.")
    else:
        networks = [
            {
                "bssid": net.bssid,
                "signal": net.signal,
                "ssid": net.ssid,
                "key": net.key,
                "id": net.id,
                "cipher": net.cipher,
                "freq": net.freq,
                "auth": net.auth,
                "akm": net.akm,
            }
            for net in results
        ]

    # シグナル強度でソート
    networks.sort(key=lambda x: x["signal"], reverse=True)

    # 重複を削除
    networks = list({v["bssid"]: v for v in networks}.values())

    return networks


def main():
    try:
        wifi = pywifi.PyWiFi()
        interfaces = wifi.interfaces()
        if not interfaces:
            print("No Wi-Fi interfaces found.")
            return

        interface = interfaces[-1]  # 最後のインターフェースを使う
        print(f"Scanning on interface: {interface.name()}\n")

        # MQTTブローカーに接続
        client = connect_mqtt(host, port)

        # GPSデータを取得
        gps = GPS()
        gps.start()

        try:
            # スキャンを2秒間隔で繰り返し実行
            while True:
                networks = scan_wifi_networks(interface)

                if networks:
                    print(f"Found {len(networks)} networks:")
                    for network in networks:
                        print(f"SSID: {network['ssid']}, BSSID: {network['bssid']}, Signal: {network['signal']}")
                    print("-" * 20)

                    # GPSデータを取得
                    gps_data = gps.get_data()

                    if gps_data:
                        latitude, longitude, time_gps = gps_data

                        if latitude == 'n/a' or longitude == 'n/a':
                            print("No GPS data available.")
                            continue

                        print(f"Latitude: {latitude}, Longitude: {longitude}, Time: {time_gps}\n")

                        # BSSIDをハッシュ化して16進数文字列に変換
                        hashed_bssid = [hashlib.sha256(network["bssid"].encode()).hexdigest() for network in
                                        networks]
                        split_hashed_bssid = ",".join(hashed_bssid)

                        # MQTTブローカーに送信
                        message = f"{latitude},{longitude},{split_hashed_bssid}".encode("utf-8")
                        publish(client, message)
                    else:
                        print("No GPS data available.")
                else:
                    print("No networks found.")

                print("\n")
                time.sleep(2)
        except KeyboardInterrupt:
            print('!!FINISH!!')
            gps.close()
            client.disconnect()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
