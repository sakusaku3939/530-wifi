from gps3 import gps3


def main():
    # gpsdソケットを接続
    gps_socket = gps3.GPSDSocket()
    data_stream = gps3.DataStream()
    gps_socket.connect()
    gps_socket.watch()

    try:
        print("Receiving GPS data...")
        for new_data in gps_socket:
            if new_data:
                data_stream.unpack(new_data)
                latitude = data_stream.TPV['lat']
                longitude = data_stream.TPV['lon']
                altitude = data_stream.TPV['alt']

                # データが取得できた場合に出力
                print(f"Latitude: {latitude}, Longitude: {longitude}, Altitude: {altitude}")
    except KeyboardInterrupt:
        print("\n終了します")


if __name__ == "__main__":
    main()
