# ============================================
# DỰ ÁN: PHÂN TÍCH NGÀNH SỮA VIỆT NAM (2020–2025)
# Xuất 2 file:
#   1. Data_Milk_RAW.csv – Dữ liệu gốc sau khi thu thập
#   2. Data_Milk_CLEANED.csv – Dữ liệu sau tiền xử lý
# ============================================

import os
import traceback
import pandas as pd
from datetime import datetime

# ==============================
# 1. Cấu hình ban đầu
# ==============================
SYMBOLS = ["VNM", "IDP", "MCM", "HNM", "QNS"]
START = "2020-01-01"
END = "2025-01-01"

# ==============================
# 2. Chuẩn hóa DataFrame
# ==============================
def _standardize_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.copy()

    # Đổi tên cột thời gian nếu cần
    if 'time' not in df.columns:
        if 'date' in df.columns:
            df.rename(columns={'date': 'time'}, inplace=True)
        elif 'Date' in df.columns:
            df.rename(columns={'Date': 'time'}, inplace=True)
        elif isinstance(df.index, pd.DatetimeIndex):
            df.reset_index(inplace=True)
            df.rename(columns={'index': 'time'}, inplace=True)

    # Đổi tên các cột chuẩn
    rename_map = {
        'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close',
        'Adj Close': 'adj_close', 'Volume': 'volume',
        'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume',
        'openPrice': 'open', 'highPrice': 'high', 'lowPrice': 'low',
        'closePrice': 'close', 'nmVolume': 'volume'
    }
    for k, v in rename_map.items():
        if k in df.columns and v not in df.columns:
            df.rename(columns={k: v}, inplace=True)

    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        df.dropna(subset=['time'], inplace=True)
        df.sort_values('time', inplace=True)

    return df

# ==============================
# 3. Hàm lấy dữ liệu vnstock
# ==============================
def fetch_vnstock_new(symbol, start, end):
    from vnstock import Vnstock
    stock = Vnstock().stock(symbol=symbol, source='VCI')
    df = stock.quote.history(start=start, end=end, interval='1D')
    return _standardize_df(df)

def fetch_vnstock_old(symbol, start, end):
    from vnstock import stock_historical_data
    df = stock_historical_data(symbol=symbol, start_date=start, end_date=end, resolution='1D', type='stock')
    return _standardize_df(df)

def robust_fetch(symbol, start, end):
    try:
        return fetch_vnstock_new(symbol, start, end)
    except Exception as e1:
        print(f"[{symbol}] API mới lỗi: {e1}")
        try:
            return fetch_vnstock_old(symbol, start, end)
        except Exception as e2:
            print(f"[{symbol}] API cũ cũng lỗi: {e2}")
            traceback.print_exc()
            return pd.DataFrame()

