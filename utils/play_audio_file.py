# sudo apt install portaudio19-dev
import pyaudio
import wave


def play_audio_file(file_path):
    file = wave.open(file_path, 'rb')
    # Define stream chunk
    CHUNK = 1024

    # Instantiate PyAudio
    p = pyaudio.PyAudio()
    # Open stream
    stream = p.open(format=p.get_format_from_width(file.getsampwidth()),
                    channels=file.getnchannels(),
                    rate=file.getframerate(),
                    output=True)
    # Read data
    data = file.readframes(CHUNK)

    # Play stream
    while data:
        stream.write(data)
        data = file.readframes(CHUNK)

    # Stop stream
    stream.stop_stream()
    stream.close()

    # Close PyAudio
    p.terminate()
