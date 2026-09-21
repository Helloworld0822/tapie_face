const allowedTypes = new Set(["image/jpeg", "image/png", "image/webp"]);
const maxBytes = 10 * 1024 * 1024;

const ui = {
  input: document.querySelector("#image-input"),
  well: document.querySelector("#upload-well"),
  meta: document.querySelector("#upload-meta"),
  summary: document.querySelector("#file-summary"),
  analyze: document.querySelector("#analyze-button"),
  reindex: document.querySelector("#reindex-button"),
  reset: document.querySelector("#reset-button"),
  state: document.querySelector("#model-state"),
  message: document.querySelector("#model-message"),
  personCount: document.querySelector("#person-count"),
  imageCount: document.querySelector("#image-count"),
  empty: document.querySelector("#result-empty"),
  content: document.querySelector("#result-content"),
  error: document.querySelector("#error-banner"),
  warning: document.querySelector("#quality-notice"),
  winnerLabel: document.querySelector("#winner-label"),
  winnerScore: document.querySelector("#winner-score"),
  winnerCosine: document.querySelector("#winner-cosine"),
  scoreBar: document.querySelector("#score-bar"),
  interpretation: document.querySelector("#interpretation"),
  matchList: document.querySelector("#match-list"),
};

let selectedFile = null;
let modelReady = false;
let previewUrl = null;

function setStatus(status) {
  modelReady = status.state === "ready";
  ui.state.dataset.state = status.state;
  ui.message.textContent = status.message;
  ui.personCount.textContent = String(status.indexed_people);
  ui.imageCount.textContent = String(status.indexed_images);
  ui.analyze.disabled = !selectedFile || !modelReady;
}

async function readJson(response) {
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.message || "요청을 처리하지 못했습니다.");
  return payload;
}

async function refreshStatus() {
  try {
    setStatus(await readJson(await fetch("/api/status")));
  } catch (error) {
    ui.state.dataset.state = "error";
    ui.message.textContent = error.message;
  }
}

function frame(name) {
  return document.querySelector(`[data-frame="${name}"]`);
}

function setFrame(name, source, status) {
  const container = frame(name);
  const image = container.querySelector("img");
  container.classList.remove("is-loading", "is-error");
  container.classList.add("is-success");
  image.src = source;
  image.hidden = false;
  requestAnimationFrame(() => image.classList.add("is-visible"));
  container.querySelector("p").textContent = status;
}

function resetFrames() {
  document.querySelectorAll(".process-frame").forEach((container) => {
    container.classList.remove("is-loading", "is-success", "is-error");
    const image = container.querySelector("img");
    image.classList.remove("is-visible");
    image.hidden = true;
    image.removeAttribute("src");
    container.querySelector("p").textContent = "입력 대기";
  });
}

function setSelectedFile(file) {
  hideError();
  if (!allowedTypes.has(file.type)) {
    ui.well.classList.add("is-error");
    const suffix = selectedFile ? " 이전에 선택한 사진은 그대로 유지됩니다." : "";
    return showError(`JPG, PNG 또는 WebP 이미지만 사용할 수 있습니다.${suffix}`);
  }
  if (file.size > maxBytes) {
    ui.well.classList.add("is-error");
    const suffix = selectedFile ? " 이전에 선택한 사진은 그대로 유지됩니다." : "";
    return showError(`이미지 크기는 10MB 이하여야 합니다.${suffix}`);
  }
  selectedFile = file;
  ui.well.classList.remove("is-error");
  ui.well.classList.add("has-file");
  ui.meta.textContent = `${file.name} · ${formatBytes(file.size)}`;
  ui.summary.textContent = `${file.name}을 분석할 준비가 되었습니다.`;
  ui.analyze.disabled = !modelReady;
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = URL.createObjectURL(file);
  setFrame("original", previewUrl, "선택 완료");
}

function formatBytes(bytes) {
  return bytes >= 1024 * 1024 ? `${(bytes / 1024 / 1024).toFixed(1)} MB` : `${Math.ceil(bytes / 1024)} KB`;
}

function showError(message) {
  ui.error.textContent = message;
  ui.error.hidden = false;
}

function hideError() {
  ui.error.hidden = true;
  ui.error.textContent = "";
  ui.well.classList.remove("is-error");
}

function setProcessingError() {
  const statuses = {
    detected: "얼굴 검출 단계 실패",
    aligned: "검출 실패로 정렬 미완료",
    masked: "검출 실패로 얼굴 영역 미완료",
  };
  Object.entries(statuses).forEach(([name, status]) => {
    const container = frame(name);
    container.classList.remove("is-loading", "is-success");
    container.classList.add("is-error");
    container.querySelector("p").textContent = status;
  });
}

