async function loadChart() {
  const symbol = document.getElementById("symbolSelect").value;
  const start = document.getElementById("startDate").value;
  const end = document.getElementById("endDate").value;

  const res = await fetch(`/api/stock_data?symbol=${symbol}&start=${start}&end=${end}`);
  const data = await res.json();
  if (!data.success) {
    alert("Không có dữ liệu!");
    return;
  }

  document.getElementById("priceBox").innerText = `Giá hiện tại: ${data.current_price.toFixed(2)}`;
  document.getElementById("changeBox").innerText = `Thay đổi: ${data.price_change.toFixed(2)}`;
  document.getElementById("volumeBox").innerText = `Khối lượng: ${data.volume_current}`;
  document.getElementById("rsiBox").innerText = `RSI: ${data.rsi.toFixed(2)}`;

  const trace = {
    x: data.dates,
    y: data.prices,
    type: "scatter",
    mode: "lines+markers",
    line: { color: "#1f2a44" }
  };

  Plotly.newPlot("chartContainer", [trace], {
    title: `Giá cổ phiếu ${symbol}`,
    paper_bgcolor: "#fff",
    plot_bgcolor: "#fff"
  });
}
