import joblib
import numpy as np
from pathlib import Path
from data_loader import get_stock_data

MODEL_DIR = Path("models")

def predict_price(symbol, model_name="random_forest"):
    """Dự đoán giá cổ phiếu dựa vào mô hình đã huấn luyện"""
    df = get_stock_data(symbol)
    if df is None or len(df) < 10:
        return None, "Không đủ dữ liệu để dự đoán."

    X_latest = df[["open", "high", "low", "volume"]].iloc[-1:].copy()
    try:
        if model_name == "arima_model":
            from statsmodels.tsa.arima.model import ARIMAResults
            arima = ARIMAResults.load(MODEL_DIR / "arima_model.pkl")
            forecast = arima.forecast(steps=1).values[0]
            return forecast, "Dự đoán bằng ARIMA thành công."

        elif model_name == "lstm_model":
            from tensorflow.keras.models import load_model
            scaler = joblib.load(MODEL_DIR / "lstm_scaler.joblib")
            lstm_model = load_model(MODEL_DIR / "lstm_model.h5")

            scaled_close = scaler.transform(df[["close"]])
            last_window = scaled_close[-30:].reshape(1, 30, 1)
            pred_scaled = lstm_model.predict(last_window, verbose=0)
            pred = scaler.inverse_transform(pred_scaled)[0, 0]
            return pred, "Dự đoán bằng LSTM thành công."

        else:
            model_path = MODEL_DIR / f"{model_name}.joblib"
            if not model_path.exists():
                return None, f"Không tìm thấy mô hình {model_name}."
            model = joblib.load(model_path)

            scaler_path = MODEL_DIR / "scaler.joblib"
            if scaler_path.exists():
                scaler = joblib.load(scaler_path)
                X_latest = scaler.transform(X_latest)

            pred = model.predict(X_latest)[0]
            return float(pred), f"Dự đoán bằng {model_name} thành công."
    except Exception as e:
        return None, f"Lỗi khi dự đoán: {e}"
