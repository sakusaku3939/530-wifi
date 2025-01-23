import time
from gps3 import gps3


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

    def stop(self):
        self.gps_socket.close()


if __name__ == '__main__':
    # gps = GPS()

    try:
        gps_socket = gps3.GPSDSocket()
        data_stream = gps3.DataStream()
        gps_socket.connect()
        gps_socket.watch()

        for new_data in gps_socket:
            if new_data:
                data_stream.unpack(new_data)
                print('time : ', data_stream.TPV['time'])
                print('lat : ', data_stream.TPV['lat'])
                print('lon : ', data_stream.TPV['lon'])
                print('alt : ', data_stream.TPV['alt'])
                print('speed : ', data_stream.TPV['speed'])

    except KeyboardInterrupt:
        # gps.stop()
        print('!!FINISH!!')
