# ====================================================
# TRAINING MODULE
# ====================================================

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # Ẩn cảnh báo TensorFlow CPU

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings("ignore")

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# ====================================================
# 1) CẤU HÌNH THƯ MỤC LƯU MÔ HÌNH
# ====================================================
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

# ====================================================
# 2) LOAD DỮ LIỆU
# ====================================================
DATA_PATH = "Data_Milk_CLEANED.csv"

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Không tìm thấy file dữ liệu: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values(["symbol", "time"])

# ====================================================
# 3) CHUẨN BỊ DỮ LIỆU
# ====================================================
symbol = "VNM"  # Mặc định, có thể thay đổi
df_symbol = df[df["symbol"] == symbol].copy()

features = ["open", "high", "low", "volume"]
target = "close"

X = df_symbol[features]
y = df_symbol[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=False
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
joblib.dump(scaler, MODEL_DIR / "scaler.joblib")

# ====================================================
# 4) HÀM ĐÁNH GIÁ MÔ HÌNH
# ====================================================
def evaluate(model, X_test, y_test, name):
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"{name} - MSE: {mse:.4f}, R2: {r2:.4f}")
    return {"model": name, "MSE": mse, "R2": r2}

# ====================================================
# 5) LINEAR REGRESSION
# ====================================================
print("\n==============================")
print("Training Linear Regression...")
linear_model = LinearRegression()
linear_model.fit(X_train_scaled, y_train)
joblib.dump(linear_model, MODEL_DIR / "linear_regression.joblib")
evaluate(linear_model, X_test_scaled, y_test, "Linear Regression")

# ====================================================
# 6) RANDOM FOREST
# ====================================================
print("\n==============================")
print("Training Random Forest...")
rf_model = RandomForestRegressor(n_estimators=150, random_state=42)
rf_model.fit(X_train_scaled, y_train)
joblib.dump(rf_model, MODEL_DIR / "random_forest.joblib")
evaluate(rf_model, X_test_scaled, y_test, "Random Forest")

# ====================================================
# 7) VOTING REGRESSOR (LINEAR + RF)
# ====================================================
print("\n==============================")
print("Training Voting Regressor...")
voting_model = VotingRegressor([("lr", linear_model), ("rf", rf_model)])
voting_model.fit(X_train_scaled, y_train)
joblib.dump(voting_model, MODEL_DIR / "voting_regressor.joblib")
evaluate(voting_model, X_test_scaled, y_test, "Voting Regressor")

# ====================================================
# 8) ARIMA MODEL (TIME SERIES)
# ====================================================
print("\n==============================")
print("Training ARIMA...")

ts = df_symbol.set_index("time")["close"].astype(float)
ts = ts.asfreq("D")  # Fix lỗi tần suất thời gian

try:
    arima_model = ARIMA(ts, order=(2, 1, 2)).fit()
    arima_model.save(str(MODEL_DIR / "arima_model.pkl"))
    print("ARIMA Model trained and saved successfully.")

    # Đánh giá ARIMA
    forecast_steps = 10
    arima_forecast = arima_model.forecast(steps=forecast_steps)
    real_tail = ts[-forecast_steps:]

    common_len = min(len(real_tail), len(arima_forecast))
    real_tail = real_tail[-common_len:].astype(float)
    arima_forecast = np.array(arima_forecast[-common_len:], dtype=float)

    rmse_arima = np.sqrt(mean_squared_error(real_tail, arima_forecast))
    print(f"ARIMA RMSE: {rmse_arima:.4f}")

except Exception as e:
    print(f"Lỗi khi train hoặc đánh giá ARIMA: {e}")



# ====================================================
# 10) HOÀN TẤT
# ====================================================
print("\n==============================")
print("TRAINING HOÀN TẤT CHO 4 MÔ HÌNH:")
print(" - Linear Regression")
print(" - Random Forest")
print(" - Voting Regressor")
print(" - ARIMA")

