import threading
import time
from gps3 import gps3
from queue import Queue


class GPS:
    def __init__(self):
        self.gps_socket = gps3.GPSDSocket()
        self.data_stream = gps3.DataStream()
        self.running = False
        self.data_queue = Queue()

    def start(self):
        """GPSデータの取得を開始する"""
        self.running = True
        self.gps_socket.connect()
        self.gps_socket.watch()
        threading.Thread(target=self._read_data, daemon=True).start()

    def _read_data(self):
        """バックグラウンドでGPSデータを取得する"""
        while self.running:
            try:
                new_data = self.gps_socket.next()
                if new_data:
                    self.data_stream.unpack(new_data)
                    latitude = self.data_stream.TPV.get('lat', 'n/a')
                    longitude = self.data_stream.TPV.get('lon', 'n/a')
                    time_gps = self.data_stream.TPV.get('time', 'n/a')

                    # データが有効な場合のみキューに追加
                    if latitude != 'n/a' and longitude != 'n/a':
                        self.data_queue.put((latitude, longitude, time_gps))
            except Exception as e:
                print(f"Error retrieving GPS data: {e}")
            time.sleep(1)  # データがない場合は少し待機

    def get_latest_data(self):
        """キューから最新のGPSデータを取得する"""
        try:
            return self.data_queue.get_nowait()  # 最新データを取得
        except Exception as e:
            print(f"No GPS data available: {e}")  # エラーがあれば表示
            return None  # データがない場合はNoneを返す

    def stop(self):
        """GPSデータ取得を停止する"""
        self.running = False
        self.gps_socket.close()


if __name__ == '__main__':
    gps = GPS()
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
