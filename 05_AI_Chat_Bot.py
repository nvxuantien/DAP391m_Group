import re
import pandas as pd
import numpy as np

DATA_PATH = "Data_Milk_CLEANED.csv"

# ---------------------------
# HÀM ĐỌC DỮ LIỆU
# ---------------------------
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["time"] = pd.to_datetime(df["time"])
    if "range" not in df.columns:
        df["range"] = df["high"] - df["low"]
    return df

data = load_data()

# ---------------------------
# HÀM TRẢ LỜI CHATBOT
# ---------------------------
def chatbot_reply(user_message: str) -> str:
    msg_original = user_message.strip()
    msg = msg_original.lower()
    response = "Xin lỗi, tôi chưa hiểu câu hỏi của bạn. Hãy thử hỏi về giá, khối lượng, xu hướng hoặc giai đoạn dữ liệu cổ phiếu."

    # Làm sạch câu để xử lý từ khóa
    msg_clean = re.sub(r"[^\w\s]", " ", msg)

    # ====== CHÀO HỎI (ĐÃ FIX KHÔNG BỊ NHẦM “hiện”, “phiếu”, “hiệu”) ======
    if re.search(r"\b(xin chào|chào|hello|hi)\b", msg_clean):
        return (
            "Xin chào! Tôi là Chatbot AI hỗ trợ dữ liệu cổ phiếu sữa. "
            "Bạn có thể hỏi tôi về giá, khối lượng, xu hướng hoặc giai đoạn dữ liệu."
        )

    # ====== THÔNG TIN CHUNG ======
    if "bạn là ai" in msg or "mày là ai" in msg:
        return "Tôi là Chatbot AI được xây dựng để hỗ trợ phân tích cổ phiếu ngành sữa Việt Nam dựa trên dữ liệu lịch sử."

    if "bạn có thể làm gì" in msg or "chức năng" in msg:
        return (
            "Tôi có thể:\n"
            "- Trả lời về giá cao nhất, thấp nhất, trung bình của cổ phiếu.\n"
            "- Cho biết khối lượng giao dịch trung bình.\n"
            "- Xác định cổ phiếu tăng trưởng mạnh, tiềm năng hoặc ổn định.\n"
            "- Cung cấp giai đoạn dữ liệu (từ ngày đầu đến ngày cuối trong file).\n"
            "- Và trò chuyện cơ bản với bạn."
        )

    if "cảm ơn" in msg or "thank" in msg:
        return "Không có gì đâu! Rất vui được giúp bạn."

    if "tạm biệt" in msg or "bye" in msg:
        return "Tạm biệt! Hẹn gặp lại bạn sau nhé."

    # ====== GIÁ CAO / THẤP ======
    if "cao nhất" in msg:
        stock = extract_symbol(msg)
        if stock:
            val = data.loc[data["symbol"] == stock, "high"].max()
            response = f"Giá cao nhất của {stock.upper()} là {val:.2f}."
        else:
            val = data.groupby("symbol")["high"].max()
            best = val.idxmax()
            response = f"Cổ phiếu {best} có giá cao nhất hiện tại là {val[best]:.2f}."

    elif "thấp nhất" in msg:
        stock = extract_symbol(msg)
        if stock:
            val = data.loc[data["symbol"] == stock, "low"].min()
            response = f"Giá thấp nhất của {stock.upper()} là {val:.2f}."
        else:
            val = data.groupby("symbol")["low"].min()
            best = val.idxmin()
            response = f"Cổ phiếu {best} có giá thấp nhất là {val[best]:.2f}."

    # ====== KHỐI LƯỢNG ======
    elif "khối lượng" in msg:
        stock = extract_symbol(msg)
        avg = data.groupby("symbol")["volume"].mean()
        if "trung bình" in msg:
            if stock:
                mean_vol = data.loc[data["symbol"] == stock, "volume"].mean()
                response = f"Khối lượng trung bình của {stock.upper()} là {mean_vol:,.0f} cổ phiếu/ngày."
            else:
                best = avg.idxmax()
                response = f"Khối lượng trung bình cao nhất thuộc về {best} với {avg[best]:,.0f} cổ phiếu/ngày."
        elif "cao nhất" in msg:
            best = avg.idxmax()
            response = f"Cổ phiếu {best} có khối lượng giao dịch trung bình cao nhất ({avg[best]:,.0f})."
        elif "thấp nhất" in msg:
            best = avg.idxmin()
            response = f"Cổ phiếu {best} có khối lượng trung bình thấp nhất ({avg[best]:,.0f})."
        else:
            best = avg.idxmax()
            response = f"Cổ phiếu {best} có khối lượng giao dịch lớn nhất trong giai đoạn này."

    # ====== TĂNG TRƯỞNG / TIỀM NĂNG ======
    elif any(k in msg for k in ["tăng trưởng", "tăng mạnh", "hiệu suất", "tiềm năng", "tốt nhất"]):
        growth = data.groupby("symbol").agg(first=("close", "first"), last=("close", "last"))
        growth["pct"] = (growth["last"] - growth["first"]) / growth["first"] * 100
        best = growth["pct"].idxmax()
        worst = growth["pct"].idxmin()
        response = (
            f"Cổ phiếu tăng trưởng mạnh nhất là {best} "
            f"với mức tăng {growth.loc[best, 'pct']:.2f}%.\n"
            f"Cổ phiếu giảm mạnh nhất là {worst} ({growth.loc[worst, 'pct']:.2f}%)."
        )

    # ====== ỔN ĐỊNH ======
    elif "ổn định" in msg or "biến động thấp" in msg:
        stab = data.groupby("symbol").agg(range_std=('range', 'std'), volume_std=('volume', 'std'))
        stab["stability_score"] = stab["range_std"].rank() + stab["volume_std"].rank()
        best = stab["stability_score"].idxmin()
        response = f"Cổ phiếu ổn định nhất là {best}, có biến động giá và khối lượng thấp nhất."

    # ====== GIAI ĐOẠN DỮ LIỆU ======
    elif "giai đoạn" in msg or "thời gian" in msg or "năm" in msg:
        start = data["time"].min().strftime("%Y-%m-%d")
        end = data["time"].max().strftime("%Y-%m-%d")
        response = f"Dữ liệu cổ phiếu bao gồm giai đoạn từ {start} đến {end}."

    return response


# ---------------------------
# HÀM XÁC ĐỊNH MÃ CỔ PHIẾU
# ---------------------------
def extract_symbol(message: str):
    message = message.lower()
    symbols = data["symbol"].unique().tolist()
    for s in symbols:
        if s.lower() in message:
            return s
    return None
