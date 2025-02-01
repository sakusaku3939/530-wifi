import hashlib
import threading

import pywifi
import subprocess
import platform
import time
from datetime import datetime

from gps_helper.gps_helper import GPSHelper
from mqtt.mqtt_common import connect_mqtt, host, port
from mqtt.publisher import publish
from running import Running
from system_log.system_log import log_system_usage

SCAN_INTERVAL = 4
INTERFACE_NAME = "wlan1"


def scan_wifi_networks(interface):
    """
    指定されたインターフェースでWi-Fiネットワークをスキャンし、結果を返す。
    """
    try:
        if platform.system().lower() == 'linux':
            # Linuxの場合はwpa_supplicantでWi-Fiスキャンをトリガーしておく
            subprocess.run(["sudo", "wpa_cli", "-i", INTERFACE_NAME, "scan"], check=True)
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
        # システムログを別スレッドで記録
        log_thread = threading.Thread(target=log_system_usage, daemon=True)
        log_thread.start()

        wifi = pywifi.PyWiFi()
        interfaces = wifi.interfaces()
        if not interfaces:
            print("No Wi-Fi interfaces found.")
            return

        # wlan1を指定
        interface = None
        for i in interfaces:
            if i.name() == INTERFACE_NAME:
                interface = i
                break

        print(f"Scanning on interface: {interface.name()}\n")

        # MQTTブローカーに接続
        client = connect_mqtt(host, port)

        # GPSデータを初回取得
        gps = GPSHelper()
        gps.start()
        data = gps.get_latest_data()
        if data:
            lat, lng, t_gps = data
            print(f"Succeeded to get GPS data: Latitude: {lat}, Longitude: {lng}, Time: {t_gps}")
        else:
            print("No new GPS data available.")
            gps.stop()
            client.disconnect()
            return  # GPSデータがない場合は終了

        # Wi-FI BSSIDとRSSIのキャッシュ
        rssi_cache_map = {}

        try:
            # スキャンを5秒間隔で繰り返し実行
            while True:
                print("\n")
                networks = scan_wifi_networks(interface)

                if networks:
                    print(f"Found {len(networks)} networks:")
                    for network in networks:
                        print(f"SSID: {network['ssid']}, BSSID: {network['bssid']}, Signal: {network['signal']}")
                    print("-" * 20)

                    # GPSデータを取得
                    gps_data = gps.get_latest_data()

                    if gps_data:
                        latitude, longitude, time_gps = gps_data

                        if latitude == 'n/a' or longitude == 'n/a':
                            print("GPS data is N/A.")
                            continue

                        print(f"Latitude: {latitude}, Longitude: {longitude}, Time: {time_gps}\n")

                        # キャッシュに存在するRSSIよりも強い信号のみを送信
                        networks_to_update = [network for network in networks if
                                              rssi_cache_map.get(network["bssid"], -100) < network["signal"]]

                        # キャッシュを更新
                        rssi_cache_map.update({network["bssid"]: network["signal"] for network in networks_to_update})

                        if not networks_to_update:
                            print("No new networks found.")
                            time.sleep(SCAN_INTERVAL)
                            continue

                        # BSSIDをハッシュ化して16進数文字列に変換
                        hashed_bssid = [hashlib.sha256(network["bssid"].encode()).hexdigest() for network in
                                        networks_to_update]
                        split_hashed_bssid = ",".join(hashed_bssid)

                        # MQTTブローカーに送信
                        message = f"{latitude},{longitude},{split_hashed_bssid}".encode("utf-8")
                        publish(client, message)
                    else:
                        print("No GPS data available.")
                else:
                    print("No networks found.")

                time.sleep(SCAN_INTERVAL)

        except KeyboardInterrupt:
            print('!!FINISH!!')
            Running.stop()
            gps.stop()
            client.disconnect()
            log_thread.join()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
