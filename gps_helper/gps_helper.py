import time
from gps3 import gps3
from queue import Queue


class GPS:
    def __init__(self):
        self.gps_socket = gps3.GPSDSocket()
        self.data_stream = gps3.DataStream()
        self.running = False
        self.data_queue = Queue(maxsize=1)  # 最新データのみ保持

    def start(self):
        print("Receiving GPS data...")
        self.gps_socket.connect()
        self.gps_socket.watch()

    def get_data(self):
        new_data = self.gps_socket.next()
        if new_data:
            self.data_stream.unpack(new_data)
            latitude = self.data_stream.TPV['lat']
            longitude = self.data_stream.TPV['lon']
            time_gps = self.data_stream.TPV['time']
            return latitude, longitude, time_gps

    def stop(self):
        self.gps_socket.close()


if __name__ == '__main__':
    gps = GPS()

    try:
        while True:
            gps.start()
            data = gps.get_data()
            if data:
                lat, lng, t_gps = data
                print(f"Latitude: {lat}, Longitude: {lng}, Time: {t_gps}")
            else:
                print("No new GPS data available.")
            gps.stop()
            time.sleep(5)  # 他の処理も考慮して適切な間隔でループ
    except KeyboardInterrupt:
        gps.stop()
        print('!!FINISH!!')