function setProcessing(active) {
  ui.analyze.disabled = active || !selectedFile || !modelReady;
  ui.reindex.disabled = active;
  ui.input.disabled = active;
  ui.analyze.querySelector("span").textContent = active ? "얼굴 분석 중" : "닮음 분석 시작";
  if (active) {
    ["detected", "aligned", "masked"].forEach((name) => {
      const container = frame(name);
      container.classList.remove("is-error");
      container.classList.add("is-loading");
      container.querySelector("p").textContent = "처리 중";
    });
  }
}

function interpretation(score) {
  if (score >= 80) return "기준 벡터와 얼굴 특징이 매우 가깝습니다. 그래도 이 결과는 신원 증명이 아닙니다.";
  if (score >= 50) return "여러 얼굴 특징이 비슷하지만 촬영 각도와 표정에 따라 달라질 수 있습니다.";
  return "기준 벡터와 겹치는 얼굴 특징이 적습니다. 더 선명한 정면 사진으로 다시 확인해 보세요.";
}

function renderMatches(matches) {
  ui.matchList.replaceChildren();
  matches.forEach((match, index) => {
    const row = document.createElement("li");
    row.className = "match-row";
    const rank = document.createElement("span");
    rank.className = "match-rank";
    rank.textContent = String(index + 1);
    const name = document.createElement("div");
    name.className = "match-name";
    name.textContent = match.label;
    name.title = match.label;
    const metric = document.createElement("div");
    metric.className = "match-metric";
    const score = document.createElement("strong");
    score.textContent = `${match.score.toFixed(1)}%`;
    const cosine = document.createElement("small");
    cosine.textContent = `cos ${match.cosine.toFixed(4)} · ${match.reference_count}장`;
    metric.append(score, cosine);
    row.append(rank, name, metric);
    ui.matchList.append(row);
  });
}

function renderResult(result) {
  const best = result.matches[0];
  setFrame("original", result.artifacts.original, "업로드 원본");
  setFrame("detected", result.artifacts.detected, `신뢰도 ${(result.detector_confidence * 100).toFixed(1)}%`);
  setFrame("aligned", result.artifacts.aligned, "표준 좌표 정렬 완료");
  setFrame("masked", result.artifacts.masked, "배경·헤어 억제 완료");
  ui.winnerLabel.textContent = best.label;
  ui.winnerLabel.title = best.label;
  ui.winnerScore.textContent = best.score.toFixed(1);
  ui.winnerCosine.textContent = `cos ${best.cosine.toFixed(4)} · 기준 ${best.reference_count}장`;
  ui.scoreBar.style.inlineSize = `${best.score}%`;
  ui.interpretation.textContent = interpretation(best.score);
  ui.warning.hidden = result.warnings.length === 0;
  ui.warning.textContent = result.warnings.join(" ");
  renderMatches(result.matches);
  ui.empty.hidden = true;
  ui.content.hidden = false;
  ui.reset.disabled = false;
}

async function analyze() {
  if (!selectedFile) return;
  hideError();
  setProcessing(true);
  const data = new FormData();
  data.append("image", selectedFile);
  try {
    renderResult(await readJson(await fetch("/api/analyze", { method: "POST", body: data })));
  } catch (error) {
    showError(error.message);
    setProcessingError();
  } finally {
    setProcessing(false);
  }
}

async function reindex() {
  hideError();
  ui.reindex.disabled = true;
  setStatus({ state: "indexing", message: "모델과 기준 벡터 준비 중", indexed_people: 0, indexed_images: 0 });
  try {
    setStatus(await readJson(await fetch("/api/reindex", { method: "POST" })));
  } catch (error) {
    ui.state.dataset.state = "error";
    ui.message.textContent = "기준 벡터 생성 실패";
    showError(error.message);
  } finally {
    ui.reindex.disabled = false;
  }
}

function reset() {
  selectedFile = null;
  ui.input.value = "";
  ui.well.classList.remove("has-file", "is-error");
  ui.meta.textContent = "JPG, PNG, WebP · 최대 10MB";
  ui.summary.textContent = "선택된 사진이 없습니다.";
  ui.analyze.disabled = true;
  ui.reset.disabled = true;
  ui.empty.hidden = false;
  ui.content.hidden = true;
  ui.warning.hidden = true;
  hideError();
  resetFrames();
}

ui.input.addEventListener("change", () => ui.input.files?.[0] && setSelectedFile(ui.input.files[0]));
["dragenter", "dragover"].forEach((type) => ui.well.addEventListener(type, (event) => { event.preventDefault(); ui.well.classList.add("is-dragging"); }));
["dragleave", "drop"].forEach((type) => ui.well.addEventListener(type, (event) => { event.preventDefault(); ui.well.classList.remove("is-dragging"); }));
ui.well.addEventListener("drop", (event) => event.dataTransfer?.files[0] && setSelectedFile(event.dataTransfer.files[0]));
ui.analyze.addEventListener("click", analyze);
ui.reindex.addEventListener("click", reindex);
ui.reset.addEventListener("click", reset);
refreshStatus();
