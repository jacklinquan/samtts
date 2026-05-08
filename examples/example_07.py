import pyaudio
from samtts import Reciter, Processor, Renderer


def pyaudio_play_buffer(
    audio_data: bytes | bytearray,
    num_channels: int = 1,
    bytes_per_sample: int = 1,
    sample_rate: int = 22050,
):
    p = pyaudio.PyAudio()

    try:
        if bytes_per_sample == 1:
            audio_format = pyaudio.paUInt8
        else:
            audio_format = p.get_format_from_width(bytes_per_sample)

        stream = p.open(
            format=audio_format,
            channels=num_channels,
            rate=sample_rate,
            output=True,
        )

        try:
            stream.write(bytes(audio_data))
        finally:
            stream.stop_stream()
            stream.close()

    finally:
        p.terminate()


reciter = Reciter()
processor = Processor()
renderer = Renderer()

input_text = "Hello. My name is Sam. How are you?"
print(f"{input_text = }")

phonemes = reciter.text_to_phonemes(input_text)
print(f"{phonemes = }")

processor.process(phonemes)
renderer.render(processor)

print(f"{renderer.buffer_end = }")
print(f"The first 100 bytes in the buffer: {renderer.buffer[: 100]}")

pyaudio_play_buffer(
    renderer.buffer[: renderer.buffer_end],
    num_channels=1,
    bytes_per_sample=1,
    sample_rate=22050,
)
