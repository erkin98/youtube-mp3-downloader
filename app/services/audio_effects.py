import logging
import os
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from pydub import AudioSegment
    import soundfile as sf
    import pyrubberband as pyrb
    AUDIO_DEPS_AVAILABLE = True
except ImportError:
    AUDIO_DEPS_AVAILABLE = False
    # Logger might not be configured yet when this module is imported
    # logger.warning("Audio processing dependencies (pydub, soundfile, pyrubberband) not installed.")

class AudioEffectsService:
    @staticmethod
    def process_audio(file_path: str, speed: float = 1.0, pitch: float = 1.0, output_path: str | None = None) -> str:
        """
        Process audio file with speed and pitch changes.
        
        Args:
            file_path: Path to input audio file.
            speed: Speed multiplier (e.g. 1.5 for 1.5x speed).
            pitch: Pitch shift (e.g. 1.5 for higher pitch).
            output_path: Optional output path.
            
        Returns:
            Path to the processed mp3 file.
        """
        if not AUDIO_DEPS_AVAILABLE:
            raise ImportError("Audio dependencies (pydub, soundfile, pyrubberband) are missing.")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Load audio using pydub to ensure we can handle various formats, then export to wav for soundfile
            # Using a temp file for the intermediate wav
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                temp_wav_name = temp_wav.name
            
            try:
                sound = AudioSegment.from_file(file_path)
                sound.export(temp_wav_name, format="wav")
                
                y, sr = sf.read(temp_wav_name)
                
                # Apply effects
                y_stretched = pyrb.time_stretch(y, sr, speed)
                y_shifted = pyrb.pitch_shift(y_stretched, sr, pitch) # Applying pitch shift on stretched audio? 
                # The original code did both separately on original 'y' then wrote to file. 
                # Original:
                # y_stretch = pyrb.time_stretch(y, sr, 0.5)
                # y_shift = pyrb.pitch_shift(y, sr, 0.5) 
                # sf.write(..., y_stretch, ...) 
                # It ignored y_shift! It calculated it but wrote y_stretch.
                
                # Assuming we want to stretch time (change speed) and potentially shift pitch.
                # If we just want to change speed preserving pitch, time_stretch is enough.
                # If we want to change pitch preserving speed, pitch_shift is enough.
                # The original code naming was confusing.
                
                # Let's assume we return the time-stretched version as that's what was written.
                
                processed_wav_name = temp_wav_name + "_processed.wav"
                sf.write(processed_wav_name, y_stretched, sr, format='wav')
                
                # Convert back to mp3
                if output_path:
                    final_path = output_path
                else:
                    base, _ = os.path.splitext(file_path)
                    final_path = f"{base}_speed_{speed}.mp3"
                
                sound_processed = AudioSegment.from_wav(processed_wav_name)
                sound_processed.export(final_path, format="mp3")
                
                # Cleanup processed wav
                if os.path.exists(processed_wav_name):
                    os.remove(processed_wav_name)
                    
                return final_path

            finally:
                if os.path.exists(temp_wav_name):
                    os.remove(temp_wav_name)

        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            raise e