# ==============================
# 4. Hàm tiền xử lý dữ liệu
# ==============================
def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Tiền xử lý dữ liệu ngành sữa với in chi tiết kết quả từng bước để phục vụ báo cáo."""
    df = df.copy()
    print("=== BẮT ĐẦU TIỀN XỬ LÝ DỮ LIỆU ===")
    print(f"Tổng số dòng ban đầu: {len(df)}")
    print(df.head(), "\n")

    # 1. Loại bỏ trùng lặp & dòng thiếu giá trị chính
    before = len(df)
    df.drop_duplicates(subset=["symbol", "time"], inplace=True)
    print(f"[B1] Đã loại bỏ {before - len(df)} dòng trùng lặp (theo symbol + time)")
    print(f"→ Còn lại: {len(df)} dòng")
    print(df.head(), "\n")

    before = len(df)
    df.dropna(subset=["open", "high", "low", "close", "volume"], inplace=True)
    print(f"[B2] Đã loại bỏ {before - len(df)} dòng thiếu giá trị chính")
    print(f"→ Còn lại: {len(df)} dòng")
    print(df.head(), "\n")

    # 2. Chuyển kiểu dữ liệu
    print("[B3] Chuyển kiểu dữ liệu sang numeric...")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    print(df.dtypes, "\n")

    # 3. Loại bỏ giá trị âm
    before = len(df)
    df = df[(df["open"] >= 0) & (df["high"] >= 0) &
            (df["low"] >= 0) & (df["close"] >= 0) & (df["volume"] >= 0)]
    print(f"[B4] Đã loại bỏ {before - len(df)} dòng có giá trị âm")
    print(f"→ Còn lại: {len(df)} dòng\n")

    # 4. Chuẩn hóa thời gian
    print("[B5] Chuẩn hóa cột thời gian...")
    before = len(df)
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df.dropna(subset=["time"], inplace=True)
    df.sort_values(by=["symbol", "time"], inplace=True)
    print(f"-> Đã loại bỏ {before - len(df)} dòng có time không hợp lệ")
    print("Mẫu dữ liệu sau chuẩn hóa thời gian:")
    print(df.head(), "\n")

    # 5. Tạo thêm các cột hỗ trợ
    df["range"] = df["high"] - df["low"]
    df["return"] = (df["close"] - df["open"]) / df["open"]
    print("[B6] Đã tạo thêm cột range & return")
    print(df[["symbol", "time", "open", "close", "range", "return"]].head(), "\n")

    # 6. Reset index
    df.reset_index(drop=True, inplace=True)
    print("[B7] Reset lại index\n")

    print("=== TIỀN XỬ LÝ HOÀN TẤT ===")
    print(f"Số mã cổ phiếu: {df['symbol'].nunique()}")
    print(f"Tổng số dòng sau xử lý: {len(df)}")
    print("Danh sách mã:", sorted(df['symbol'].unique()))
    print("=" * 70)

    return df
# ==============================
# 5. Chương trình chính
# ==============================
def main():
    all_data = []
    print("=== BẮT ĐẦU: Lấy dữ liệu ngành sữa (2020–2025) ===")

    for sym in SYMBOLS:
        print(f"\n>>> Đang tải {sym} ...")
        df = robust_fetch(sym, START, END)
        if df.empty:
            print(f"[{sym}] Không có dữ liệu.")
            continue

        keep_cols = [c for c in ['time', 'open', 'high', 'low', 'close', 'volume'] if c in df.columns]
        df = df[keep_cols]
        df['symbol'] = sym
        all_data.append(df)
        print(f"[{sym}] Hoàn tất ({len(df)} dòng).")

    # --- Gộp toàn bộ ---
    if not all_data:
        print("Không có dữ liệu nào được tải.")
        return

    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df.sort_values(by=['symbol', 'time'], inplace=True)

    # --- Đưa cột symbol lên đầu ---
    raw_cols = ['symbol'] + [c for c in combined_df.columns if c != 'symbol']
    combined_df = combined_df[raw_cols]

    # --- Xuất file trước tiền xử lý ---
    raw_file = "Data_Milk_RAW.csv"
    combined_df.to_csv(raw_file, index=False, encoding="utf-8-sig")
    print(f"\nĐã lưu file thô: {raw_file} ({len(combined_df)} dòng)")

    # --- Tiền xử lý dữ liệu ---
    cleaned_df = preprocess_data(combined_df)

    # --- Đưa cột symbol lên đầu (sau khi xử lý) ---
    clean_cols = ['symbol'] + [c for c in cleaned_df.columns if c != 'symbol']
    cleaned_df = cleaned_df[clean_cols]

    # --- Xuất file sau tiền xử lý ---
    cleaned_file = "Data_Milk_CLEANED.csv"
    cleaned_df.to_csv(cleaned_file, index=False, encoding="utf-8-sig")

    print(f"\nĐã lưu file sau tiền xử lý: {cleaned_file}")
    print(f"Tổng số dòng sau xử lý: {len(cleaned_df)}")
    print("\nXem trước 10 dòng đầu tiên sau xử lý:")
    print(cleaned_df.head(10))

# ==============================
# 6. Chạy chương trình
# ==============================
if __name__ == "__main__":
    main()
