import simpleaudio
from samtts import Reciter, Processor, Renderer

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

play_obj = simpleaudio.play_buffer(
    renderer.buffer[: renderer.buffer_end],
    num_channels=1,
    bytes_per_sample=1,
    sample_rate=22050,
)
while play_obj.is_playing():
    pass
