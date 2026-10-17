"""
JARVIS Voice Engine
Handles wake word detection, speech-to-text, and text-to-speech.
"""
import asyncio
import io
import json
import logging
import os
import queue
import struct
import tempfile
import threading
import time
import wave

import numpy as np
import sounddevice as sd

logger = logging.getLogger("jarvis.voice")


class VoiceEngine:
    """Complete voice pipeline: wake word → STT → TTS."""

    def __init__(self, config, on_wake=None, on_command=None, on_state_change=None):
        self.config = config
        self.on_wake = on_wake              # callback()
        self.on_command = on_command          # callback(text: str)
        self.on_state_change = on_state_change  # callback(state: str)

        self._running = False
        self._listening = False
        self._audio_queue = queue.Queue()
        self._stream = None
        self._wake_model = None
        self._whisper_model = None
        self._sample_rate = 16000
        self._channels = 1

    def start(self):
        """Start the voice engine in a background thread."""
        self._running = True
        self._init_wake_word()
        self._init_whisper()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Voice engine started.")

    def stop(self):
        """Stop the voice engine."""
        self._running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
        logger.info("Voice engine stopped.")

    def force_listen(self):
        """Force start listening without wake word (for button press)."""
        self._listening = True
        if self.on_state_change:
            self.on_state_change("listening")

    def _init_wake_word(self):
        """Initialize OpenWakeWord model."""
        try:
            from openwakeword.model import Model
            self._wake_model = Model(
                wakeword_models=["hey_jarvis"],
                inference_framework="onnx"
            )
            logger.info("Wake word model loaded (hey_jarvis).")
        except Exception as e:
            logger.warning(f"OpenWakeWord init failed: {e}. Trying fallback...")
            try:
                from openwakeword.model import Model
                self._wake_model = Model(inference_framework="onnx")
                logger.info("Wake word model loaded (default models).")
            except Exception as e2:
                logger.error(f"Wake word init completely failed: {e2}")
                self._wake_model = None

    def _init_whisper(self):
        """Initialize faster-whisper model."""
        try:
            from faster_whisper import WhisperModel
            model_size = self.config.WHISPER_MODEL
            self._whisper_model = WhisperModel(
                model_size,
                device="cpu",
                compute_type="int8"
            )
            logger.info(f"Whisper model loaded: {model_size}")
        except Exception as e:
            logger.error(f"Whisper init failed: {e}")
            self._whisper_model = None

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream — pushes audio chunks to queue."""
        if status:
            logger.warning(f"Audio status: {status}")
        self._audio_queue.put(indata.copy())

    def _run_loop(self):
        """Main voice loop: wake word detection → STT."""
        try:
            self._stream = sd.InputStream(
                samplerate=self._sample_rate,
                channels=self._channels,
                dtype="int16",
                blocksize=1280,  # 80ms chunks at 16kHz
                callback=self._audio_callback
            )
            self._stream.start()
        except Exception as e:
            logger.error(f"Microphone stream failed: {e}")
            if self.on_state_change:
                self.on_state_change("error")
            return

        if self.on_state_change:
            self.on_state_change("idle")

        while self._running:
            try:
                audio_chunk = self._audio_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if self._listening:
                # We're in listening mode — accumulate audio for STT
                self._process_listening(audio_chunk)
            else:
                # We're in idle mode — detect wake word
                self._process_wake_word(audio_chunk)

    def _process_wake_word(self, audio_chunk):
        """Check audio for wake word."""
        if self._wake_model is None:
            # Fallback: no wake word model, use keyboard trigger only
            return

        try:
            # OpenWakeWord expects int16 numpy array
            audio_data = audio_chunk.flatten().astype(np.int16)
            prediction = self._wake_model.predict(audio_data)

            # Check all model predictions
            for model_name, score in prediction.items():
                if score > self.config.WAKE_WORD_THRESHOLD:
                    logger.info(f"Wake word detected! ({model_name}: {score:.2f})")
                    self._wake_model.reset()
                    self._start_listening()
                    return
        except Exception as e:
            logger.error(f"Wake word processing error: {e}")

    def _start_listening(self):
        """Transition to listening mode."""
        self._listening = True
        self._listen_buffer = []
        self._silence_start = None
        self._listen_start = time.time()

        if self.on_wake:
            self.on_wake()
        if self.on_state_change:
            self.on_state_change("listening")

        logger.info("Listening for command...")

    def _process_listening(self, audio_chunk):
        """Accumulate audio while listening, detect silence to stop."""
        self._listen_buffer.append(audio_chunk.copy())

        # Check for timeout
        elapsed = time.time() - self._listen_start
        if elapsed > self.config.LISTEN_TIMEOUT:
            logger.info("Listen timeout reached.")
            self._finish_listening()
            return

        # Simple energy-based silence detection
        energy = np.abs(audio_chunk.astype(np.float32)).mean()
        silence_threshold = 300  # Adjust based on environment

        if energy < silence_threshold:
            if self._silence_start is None:
                self._silence_start = time.time()
            elif time.time() - self._silence_start > self.config.SILENCE_TIMEOUT:
                # Enough silence accumulated — we have a complete utterance
                if len(self._listen_buffer) > 10:  # At least ~0.8s of audio
                    self._finish_listening()
                return
        else:
            self._silence_start = None

    def _finish_listening(self):
        """Process accumulated audio through STT."""
        self._listening = False

        if self.on_state_change:
            self.on_state_change("processing")

        if not self._listen_buffer:
            if self.on_state_change:
                self.on_state_change("idle")
            return

        # Combine audio chunks
        audio_data = np.concatenate(self._listen_buffer, axis=0)
        audio_float = audio_data.astype(np.float32) / 32768.0
        audio_mono = audio_float.flatten()

        # Run STT
        text = self._transcribe(audio_mono)
        if text and text.strip():
            logger.info(f"Transcribed: {text}")
            if self.on_command:
                self.on_command(text.strip())
        else:
            logger.info("No speech detected.")
            if self.on_state_change:
                self.on_state_change("idle")

        self._listen_buffer = []

    def _transcribe(self, audio_float):
        """Transcribe audio using faster-whisper."""
        if self._whisper_model is None:
            logger.error("Whisper model not loaded.")
            return ""

        try:
            segments, info = self._whisper_model.transcribe(
                audio_float,
                beam_size=5,
                language="en",
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=500
                )
            )
            text = " ".join(seg.text for seg in segments)
            return text.strip()
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""

    async def speak(self, text):
        """Convert text to speech using edge-tts and play it."""
        if not text:
            return

        if self.on_state_change:
            self.on_state_change("speaking")

        try:
            import edge_tts

            communicate = edge_tts.Communicate(
                text,
                voice=self.config.TTS_VOICE,
                rate=self.config.TTS_RATE,
                volume=self.config.TTS_VOLUME
            )

            # Save to temp file and play
            temp_path = os.path.join(tempfile.gettempdir(), "jarvis_tts.mp3")
            await communicate.save(temp_path)

            # Play using sounddevice + reading mp3
            self._play_audio_file(temp_path)

        except Exception as e:
            logger.error(f"TTS error: {e}")
        finally:
            if self.on_state_change:
                self.on_state_change("idle")

    def speak_sync(self, text):
        """Synchronous wrapper for speak()."""
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.speak(text))
            loop.close()
        except Exception as e:
            logger.error(f"Sync speak error: {e}")

    def _play_audio_file(self, filepath):
        """Play an audio file through speakers."""
        try:
            # Use a subprocess to play via Windows built-in
            import subprocess
            # Use ffplay (if available) or PowerShell
            try:
                subprocess.run(
                    [
                        "powershell", "-c",
                        f'(New-Object Media.SoundPlayer "{filepath}").PlaySync()'
                    ],
                    capture_output=True, timeout=30,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except Exception:
                # Fallback: use the start command
                os.startfile(filepath)
                time.sleep(3)
        except Exception as e:
            logger.error(f"Audio playback error: {e}")


def generate_wake_sound():
    """Generate a simple wake acknowledgment chime (WAV)."""
    sample_rate = 44100
    duration = 0.3
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # Two-tone chime: C5 → E5
    tone1 = np.sin(2 * np.pi * 523 * t[:len(t)//2]) * 0.5
    tone2 = np.sin(2 * np.pi * 659 * t[len(t)//2:]) * 0.5

    # Apply fade
    fade_len = int(sample_rate * 0.05)
    tone1[:fade_len] *= np.linspace(0, 1, fade_len)
    tone2[-fade_len:] *= np.linspace(1, 0, fade_len)

    audio = np.concatenate([tone1, tone2])
    audio = (audio * 32767).astype(np.int16)

    return sample_rate, audio
