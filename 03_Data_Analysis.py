import pandas as pd
import numpy as np

# ===== 0) Đọc dữ liệu =====
data = pd.read_csv("Data_Milk_CLEANED.csv")
data["time"] = pd.to_datetime(data["time"])
data = data.sort_values(["symbol", "time"])

# ===== 1) Xu hướng giá đóng cửa theo thời gian =====
first_close = data.groupby("symbol")["close"].first()
last_close  = data.groupby("symbol")["close"].last()
trend_pct   = ((last_close - first_close) / first_close).rename("trend_pct")

# ===== 2) Độ biến động giá (High−Low) lớn nhất =====
volatility_max = data.groupby("symbol")["range"].max()

# ===== 3) Khối lượng giao dịch bất thường (>2×TB) =====
mean_vol = data.groupby("symbol")["volume"].transform("mean")
unusual_volume = data.loc[data["volume"] > 2 * mean_vol, ["time", "symbol", "volume"]]

# ===== 4) Hiện tượng Break-out =====
# Ngày giá đóng cửa vượt đỉnh cũ (new high)
data["prev_max"] = data.groupby("symbol")["close"].transform(lambda s: s.cummax().shift(1))
data["breakout"] = data["close"] > data["prev_max"]

# Tính số ngày break-out liên tiếp (chuỗi)
tmp = data[["symbol", "breakout"]].copy()
tmp["block"] = tmp.groupby("symbol")["breakout"].transform(lambda s: (~s).cumsum())
streaks = (
    tmp[tmp["breakout"]]
    .groupby(["symbol", "block"])
    .size()
    .groupby("symbol").max()
    .fillna(0).astype(int)
)

# Mã có chuỗi break-out ≥3 ngày liên tiếp
breakout_3plus = streaks[streaks >= 3].sort_values(ascending=False)

# ===== 5) Cổ phiếu “ổn định” =====
stab = data.groupby("symbol").agg(range_std=("range", "std"), volume_std=("volume", "std"))
stab["stability_score"] = stab["range_std"].rank() + stab["volume_std"].rank()
most_stable_symbol = stab["stability_score"].idxmin()

# ===== In kết quả =====
print("1) Xu hướng giá đóng cửa (% thay đổi toàn kỳ):\n", trend_pct, "\n")
print("2) Biên độ giá (High−Low) lớn nhất:\n", volatility_max, "\n")
print("3) Ngày Volume tăng bất thường (10 dòng đầu):\n", unusual_volume.head(10), "\n")
print("4) Hiện tượng Break-out:")
print("   Số ngày liên tiếp lập đỉnh (streak):\n", streaks, "\n")
print("   Mã có ≥3 ngày break-out liên tiếp:\n", breakout_3plus, "\n")
print("5) Cổ phiếu ổn định (std range/volume & điểm):\n", stab, "\n",
      "   Mã ổn định nhất:", most_stable_symbol, "\n")
