from time import sleep

from gpsdclient import GPSDClient

# GPSDクライアントを初期化
client = GPSDClient(host="127.0.0.1", port=2947)

print("リアルタイムで緯度・経度を取得中...（Ctrl+Cで終了）")
try:
    for result in client.dict_stream():
        if "lat" in result and "lon" in result:
            print(f"緯度: {result['lat']}, 経度: {result['lon']}")
        sleep(1)
except KeyboardInterrupt:
    print("終了しました。")
