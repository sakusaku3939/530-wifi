import pywifi
import time
from datetime import datetime


def scan_wifi_networks(interface, timeout=5):
    """
    指定されたインターフェースでWi-Fiネットワークをスキャンし、結果を返す。
    """
    try:
        interface.scan()
    except Exception as e:
        print(f"Error while starting scan: {e}")
        return []

    start_time = time.time()
    networks = []

    while time.time() < start_time + timeout:
        results = interface.scan_results()
        if not results:
            print(f"{datetime.now().isoformat(sep=' ', timespec='milliseconds')}: No networks found yet.")
            time.sleep(0.5)
            # timeout秒まで0.5秒間隔で再スキャンし、結果が得られなかった場合は空リストを返す
            continue
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
            break

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

        for interface in interfaces:
            print(f"Scanning on interface: {interface.name()}\n")
            networks = scan_wifi_networks(interface)

            if networks:
                print(f"Found {len(networks)} networks:")
                for network in networks:
                    print(f"SSID: {network['ssid']}, BSSID: {network['bssid']}, Signal: {network['signal']}")
            else:
                print("No networks found.")

            print("\n")

    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
