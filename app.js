const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const scriptInput = $('#scriptInput');
const voiceSelect = $('#voiceSelect');
const voiceMeta = {
  Ava: { style: 'Warm · Conversational', className: 'ava', letter: 'A', rate: 1 },
  Theo: { style: 'Clear · Confident', className: 'theo', letter: 'T', rate: 0.94 },
  Mira: { style: 'Bright · Energetic', className: 'mira', letter: 'M', rate: 1.06 },
  Sam: { style: 'Calm · Grounded', className: 'theo', letter: 'S', rate: 0.88 },
};
let selectedStyle = 'Conversational';
let speaking = false;
let generationCount = 0;
let catalog = null;

function showToast(message) {
  const toast = $('#toast');
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(showToast.timeout);
  showToast.timeout = setTimeout(() => toast.classList.remove('show'), 2600);
}

function csrfToken() {
  return document.cookie.split('; ').find((row) => row.startsWith('csrftoken='))?.split('=')[1] || '';
}

function updateCharCount() {
  $('#charCount').textContent = `${scriptInput.value.length.toLocaleString()} / 5,000`;
}

function updateRange(input) {
  const min = Number(input.min || 0);
  const max = Number(input.max || 100);
  const progress = ((Number(input.value) - min) / (max - min)) * 100;
  input.style.setProperty('--range-progress', `${progress}%`);
  const valueTarget = $(`#${input.id}Value`);
  if (valueTarget) valueTarget.textContent = input.id === 'speed' ? `${(Number(input.value) / 100).toFixed(1)}×` : `${input.value}%`;
}

function updateVoice() {
  const voice = voiceSelect.value;
  const meta = voiceMeta[voice] || { style: 'AI voice', className: 'ava', letter: voice.slice(0, 1) || 'V', rate: 1 };
  $('#previewAvatar').textContent = meta.letter;
  $('#selectAvatar').textContent = meta.letter;
  $('#previewAvatar').className = `voice-avatar ${meta.className}`;
  $('#selectAvatar').className = `voice-avatar ${meta.className}`;
  $('#previewVoiceName').textContent = voice;
  $('#previewVoiceStyle').textContent = meta.style;
}

function populateCatalog(data) {
  catalog = data;
  const selectedVoice = voiceSelect.value;
  const selectedLanguage = $('#languageSelect').value;
  const selectedModel = $('#modelSelect').value;
  if (data.voices?.length) {
    voiceSelect.innerHTML = data.voices.map((voice) => `<option value="${voice.name}">${voice.name} — ${voice.description}</option>`).join('');
    voiceSelect.value = data.voices.some((voice) => voice.name === selectedVoice) ? selectedVoice : data.voices[0].name;
    data.voices.forEach((voice) => { voiceMeta[voice.name] = { style: `${voice.accent} · ${voice.category}`, className: voice.slug === 'mira' ? 'mira' : voice.slug === 'theo' ? 'theo' : 'ava', letter: voice.name.slice(0, 1), rate: 1 }; });
  }
  if (data.languages?.length) {
    $('#languageSelect').innerHTML = data.languages.map((language) => `<option value="${language.name}">${language.name}</option>`).join('');
    $('#languageSelect').value = data.languages.some((language) => language.name === selectedLanguage) ? selectedLanguage : data.languages[0].name;
  }
  if (data.models?.length) {
    $('#modelSelect').innerHTML = data.models.map((model) => `<option value="${model.name}">${model.name} — ${model.description}</option>`).join('');
    $('#modelSelect').value = data.models.some((model) => model.name === selectedModel) ? selectedModel : data.models[0].name;
  }
  if (data.styles?.length) {
    $('#styleChips').innerHTML = data.styles.map((style, index) => `<button class="style-chip ${index === 0 ? 'active' : ''}" data-style="${style.name}" title="${style.description}">${style.name}</button>`).join('');
    selectedStyle = data.styles[0].name;
    $('#styleValue').textContent = selectedStyle;
    $$('#styleChips .style-chip').forEach((chip) => chip.addEventListener('click', selectStyle));
  }
  updateVoice();
}

