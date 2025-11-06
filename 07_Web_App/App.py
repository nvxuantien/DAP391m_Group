from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import google.generativeai as genai
from data_loader import get_symbols, get_stock_data, get_latest_info, load_data
from prediction_model import predict_price
from query_analysis import run_queries


app = Flask(__name__)
app.secret_key = "milk_dashboard_secret_key"

# ========== Cấu hình Gemini ==========
GEN_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyBEELt3L6E7tiqUx6wXqRdPhVdfzblYMBE")
genai.configure(api_key=GEN_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")
# =====================================

@app.route("/")
def home():
    if "authenticated" in session and session["authenticated"]:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "123":
            session["authenticated"] = True
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Sai tài khoản hoặc mật khẩu!")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "authenticated" not in session:
        return redirect(url_for("login"))
    symbols = get_symbols()
    return render_template("dashboard.html", stocks=symbols)

@app.route("/api/stock_data")
def stock_data():
    symbol = request.args.get("symbol")
    start = request.args.get("start")
    end = request.args.get("end")

    df = get_stock_data(symbol, start, end)
    if df is None:
        return jsonify({"success": False, "error": "Không có dữ liệu."})

    current = float(df["close"].iloc[-1])
    prev = float(df["close"].iloc[-2]) if len(df) > 1 else current
    change = current - prev
    return jsonify({
        "success": True,
        "dates": df["time"].dt.strftime("%Y-%m-%d").tolist(),
        "prices": df["close"].tolist(),
        "volume": df["volume"].tolist(),
        "current_price": current,
        "price_change": change,
        "volume_current": int(df["volume"].iloc[-1]),
        "rsi": 50 + (df["close"].iloc[-1] - df["close"].mean()) / 2
    })


@app.route("/chatbot", methods=["POST"])
def chatbot():
    from chatbot_enhanced import chatbot_reply
    from flask import request, jsonify, session

    user_msg = request.json.get("message", "").strip()
    if not user_msg:
        return jsonify({"reply": "Vui lòng nhập tin nhắn."})

    # Lấy lịch sử cũ từ session
    history = session.get("chat_history", [])

    # Gọi chatbot xử lý (chatbot_enhanced.py sẽ đọc file CSV)
    try:
        bot_reply = chatbot_reply(user_msg)
    except Exception as e:
        bot_reply = f"Lỗi xử lý dữ liệu: {str(e)}"

    # Thêm tin mới vào lịch sử
    history.append({"user": user_msg, "bot": bot_reply})
    if len(history) > 6:
        history = history[-6:]

    session["chat_history"] = history

    return jsonify({
        "reply": bot_reply,
        "history": history
    })



@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "authenticated" not in session:
        return redirect(url_for("login"))

    result = None
    msg = None
    symbol = None
    model_name = None

    # Lấy danh sách mã cổ phiếu để hiển thị trong dropdown
    stocks = get_symbols()

    if request.method == "POST":
        # Lấy symbol và model người dùng chọn
        symbol = request.form.get("symbol")
        model_name = request.form.get("model")

        # Gọi hàm dự đoán giá từ prediction_model.py
        result, msg = predict_price(symbol, model_name)

    # Trả kết quả ra giao diện
    return render_template(
        "prediction.html",
        result=result,
        symbol=symbol,
        model=model_name,
        message=msg,
        stocks=stocks
    )


@app.route("/analysis")
def analysis_page():
    if "authenticated" not in session:
        return redirect(url_for("login"))

    from query_analysis import run_queries
    results = run_queries()

    return render_template("analysis.html", results=results)

@app.route("/chart")
def chart_page():
    chart_folder = os.path.join("static", "charts")
    charts = []

    # Sắp xếp theo số thứ tự đầu file: 1_, 2_, 3_, ...
    files = sorted(
        [f for f in os.listdir(chart_folder) if f.endswith(".png")],
        key=lambda x: int(x.split("_")[0])  # lấy phần số trước dấu "_"
    )

    for file in files:
        charts.append({
            "name": file.replace("_", " ").replace(".png", ""),
            "path": url_for("static", filename=f"charts/{file}")
        })

    return render_template("chart.html", charts=charts)



if __name__ == "__main__":
    app.run(debug=True)
