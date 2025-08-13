import os
import subprocess
import tempfile
import logging
import sounddevice as sd
import numpy as np
from pydub import AudioSegment
from pydub.playback import play

logger = logging.getLogger(__name__)


class SpeechRecognition:
    def __init__(self, config):
        self.config = config
        self.whisper_cpp_path = config.WHISPER_CPP_PATH
        self.whisper_executable = config.WHISPER_EXECUTABLE
        self.model_path = config.WHISPER_MODEL_PATH
        self._validate_whisper_setup()

    def _validate_whisper_setup(self):
        # Validate that whisper.cpp and model are available
        if not os.path.exists(self.whisper_cpp_path):
            raise FileNotFoundError(
                f"Whisper.cpp not found at {self.whisper_cpp_path}"
            )
        if not os.path.exists(self.whisper_executable):
            raise FileNotFoundError(
                f"Whisper executable not found at {self.whisper_executable}"
            )
        if not os.path.exists(self.model_path):
            logger.warning(f"Whisper model not found at {self.model_path}")
            logger.info(
                "You need to download the model file: ggml-large-v3-turbo-q5_0.bin"
            )

    def record_audio(self, duration: int = 5, sample_rate: int = 16000) -> np.ndarray:
        # Record audio from microphone
        logger.info(f"Recording audio for {duration} seconds...")
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.int16
        )
        sd.wait()
        logger.info("Audio recording completed")
        return audio_data

    def save_audio_to_file(
        self, audio_data: np.ndarray, file_path: str, sample_rate: int = 16000
    ):
        """Save audio data to WAV file"""
        import wave
        with wave.open(file_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())

    def transcribe_audio_file(self, audio_file_path: str) -> str:
        """Transcribe audio file using whisper.cpp"""
        try:
            # Run whisper.cpp command
            threads = getattr(self.config, 'WHISPER_THREADS', os.cpu_count() or 4)
            timeout_sec = getattr(self.config, 'WHISPER_TIMEOUT', 180)
            cmd = [
                self.whisper_executable,
                "-m", self.model_path,
                "-f", audio_file_path,
                "-otxt",
                "-of", audio_file_path.replace('.wav', ''),
                "-t", str(threads)
            ]
            logger.info(
                f"Running whisper.cpp: {' '.join(cmd)} (timeout={timeout_sec}s)"
            )
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout_sec
            )
            if result.returncode != 0:
                logger.error(f"Whisper.cpp error: {result.stderr}")
                return "Error transcribing audio"
            # Read the output file
            output_file = audio_file_path.replace('.wav', '.txt')
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    transcription = f.read().strip()
                # Clean up output file
                os.remove(output_file)
                return transcription
            else:
                return "No transcription output found"
        except subprocess.TimeoutExpired:
            logger.error("Whisper.cpp transcription timed out")
            return "Transcription timed out"
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return f"Error transcribing audio: {str(e)}"

    def transcribe_voice_message(self, voice_file_path: str) -> str:
        """Transcribe a voice message file (e.g., from Telegram)"""
        try:
            # Convert voice file to WAV if needed
            audio = AudioSegment.from_file(voice_file_path)
            # Export as WAV
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            audio.export(temp_wav.name, format='wav')
            # Transcribe
            transcription = self.transcribe_audio_file(temp_wav.name)
            # Clean up
            os.unlink(temp_wav.name)
            return transcription
        except Exception as e:
            logger.error(f"Error transcribing voice message: {e}")
            return f"Error transcribing voice message: {str(e)}"

    def record_and_transcribe(self, duration: int = 5) -> str:
        """Record audio and transcribe it"""
        try:
            # Record audio
            audio_data = self.record_audio(duration)
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            self.save_audio_to_file(audio_data, temp_file.name)
            # Transcribe
            transcription = self.transcribe_audio_file(temp_file.name)
            # Clean up
            os.unlink(temp_file.name)
            return transcription
        except Exception as e:
            logger.error(f"Error in record and transcribe: {e}")
            return f"Error recording and transcribing: {str(e)}"

    def is_whisper_available(self) -> bool:
        """Check if whisper.cpp is properly set up"""
        return (
            os.path.exists(self.whisper_executable)
            and os.path.exists(self.model_path)
        )
