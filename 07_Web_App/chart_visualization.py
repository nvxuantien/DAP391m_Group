import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ------------------------
# 1. Đường dẫn file và thư mục lưu
# ------------------------
DATA_PATH = "Data_Milk_CLEANED.csv"
CHART_FOLDER = "static/charts"   # Lưu trực tiếp vào static/charts

# ------------------------
# 2. Đọc dữ liệu
# ------------------------
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values(["symbol", "time"]).reset_index(drop=True)

    # Bổ sung cột nếu thiếu
    if "range" not in df.columns:
        df["range"] = df["high"] - df["low"]
    if "daily_return" not in df.columns:
        df["daily_return"] = df["close"] - df["open"]

    # Loại bỏ hàng rỗng
    df = df.dropna(subset=["open", "high", "low", "close", "volume"])
    return df

# ------------------------
# 3. Hàm lưu biểu đồ
# ------------------------
def save_chart(fig, name):
    os.makedirs(CHART_FOLDER, exist_ok=True)
    path = os.path.join(CHART_FOLDER, name)
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)

# ------------------------
# 4. Sinh toàn bộ biểu đồ
# ------------------------
def generate_all_charts():
    df = load_data()
    os.makedirs(CHART_FOLDER, exist_ok=True)

    # 1. Xu hướng giá đóng cửa
    fig, ax = plt.subplots(figsize=(10,5))
    sns.lineplot(data=df, x="time", y="close", hue="symbol", ax=ax)
    ax.set_title("Xu hướng giá đóng cửa (2020–2025)")
    save_chart(fig, "1_xu_huong_gia_dong_cua.png")

    # 2. Biến động giá (High−Low)
    fig, ax = plt.subplots(figsize=(10,5))
    sns.lineplot(data=df, x="time", y="range", hue="symbol", ax=ax)
    ax.set_title("Biến động giá (High−Low)")
    save_chart(fig, "2_bien_dong_gia.png")

    # 3. Trung bình giá Mở/Đóng
    avg = df.groupby("symbol")[["open","close"]].mean().reset_index()
    fig, ax = plt.subplots(figsize=(8,5))
    avg.plot(kind="bar", x="symbol", ax=ax)
    ax.set_title("So sánh trung bình giá Mở và Đóng")
    save_chart(fig, "3_trung_binh_open_close.png")

    # 4. Tăng trưởng giá (%)
    trend = df.groupby("symbol").agg(first=("close","first"), last=("close","last"))
    trend["trend_pct"] = (trend["last"] - trend["first"]) / trend["first"] * 100
    fig, ax = plt.subplots(figsize=(8,5))
    trend["trend_pct"].sort_values().plot(kind="barh", color="green", ax=ax)
    ax.set_title("Tăng trưởng giá (%) 2020–2025")
    save_chart(fig, "4_tang_truong_gia.png")

    # 5. Phân bố khối lượng
    fig, ax = plt.subplots(figsize=(8,5))
    sns.histplot(df["volume"], bins=50, color="orange", ax=ax)
    ax.set_title("Phân bố khối lượng giao dịch")
    save_chart(fig, "5_phan_bo_khoi_luong.png")

    # 6. Giá cao nhất
    max_high = df.groupby("symbol")["high"].max()
    fig, ax = plt.subplots(figsize=(8,5))
    max_high.plot(kind="bar", color="red", ax=ax)
    ax.set_title("Giá cao nhất (High)")
    save_chart(fig, "6_gia_cao_nhat.png")

    # 7. Giá thấp nhất
    min_low = df.groupby("symbol")["low"].min()
    fig, ax = plt.subplots(figsize=(8,5))
    min_low.plot(kind="bar", color="teal", ax=ax)
    ax.set_title("Giá thấp nhất (Low)")
    save_chart(fig, "7_gia_thap_nhat.png")

    # 8. Khối lượng theo thời gian
    fig, ax = plt.subplots(figsize=(10,5))
    sns.lineplot(data=df, x="time", y="volume", hue="symbol", ax=ax)
    ax.set_title("Khối lượng giao dịch theo thời gian")
    save_chart(fig, "8_khoi_luong_theo_thoi_gian.png")

    # 9. Lợi nhuận nội ngày
    fig, ax = plt.subplots(figsize=(10,5))
    sns.lineplot(data=df, x="time", y="daily_return", hue="symbol", ax=ax)
    ax.set_title("Lợi nhuận nội ngày (Close−Open)")
    save_chart(fig, "9_loi_nhuan_noi_ngay.png")

    # 10. Tương quan Open–Close
    fig, ax = plt.subplots(figsize=(6,6))
    sns.scatterplot(data=df, x="open", y="close", hue="symbol", ax=ax)
    ax.set_title("Tương quan giữa giá Mở và giá Đóng")
    save_chart(fig, "10_tuong_quan_open_close.png")

    # 11. Tương quan Range–Volume
    fig, ax = plt.subplots(figsize=(6,6))
    sns.scatterplot(data=df, x="range", y="volume", hue="symbol", ax=ax)
    ax.set_title("Tương quan Biên độ giá và Khối lượng")
    save_chart(fig, "11_tuong_quan_biendo_volume.png")

    # 12. Trung vị giá đóng cửa
    median_close = df.groupby("symbol")["close"].median()
    fig, ax = plt.subplots(figsize=(8,5))
    median_close.sort_values().plot(kind="barh", color="limegreen", ax=ax)
    ax.set_title("Giá đóng cửa trung vị (Median Close)")
    save_chart(fig, "12_trung_vi_close.png")

    print(f" Tất cả biểu đồ đã được lưu tại thư mục: '{CHART_FOLDER}'")

# ------------------------
# 5. Chạy độc lập
# ------------------------
if __name__ == "__main__":
    generate_all_charts()