function selectStyle(event) {
  $$('#styleChips .style-chip').forEach((item) => item.classList.remove('active'));
  event.currentTarget.classList.add('active');
  selectedStyle = event.currentTarget.dataset.style;
  $('#styleValue').textContent = selectedStyle;
}

function buildWaveform() {
  const waveform = $('#waveform');
  waveform.innerHTML = '';
  const heights = [20,34,12,47,29,55,37,21,41,18,31,50,25,39,16,46,30,22,43,33,16,52,27,37,18,44,24,31,48,20,35,14,42,28,51,22,38,17,45,26,34,19,48,29,39,15,44,24,35,18,49,27,41,20,32,14,45,25,36,16,43,22,30,47,18,39,28,45,21,33,15,42];
  heights.forEach((height, index) => {
    const bar = document.createElement('span');
    bar.className = `wave-bar ${index > 46 ? 'dim' : ''}`;
    bar.style.height = `${height}px`;
    waveform.appendChild(bar);
  });
}

function browserVoiceFor(name) {
  const voices = window.speechSynthesis?.getVoices?.() || [];
  const preferred = name === 'Mira' ? ['Samantha', 'Google US English'] : name === 'Theo' ? ['Alex', 'Daniel', 'Google UK English Male'] : ['Karen', 'Google US English', 'Samantha'];
  return voices.find((voice) => preferred.some((choice) => voice.name.includes(choice))) || voices.find((voice) => voice.lang.startsWith('en')) || voices[0];
}

function speakPreview() {
  if (!scriptInput.value.trim()) {
    showToast('Add a script before generating a preview.');
    scriptInput.focus();
    return;
  }
  window.speechSynthesis?.cancel();
  const utterance = new SpeechSynthesisUtterance(scriptInput.value);
  const meta = voiceMeta[voiceSelect.value];
  utterance.voice = browserVoiceFor(voiceSelect.value);
  utterance.rate = meta.rate * (Number($('#speed').value) / 100);
  utterance.pitch = voiceSelect.value === 'Mira' ? 1.12 : voiceSelect.value === 'Theo' ? .88 : 1;
  utterance.volume = 1;
  utterance.onstart = () => { speaking = true; $('#waveform').classList.add('is-playing'); $('#previewStatus').classList.add('generating'); $('#previewStatus').innerHTML = '<span class="status-dot"></span> Playing preview'; $('#playPreview').textContent = 'Ⅱ'; };
  utterance.onend = () => finishSpeaking();
  utterance.onerror = () => { finishSpeaking(); showToast('Preview could not start in this browser.'); };
  if (!window.speechSynthesis) { showToast('Speech preview is not supported in this browser.'); return; }
  window.speechSynthesis.speak(utterance);
}

function finishSpeaking() { speaking = false; $('#waveform').classList.remove('is-playing'); $('#previewStatus').classList.remove('generating'); $('#previewStatus').innerHTML = '<span class="status-dot"></span> Ready to generate'; $('#playPreview').textContent = '▶'; }

function addRecentItem() {
  generationCount += 1;
  const item = document.createElement('div');
  item.className = 'recent-item';
  item.innerHTML = `<button class="play-small" aria-label="Play generation">▶</button><div><strong>${scriptInput.value.trim().slice(0, 34)}${scriptInput.value.trim().length > 34 ? '…' : ''}</strong><span>${voiceSelect.value} · ${selectedStyle} · just now</span></div>`;
  item.querySelector('button').addEventListener('click', speakPreview);
  $('#recentList').prepend(item);
  if ($('#recentList').children.length > 4) $('#recentList').lastElementChild.remove();
}

