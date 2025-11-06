import pandas as pd
import os

DATA_PATH = "Data_Milk_CLEANED.csv"

def load_data():
    """Đọc dữ liệu chính của cổ phiếu"""
    if not os.path.exists(DATA_PATH):
        print(f"Không tìm thấy file {DATA_PATH}")
        return None
    try:
        df = pd.read_csv(DATA_PATH)
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"])
        return df
    except Exception as e:
        print("Lỗi khi đọc dữ liệu:", e)
        return None

def get_symbols():
    """Trả về danh sách mã cổ phiếu"""
    df = load_data()
    if df is not None and "symbol" in df.columns:
        return df["symbol"].unique().tolist()
    return []

def get_stock_data(symbol, start=None, end=None):
    """Lọc dữ liệu theo mã cổ phiếu và thời gian"""
    df = load_data()
    if df is None or "symbol" not in df.columns:
        return None
    df = df[df["symbol"] == symbol].sort_values("time")
    if start:
        df = df[df["time"] >= pd.to_datetime(start)]
    if end:
        df = df[df["time"] <= pd.to_datetime(end)]
    return df if not df.empty else None

def get_latest_info(symbol):
    """Lấy thông tin mới nhất (giá, thay đổi, volume, RSI)"""
    df = get_stock_data(symbol)
    if df is None or df.empty:
        return None
    current_price = float(df["close"].iloc[-1])
    prev_price = float(df["close"].iloc[-2]) if len(df) > 1 else current_price
    change = current_price - prev_price
    rsi = 50 + (current_price - df["close"].mean()) / 2
    return {
        "price": current_price,
        "change": change,
        "volume": int(df["volume"].iloc[-1]),
        "rsi": round(rsi, 2)
    }
