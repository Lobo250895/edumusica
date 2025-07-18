document.addEventListener('DOMContentLoaded', function() {
const btnRecord = document.getElementById('btnRecord');
  const btnStop = document.getElementById('btnStop');
  const btnPlay = document.getElementById('btnPlay');
  const btnGuardar = document.getElementById('btnGuardar');
  const btnOpen = document.getElementById('btnOpen');
  const fileInput = document.getElementById('fileInput');
  const volumeSlider = document.getElementById('volumeSlider');
  const volumeValue = document.getElementById('volumeValue');
  const status = document.getElementById('status');
  const canvas = document.getElementById('waveform');
  const ctx = canvas.getContext('2d');

  let mediaRecorder;
  let audioChunks = [];
  let audioBlob;
  let audioUrl;
  let audio;
  let recordingVolume = 1.5; 
  let animationId;
  let analyser;
  let dataArray;
  let sourceNode;
  let audioContext;
  let audioSourceBuffer;


  function resizeCanvas() {
    canvas.width = canvas.clientWidth;
    canvas.height = canvas.clientHeight;
  }
  window.addEventListener('resize', resizeCanvas);
  resizeCanvas();

  function drawWaveform() {
    if (!analyser) return;
    analyser.getByteTimeDomainData(dataArray);
    ctx.fillStyle = '#e0fbfc';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.lineWidth = 2;
    ctx.strokeStyle = '#005f73';
    ctx.beginPath();
    const sliceWidth = canvas.width / dataArray.length;
    let x = 0;
    for(let i = 0; i < dataArray.length; i++) {
      let v = dataArray[i] / 128.0;
      let y = v * canvas.height / 2;
      if(i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
      x += sliceWidth;
    }
    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.stroke();
    animationId = requestAnimationFrame(drawWaveform);
  }

  btnRecord.onclick = async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert('Tu navegador no soporta grabación de audio.');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioContext = new AudioContext();
      sourceNode = audioContext.createMediaStreamSource(stream);
      analyser = audioContext.createAnalyser();
      analyser.fftSize = 2048;
      const bufferLength = analyser.frequencyBinCount;
      dataArray = new Uint8Array(bufferLength);
      sourceNode.connect(analyser);
      drawWaveform();

      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
      mediaRecorder.onstart = () => {
        status.textContent = 'Grabando...';
        btnRecord.disabled = true;
        btnStop.disabled = false;
        btnPlay.disabled = true;
        btnGuardar.disabled = true;
      };
      mediaRecorder.onstop = () => {
        audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        audioUrl = URL.createObjectURL(audioBlob);
        audio = new Audio(audioUrl);
        status.textContent = 'Grabación detenida.';
        btnRecord.disabled = false;
        btnStop.disabled = true;
        btnPlay.disabled = false;
        btnGuardar.disabled = false;
        cancelAnimationFrame(animationId);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        audioContext.close();
      };

      mediaRecorder.start();
    } catch (error) {
      alert('Error accediendo al micrófono: ' + error.message);
    }
  };

  btnStop.onclick = () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
    }
  };

  btnPlay.onclick = () => {
    if (audio) {
      audio.play();
      status.textContent = 'Reproduciendo...';
      audio.onended = () => status.textContent = 'Reproducción finalizada.';
    }
  };

  btnGuardar.onclick = async () => {
  if (!audioBlob) {
    alert('No hay grabación para guardar.');
    return;
  }

  const idUsuario = document.getElementById('id_usuario').value;

  const formData = new FormData();
  formData.append('audio', audioBlob, 'grabacion.webm');
  formData.append('id_usuario', idUsuario);


  status.textContent = 'Enviando grabación al servidor...';

  try {
    const response = await fetch('/guardar_audio', {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      status.textContent = 'Grabación guardada correctamente en el servidor.';
    } else {
      status.textContent = 'Error al guardar la grabación en el servidor.';
    }
  } catch (error) {
    status.textContent = 'Error de red: ' + error.message;
  }
};


  btnOpen.onclick = () => {
    fileInput.click();
  };

  fileInput.onchange = () => {
    const file = fileInput.files[0];
    if (!file) return;
    if (audio) audio.pause();
    audioUrl = URL.createObjectURL(file);
    audio = new Audio(audioUrl);
    status.textContent = `Archivo cargado: ${file.name}`;
    btnPlay.disabled = false;
    btnGuardar.disabled = false;

  };

  volumeSlider.oninput = () => {
    recordingVolume = volumeSlider.value / 100;
    volumeValue.textContent = `${volumeSlider.value}%`;
    status.textContent = `Volumen micrófono: ${volumeSlider.value}%`;
  };

  fileInput.onchange = () => {
    const file = fileInput.files[0];
    if (!file) return;
    if (audio) audio.pause();
    audioUrl = URL.createObjectURL(file);
    audio = new Audio(audioUrl);
    status.textContent = `Archivo cargado: ${file.name}`;
    btnPlay.disabled = false;
    btnGuardar.disabled = false;

    const canvasCargado = document.getElementById('waveform-cargado');
    const ctxCargado = canvasCargado.getContext('2d');
    canvasCargado.width = canvasCargado.clientWidth;
    canvasCargado.height = canvasCargado.clientHeight;
    const actx = new AudioContext();
    const reader = new FileReader();
    reader.onload = function(ev) {
      actx.decodeAudioData(ev.target.result, function(buffer) {
        const data = buffer.getChannelData(0);
        ctxCargado.fillStyle = '#edf6f9';
        ctxCargado.fillRect(0, 0, canvasCargado.width, canvasCargado.height);
        ctxCargado.strokeStyle = '#8338ec';
        ctxCargado.beginPath();
        const step = Math.ceil(data.length / canvasCargado.width);
        const amp = canvasCargado.height / 2;
        for(let i = 0; i < canvasCargado.width; i++) {
          let min = 1.0, max = -1.0;
          for (let j = 0; j < step; j++) {
            const datum = data[(i * step) + j];
            if (datum < min) min = datum;
            if (datum > max) max = datum;
          }
          ctxCargado.moveTo(i, (1 + min) * amp);
          ctxCargado.lineTo(i, (1 + max) * amp);
        }
        ctxCargado.stroke();
      });
    };
    reader.readAsArrayBuffer(file);
  };
});