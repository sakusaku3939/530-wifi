import os

import psutil
import time
import csv
from datetime import datetime

from running import Running

# CSV出力
csv_path = "log_system_monitor"
os.makedirs(csv_path, exist_ok=True)
csv_filename =  os.path.join(csv_path, f"{time.strftime('%Y%m%d_%H%M%S')}.csv")


# CSVヘッダーを書き込む（ファイルが存在しない場合のみ）
def initialize_csv():
    try:
        with open(csv_filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "cpu_usage", "cpu_freq_mhz", "ram_usage", "available_ram"])
    except FileExistsError:
        pass  # 既にファイルがある場合は何もしない


# ログの記録を開始
def log_system_usage(interval=1):
    initialize_csv()  # CSVのヘッダーを初期化

    try:
        while Running.is_run():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 現在時刻
            cpu_usage = psutil.cpu_percent(interval=1)  # CPU 使用率
            cpu_freq = psutil.cpu_freq().current  # CPU周波数 (MHz)
            ram_info = psutil.virtual_memory()
            ram_usage = ram_info.percent  # RAM 使用率
            available_ram = ram_info.available // (1024 * 1024)  # 利用可能なRAM (MB)

            # CSVファイルに追記
            with open(csv_filename, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, cpu_usage, cpu_freq, ram_usage, available_ram])

            print(
                f"{timestamp} | CPU: {cpu_usage}% | Freq: {cpu_freq} MHz | RAM: {ram_usage}% | Available RAM: {available_ram} MB")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nログ記録を終了します。")


if __name__ == "__main__":
    log_system_usage(interval=1)
