const TOTAL_TITLES = 10;

const titlesGrid = document.getElementById("titlesGrid");
const txtFileInput = document.getElementById("txtFileInput");
const generateBtn = document.getElementById("generateBtn");
const resetBtn = document.getElementById("resetBtn");
const progressBar = document.getElementById("progressBar");
const statusText = document.getElementById("statusText");
const resultBox = document.getElementById("resultBox");
const copyBtn = document.getElementById("copyBtn");
const downloadBtn = document.getElementById("downloadBtn");

let currentJobId = null;
let pollingTimer = null;

function createTitleInputs() {
  titlesGrid.innerHTML = "";
  for (let i = 1; i <= TOTAL_TITLES; i += 1) {
    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = `Judul ${i}`;
    input.id = `title-${i}`;
    titlesGrid.appendChild(input);
  }
}

function getTitlesFromForm() {
  const titles = [];
  for (let i = 1; i <= TOTAL_TITLES; i += 1) {
    const value = document.getElementById(`title-${i}`).value.trim();
    titles.push(value);
  }
  return titles;
}

function setProgress(percent) {
  const safePercent = Number.isFinite(percent) ? Math.max(0, Math.min(100, percent)) : 0;
  progressBar.style.width = `${safePercent}%`;
  progressBar.textContent = `${safePercent}%`;
}

function setDownloadEnabled(jobId) {
  if (!jobId) {
    downloadBtn.href = "#";
    downloadBtn.classList.add("disabled");
    downloadBtn.setAttribute("aria-disabled", "true");
    return;
  }
  downloadBtn.href = `/api/download/${jobId}`;
  downloadBtn.classList.remove("disabled");
  downloadBtn.setAttribute("aria-disabled", "false");
}

function resetDashboard() {
  if (pollingTimer) {
    clearInterval(pollingTimer);
    pollingTimer = null;
  }
  currentJobId = null;
  setProgress(0);
  statusText.textContent = "Belum ada proses.";
  resultBox.value = "";
  setDownloadEnabled(null);
  createTitleInputs();
  txtFileInput.value = "";
}

async function fetchResult(jobId) {
  const response = await fetch(`/api/result/${jobId}`);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Gagal mengambil result.");
  }
  resultBox.value = data.compiled_output || "";
}

async function pollStatus() {
  if (!currentJobId) return;

  const response = await fetch(`/api/status/${currentJobId}`);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Gagal mengambil status.");
  }

  setProgress(data.progress_percent || 0);
  const batchInfo = `Batch ${data.current_batch || 0}/${data.total_batches || 5}`;
  statusText.textContent = `${data.status || "unknown"} - ${batchInfo} - ${data.message || ""}`;

  if (data.status === "failed") {
    clearInterval(pollingTimer);
    pollingTimer = null;
    generateBtn.disabled = false;
    throw new Error(data.error || "Proses gagal.");
  }

  if (data.status === "completed") {
    clearInterval(pollingTimer);
    pollingTimer = null;
    await fetchResult(currentJobId);
    setDownloadEnabled(currentJobId);
    generateBtn.disabled = false;
  }
}

async function startGenerate() {
  try {
    const titles = getTitlesFromForm();
    const nonEmpty = titles.filter((item) => item.trim() !== "");
    if (nonEmpty.length !== TOTAL_TITLES) {
      alert("Harus mengisi tepat 10 judul non-kosong.");
      return;
    }

    generateBtn.disabled = true;
    resultBox.value = "";
    setDownloadEnabled(null);
    setProgress(0);
    statusText.textContent = "Mengirim job...";

    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ titles }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Gagal membuat job.");
    }

    currentJobId = data.job_id;
    statusText.textContent = `Job dibuat: ${currentJobId}`;

    pollingTimer = setInterval(async () => {
      try {
        await pollStatus();
      } catch (err) {
        clearInterval(pollingTimer);
        pollingTimer = null;
        generateBtn.disabled = false;
        statusText.textContent = err.message;
      }
    }, 1500);
  } catch (err) {
    generateBtn.disabled = false;
    statusText.textContent = err.message;
  }
}

function handleTxtUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = () => {
    const content = String(reader.result || "");
    const titles = content
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter((line) => line !== "")
      .slice(0, TOTAL_TITLES);

    for (let i = 1; i <= TOTAL_TITLES; i += 1) {
      const input = document.getElementById(`title-${i}`);
      input.value = titles[i - 1] || "";
    }
  };
  reader.readAsText(file);
}

copyBtn.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(resultBox.value);
    statusText.textContent = "Output berhasil disalin.";
  } catch (_) {
    statusText.textContent = "Gagal menyalin output.";
  }
});

generateBtn.addEventListener("click", startGenerate);
resetBtn.addEventListener("click", resetDashboard);
txtFileInput.addEventListener("change", handleTxtUpload);

resetDashboard();
