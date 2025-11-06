import pandas as pd

# Đọc dữ liệu đã làm sạch
def load_data():
    try:
        df = pd.read_csv("Data_Milk_CLEANED.csv", parse_dates=["time"])
        return df
    except Exception as e:
        print("Lỗi khi đọc dữ liệu:", e)
        return None


def run_queries():
    df = load_data()
    if df is None:
        return {"error": "Không thể đọc dữ liệu!"}

    results = {}

    # ===== 1) Xu hướng giá đóng cửa theo thời gian =====
    try:
        data_sorted = df.sort_values(["symbol", "time"])
        first_close = data_sorted.groupby("symbol")["close"].first()
        last_close = data_sorted.groupby("symbol")["close"].last()
        trend_pct = ((last_close - first_close) / first_close * 100).rename("Tăng trưởng (%)")
        results["query1_title"] = "1) Xu hướng giá đóng cửa theo thời gian"
        results["query1"] = trend_pct.reset_index().to_html(index=False, classes="data-table", border=0)
    except Exception as e:
        results["query1"] = f"Lỗi khi chạy câu 1: {e}"

    # ===== 2) Độ biến động giá (Volatility) =====
    try:
        df["range"] = df["high"] - df["low"]
        volatility = df.groupby("symbol")["range"].mean().rename("Biên độ TB")
        results["query2_title"] = "2) Độ biến động giá (Volatility)"
        results["query2"] = volatility.reset_index().to_html(index=False, classes="data-table", border=0)
    except Exception as e:
        results["query2"] = f"Lỗi khi chạy câu 2: {e}"

    # ===== 3) Khối lượng giao dịch bất thường =====
    try:
        mean_vol = df.groupby("symbol")["volume"].transform("mean")
        unusual_volume = df.loc[df["volume"] > 2 * mean_vol, ["time", "symbol", "volume"]]
        results["query3_title"] = "3) Khối lượng giao dịch bất thường (> 2× trung bình)"
        results["query3"] = unusual_volume.to_html(index=False, classes="data-table", border=0)
    except Exception as e:
        results["query3"] = f"Lỗi khi chạy câu 3: {e}"

    # ===== 4) Hiện tượng Break-out =====
    try:
        breakout_days = []
        for symbol, group in df.groupby("symbol"):
            group = group.sort_values("time")
            group["previous_high"] = group["high"].shift(1)
            condition = group["close"] > group["previous_high"]
            breakout = group.loc[condition, ["time", "symbol", "close", "high", "previous_high"]]
            breakout_days.append(breakout)
        breakout_df = pd.concat(breakout_days)
        results["query4_title"] = "4) Hiện tượng Break-out (Đóng cửa vượt đỉnh cũ)"
        results["query4"] = breakout_df.to_html(index=False, classes="data-table", border=0)
    except Exception as e:
        results["query4"] = f"Lỗi khi chạy câu 4: {e}"

    # ===== 5) Cổ phiếu “ổn định” =====
    try:
        stab = df.groupby("symbol").agg(
            range_std=("range", "std"),
            volume_std=("volume", "std")
        )
        stab["stability_score"] = stab["range_std"].rank() + stab["volume_std"].rank()
        stab_sorted = stab.sort_values("stability_score")
        results["query5_title"] = "5) Cổ phiếu ổn định (biến động giá thấp, khối lượng ổn định)"
        results["query5"] = stab_sorted.reset_index().to_html(index=False, classes="data-table", border=0)
    except Exception as e:
        results["query5"] = f"Lỗi khi chạy câu 5: {e}"

    return results
