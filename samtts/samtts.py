"""SAMTTS SamTTS

SamTTS combines Reciter, Processor and Renderer together.
"""

from __future__ import annotations
from typing import Iterable, Callable, Awaitable
import wave
import asyncio

try:
    import simpleaudio
except ModuleNotFoundError:
    pass

from .reciter import Reciter
from .processor import Processor
from .renderer import Renderer


def iter_by_punctuations(paragraph: str) -> Iterable[str]:
    """Split the paragraph into segments by punctuations.

    The recognized punctuations are "!,.:;?".

    Args:
        paragraph:
            The input string paragraph.

    Yields:
        Segments of the paragraph.
    """

    head = 0
    tail = head
    while head < len(paragraph):
        while tail < len(paragraph):
            tail += 1
            if tail >= len(paragraph):
                yield paragraph[head : tail + 1]
                head = tail + 1
                tail = head
                break

            if paragraph[tail] in "!,.:;?":
                yield paragraph[head : tail + 1]
                head = tail + 1
                tail = head


def save_audio_data_in_wav_format(
    audio_data: bytes | bytearray,
    output_file_path: str,
    num_channels: int = 1,
    bytes_per_sample: int = 1,
    sample_rate: int = 22050,
):
    """Save audio data to wav file.

    Args:
        audio_data:
            The audio data to save.
        output_file_path:
            The path of the output file.
        num_channels:
            The number of channels.
        bytes_per_sample:
            The width of the sample in bytes.
        sample_rate:
            The sample rate of the audio data.
    """

    output_file_path = str(output_file_path)
    with wave.open(output_file_path, mode="wb") as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(bytes_per_sample)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data)


def play_audio_data_with_simpleaudio(
    audio_data: bytes | bytearray,
    num_channels: int = 1,
    bytes_per_sample: int = 1,
    sample_rate: int = 22050,
):
    """Play audio data with simpleaudio.

    Args:
        audio_data:
            The audio data to play.
        num_channels:
            The number of channels.
        bytes_per_sample:
            The width of the sample in bytes.
        sample_rate:
            The sample rate of the audio data.
    """

    try:
        play_obj = simpleaudio.play_buffer(
            audio_data, num_channels, bytes_per_sample, sample_rate
        )
        while play_obj.is_playing():
            pass
    except NameError as err:
        err.add_note(
            "Please install `simpleaudio` or defind your own `play_audio_data` function."
        )
        raise err


async def async_play_audio_data_with_simpleaudio(
    audio_data: bytes | bytearray,
    num_channels: int = 1,
    bytes_per_sample: int = 1,
    sample_rate: int = 22050,
):
    """Async play audio data with simpleaudio.

    Args:
        audio_data:
            The audio data to play.
        num_channels:
            The number of channels.
        bytes_per_sample:
            The width of the sample in bytes.
        sample_rate:
            The sample rate of the audio data.
    """

    try:
        play_obj = simpleaudio.play_buffer(
            audio_data, num_channels, bytes_per_sample, sample_rate
        )
        while play_obj.is_playing():
            await asyncio.sleep(0)
    except NameError as err:
        err.add_note(
            "Please install `simpleaudio` or defind your own `play_audio_data` function."
        )
        raise err