async function generate() {
  if (!scriptInput.value.trim()) { showToast('Add a script before generating a preview.'); scriptInput.focus(); return; }
  updateCharCount();
  const payload = { text: scriptInput.value, voice: voiceSelect.value, model: $('#modelSelect').value, controls: Object.fromEntries($$('.range').map((input) => [input.id, Number(input.value)])) };
  $('#previewStatus').classList.add('generating');
  $('#previewStatus').innerHTML = '<span class="status-dot"></span> Preparing preview';
  try {
    const response = await fetch('/api/generate/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() }, credentials: 'same-origin', body: JSON.stringify(payload) });
    if (response.ok) {
      const audio = new Audio(URL.createObjectURL(await response.blob()));
      audio.onplay = () => { $('#waveform').classList.add('is-playing'); $('#previewStatus').innerHTML = '<span class="status-dot"></span> Playing cloud preview'; };
      audio.onended = finishSpeaking;
      audio.onerror = finishSpeaking;
      await audio.play();
      addRecentItem();
      showToast(`AI preview generated with ${voiceSelect.value}.`);
      return;
    }
  } catch { /* The local browser preview remains available without a provider key. */ }
  addRecentItem();
  showToast('Using local browser preview. Add a provider key for AI audio.');
  speakPreview();
}

scriptInput.addEventListener('input', updateCharCount);
voiceSelect.addEventListener('change', updateVoice);
$$('.range').forEach((input) => { updateRange(input); input.addEventListener('input', () => updateRange(input)); });
$$('.style-chip').forEach((chip) => chip.addEventListener('click', selectStyle));
$$('.refine-tag').forEach((tag) => tag.addEventListener('click', () => { scriptInput.value = `${scriptInput.value.trim()}\n\n[Direction: ${tag.dataset.insert}]`; updateCharCount(); showToast('Direction added to your script.'); scriptInput.focus(); }));
$$('.voice-list-item').forEach((item) => item.addEventListener('click', () => { voiceSelect.value = item.dataset.voice; updateVoice(); showToast(`${item.dataset.voice} selected.`); }));
$('#generateButton').addEventListener('click', generate);
$('#playPreview').addEventListener('click', () => speaking ? (window.speechSynthesis.cancel(), finishSpeaking()) : speakPreview());
$('#stopPreview').addEventListener('click', () => { window.speechSynthesis?.cancel(); finishSpeaking(); });
$('#clearScript').addEventListener('click', () => { scriptInput.value = ''; updateCharCount(); scriptInput.focus(); });
$('#refineScript').addEventListener('click', () => { scriptInput.value = `${scriptInput.value.trim()}\n\n[Direction: Make the delivery natural, warm, and easy to follow.]`; updateCharCount(); showToast('AI refinement direction added.'); });
$('#newProject').addEventListener('click', () => { scriptInput.value = ''; updateCharCount(); $('#recentList').innerHTML = ''; showToast('New project started.'); });
$('#saveProject').addEventListener('click', async () => {
  const data = projectData();
  localStorage.setItem('sonora-project', JSON.stringify(data));
  try {
    const response = await fetch('/api/projects/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() }, credentials: 'same-origin', body: JSON.stringify({ name: 'Untitled voiceover', ...data }) });
    showToast(response.ok ? 'Project saved to your Sonora account.' : 'Project saved locally. Sign in to sync across devices.');
  } catch { showToast('Project saved locally.'); }
});
$('#downloadProject').addEventListener('click', () => { const blob = new Blob([JSON.stringify(projectData(), null, 2)], { type: 'application/json' }); const url = URL.createObjectURL(blob); const link = document.createElement('a'); link.href = url; link.download = 'sonora-project.json'; link.click(); URL.revokeObjectURL(url); showToast('Settings exported.'); });
document.addEventListener('keydown', (event) => { if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') generate(); });
window.speechSynthesis?.addEventListener?.('voiceschanged', () => browserVoiceFor('Ava'));

function projectData() { return { app: 'Sonora', script: scriptInput.value, voice: voiceSelect.value, language: $('#languageSelect').value, model: $('#modelSelect').value, style: selectedStyle, controls: Object.fromEntries($$('.range').map((input) => [input.id, input.value])) }; }

buildWaveform(); updateCharCount(); updateVoice();
fetch('/api/catalog/').then((response) => response.ok ? response.json() : null).then((data) => data && populateCatalog(data)).catch(() => {});
document.querySelectorAll('select').forEach((select) => select.addEventListener('change', () => showToast(`${select.value} selected.`)));
