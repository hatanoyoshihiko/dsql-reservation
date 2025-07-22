let API_BASE = '';

// 設定ファイル読み込み
async function loadConfig() {
  try {
    const response = await fetch('config.json');
    const config = await response.json();
    API_BASE = config.API_BASE;
  } catch (error) {
    console.error("設定ファイルの読み込みに失敗しました", error);
  }
}

// 予約一覧を取得して表示
async function loadReservations() {
  try {
    const res = await fetch(`${API_BASE}/reservations`);
    const data = await res.json();
    const tbody = document.getElementById("reservationList");
    if (!tbody) {
      console.warn("reservationList が見つかりません");
      return;
    }
    tbody.innerHTML = "";
    data.forEach(r => {
      const row = `<tr><td>${r.name}</td><td>${r.reserved_date}</td></tr>`;
      tbody.innerHTML += row;
    });
  } catch (e) {
    console.error("予約一覧の取得に失敗しました:", e);
  }
}

// ステップ表示制御
function showStep(stepId) {
  document.querySelectorAll('.step').forEach(el => el.classList.add('hidden'));
  const el = document.getElementById(stepId);
  if (el) {
    el.classList.remove('hidden');
  } else {
    console.warn(`step '${stepId}' が見つかりません`);
  }
}

// 現在時刻を初回のみ表示
function showCurrentTimeOnce() {
  const currentTimeEl = document.getElementById("currentTime");
  if (!currentTimeEl) return;

  const now = new Date();
  const formatted = now.toLocaleString("ja-JP", {
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit"
  });
  currentTimeEl.textContent = `現在時刻：${formatted}`;
}

// ページ読み込み後の初期処理
document.addEventListener("DOMContentLoaded", async () => {
  await loadConfig();
  showCurrentTimeOnce();
  showStep("startForm");
  loadReservations();

  const startBtn = document.getElementById("startReservation");
  const dateForm = document.getElementById("dateForm");
  const timeForm = document.getElementById("timeForm");
  const nameForm = document.getElementById("nameForm");
  const confirmForm = document.getElementById("confirmForm");
  const reserveBtn = document.getElementById("confirmReserve");

  startBtn?.addEventListener("click", () => {
    showStep("dateForm");
  });

  dateForm?.addEventListener("submit", (e) => {
    e.preventDefault();
    const date = document.getElementById("date")?.value;
    if (!date) {
      Swal.fire("入力エラー", "宿泊日を入力してください。", "warning");
      return;
    }
    showStep("timeForm");
  });

  timeForm?.addEventListener("submit", (e) => {
    e.preventDefault();
    const time = document.getElementById("time")?.value;
    if (!time) {
      Swal.fire("入力エラー", "到着時間を入力してください。", "warning");
      return;
    }
    showStep("nameForm");
  });

  nameForm?.addEventListener("submit", (e) => {
    e.preventDefault();
    const name = document.getElementById("name")?.value.trim();
    if (!name) {
      Swal.fire("入力エラー", "名前を入力してください。", "warning");
      return;
    }
    showStep("confirmForm");
  });

  reserveBtn?.addEventListener("click", async () => {
    reserveBtn.disabled = true;

    const name = document.getElementById("name")?.value.trim();
    const date = document.getElementById("date")?.value;
    const time = document.getElementById("time")?.value;

    const body = { name, date, time };

    try {
      const res = await fetch(`${API_BASE}/reserve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (res.ok) {
        Swal.fire("成功", "予約が登録されました！", "success");
        await loadReservations();
        showStep("step4");
      } else {
        const result = await res.json();
        Swal.fire("エラー", result.error || "予約に失敗しました", "error");
        reserveBtn.disabled = false;
        showStep("step4");
      }
    } catch (err) {
      console.error(err);
      Swal.fire("通信エラー", "APIとの通信に失敗しました。", "error");
      reserveBtn.disabled = false;
    }
  });

  const backBtn = document.getElementById("backToStart");
  backBtn?.addEventListener("click", () => {
    document.getElementById("nameForm")?.reset();
    document.getElementById("dateForm")?.reset();
    document.getElementById("timeForm")?.reset();
    reserveBtn.disabled = false;
    showStep("startForm");
  });
});
