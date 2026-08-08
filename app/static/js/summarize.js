/* ===== summarize.js ===== */

let currentSummary = '';
let currentSummaryId = null;

// Đếm ký tự realtime
document.getElementById('inputText').addEventListener('input', function () {
  document.getElementById('charCount').textContent = this.value.length + ' ký tự';
});

// Upload file .txt
document.getElementById('fileUpload').addEventListener('change', async function () {
  if (!this.files.length) return;
  const file = this.files[0];
  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/api/upload', { method: 'POST', body: formData });
    const data = await res.json();
    if (res.ok) {
      document.getElementById('inputText').value = data.text;
      document.getElementById('charCount').textContent = data.text.length + ' ký tự';
      document.getElementById('uploadFilename').textContent = '📄 ' + data.filename;
    } else {
      showAlert(data.error || 'Lỗi khi đọc file.', 'danger');
    }
  } catch {
    showAlert('Không thể kết nối máy chủ.', 'danger');
  }
  this.value = ''; // Reset input để có thể upload lại cùng file
});

// Xóa input
function clearInput() {
  document.getElementById('inputText').value = '';
  document.getElementById('charCount').textContent = '0 ký tự';
  document.getElementById('uploadFilename').textContent = '';
  resetOutput();
}

// Gọi API tóm tắt
async function doSummarize() {
  const text = document.getElementById('inputText').value.trim();
  const ratio = parseInt(document.getElementById('ratioSlider').value) / 100;
  const method = document.getElementById('methodSelect').value;
  const useMmr = document.getElementById('useMmr').checked;

  if (!text) {
    showAlert('Vui lòng nhập văn bản cần tóm tắt.', 'warning');
    return;
  }

  setLoading(true);

  try {
    const res = await fetch('/api/summarize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, method, ratio, use_mmr: useMmr })
    });

    const data = await res.json();

    if (!res.ok) {
      showAlert(data.error || 'Có lỗi xảy ra.', 'danger');
      setLoading(false);
      return;
    }

    currentSummary = data.summary;
    currentSummaryId = data.summary_id;
    showResult(data);

  } catch {
    showAlert('Không thể kết nối máy chủ.', 'danger');
  }

  setLoading(false);
}

function showResult(data) {
  document.getElementById('placeholder').classList.add('d-none');
  document.getElementById('loadingState').classList.add('d-none');
  document.getElementById('resultContainer').classList.remove('d-none');
  document.getElementById('resultActions').style.display = '';

  // Stats bar
  const statsBar = document.getElementById('statsBar');
  statsBar.innerHTML = `
    <div class="col-3">
      <div class="result-stat">
        <div class="stat-val">${data.sentence_count}</div>
        <div class="stat-label">Câu gốc</div>
      </div>
    </div>
    <div class="col-3">
      <div class="result-stat">
        <div class="stat-val">${data.selected_count}</div>
        <div class="stat-label">Câu chọn</div>
      </div>
    </div>
    <div class="col-3">
      <div class="result-stat">
        <div class="stat-val text-success">-${data.compression}%</div>
        <div class="stat-label">Rút gọn</div>
      </div>
    </div>
    <div class="col-3">
      <div class="result-stat">
        <div class="stat-val">${data.processing_time}s</div>
        <div class="stat-label">Xử lý</div>
      </div>
    </div>
  `;

  // Keywords
  const keywordsBar = document.getElementById('keywordsBar');
  const keywordsList = document.getElementById('keywordsList');
  if (data.keywords && data.keywords.length) {
    keywordsList.innerHTML = '';
    data.keywords.forEach(kw => {
      const badge = document.createElement('span');
      badge.className = 'badge rounded-pill text-bg-light border';
      badge.textContent = kw;
      keywordsList.appendChild(badge);
    });
    keywordsBar.classList.remove('d-none');
  } else {
    keywordsBar.classList.add('d-none');
  }

  // Summary text
  document.getElementById('summaryText').textContent = data.summary;
}

function resetOutput() {
  document.getElementById('placeholder').classList.remove('d-none');
  document.getElementById('loadingState').classList.add('d-none');
  document.getElementById('resultContainer').classList.add('d-none');
  document.getElementById('resultActions').style.display = 'none';
  document.getElementById('keywordsBar').classList.add('d-none');
  currentSummary = '';
  currentSummaryId = null;
}

function setLoading(on) {
  const btn = document.getElementById('btnSummarize');
  if (on) {
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Đang xử lý…';
    document.getElementById('placeholder').classList.add('d-none');
    document.getElementById('loadingState').classList.remove('d-none');
    document.getElementById('resultContainer').classList.add('d-none');
  } else {
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-magic me-2"></i>Tóm tắt ngay';
  }
}

// Sao chép kết quả
function copyResult() {
  if (!currentSummary) return;
  navigator.clipboard.writeText(currentSummary).then(() => {
    showToast('Đã sao chép vào clipboard!');
  });
}

// Tải kết quả về .txt
function downloadResult() {
  if (!currentSummaryId) return;
  window.location.href = `/api/history/download/${currentSummaryId}`;
}

// Toast thông báo nhỏ
function showToast(msg) {
  let toast = document.getElementById('copyToast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'copyToast';
    toast.className = 'toast align-items-center text-bg-success border-0 show';
    toast.innerHTML = `<div class="d-flex"><div class="toast-body">${msg}</div></div>`;
    document.body.appendChild(toast);
  } else {
    toast.querySelector('.toast-body').textContent = msg;
    toast.classList.add('show');
  }
  setTimeout(() => toast.classList.remove('show'), 2500);
}

function showAlert(msg, type = 'danger') {
  const container = document.querySelector('.container.mt-3') ||
                    document.querySelector('main.container');
  const el = document.createElement('div');
  el.className = `alert alert-${type} alert-dismissible fade show`;
  el.innerHTML = `${msg}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
  container.prepend(el);
  setTimeout(() => el.remove(), 5000);
}

// Cho phép nhấn Ctrl+Enter để tóm tắt
document.getElementById('inputText').addEventListener('keydown', function (e) {
  if (e.ctrlKey && e.key === 'Enter') doSummarize();
});
