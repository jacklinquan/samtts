"""SAMTTS CLI

The command line interface of samtts.
"""

from __future__ import annotations

try:
    import typer
    from typing_extensions import Annotated
except ModuleNotFoundError:
    pass

from .samtts import SamTTS


phoneme_info_text = """
                 Phoneme Information

     VOWELS                             VOICED CONSONANTS
IY           f(ee)t                     R        red
IH           p(i)n                      L        allow
EH           beg                        W        away
AE           Sam                        W        whale
AA           pot                        Y        you
AH           b(u)dget                   M        Sam
AO           t(al)k                     N        man
OH           cone                       NX       so(ng)
UH           book                       B        bad
UX           l(oo)t                     D        dog
ER           bird                       G        again
AX           gall(o)n                   J        judge
IX           dig(i)t                    Z        zoo
                                        ZH       plea(s)ure
   DIPHTHONGS                           V        seven
EY           m(a)de                     DH       (th)en
AY           h(igh)
OY           boy
AW           h(ow)                      UNVOICED CONSONANTS
OW           slow                       S         Sam
UW           crew                       Sh        fish
                                        F         fish
                                        TH        thin
 SPECIAL PHONEMES                       P         poke
UL           sett(le) (=AXL)            T         talk
UM           astron(omy) (=AXM)         K         cake
UN           functi(on) (=AXN)          CH        speech
Q            kitt-en (glottal stop)     /H        a(h)ead
"""

pitch_info_text = """
                  Pitch Information

PITCH   NOTE    |   PITCH   NOTE    |   PITCH   NOTE
 104     C1     |     52     C2     |     26     C3
  92     D1     |     46     D2     |     23     D3
  82     E1     |     41     E2     |     21     E3
  78     F1     |     39     F2     |     19     F3
  68     G1     |     34     G2     |     17     G3
  62     A1     |     31     A2     |
  55     B1     |     28     B2     |
"""

try:
    app = typer.Typer()
except NameError as err:
    err.add_note("Please install `typer`.")
    raise err


@app.command(no_args_is_help=True)
def app_main(
    input_string: Annotated[str, typer.Argument(help="Input text or phonemes.")] = "",
    phoneme_info: Annotated[bool, typer.Option(help="Show phoneme info.")] = False,
    pitch_info: Annotated[bool, typer.Option(help="Show pitch info.")] = False,
    phonetic: Annotated[bool, typer.Option(help="Set phonetic flag.")] = False,
    speed: Annotated[int, typer.Option(help="Set speed value.")] = 72,
    pitch: Annotated[int, typer.Option(help="Set pitch value.")] = 64,
    mouth: Annotated[int, typer.Option(help="Set mouth value.")] = 128,
    throat: Annotated[int, typer.Option(help="Set throat value.")] = 128,
    sing: Annotated[bool, typer.Option(help="Set sing mode.")] = False,
    sample_rate: Annotated[
        int, typer.Option(help="Set sample rate 11025 or 22050.")
    ] = 22050,
    wav: Annotated[str, typer.Option(help="Set output wav file name or path.")] = "",
    debug: Annotated[bool, typer.Option(help="Set debug flag.")] = False,
):
    """A python port of Software Automatic Mouth Test-To-Speech program.

    - If `--phoneme-info` or `--pitch-info` is used, the argument and all the other options are ignored.

    - If `--phonetic` is used, the input must be valid phonemes.
    """

    if phoneme_info:
        print(phoneme_info_text)
        print()
    if pitch_info:
        print(pitch_info_text)
        print()
    if phoneme_info or pitch_info:
        return

    if sample_rate not in (11025, 22050):
        print("Sample rate must be 11025 or 22050.")
        return

    sam = SamTTS(debug=debug)

    if wav:
        sam.save(
            input_string,
            wav,
            phonetic=phonetic,
            speed=speed,
            pitch=pitch,
            mouth=mouth,
            throat=throat,
            sing_mode=sing,
            sample_rate=sample_rate,
        )
    else:
        sam.play(
            input_string,
            phonetic=phonetic,
            speed=speed,
            pitch=pitch,
            mouth=mouth,
            throat=throat,
            sing_mode=sing,
            sample_rate=sample_rate,
        )


def main():
    app()


if __name__ == "__main__":
    main()
