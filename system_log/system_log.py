import psutil
import time
import logging

# ログの設定
logging.basicConfig(
    filename="system_monitor.log",
    level=logging.INFO,
    format="%(asctime)s - CPU: %(cpu_usage)s%% | RAM: %(ram_usage)s%% | Available RAM: %(available_ram)d MB",
)


def log_system_usage(interval=5):
    """
    指定した間隔 (秒) ごとに CPU 負荷率と RAM の使用状況をログに記録する
    """
    try:
        while True:
            cpu_usage = psutil.cpu_percent(interval=1)  # CPU 使用率 (1秒間の平均)
            ram_info = psutil.virtual_memory()
            ram_usage = ram_info.percent  # RAM 使用率
            available_ram = ram_info.available // (1024 * 1024)  # 利用可能なRAM (MB)

            logging.info(
                "",
                extra={
                    "cpu_usage": cpu_usage,
                    "ram_usage": ram_usage,
                    "available_ram": available_ram,
                }
            )

            print(f"CPU: {cpu_usage}% | RAM: {ram_usage}% | Available RAM: {available_ram} MB")
            time.sleep(interval)  # 次の測定まで待機

    except KeyboardInterrupt:
        print("\nログ記録を終了します。")


if __name__ == "__main__":
    log_system_usage(interval=5)
