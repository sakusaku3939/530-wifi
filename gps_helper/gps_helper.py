import threading
import time
from gps3 import gps3
from queue import Queue


class GPSHelper:
    def __init__(self):
        self.gps_socket = gps3.GPSDSocket()
        self.data_stream = gps3.DataStream()
        self.running = False
        self.data_queue = Queue(maxsize=1)  # 最新データのみ保持

    def start(self):
        """GPSデータの取得を開始する"""
        self.running = True
        self.gps_socket.connect()
        self.gps_socket.watch()
        threading.Thread(target=self._read_data, daemon=True).start()

    def _read_data(self):
        """バックグラウンドでGPSデータを取得する"""
        last_lat, last_lng = None, None  # 最後に取得した値を記録
        while self.running:
            try:
                new_data = self.gps_socket.next()
                if new_data:
                    self.data_stream.unpack(new_data)
                    latitude = self.data_stream.TPV.get('lat', 'n/a')
                    longitude = self.data_stream.TPV.get('lon', 'n/a')
                    time_gps = self.data_stream.TPV.get('time', 'n/a')

                    # データが有効であり、更新されている場合のみキューに追加
                    if self.data_queue.full():  # キューが満杯の場合、古いデータを破棄
                        self.data_queue.get()
                    self.data_queue.put((latitude, longitude, time_gps))
            except Exception as e:
                print(f"Error retrieving GPS data: {e}")
            time.sleep(1)  # 次のデータ取得を待つ

    def get_latest_data(self):
        """キューから最新のGPSデータを取得する"""
        while True:
            try:
                return self.data_queue.get(timeout=2)  # データが来るまで最大2秒待つ
            except Exception as e:
                print(f"Waiting for GPS data...: ({e})")
                continue

    def stop(self):
        """GPSデータ取得を停止する"""
        self.running = False
        self.gps_socket.close()


if __name__ == '__main__':
    gps = GPSHelper()
    gps.start()

    try:
        while True:
            data = gps.get_latest_data()
            if data:
                lat, lng, t_gps = data
                print(f"Latitude: {lat}, Longitude: {lng}, Time: {t_gps}")
            else:
                print("No new GPS data available.")
            time.sleep(1)  # 他の処理も考慮して適切な間隔でループ
    except KeyboardInterrupt:
        gps.stop()
        print('!!FINISH!!')
