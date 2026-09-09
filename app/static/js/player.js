/**
 * Kassetalar Vintage Audio Player Engine
 */

class VintageCassettePlayer {
  constructor() {
    this.audio = new Audio();
    this.isPlaying = false;
    this.currentTrack = null;
    this.audioCtx = null;
    this.synthInterval = null;
    
    this.initElements();
    this.bindEvents();
  }

  initElements() {
    this.playerContainer = document.getElementById('global-tape-player');
    this.playBtn = document.getElementById('tape-play-btn');
    this.trackTitle = document.getElementById('tape-track-title');
    this.trackArtist = document.getElementById('tape-track-artist');
    this.progressBar = document.getElementById('tape-progress-bar');
    this.timeDisplay = document.getElementById('tape-time-display');
    this.reels = document.querySelectorAll('.tape-reel');
    this.eqVisualizer = document.getElementById('tape-equalizer');
  }

  bindEvents() {
    if (!this.playBtn) return;

    this.playBtn.addEventListener('click', () => {
      this.togglePlay();
    });

    this.audio.addEventListener('timeupdate', () => {
      this.updateProgress();
    });

    this.audio.addEventListener('ended', () => {
      this.stop();
    });

    this.audio.addEventListener('error', () => {
      // Fallback: Agar audio yuklanmasa, WebAudio analog synth ijro etiladi
      this.startSynthPlayback();
    });

    if (this.progressBar) {
      this.progressBar.addEventListener('input', (e) => {
        if (this.audio.duration) {
          const seekTime = (e.target.value / 100) * this.audio.duration;
          this.audio.currentTime = seekTime;
        }
      });
    }
  }

  loadAndPlay(track) {
    this.currentTrack = track;
    if (this.trackTitle) this.trackTitle.textContent = track.title || 'Kasseta Taronasi';
    if (this.trackArtist) this.trackArtist.textContent = track.artist || 'Ijrochi';
    
    if (this.playerContainer) {
      this.playerContainer.classList.remove('hidden');
      this.playerContainer.classList.add('flex');
    }

    if (track.audioUrl) {
      this.stopSynth();
      this.audio.src = track.audioUrl;
      this.audio.play()
        .then(() => {
          this.setPlayingState(true);
        })
        .catch(() => {
          // Agar autoplay bloklansa yoki audio yuklanmasa, analog synth ishga tushadi
          this.startSynthPlayback();
        });
    } else {
      this.startSynthPlayback();
    }
  }

  togglePlay() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  }

  play() {
    if (this.currentTrack) {
      if (this.audio.src && !this.synthInterval) {
        this.audio.play()
          .then(() => this.setPlayingState(true))
          .catch(() => this.startSynthPlayback());
      } else {
        this.startSynthPlayback();
      }
    }
  }

  pause() {
    this.audio.pause();
    this.stopSynth();
    this.setPlayingState(false);
  }

  stop() {
    this.audio.pause();
    this.audio.currentTime = 0;
    this.stopSynth();
    this.setPlayingState(false);
    if (this.progressBar) this.progressBar.value = 0;
  }

  setPlayingState(playing) {
    this.isPlaying = playing;
    if (this.playBtn) {
      this.playBtn.innerHTML = playing 
        ? '<i data-lucide="pause" class="w-6 h-6 text-black"></i>' 
        : '<i data-lucide="play" class="w-6 h-6 text-black ml-0.5"></i>';
      if (window.lucide) lucide.createIcons();
    }

    this.reels.forEach(reel => {
      if (playing) {
        reel.classList.remove('paused');
        reel.classList.add('spinning-reel');
      } else {
        reel.classList.add('paused');
      }
    });

    if (this.eqVisualizer) {
      if (playing) {
        this.eqVisualizer.classList.remove('opacity-20');
        this.eqVisualizer.classList.add('opacity-100');
      } else {
        this.eqVisualizer.classList.add('opacity-20');
        this.eqVisualizer.classList.remove('opacity-100');
      }
    }
  }

  updateProgress() {
    if (!this.audio.duration) return;
    const progress = (this.audio.currentTime / this.audio.duration) * 100;
    if (this.progressBar) this.progressBar.value = progress;
    
    if (this.timeDisplay) {
      const curMins = Math.floor(this.audio.currentTime / 60);
      const curSecs = Math.floor(this.audio.currentTime % 60).toString().padStart(2, '0');
      const durMins = Math.floor(this.audio.duration / 60) || 0;
      const durSecs = Math.floor(this.audio.duration % 60 || 0).toString().padStart(2, '0');
      this.timeDisplay.textContent = `${curMins}:${curSecs} / ${durMins}:${durSecs}`;
    }
  }

  // Vintage Lo-Fi synth audio generator (offline / fallback demo)
  startSynthPlayback() {
    this.setPlayingState(true);
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!this.audioCtx) this.audioCtx = new AudioContext();
      if (this.audioCtx.state === 'suspended') this.audioCtx.resume();

      const notes = [220, 261.63, 329.63, 392, 440, 523.25]; // Warm vintage scale
      let noteIdx = 0;
      
      this.stopSynth();
      this.synthInterval = setInterval(() => {
        if (!this.isPlaying) return;
        const osc = this.audioCtx.createOscillator();
        const gain = this.audioCtx.createGain();
        
        osc.type = 'triangle'; // Warm retro sound
        osc.frequency.setValueAtTime(notes[noteIdx % notes.length], this.audioCtx.currentTime);
        
        gain.gain.setValueAtTime(0.08, this.audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, this.audioCtx.currentTime + 1.2);
        
        osc.connect(gain);
        gain.connect(this.audioCtx.destination);
        
        osc.start();
        osc.stop(this.audioCtx.currentTime + 1.2);
        noteIdx++;
      }, 700);

      // Fake timer progress for synth preview
      let synthSeconds = 0;
      this.synthTimer = setInterval(() => {
        synthSeconds++;
        const curMins = Math.floor(synthSeconds / 60);
        const curSecs = (synthSeconds % 60).toString().padStart(2, '0');
        if (this.timeDisplay) this.timeDisplay.textContent = `${curMins}:${curSecs} / 03:45 (Demo)`;
        if (this.progressBar) this.progressBar.value = (synthSeconds / 225) * 100;
        if (synthSeconds >= 225) this.stop();
      }, 1000);

    } catch (e) {
      console.log("Synth audio fallback initialized");
    }
  }

  stopSynth() {
    if (this.synthInterval) {
      clearInterval(this.synthInterval);
      this.synthInterval = null;
    }
    if (this.synthTimer) {
      clearInterval(this.synthTimer);
      this.synthTimer = null;
    }
  }
}

// Global player instance
document.addEventListener('DOMContentLoaded', () => {
  window.cassettePlayer = new VintageCassettePlayer();
});

function playCassettePreview(title, artist, audioUrl) {
  if (window.cassettePlayer) {
    window.cassettePlayer.loadAndPlay({
      title: title,
      artist: artist,
      audioUrl: audioUrl
    });
  }
}
