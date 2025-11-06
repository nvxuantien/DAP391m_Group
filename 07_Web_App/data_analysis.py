import pandas as pd
from data_loader import load_data

def analyze_stock(symbol):
    """Trả về phân tích cơ bản: xu hướng, độ biến động, khối lượng TB, ngày rủi ro"""
    df = load_data()
    if df is None or symbol not in df["symbol"].unique():
        return None

    df_symbol = df[df["symbol"] == symbol].copy().sort_values("time")
    df_symbol["range"] = df_symbol["high"] - df_symbol["low"]

    trend = "tăng" if df_symbol["close"].iloc[-1] > df_symbol["close"].iloc[0] else "giảm"
    volatility = df_symbol["range"].mean()
    avg_volume = df_symbol["volume"].mean()
    max_day = df_symbol.loc[df_symbol["range"].idxmax(), "time"]

    return {
        "symbol": symbol,
        "trend": trend,
        "volatility": round(volatility, 2),
        "avg_volume": int(avg_volume),
        "max_risk_day": str(max_day.date())
    }
