from gps3 import gps3
import time


def get_gps_data():
    gps_socket = gps3.GPSDSocket()
    data_stream = gps3.DataStream()
    gps_socket.connect()
    gps_socket.watch()

    try:
        print("Receiving GPS data...")

        while True:
            new_data = gps_socket.next()
            if new_data:
                data_stream.unpack(new_data)
                latitude = data_stream.TPV['lat']
                longitude = data_stream.TPV['lon']
                time_gps = data_stream.TPV['time']
                print(f"Latitude: {latitude}, Longitude: {longitude}, Time: {time_gps}")

            time.sleep(1)

    except KeyboardInterrupt:
        print('!!FINISH!!')


if __name__ == '__main__':
    get_gps_data()
