const chatbotContainer = document.getElementById("chatbotContainer");
const chatbotBtn = document.getElementById("chatbotBtn");

chatbotBtn.addEventListener("click", () => {
  chatbotContainer.classList.toggle("hidden");
});

async function sendMessage() {
  const input = document.getElementById("userInput");
  const msg = input.value.trim();
  if (!msg) return;

  const chatBox = document.getElementById("chatMessages");

  // Hiển thị tạm tin nhắn người dùng
  chatBox.innerHTML += `<div class="user-msg"><strong>Bạn:</strong> ${msg}</div>`;
  input.value = "";

  try {
    const res = await fetch("/chatbot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg })
    });

    const data = await res.json();

    // 🔁 Làm sạch khung chat và hiển thị lại 6 tin nhắn gần nhất
    chatBox.innerHTML = "";
    data.history.forEach(entry => {
      chatBox.innerHTML += `<div class="user-msg"><strong>Bạn:</strong> ${entry.user}</div>`;
      chatBox.innerHTML += `<div class="bot-msg"><strong>Bot:</strong> ${entry.bot}</div>`;
    });

    chatBox.scrollTop = chatBox.scrollHeight;
  } catch (error) {
    chatBox.innerHTML += `<div class="bot-msg error">Lỗi khi gửi tin nhắn!</div>`;
  }
}
