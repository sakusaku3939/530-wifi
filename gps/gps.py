from gps3 import gps3
import time


class GPS:
    def __init__(self):
        self.gps_socket = gps3.GPSDSocket()
        self.data_stream = gps3.DataStream()

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

    def close(self):
        self.gps_socket.close()


if __name__ == '__main__':
    gps = GPS()
    gps.start()

    try:
        while True:
            data = gps.get_data()
            if data:
                print(f"Latitude: {data[0]}, Longitude: {data[1]}, Time: {data[2]}")
            time.sleep(1)
    except KeyboardInterrupt:
        gps.close()
        print('!!FINISH!!')
