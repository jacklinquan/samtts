import asyncio

from samtts import SamTTS


def test_play():
    sam = SamTTS()
    sam.play("Test play function.")
    sam.play("Hello, hello. Hello? Hello!")
    sam.play("0 1 2 3 4 5 6 7 8 9!")
    sam.play(
        " ".join(
            [
                "feet.",
                "pin.",
                "beg.",
                "sam.",
                "pot.",
                "budget.",
                "talk.",
                "cone.",
                "book.",
                "loot.",
                "bird.",
                "gallon.",
                "digit.",
                "made.",
                "high.",
                "boy.",
                "how.",
                "slow.",
                "crew.",
                "settle.",
                "astronomy.",
                "function.",
                "kitten.",
                "red.",
                "allow.",
                "away.",
                "whale.",
                "you.",
                "man.",
                "song.",
                "bad.",
                "dog.",
                "again.",
                "judge.",
                "zoo.",
                "pleasure.",
                "seven.",
                "then.",
                "fish.",
                "thin.",
                "poke.",
                "cake.",
                "speech.",
                "ahead.",
            ]
        )
    )


def test_async_play():
    sam = SamTTS()
    asyncio.run(
        sam.async_play(
            " ".join(
                [
                    "Test async play function.",
                    "The quick brown fox jumps over the lazy dog.",
                ]
            )
        )
    )
