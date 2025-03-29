from samtts import SamTTS


sam = SamTTS(debug=True)
sam.play(
    "To be or not to be, that is the question.",
)

sam.reciter.debug = False
sam.processor.debug = False
sam.renderer.debug = False
sam.play(
    "MAY4 NEYM IHZ SAE4M.",
    phonetic=True,
)