class SamTTS:
    """SamTTS combines Reciter, Processor and Renderer together.

    Args:
        speed:
            Set speed value.
        pitch:
            Set pitch value.
        mouth:
            Set mouth value.
        throat:
            Set throat value.
        sing_mode:
            Set or clear sing_mode flag.
        buffer_size:
            Set a large enough buffer size for rendering.
        debug:
            Set or clear debug flag.
    """

    def __init__(
        self,
        speed: int = 72,
        pitch: int = 64,
        mouth: int = 128,
        throat: int = 128,
        sing_mode: bool = False,
        buffer_size: int = 220500,  # 22050*10, 10s of 22050Hz sound waveform
        debug: bool = False,
    ):
        self.reciter = Reciter(debug)
        self.processor = Processor(debug)
        self.renderer = Renderer(
            speed=speed,
            pitch=pitch,
            mouth=mouth,
            throat=throat,
            sing_mode=sing_mode,
            buffer_size=buffer_size,
            debug=debug,
        )

    def get_audio_data(
        self,
        input_data: str | bytes | bytearray,
        phonetic: bool = False,
        speed: int | None = None,
        pitch: int | None = None,
        mouth: int | None = None,
        throat: int | None = None,
        sing_mode: bool | None = None,
        sample_rate: int = 22050,
    ) -> bytearray:
        """Get audio data from input text or phonemes.

        It can only process very short inputs.

        Args:
            input_data:
                The input text or phonemes.
            phonetic:
                The flag indicates if the input is phonemes.
            speed:
                Set speed value.
            pitch:
                Set pitch value.
            mouth:
                Set mouth value.
            throat:
                Set throat value.
            sing_mode:
                Set or clear sing_mode flag.
            sample_rate:
                The sample rate of the audio data. It can be one of 5513, 11025 and 22050.

        Returns:
            The rendered audio data bytearray.
        """

        if sample_rate not in (5513, 11025, 22050):
            raise Exception("Sample rate must be one of (5513, 11025, 22050).")

        if not phonetic:
            if self.reciter.debug:
                print(f"Input text: {input_data}")
                print()
            phonemes = self.reciter.text_to_phonemes(input_data)
        else:
            phonemes = input_data

        if self.processor.debug:
            print(f"Input phonemes: {phonemes}")
            print()
        self.processor.process(phonemes)

        speed = speed if speed is not None else self.renderer.speed
        pitch = pitch if pitch is not None else self.renderer.pitch
        mouth = mouth if mouth is not None else self.renderer.mouth
        throat = throat if throat is not None else self.renderer.throat
        sing_mode = sing_mode if sing_mode is not None else self.renderer.sing_mode
        self.renderer.config(speed, pitch, mouth, throat, sing_mode)
        self.renderer.render(self.processor)

        if sample_rate == 22050:
            return self.renderer.buffer[: self.renderer.buffer_end]
        elif sample_rate == 11025:
            return self.renderer.buffer[: self.renderer.buffer_end : 2]
        elif sample_rate == 5513:
            return self.renderer.buffer[: self.renderer.buffer_end : 4]

    def iter_audio_data_from_paragraph(
        self,
        paragraph: str,
        phonetic: bool = False,
        speed: int | None = None,
        pitch: int | None = None,
        mouth: int | None = None,
        throat: int | None = None,
        sing_mode: bool | None = None,
        sample_rate: int = 22050,
        iter_segments_from_paragraph: Callable = iter_by_punctuations,
    ) -> Iterable[bytearray]:
        """Get audio data from a paragraph segment by segment.

        Args:
            paragraph:
                The input string paragraph.
            phonetic:
                The flag indicates if the input is phonemes.
            speed:
                Set speed value.
            pitch:
                Set pitch value.
            mouth:
                Set mouth value.
            throat:
                Set throat value.
            sing_mode:
                Set or clear sing_mode flag.
            sample_rate:
                The sample rate of the audio data. It can be one of 5513, 11025 and 22050.
            iter_segments_from_paragraph:
                The `iter_segments_from_paragraph` function whose signature is:
                ```python
                iter_segments_from_paragraph(paragraph: str) -> Iterable[str]
                ```

        Yields:
            Audio data.
        """

        if sample_rate not in (5513, 11025, 22050):
            raise Exception("Sample rate must be one of (5513, 11025, 22050).")

        speed = speed if speed is not None else self.renderer.speed
        pitch = pitch if pitch is not None else self.renderer.pitch
        mouth = mouth if mouth is not None else self.renderer.mouth
        throat = throat if throat is not None else self.renderer.throat
        sing_mode = sing_mode if sing_mode is not None else self.renderer.sing_mode
        self.renderer.config(speed, pitch, mouth, throat, sing_mode)

        for segment in iter_segments_from_paragraph(paragraph):
            if (not segment) or (
                len(segment) == 1
                and (not segment.isalpha())
                and (not segment.isdigit())
            ):
                continue

            if not phonetic:
                if self.reciter.debug:
                    print(f"Input text: {segment}")
                    print()
                phonemes = self.reciter.text_to_phonemes(segment)
            else:
                phonemes = segment

            if self.processor.debug:
                print(f"Input phonemes: {phonemes}")
                print()
            self.processor.process(phonemes)

            self.renderer.render(self.processor)

            if sample_rate == 22050:
                yield self.renderer.buffer[: self.renderer.buffer_end]
            elif sample_rate == 11025:
                yield self.renderer.buffer[: self.renderer.buffer_end : 2]
            elif sample_rate == 5513:
                yield self.renderer.buffer[: self.renderer.buffer_end : 4]

    def save(
        self,
        paragraph: str,
        output_file_path: str,
        phonetic: bool = False,
        speed: int | None = None,
        pitch: int | None = None,
        mouth: int | None = None,
        throat: int | None = None,
        sing_mode: bool | None = None,
        sample_rate: int = 22050,
        iter_segments_from_paragraph: Callable = iter_by_punctuations,
        save_audio_data: Callable = save_audio_data_in_wav_format,
    ):
        """Save audio data from a paragraph to output file.

        Args:
            paragraph:
                The input paragraph.
            output_file_path:
                The path of the output file.
            phonetic:
                The flag indicates if the input is phonemes.
            speed:
                Set speed value.
            pitch:
                Set pitch value.
            mouth:
                Set mouth value.
            throat:
                Set throat value.
            sing_mode:
                Set or clear sing_mode flag.
            sample_rate:
                The sample rate of the audio data. It can be one of 5513, 11025 and 22050.
            iter_segments_from_paragraph:
                The `iter_segments_from_paragraph` function whose signature is:
                ```python
                iter_segments_from_paragraph(paragraph: str) -> Iterable[str]
                ```
            save_audio_data:
                The `save_audio_data` function whose signature is:
                ```python
                save_audio_data(
                    audio_data: bytes | bytearray,
                    output_file_path: str,
                    num_channels: int,
                    bytes_per_sample: int,
                    sample_rate: int,
                )
                ```
        """

        full_audio_data = bytearray()

        for audio_data in self.iter_audio_data_from_paragraph(
            paragraph,
            phonetic=phonetic,
            speed=speed if speed is not None else self.renderer.speed,
            pitch=pitch if pitch is not None else self.renderer.pitch,
            mouth=mouth if mouth is not None else self.renderer.mouth,
            throat=throat if throat is not None else self.renderer.throat,
            sing_mode=sing_mode if sing_mode is not None else self.renderer.sing_mode,
            sample_rate=sample_rate,
            iter_segments_from_paragraph=iter_segments_from_paragraph,
        ):
            if self.renderer.debug:
                print(f"Audio data length: {len(audio_data)} bytes")

            full_audio_data += audio_data

        if self.renderer.debug:
            print(f"Total audio data length: {len(full_audio_data)} bytes")

        save_audio_data(
            full_audio_data,
            output_file_path,
            num_channels=1,
            bytes_per_sample=1,
            sample_rate=sample_rate,
        )

    def play(
        self,
        paragraph: str,
        phonetic: bool = False,
        speed: int | None = None,
        pitch: int | None = None,
        mouth: int | None = None,
        throat: int | None = None,
        sing_mode: bool | None = None,
        sample_rate: int = 22050,
        iter_segments_from_paragraph: Callable = iter_by_punctuations,
        play_audio_data: Callable = play_audio_data_with_simpleaudio,
    ):
        """Play audio data from a paragraph.

        Args:
            paragraph:
                The input paragraph.
            phonetic:
                The flag indicates if the input is phonemes.
            speed:
                Set speed value.
            pitch:
                Set pitch value.
            mouth:
                Set mouth value.
            throat:
                Set throat value.
            sing_mode:
                Set or clear sing_mode flag.
            sample_rate:
                The sample rate of the audio data. It can be one of 5513, 11025 and 22050.
            iter_segments_from_paragraph:
                The `iter_segments_from_paragraph` function whose signature is:
                ```python
                iter_segments_from_paragraph(paragraph: str) -> Iterable[str]
                ```
            play_audio_data:
                The `play_audio_data` function whose signature is:
                ```python
                play_audio_data(
                    audio_data: bytes | bytearray,
                    num_channels: int,
                    bytes_per_sample: int,
                    sample_rate: int,
                )
                ```
        """

        for audio_data in self.iter_audio_data_from_paragraph(
            paragraph,
            phonetic=phonetic,
            speed=speed if speed is not None else self.renderer.speed,
            pitch=pitch if pitch is not None else self.renderer.pitch,
            mouth=mouth if mouth is not None else self.renderer.mouth,
            throat=throat if throat is not None else self.renderer.throat,
            sing_mode=sing_mode if sing_mode is not None else self.renderer.sing_mode,
            sample_rate=sample_rate,
            iter_segments_from_paragraph=iter_segments_from_paragraph,
        ):
            play_audio_data(
                audio_data,
                num_channels=1,
                bytes_per_sample=1,
                sample_rate=sample_rate,
            )

    async def async_play(
        self,
        paragraph: str,
        phonetic: bool = False,
        speed: int | None = None,
        pitch: int | None = None,
        mouth: int | None = None,
        throat: int | None = None,
        sing_mode: bool | None = None,
        sample_rate: int = 22050,
        iter_segments_from_paragraph: Callable = iter_by_punctuations,
        async_play_audio_data: Awaitable = async_play_audio_data_with_simpleaudio,
    ):
        """Async play audio data from a paragraph.

        Args:
            paragraph:
                The input paragraph.
            phonetic:
                The flag indicates if the input is phonemes.
            speed:
                Set speed value.
            pitch:
                Set pitch value.
            mouth:
                Set mouth value.
            throat:
                Set throat value.
            sing_mode:
                Set or clear sing_mode flag.
            sample_rate:
                The sample rate of the audio data. It can be one of 5513, 11025 and 22050.
            iter_segments_from_paragraph:
                The `iter_segments_from_paragraph` function whose signature is:
                ```python
                iter_segments_from_paragraph(paragraph: str) -> Iterable[str]
                ```
            async_play_audio_data:
                The `async_play_audio_data` function whose signature is:
                ```python
                async_play_audio_data(
                    audio_data: bytes | bytearray,
                    num_channels: int,
                    bytes_per_sample: int,
                    sample_rate: int,
                )
                ```
        """

        for audio_data in self.iter_audio_data_from_paragraph(
            paragraph,
            phonetic=phonetic,
            speed=speed if speed is not None else self.renderer.speed,
            pitch=pitch if pitch is not None else self.renderer.pitch,
            mouth=mouth if mouth is not None else self.renderer.mouth,
            throat=throat if throat is not None else self.renderer.throat,
            sing_mode=sing_mode if sing_mode is not None else self.renderer.sing_mode,
            sample_rate=sample_rate,
            iter_segments_from_paragraph=iter_segments_from_paragraph,
        ):
            await async_play_audio_data(
                audio_data,
                num_channels=1,
                bytes_per_sample=1,
                sample_rate=sample_rate,
            )
