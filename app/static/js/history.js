/* ===== history.js ===== */

const modal = new bootstrap.Modal(document.getElementById('detailModal'));
let modalSummaryText = '';

async function viewDetail(sid) {
  try {
    const res = await fetch(`/api/history/${sid}`);
    if (!res.ok) { alert('Không tìm thấy bản ghi.'); return; }
    const d = await res.json();

    modalSummaryText = d.summary_text;

    // Stats
    document.getElementById('modalStats').innerHTML = `
      <div class="col-3">
        <div class="result-stat">
          <div class="stat-val">${d.original_length.toLocaleString()}</div>
          <div class="stat-label">Ký tự gốc</div>
        </div>
      </div>
      <div class="col-3">
        <div class="result-stat">
          <div class="stat-val">${d.summary_length.toLocaleString()}</div>
          <div class="stat-label">Ký tự tóm tắt</div>
        </div>
      </div>
      <div class="col-3">
        <div class="result-stat">
          <div class="stat-val text-success">-${d.compression}%</div>
          <div class="stat-label">Rút gọn</div>
        </div>
      </div>
      <div class="col-3">
        <div class="result-stat">
          <div class="stat-val">${d.processing_time || '–'}s</div>
          <div class="stat-label">Xử lý</div>
        </div>
      </div>
    `;

    document.getElementById('modalOriginal').textContent = d.original_text;
    document.getElementById('modalSummary').textContent = d.summary_text;
    modal.show();
  } catch {
    alert('Lỗi kết nối.');
  }
}

async function deleteRecord(sid) {
  if (!confirm('Xóa bản ghi này khỏi lịch sử?')) return;
  const res = await fetch(`/api/history/${sid}`, { method: 'DELETE' });
  if (res.ok) {
    const row = document.getElementById(`row-${sid}`);
    row.style.transition = 'opacity .3s';
    row.style.opacity = '0';
    setTimeout(() => row.remove(), 300);
  } else {
    alert('Có lỗi xảy ra.');
  }
}

function copyModal() {
  if (!modalSummaryText) return;
  navigator.clipboard.writeText(modalSummaryText).then(() => {
    const btn = event.target.closest('button');
    const orig = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Đã sao chép!';
    btn.classList.replace('btn-outline-success', 'btn-success');
    setTimeout(() => {
      btn.innerHTML = orig;
      btn.classList.replace('btn-success', 'btn-outline-success');
    }, 2000);
  });
}
