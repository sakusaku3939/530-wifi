import gps

# GPSセッションを開始
session = gps.gps_helper(mode=gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

print("リアルタイムで緯度・経度を取得中...（Ctrl+Cで終了）")
try:
    while True:
        # 次のGPSデータを取得
        report = session.next()
        # 緯度・経度が含まれるTPVデータをチェック
        if report['class'] == 'TPV':
            if hasattr(report, 'lat') and hasattr(report, 'lon'):
                print(f"緯度: {report.lat}, 経度: {report.lon}")
except KeyboardInterrupt:
    print("終了しました。")
except Exception as e:
    print(f"エラーが発生しました: {e}")
