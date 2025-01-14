from gps3 import gps3


def get_gps_data():
    gps_socket = gps3.GPSDSocket()
    data_stream = gps3.DataStream()
    gps_socket.connect()
    gps_socket.watch()

    for new_data in gps_socket:
        if new_data:
            data_stream.unpack(new_data)
            time = data_stream.TPV['time']
            lat = data_stream.TPV['lat']
            lon = data_stream.TPV['lon']
            print('time : ', time)
            print('lat : ', lat)
            print('lon : ', lon)
            return time, lat, lon


if __name__ == '__main__':
    get_gps_data()
