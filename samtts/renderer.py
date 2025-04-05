"""SAMTTS Renderer

Renderer takes the phoneme parameters and renders sound waveform.
"""

from __future__ import annotations

from .processor import Processor


PHONEME_PERIOD = 1
PHONEME_QUESTION = 2

RISING_INFLECTION = 1
FALLING_INFLECTION = 255

# tab48426 = bytes([
#     0x18, 0x1A, 0x17, 0x17, 0x17
# ])
tab48426 = b"\x18\x1a\x17\x17\x17"

# tab47492 = bytes([
#     0 , 0 , 0xE0 , 0xE6 , 0xEC , 0xF3 , 0xF9 , 0 ,
#     6 , 0xC , 6
# ])
tab47492 = b"\x00\x00\xe0\xe6\xec\xf3\xf9\x00\x06\x0c\x06"

# amplitude_rescale = bytes([
#     0 , 1 , 2 , 2 , 2 , 3 , 3 , 4 ,
#     4 , 5 , 6 , 8 , 9 ,0xB ,0xD ,0xF, 0  # //17 elements?
# ])
amplitude_rescale = b"\x00\x01\x02\x02\x02\x03\x03\x04\x04\x05\x06\x08\t\x0b\r\x0f\x00"

# // Used to decide which phoneme's blend lengths. The candidate with the lower score is selected.
# blend_rank = bytes([
#     0 , 0x1F , 0x1F , 0x1F , 0x1F , 2 , 2 , 2 ,
#     2 , 2 , 2 , 2 , 2 , 2 , 5 , 5 ,
#     2 ,0xA , 2 , 8 , 5 , 5 ,0xB ,0xA ,
#     9 , 8 , 8 , 0xA0 , 8 , 8 , 0x17 , 0x1F ,
#     0x12 , 0x12 , 0x12 , 0x12 , 0x1E , 0x1E , 0x14 , 0x14 ,
#     0x14 , 0x14 , 0x17 , 0x17 , 0x1A , 0x1A , 0x1D , 0x1D ,
#     2 , 2 , 2 , 2 , 2 , 2 , 0x1A , 0x1D ,
#     0x1B , 0x1A , 0x1D , 0x1B , 0x1A , 0x1D , 0x1B , 0x1A ,
#     0x1D , 0x1B , 0x17 , 0x1D , 0x17 , 0x17 , 0x1D , 0x17 ,
#     0x17 , 0x1D , 0x17 , 0x17 , 0x1D , 0x17 , 0x17 , 0x17
# ])
blend_rank = b"\x00\x1f\x1f\x1f\x1f\x02\x02\x02\x02\x02\x02\x02\x02\x02\x05\x05\x02\n\x02\x08\x05\x05\x0b\n\t\x08\x08\xa0\x08\x08\x17\x1f\x12\x12\x12\x12\x1e\x1e\x14\x14\x14\x14\x17\x17\x1a\x1a\x1d\x1d\x02\x02\x02\x02\x02\x02\x1a\x1d\x1b\x1a\x1d\x1b\x1a\x1d\x1b\x1a\x1d\x1b\x17\x1d\x17\x17\x1d\x17\x17\x1d\x17\x17\x1d\x17\x17\x17"

# // Number of frames at the end of a phoneme devoted to interpolating to next phoneme's final value
# out_blend_length = bytes([
#     0 , 2 , 2 , 2 , 2 , 4 , 4 , 4 ,
#     4 , 4 , 4 , 4 , 4 , 4 , 4 , 4 ,
#     4 , 4 , 3 , 2 , 4 , 4 , 2 , 2 ,
#     2 , 2 , 2 , 1 , 1 , 1 , 1 , 1 ,
#     1 , 1 , 1 , 1 , 1 , 1 , 2 , 2 ,
#     2 , 1 , 0 , 1 , 0 , 1 , 0 , 5 ,
#     5 , 5 , 5 , 5 , 4 , 4 , 2 , 0 ,
#     1 , 2 , 0 , 1 , 2 , 0 , 1 , 2 ,
#     0 , 1 , 2 , 0 , 2 , 2 , 0 , 1 ,
#     3 , 0 , 2 , 3 , 0 , 2 , 0xA0 , 0xA0
# ])
out_blend_length = b"\x00\x02\x02\x02\x02\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x03\x02\x04\x04\x02\x02\x02\x02\x02\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x02\x02\x02\x01\x00\x01\x00\x01\x00\x05\x05\x05\x05\x05\x04\x04\x02\x00\x01\x02\x00\x01\x02\x00\x01\x02\x00\x01\x02\x00\x02\x02\x00\x01\x03\x00\x02\x03\x00\x02\xa0\xa0"

# // Number of frames at beginning of a phoneme devoted to interpolating to phoneme's final value
# in_blend_length = bytes([
#     0 , 2 , 2 , 2 , 2 , 4 , 4 , 4 ,
#     4 , 4 , 4 , 4 , 4 , 4 , 4 , 4 ,
#     4 , 4 , 3 , 3 , 4 , 4 , 3 , 3 ,
#     3 , 3 , 3 , 1 , 2 , 3 , 2 , 1 ,
#     3 , 3 , 3 , 3 , 1 , 1 , 3 , 3 ,
#     3 , 2 , 2 , 3 , 2 , 3 , 0 , 0 ,
#     5 , 5 , 5 , 5 , 4 , 4 , 2 , 0 ,
#     2 , 2 , 0 , 3 , 2 , 0 , 4 , 2 ,
#     0 , 3 , 2 , 0 , 2 , 2 , 0 , 2 ,
#     3 , 0 , 3 , 3 , 0 , 3 , 0xB0 , 0xA0
# ])
in_blend_length = b"\x00\x02\x02\x02\x02\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x03\x03\x04\x04\x03\x03\x03\x03\x03\x01\x02\x03\x02\x01\x03\x03\x03\x03\x01\x01\x03\x03\x03\x02\x02\x03\x02\x03\x00\x00\x05\x05\x05\x05\x04\x04\x02\x00\x02\x02\x00\x03\x02\x00\x04\x02\x00\x03\x02\x00\x02\x02\x00\x02\x03\x00\x03\x03\x00\x03\xb0\xa0"

# // Looks like it's used as bit flags
# // High bits masked by 248 (11111000)
# //
# // 32: S*    241         11110001
# // 33: SH    226         11100010
# // 34: F*    211         11010011
# // 35: TH    187         10111011
# // 36: /H    124         01111100
# // 37: /X    149         10010101
# // 38: Z*    1           00000001
# // 39: ZH    2           00000010
# // 40: V*    3           00000011
# // 41: DH    3           00000011
# // 43: **    114         01110010
# // 45: **    2           00000010
# // 67: **    27          00011011
# // 70: **    25          00011001
# sampled_consonant_flags = bytes([
#     0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ,
#     0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ,
#     0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ,
#     0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ,
#     0xF1 , 0xE2 , 0xD3 , 0xBB , 0x7C , 0x95 , 1 , 2 ,
#     3 , 3 , 0 , 0x72 , 0 , 2 , 0 , 0 ,
#     0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ,
#     0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ,
#     0 , 0 , 0 , 0x1B , 0 , 0 , 0x19 , 0 ,
#     0 , 0 , 0 , 0 , 0 , 0 , 0 , 0
# ])
sampled_consonant_flags = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf1\xe2\xd3\xbb|\x95\x01\x02\x03\x03\x00r\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1b\x00\x00\x19\x00\x00\x00\x00\x00\x00\x00\x00\x00"

# freq3data = bytes([
#     0x00 , 0x5B , 0x5B , 0x5B , 0x5B , 0x6E , 0x5D , 0x5B ,
#     0x58 , 0x59 , 0x57 , 0x58 , 0x52 , 0x59 , 0x5D , 0x3E ,
#     0x52 , 0x58 , 0x3E , 0x6E , 0x50 , 0x5D , 0x5A , 0x3C ,
#     0x6E , 0x5A , 0x6E , 0x51 , 0x79 , 0x65 , 0x79 , 0x5B ,
#     0x63 , 0x6A , 0x51 , 0x79 , 0x5D , 0x52 , 0x5D , 0x67 ,
#     0x4C , 0x5D , 0x65 , 0x65 , 0x79 , 0x65 , 0x79 , 0x00 ,
#     0x5A , 0x58 , 0x58 , 0x58 , 0x58 , 0x52 , 0x51 , 0x51 ,
#     0x51 , 0x79 , 0x79 , 0x79 , 0x70 , 0x6E , 0x6E , 0x5E ,
#     0x5E , 0x5E , 0x51 , 0x51 , 0x51 , 0x79 , 0x79 , 0x79 ,
#     0x65 , 0x65 , 0x70 , 0x5E , 0x5E , 0x5E , 0x08 , 0x01
# ])
freq3data = b"\x00[[[[n][XYWXRY]>RX>nP]Z<nZnQyey[cjQy]R]gL]eeyey\x00ZXXXXRQQQyyypnn^^^QQQyyyeep^^^\x08\x01"

# ampl1data = bytes([
#     0 , 0 , 0 , 0 , 0 ,0xD ,0xD ,0xE ,
#     0xF ,0xF ,0xF ,0xF ,0xF ,0xC ,0xD ,0xC ,
#     0xF ,0xF ,0xD ,0xD ,0xD ,0xE ,0xD ,0xC ,
#     0xD ,0xD ,0xD ,0xC , 9 , 9 , 0 , 0 ,
#     0 , 0 , 0 , 0 , 0 , 0 ,0xB ,0xB ,
#     0xB ,0xB , 0 , 0 , 1 ,0xB , 0 , 2 ,
#     0xE ,0xF ,0xF ,0xF ,0xF ,0xD , 2 , 4 ,
#     0 , 2 , 4 , 0 , 1 , 4 , 0 , 1 ,
#     4 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ,
#     0 ,0xC , 0 , 0 , 0 , 0 ,0xF ,0xF
# ])
ampl1data = b"\x00\x00\x00\x00\x00\r\r\x0e\x0f\x0f\x0f\x0f\x0f\x0c\r\x0c\x0f\x0f\r\r\r\x0e\r\x0c\r\r\r\x0c\t\t\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x0b\x0b\x0b\x00\x00\x01\x0b\x00\x02\x0e\x0f\x0f\x0f\x0f\r\x02\x04\x00\x02\x04\x00\x01\x04\x00\x01\x04\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x0f\x0f"

# ampl2data = bytes([
#     0 , 0 , 0 , 0 , 0 ,0xA ,0xB ,0xD ,
#     0xE ,0xD ,0xC ,0xC ,0xB , 9 ,0xB ,0xB ,
#     0xC ,0xC ,0xC , 8 , 8 ,0xC , 8 ,0xA ,
#     8 , 8 ,0xA , 3 , 9 , 6 , 0 , 0 ,
#     0 , 0 , 0 , 0 , 0 , 0 , 3 , 5 ,
#     3 , 4 , 0 , 0 , 0 , 5 ,0xA , 2 ,
#     0xE ,0xD ,0xC ,0xD ,0xC , 8 , 0 , 1 ,
#     0 , 0 , 1 , 0 , 0 , 1 , 0 , 0 ,
#     1 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ,
#     0 ,0xA , 0 , 0 ,0xA , 0 , 0 , 0
# ])
ampl2data = b"\x00\x00\x00\x00\x00\n\x0b\r\x0e\r\x0c\x0c\x0b\t\x0b\x0b\x0c\x0c\x0c\x08\x08\x0c\x08\n\x08\x08\n\x03\t\x06\x00\x00\x00\x00\x00\x00\x00\x00\x03\x05\x03\x04\x00\x00\x00\x05\n\x02\x0e\r\x0c\r\x0c\x08\x00\x01\x00\x00\x01\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\n\x00\x00\x00"

# ampl3data = bytes([
#     0 , 0 , 0 , 0 , 0 , 8 , 7 , 8 ,
#     8 , 1 , 1 , 0 , 1 , 0 , 7 , 5 ,
#     1 , 0 , 6 , 1 , 0 , 7 , 0 , 5 ,
#     1 , 0 , 8 , 0 , 0 , 3 , 0 , 0 ,
#     0 , 0 , 0 , 0 , 0 , 0 , 0 , 1 ,
#     0 , 0 , 0 , 0 , 0 , 1 ,0xE , 1 ,
#     9 , 1 , 0 , 1 , 0 , 0 , 0 , 0 ,
#     0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ,
#     0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ,
#     0 , 7 , 0 , 0 , 5 , 0 , 0x13 , 0x10
# ])
ampl3data = b"\x00\x00\x00\x00\x00\x08\x07\x08\x08\x01\x01\x00\x01\x00\x07\x05\x01\x00\x06\x01\x00\x07\x00\x05\x01\x00\x08\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x0e\x01\t\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x05\x00\x13\x10"

# sinus = bytes([
#     0x00 , 0x00 , 0x00 , 0x10 , 0x10 , 0x10 , 0x10 , 0x10 ,
#     0x10 , 0x20 , 0x20 , 0x20 , 0x20 , 0x20 , 0x20 , 0x30 ,
#     0x30 , 0x30 , 0x30 , 0x30 , 0x30 , 0x30 , 0x40 , 0x40 ,
#     0x40 , 0x40 , 0x40 , 0x40 , 0x40 , 0x50 , 0x50 , 0x50 ,
#     0x50 , 0x50 , 0x50 , 0x50 , 0x50 , 0x60 , 0x60 , 0x60 ,
#     0x60 , 0x60 , 0x60 , 0x60 , 0x60 , 0x60 , 0x60 , 0x60 ,
#     0x60 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x60 , 0x60 , 0x60 , 0x60 , 0x60 , 0x60 , 0x60 , 0x60 ,
#     0x60 , 0x60 , 0x60 , 0x60 , 0x50 , 0x50 , 0x50 , 0x50 ,
#     0x50 , 0x50 , 0x50 , 0x50 , 0x40 , 0x40 , 0x40 , 0x40 ,
#     0x40 , 0x40 , 0x40 , 0x30 , 0x30 , 0x30 , 0x30 , 0x30 ,
#     0x30 , 0x30 , 0x20 , 0x20 , 0x20 , 0x20 , 0x20 , 0x20 ,
#     0x10 , 0x10 , 0x10 , 0x10 , 0x10 , 0x10 , 0x00 , 0x00 ,
#     0x00 , 0x00 , 0x00 , 0xF0 , 0xF0 , 0xF0 , 0xF0 , 0xF0 ,
#     0xF0 , 0xE0 , 0xE0 , 0xE0 , 0xE0 , 0xE0 , 0xE0 , 0xD0 ,
#     0xD0 , 0xD0 , 0xD0 , 0xD0 , 0xD0 , 0xD0 , 0xC0 , 0xC0 ,
#     0xC0 , 0xC0 , 0xC0 , 0xC0 , 0xC0 , 0xB0 , 0xB0 , 0xB0 ,
#     0xB0 , 0xB0 , 0xB0 , 0xB0 , 0xB0 , 0xA0 , 0xA0 , 0xA0 ,
#     0xA0 , 0xA0 , 0xA0 , 0xA0 , 0xA0 , 0xA0 , 0xA0 , 0xA0 ,
#     0xA0 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0xA0 , 0xA0 , 0xA0 , 0xA0 , 0xA0 , 0xA0 , 0xA0 , 0xA0 ,
#     0xA0 , 0xA0 , 0xA0 , 0xA0 , 0xB0 , 0xB0 , 0xB0 , 0xB0 ,
#     0xB0 , 0xB0 , 0xB0 , 0xB0 , 0xC0 , 0xC0 , 0xC0 , 0xC0 ,
#     0xC0 , 0xC0 , 0xC0 , 0xD0 , 0xD0 , 0xD0 , 0xD0 , 0xD0 ,
#     0xD0 , 0xD0 , 0xE0 , 0xE0 , 0xE0 , 0xE0 , 0xE0 , 0xE0 ,
#     0xF0 , 0xF0 , 0xF0 , 0xF0 , 0xF0 , 0xF0 , 0x00 , 0x00
# ])
sinus = b"\x00\x00\x00\x10\x10\x10\x10\x10\x10      0000000@@@@@@@PPPPPPPP````````````ppppppppppppppppppppppppppppppp````````````PPPPPPPP@@@@@@@0000000      \x10\x10\x10\x10\x10\x10\x00\x00\x00\x00\x00\xf0\xf0\xf0\xf0\xf0\xf0\xe0\xe0\xe0\xe0\xe0\xe0\xd0\xd0\xd0\xd0\xd0\xd0\xd0\xc0\xc0\xc0\xc0\xc0\xc0\xc0\xb0\xb0\xb0\xb0\xb0\xb0\xb0\xb0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xb0\xb0\xb0\xb0\xb0\xb0\xb0\xb0\xc0\xc0\xc0\xc0\xc0\xc0\xc0\xd0\xd0\xd0\xd0\xd0\xd0\xd0\xe0\xe0\xe0\xe0\xe0\xe0\xf0\xf0\xf0\xf0\xf0\xf0\x00\x00"

# rectangle = bytes([
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 , 0x90 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 ,
#     0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70 , 0x70
# ])
# def rectangle(index):
#     return -112 if index < 128 else 112
rectangle = b"\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp"

# mult_table = bytes([
#   0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 ,
# 	0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 ,
# 	0x00 , 0x00 , 0x01 , 0x01 , 0x02 , 0x02 , 0x03 , 0x03 ,
# 	0x04 , 0x04 , 0x05 , 0x05 , 0x06 , 0x06 , 0x07 , 0x07 ,
# 	0x00 , 0x01 , 0x02 , 0x03 , 0x04 , 0x05 , 0x06 , 0x07 ,
# 	0x08 , 0x09 , 0x0A , 0x0B , 0x0C , 0x0D , 0x0E , 0x0F ,
# 	0x00 , 0x01 , 0x03 , 0x04 , 0x06 , 0x07 , 0x09 , 0x0A ,
# 	0x0C , 0x0D , 0x0F , 0x10 , 0x12 , 0x13 , 0x15 , 0x16 ,
# 	0x00 , 0x02 , 0x04 , 0x06 , 0x08 , 0x0A , 0x0C , 0x0E ,
# 	0x10 , 0x12 , 0x14 , 0x16 , 0x18 , 0x1A , 0x1C , 0x1E ,
# 	0x00 , 0x02 , 0x05 , 0x07 , 0x0A , 0x0C , 0x0F , 0x11 ,
# 	0x14 , 0x16 , 0x19 , 0x1B , 0x1E , 0x20 , 0x23 , 0x25 ,
# 	0x00 , 0x03 , 0x06 , 0x09 , 0x0C , 0x0F , 0x12 , 0x15 ,
# 	0x18 , 0x1B , 0x1E , 0x21 , 0x24 , 0x27 , 0x2A , 0x2D ,
# 	0x00 , 0x03 , 0x07 , 0x0A , 0x0E , 0x11 , 0x15 , 0x18 ,
# 	0x1C , 0x1F , 0x23 , 0x26 , 0x2A , 0x2D , 0x31 , 0x34 ,
# 	0x00 , 0xFC , 0xF8 , 0xF4 , 0xF0 , 0xEC , 0xE8 , 0xE4 ,
# 	0xE0 , 0xDC , 0xD8 , 0xD4 , 0xD0 , 0xCC , 0xC8 , 0xC4 ,
# 	0x00 , 0xFC , 0xF9 , 0xF5 , 0xF2 , 0xEE , 0xEB , 0xE7 ,
# 	0xE4 , 0xE0 , 0xDD , 0xD9 , 0xD6 , 0xD2 , 0xCF , 0xCB ,
# 	0x00 , 0xFD , 0xFA , 0xF7 , 0xF4 , 0xF1 , 0xEE , 0xEB ,
# 	0xE8 , 0xE5 , 0xE2 , 0xDF , 0xDC , 0xD9 , 0xD6 , 0xD3 ,
# 	0x00 , 0xFD , 0xFB , 0xF8 , 0xF6 , 0xF3 , 0xF1 , 0xEE ,
# 	0xEC , 0xE9 , 0xE7 , 0xE4 , 0xE2 , 0xDF , 0xDD , 0xDA ,
# 	0x00 , 0xFE , 0xFC , 0xFA , 0xF8 , 0xF6 , 0xF4 , 0xF2 ,
# 	0xF0 , 0xEE , 0xEC , 0xEA , 0xE8 , 0xE6 , 0xE4 , 0xE2 ,
# 	0x00 , 0xFE , 0xFD , 0xFB , 0xFA , 0xF8 , 0xF7 , 0xF5 ,
# 	0xF4 , 0xF2 , 0xF1 , 0xEF , 0xEE , 0xEC , 0xEB , 0xE9 ,
# 	0x00 , 0xFF , 0xFE , 0xFD , 0xFC , 0xFB , 0xFA , 0xF9 ,
# 	0xF8 , 0xF7 , 0xF6 , 0xF5 , 0xF4 , 0xF3 , 0xF2 , 0xF1 ,
# 	0x00 , 0xFF , 0xFF , 0xFE , 0xFE , 0xFD , 0xFD , 0xFC ,
# 	0xFC , 0xFB , 0xFB , 0xFA , 0xFA , 0xF9 , 0xF9 , 0xF8
# ])
mult_table = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x02\x02\x03\x03\x04\x04\x05\x05\x06\x06\x07\x07\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x00\x01\x03\x04\x06\x07\t\n\x0c\r\x0f\x10\x12\x13\x15\x16\x00\x02\x04\x06\x08\n\x0c\x0e\x10\x12\x14\x16\x18\x1a\x1c\x1e\x00\x02\x05\x07\n\x0c\x0f\x11\x14\x16\x19\x1b\x1e #%\x00\x03\x06\t\x0c\x0f\x12\x15\x18\x1b\x1e!$'*-\x00\x03\x07\n\x0e\x11\x15\x18\x1c\x1f#&*-14\x00\xfc\xf8\xf4\xf0\xec\xe8\xe4\xe0\xdc\xd8\xd4\xd0\xcc\xc8\xc4\x00\xfc\xf9\xf5\xf2\xee\xeb\xe7\xe4\xe0\xdd\xd9\xd6\xd2\xcf\xcb\x00\xfd\xfa\xf7\xf4\xf1\xee\xeb\xe8\xe5\xe2\xdf\xdc\xd9\xd6\xd3\x00\xfd\xfb\xf8\xf6\xf3\xf1\xee\xec\xe9\xe7\xe4\xe2\xdf\xdd\xda\x00\xfe\xfc\xfa\xf8\xf6\xf4\xf2\xf0\xee\xec\xea\xe8\xe6\xe4\xe2\x00\xfe\xfd\xfb\xfa\xf8\xf7\xf5\xf4\xf2\xf1\xef\xee\xec\xeb\xe9\x00\xff\xfe\xfd\xfc\xfb\xfa\xf9\xf8\xf7\xf6\xf5\xf4\xf3\xf2\xf1\x00\xff\xff\xfe\xfe\xfd\xfd\xfc\xfc\xfb\xfb\xfa\xfa\xf9\xf9\xf8"

# //random data ?
# sample_table = bytes([
#     # //00
#     0x38 , 0x84 , 0x6B , 0x19 , 0xC6 , 0x63 ,  0x18 , 0x86
#     ,  0x73 , 0x98 , 0xC6 , 0xB1 , 0x1C , 0xCA , 0x31 , 0x8C
#     ,  0xC7 , 0x31 , 0x88 , 0xC2 , 0x30 , 0x98 , 0x46 , 0x31
#     ,  0x18 , 0xC6 , 0x35 ,0xC , 0xCA , 0x31 ,0xC , 0xC6
#     # //20
#     ,  0x21 , 0x10 , 0x24 , 0x69 , 0x12 , 0xC2 , 0x31 , 0x14
#     ,  0xC4 , 0x71 , 8 , 0x4A , 0x22 , 0x49 , 0xAB , 0x6A
#     ,  0xA8 , 0xAC , 0x49 , 0x51 , 0x32 , 0xD5 , 0x52 , 0x88
#     ,  0x93 , 0x6C , 0x94 , 0x22 , 0x15 , 0x54 , 0xD2 , 0x25
#     # //40
#     ,  0x96 , 0xD4 , 0x50 , 0xA5 , 0x46 , 0x21 , 8 , 0x85
#     ,  0x6B , 0x18 , 0xC4 , 0x63 , 0x10 , 0xCE , 0x6B , 0x18
#     ,  0x8C , 0x71 , 0x19 , 0x8C , 0x63 , 0x35 ,0xC , 0xC6
#     ,  0x33 , 0x99 , 0xCC , 0x6C , 0xB5 , 0x4E , 0xA2 , 0x99
#     # //60
#     ,  0x46 , 0x21 , 0x28 , 0x82 , 0x95 , 0x2E , 0xE3 , 0x30
#     ,  0x9C , 0xC5 , 0x30 , 0x9C , 0xA2 , 0xB1 , 0x9C , 0x67
#     ,  0x31 , 0x88 , 0x66 , 0x59 , 0x2C , 0x53 , 0x18 , 0x84
#     ,  0x67 , 0x50 , 0xCA , 0xE3 ,0xA , 0xAC , 0xAB , 0x30
#     # //80
#     ,  0xAC , 0x62 , 0x30 , 0x8C , 0x63 , 0x10 , 0x94 , 0x62
#     ,  0xB1 , 0x8C , 0x82 , 0x28 , 0x96 , 0x33 , 0x98 , 0xD6
#     ,  0xB5 , 0x4C , 0x62 , 0x29 , 0xA5 , 0x4A , 0xB5 , 0x9C
#     ,  0xC6 , 0x31 , 0x14 , 0xD6 , 0x38 , 0x9C , 0x4B , 0xB4
#     # //A0
#     ,  0x86 , 0x65 , 0x18 , 0xAE , 0x67 , 0x1C , 0xA6 , 0x63
#     ,  0x19 , 0x96 , 0x23 , 0x19 , 0x84 , 0x13 , 8 , 0xA6
#     ,  0x52 , 0xAC , 0xCA , 0x22 , 0x89 , 0x6E , 0xAB , 0x19
#     ,  0x8C , 0x62 , 0x34 , 0xC4 , 0x62 , 0x19 , 0x86 , 0x63
#     # //C0
#     ,  0x18 , 0xC4 , 0x23 , 0x58 , 0xD6 , 0xA3 , 0x50 , 0x42
#     ,  0x54 , 0x4A , 0xAD , 0x4A , 0x25 , 0x11 , 0x6B , 0x64
#     ,  0x89 , 0x4A , 0x63 , 0x39 , 0x8A , 0x23 , 0x31 , 0x2A
#     ,  0xEA , 0xA2 , 0xA9 , 0x44 , 0xC5 , 0x12 , 0xCD , 0x42
#     # //E0
#     ,  0x34 , 0x8C , 0x62 , 0x18 , 0x8C , 0x63 , 0x11 , 0x48
#     ,  0x66 , 0x31 , 0x9D , 0x44 , 0x33 , 0x1D , 0x46 , 0x31
#     ,  0x9C , 0xC6 , 0xB1 ,0xC , 0xCD , 0x32 , 0x88 , 0xC4
#     ,  0x73 , 0x18 , 0x86 , 0x73 , 8 , 0xD6 , 0x63 , 0x58
#     # //100
#     ,    7 , 0x81 , 0xE0 , 0xF0 , 0x3C , 7 , 0x87 , 0x90
#     ,  0x3C , 0x7C ,0xF , 0xC7 , 0xC0 , 0xC0 , 0xF0 , 0x7C
#     ,  0x1E , 7 , 0x80 , 0x80 , 0 , 0x1C , 0x78 , 0x70
#     ,  0xF1 , 0xC7 , 0x1F , 0xC0 ,0xC , 0xFE , 0x1C , 0x1F
#     # //120
#     ,  0x1F ,0xE ,0xA , 0x7A , 0xC0 , 0x71 , 0xF2 , 0x83
#     ,  0x8F , 3 ,0xF ,0xF ,0xC , 0 , 0x79 , 0xF8
#     ,  0x61 , 0xE0 , 0x43 ,0xF , 0x83 , 0xE7 , 0x18 , 0xF9
#     ,  0xC1 , 0x13 , 0xDA , 0xE9 , 0x63 , 0x8F ,0xF , 0x83
#     # //140
#     ,  0x83 , 0x87 , 0xC3 , 0x1F , 0x3C , 0x70 , 0xF0 , 0xE1
#     ,  0xE1 , 0xE3 , 0x87 , 0xB8 , 0x71 ,0xE , 0x20 , 0xE3
#     ,  0x8D , 0x48 , 0x78 , 0x1C , 0x93 , 0x87 , 0x30 , 0xE1
#     ,  0xC1 , 0xC1 , 0xE4 , 0x78 , 0x21 , 0x83 , 0x83 , 0xC3
#     # //160
#     ,  0x87 , 6 , 0x39 , 0xE5 , 0xC3 , 0x87 , 7 ,0xE
#     ,  0x1C , 0x1C , 0x70 , 0xF4 , 0x71 , 0x9C , 0x60 , 0x36
#     ,  0x32 , 0xC3 , 0x1E , 0x3C , 0xF3 , 0x8F ,0xE , 0x3C
#     ,  0x70 , 0xE3 , 0xC7 , 0x8F ,0xF ,0xF ,0xE , 0x3C
#     # //180
#     ,  0x78 , 0xF0 , 0xE3 , 0x87 , 6 , 0xF0 , 0xE3 , 7
#     ,  0xC1 , 0x99 , 0x87 ,0xF , 0x18 , 0x78 , 0x70 , 0x70
#     ,  0xFC , 0xF3 , 0x10 , 0xB1 , 0x8C , 0x8C , 0x31 , 0x7C
#     ,  0x70 , 0xE1 , 0x86 , 0x3C , 0x64 , 0x6C , 0xB0 , 0xE1
#     # //1A0
#     ,  0xE3 ,0xF , 0x23 , 0x8F ,0xF , 0x1E , 0x3E , 0x38
#     ,  0x3C , 0x38 , 0x7B , 0x8F , 7 ,0xE , 0x3C , 0xF4
#     ,  0x17 , 0x1E , 0x3C , 0x78 , 0xF2 , 0x9E , 0x72 , 0x49
#     ,  0xE3 , 0x25 , 0x36 , 0x38 , 0x58 , 0x39 , 0xE2 , 0xDE
#     # //1C0
#     ,  0x3C , 0x78 , 0x78 , 0xE1 , 0xC7 , 0x61 , 0xE1 , 0xE1
#     ,  0xB0 , 0xF0 , 0xF0 , 0xC3 , 0xC7 ,0xE , 0x38 , 0xC0
#     ,  0xF0 , 0xCE , 0x73 , 0x73 , 0x18 , 0x34 , 0xB0 , 0xE1
#     ,  0xC7 , 0x8E , 0x1C , 0x3C , 0xF8 , 0x38 , 0xF0 , 0xE1
#     # //1E0
#     ,  0xC1 , 0x8B , 0x86 , 0x8F , 0x1C , 0x78 , 0x70 , 0xF0
#     ,  0x78 , 0xAC , 0xB1 , 0x8F , 0x39 , 0x31 , 0xDB , 0x38
#     ,  0x61 , 0xC3 ,0xE ,0xE , 0x38 , 0x78 , 0x73 , 0x17
#     ,  0x1E , 0x39 , 0x1E , 0x38 , 0x64 , 0xE1 , 0xF1 , 0xC1
#     # //200
#     ,  0x4E ,0xF , 0x40 , 0xA2 , 2 , 0xC5 , 0x8F , 0x81
#     ,  0xA1 , 0xFC , 0x12 , 8 , 0x64 , 0xE0 , 0x3C , 0x22
#     ,  0xE0 , 0x45 , 7 , 0x8E ,0xC , 0x32 , 0x90 , 0xF0
#     ,  0x1F , 0x20 , 0x49 , 0xE0 , 0xF8 ,0xC , 0x60 , 0xF0
#     # //220
#     ,  0x17 , 0x1A , 0x41 , 0xAA , 0xA4 , 0xD0 , 0x8D , 0x12
#     ,  0x82 , 0x1E , 0x1E , 3 , 0xF8 , 0x3E , 3 ,0xC
#     ,  0x73 , 0x80 , 0x70 , 0x44 , 0x26 , 3 , 0x24 , 0xE1
#     ,  0x3E , 4 , 0x4E , 4 , 0x1C , 0xC1 , 9 , 0xCC
#     # //240
#     ,  0x9E , 0x90 , 0x21 , 7 , 0x90 , 0x43 , 0x64 , 0xC0
#     ,   0xF , 0xC6 , 0x90 , 0x9C , 0xC1 , 0x5B , 3 , 0xE2
#     ,  0x1D , 0x81 , 0xE0 , 0x5E , 0x1D , 3 , 0x84 , 0xB8
#     ,  0x2C ,0xF , 0x80 , 0xB1 , 0x83 , 0xE0 , 0x30 , 0x41
#     # //260
#     ,  0x1E , 0x43 , 0x89 , 0x83 , 0x50 , 0xFC , 0x24 , 0x2E
#     ,  0x13 , 0x83 , 0xF1 , 0x7C , 0x4C , 0x2C , 0xC9 ,0xD
#     ,  0x83 , 0xB0 , 0xB5 , 0x82 , 0xE4 , 0xE8 , 6 , 0x9C
#     ,    7 , 0xA0 , 0x99 , 0x1D , 7 , 0x3E , 0x82 , 0x8F
#     # //280
#     ,  0x70 , 0x30 , 0x74 , 0x40 , 0xCA , 0x10 , 0xE4 , 0xE8
#     ,   0xF , 0x92 , 0x14 , 0x3F , 6 , 0xF8 , 0x84 , 0x88
#     ,  0x43 , 0x81 ,0xA , 0x34 , 0x39 , 0x41 , 0xC6 , 0xE3
#     ,  0x1C , 0x47 , 3 , 0xB0 , 0xB8 , 0x13 ,0xA , 0xC2
#     # //2A0
#     ,  0x64 , 0xF8 , 0x18 , 0xF9 , 0x60 , 0xB3 , 0xC0 , 0x65
#     ,  0x20 , 0x60 , 0xA6 , 0x8C , 0xC3 , 0x81 , 0x20 , 0x30
#     ,  0x26 , 0x1E , 0x1C , 0x38 , 0xD3 , 1 , 0xB0 , 0x26
#     ,  0x40 , 0xF4 ,0xB , 0xC3 , 0x42 , 0x1F , 0x85 , 0x32
#     # //2C0
#     ,  0x26 , 0x60 , 0x40 , 0xC9 , 0xCB , 1 , 0xEC , 0x11
#     ,  0x28 , 0x40 , 0xFA , 4 , 0x34 , 0xE0 , 0x70 , 0x4C
#     ,  0x8C , 0x1D , 7 , 0x69 , 3 , 0x16 , 0xC8 , 4
#     ,  0x23 , 0xE8 , 0xC6 , 0x9A ,0xB , 0x1A , 3 , 0xE0
#     # //2E0
#     ,  0x76 , 6 , 5 , 0xCF , 0x1E , 0xBC , 0x58 , 0x31
#     ,  0x71 , 0x66 , 0 , 0xF8 , 0x3F , 4 , 0xFC ,0xC
#     ,  0x74 , 0x27 , 0x8A , 0x80 , 0x71 , 0xC2 , 0x3A , 0x26
#     ,    6 , 0xC0 , 0x1F , 5 ,0xF , 0x98 , 0x40 , 0xAE
#     # //300
#     ,    1 , 0x7F , 0xC0 , 7 , 0xFF , 0 ,0xE , 0xFE
#     ,    0 , 3 , 0xDF , 0x80 , 3 , 0xEF , 0x80 , 0x1B
#     ,  0xF1 , 0xC2 , 0 , 0xE7 , 0xE0 , 0x18 , 0xFC , 0xE0
#     ,  0x21 , 0xFC , 0x80 , 0x3C , 0xFC , 0x40 ,0xE , 0x7E
#     # //320
#     ,    0 , 0x3F , 0x3E , 0 ,0xF , 0xFE , 0 , 0x1F
#     ,  0xFF , 0 , 0x3E , 0xF0 , 7 , 0xFC , 0 , 0x7E
#     ,  0x10 , 0x3F , 0xFF , 0 , 0x3F , 0x38 ,0xE , 0x7C
#     ,    1 , 0x87 ,0xC , 0xFC , 0xC7 , 0 , 0x3E , 4
#     # //340
#     ,   0xF , 0x3E , 0x1F ,0xF ,0xF , 0x1F ,0xF , 2
#     ,  0x83 , 0x87 , 0xCF , 3 , 0x87 ,0xF , 0x3F , 0xC0
#     ,    7 , 0x9E , 0x60 , 0x3F , 0xC0 , 3 , 0xFE , 0
#     ,  0x3F , 0xE0 , 0x77 , 0xE1 , 0xC0 , 0xFE , 0xE0 , 0xC3
#     # //360
#     ,  0xE0 , 1 , 0xDF , 0xF8 , 3 , 7 , 0 , 0x7E
#     ,  0x70 , 0 , 0x7C , 0x38 , 0x18 , 0xFE ,0xC , 0x1E
#     ,  0x78 , 0x1C , 0x7C , 0x3E ,0xE , 0x1F , 0x1E , 0x1E
#     ,  0x3E , 0 , 0x7F , 0x83 , 7 , 0xDB , 0x87 , 0x83
#     # //380
#     ,    7 , 0xC7 , 7 , 0x10 , 0x71 , 0xFF , 0 , 0x3F
#     ,  0xE2 , 1 , 0xE0 , 0xC1 , 0xC3 , 0xE1 , 0 , 0x7F
#     ,  0xC0 , 5 , 0xF0 , 0x20 , 0xF8 , 0xF0 , 0x70 , 0xFE
#     ,  0x78 , 0x79 , 0xF8 , 2 , 0x3F ,0xC , 0x8F , 3
#     # //3a0
#     ,   0xF , 0x9F , 0xE0 , 0xC1 , 0xC7 , 0x87 , 3 , 0xC3
#     ,  0xC3 , 0xB0 , 0xE1 , 0xE1 , 0xC1 , 0xE3 , 0xE0 , 0x71
#     ,  0xF0 , 0 , 0xFC , 0x70 , 0x7C ,0xC , 0x3E , 0x38
#     ,   0xE , 0x1C , 0x70 , 0xC3 , 0xC7 , 3 , 0x81 , 0xC1
#     # //3c0
#     ,  0xC7 , 0xE7 , 0 ,0xF , 0xC7 , 0x87 , 0x19 , 9
#     ,  0xEF , 0xC4 , 0x33 , 0xE0 , 0xC1 , 0xFC , 0xF8 , 0x70
#     ,  0xF0 , 0x78 , 0xF8 , 0xF0 , 0x61 , 0xC7 , 0 , 0x1F
#     ,  0xF8 , 1 , 0x7C , 0xF8 , 0xF0 , 0x78 , 0x70 , 0x3C
#     # //3e0
#     ,  0x7C , 0xCE ,0xE , 0x21 , 0x83 , 0xCF , 8 , 7
#     ,  0x8F , 8 , 0xC1 , 0x87 , 0x8F , 0x80 , 0xC7 , 0xE3
#     ,    0 , 7 , 0xF8 , 0xE0 , 0xEF , 0 , 0x39 , 0xF7
#     ,  0x80 ,0xE , 0xF8 , 0xE1 , 0xE3 , 0xF8 , 0x21 , 0x9F
#     # //400
#     ,  0xC0 , 0xFF , 3 , 0xF8 , 7 , 0xC0 , 0x1F , 0xF8
#     ,  0xC4 , 4 , 0xFC , 0xC4 , 0xC1 , 0xBC , 0x87 , 0xF0
#     ,   0xF , 0xC0 , 0x7F , 5 , 0xE0 , 0x25 , 0xEC , 0xC0
#     ,  0x3E , 0x84 , 0x47 , 0xF0 , 0x8E , 3 , 0xF8 , 3
#     # //420
#     ,  0xFB , 0xC0 , 0x19 , 0xF8 , 7 , 0x9C ,0xC , 0x17
#     ,  0xF8 , 7 , 0xE0 , 0x1F , 0xA1 , 0xFC ,0xF , 0xFC
#     ,    1 , 0xF0 , 0x3F , 0 , 0xFE , 3 , 0xF0 , 0x1F
#     ,    0 , 0xFD , 0 , 0xFF , 0x88 ,0xD , 0xF9 , 1
#     # //440
#     ,  0xFF , 0 , 0x70 , 7 , 0xC0 , 0x3E , 0x42 , 0xF3
#     ,   0xD , 0xC4 , 0x7F , 0x80 , 0xFC , 7 , 0xF0 , 0x5E
#     ,  0xC0 , 0x3F , 0 , 0x78 , 0x3F , 0x81 , 0xFF , 1
#     ,  0xF8 , 1 , 0xC3 , 0xE8 ,0xC , 0xE4 , 0x64 , 0x8F
#     # //460
#     ,  0xE4 ,0xF , 0xF0 , 7 , 0xF0 , 0xC2 , 0x1F , 0
#     ,  0x7F , 0xC0 , 0x6F , 0x80 , 0x7E , 3 , 0xF8 , 7
#     ,  0xF0 , 0x3F , 0xC0 , 0x78 ,0xF , 0x82 , 7 , 0xFE
#     ,  0x22 , 0x77 , 0x70 , 2 , 0x76 , 3 , 0xFE , 0
#     # //480
#     ,  0xFE , 0x67 , 0 , 0x7C , 0xC7 , 0xF1 , 0x8E , 0xC6
#     ,  0x3B , 0xE0 , 0x3F , 0x84 , 0xF3 , 0x19 , 0xD8 , 3
#     ,  0x99 , 0xFC , 9 , 0xB8 ,0xF , 0xF8 , 0 , 0x9D
#     ,  0x24 , 0x61 , 0xF9 ,0xD , 0 , 0xFD , 3 , 0xF0
#     # //4a0
#     ,  0x1F , 0x90 , 0x3F , 1 , 0xF8 , 0x1F , 0xD0 ,0xF
#     ,  0xF8 , 0x37 , 1 , 0xF8 , 7 , 0xF0 ,0xF , 0xC0
#     ,  0x3F , 0 , 0xFE , 3 , 0xF8 ,0xF , 0xC0 , 0x3F
#     ,    0 , 0xFA , 3 , 0xF0 ,0xF , 0x80 , 0xFF , 1
#     # //4c0
#     ,  0xB8 , 7 , 0xF0 , 1 , 0xFC , 1 , 0xBC , 0x80
#     ,  0x13 , 0x1E , 0 , 0x7F , 0xE1 , 0x40 , 0x7F , 0xA0
#     ,  0x7F , 0xB0 , 0 , 0x3F , 0xC0 , 0x1F , 0xC0 , 0x38
#     ,   0xF , 0xF0 , 0x1F , 0x80 , 0xFF , 1 , 0xFC , 3
#     # //4e0
#     ,  0xF1 , 0x7E , 1 , 0xFE , 1 , 0xF0 , 0xFF , 0
#     ,  0x7F , 0xC0 , 0x1D , 7 , 0xF0 ,0xF , 0xC0 , 0x7E
#     ,    6 , 0xE0 , 7 , 0xE0 ,0xF , 0xF8 , 6 , 0xC1
#     ,  0xFE , 1 , 0xFC , 3 , 0xE0 ,0xF , 0 , 0xFC
# ])
sample_table = b'8\x84k\x19\xc6c\x18\x86s\x98\xc6\xb1\x1c\xca1\x8c\xc71\x88\xc20\x98F1\x18\xc65\x0c\xca1\x0c\xc6!\x10$i\x12\xc21\x14\xc4q\x08J"I\xabj\xa8\xacIQ2\xd5R\x88\x93l\x94"\x15T\xd2%\x96\xd4P\xa5F!\x08\x85k\x18\xc4c\x10\xcek\x18\x8cq\x19\x8cc5\x0c\xc63\x99\xccl\xb5N\xa2\x99F!(\x82\x95.\xe30\x9c\xc50\x9c\xa2\xb1\x9cg1\x88fY,S\x18\x84gP\xca\xe3\n\xac\xab0\xacb0\x8cc\x10\x94b\xb1\x8c\x82(\x963\x98\xd6\xb5Lb)\xa5J\xb5\x9c\xc61\x14\xd68\x9cK\xb4\x86e\x18\xaeg\x1c\xa6c\x19\x96#\x19\x84\x13\x08\xa6R\xac\xca"\x89n\xab\x19\x8cb4\xc4b\x19\x86c\x18\xc4#X\xd6\xa3PBTJ\xadJ%\x11kd\x89Jc9\x8a#1*\xea\xa2\xa9D\xc5\x12\xcdB4\x8cb\x18\x8cc\x11Hf1\x9dD3\x1dF1\x9c\xc6\xb1\x0c\xcd2\x88\xc4s\x18\x86s\x08\xd6cX\x07\x81\xe0\xf0<\x07\x87\x90<|\x0f\xc7\xc0\xc0\xf0|\x1e\x07\x80\x80\x00\x1cxp\xf1\xc7\x1f\xc0\x0c\xfe\x1c\x1f\x1f\x0e\nz\xc0q\xf2\x83\x8f\x03\x0f\x0f\x0c\x00y\xf8a\xe0C\x0f\x83\xe7\x18\xf9\xc1\x13\xda\xe9c\x8f\x0f\x83\x83\x87\xc3\x1f<p\xf0\xe1\xe1\xe3\x87\xb8q\x0e \xe3\x8dHx\x1c\x93\x870\xe1\xc1\xc1\xe4x!\x83\x83\xc3\x87\x069\xe5\xc3\x87\x07\x0e\x1c\x1cp\xf4q\x9c`62\xc3\x1e<\xf3\x8f\x0e<p\xe3\xc7\x8f\x0f\x0f\x0e<x\xf0\xe3\x87\x06\xf0\xe3\x07\xc1\x99\x87\x0f\x18xpp\xfc\xf3\x10\xb1\x8c\x8c1|p\xe1\x86<dl\xb0\xe1\xe3\x0f#\x8f\x0f\x1e>8<8{\x8f\x07\x0e<\xf4\x17\x1e<x\xf2\x9erI\xe3%68X9\xe2\xde<xx\xe1\xc7a\xe1\xe1\xb0\xf0\xf0\xc3\xc7\x0e8\xc0\xf0\xcess\x184\xb0\xe1\xc7\x8e\x1c<\xf88\xf0\xe1\xc1\x8b\x86\x8f\x1cxp\xf0x\xac\xb1\x8f91\xdb8a\xc3\x0e\x0e8xs\x17\x1e9\x1e8d\xe1\xf1\xc1N\x0f@\xa2\x02\xc5\x8f\x81\xa1\xfc\x12\x08d\xe0<"\xe0E\x07\x8e\x0c2\x90\xf0\x1f I\xe0\xf8\x0c`\xf0\x17\x1aA\xaa\xa4\xd0\x8d\x12\x82\x1e\x1e\x03\xf8>\x03\x0cs\x80pD&\x03$\xe1>\x04N\x04\x1c\xc1\t\xcc\x9e\x90!\x07\x90Cd\xc0\x0f\xc6\x90\x9c\xc1[\x03\xe2\x1d\x81\xe0^\x1d\x03\x84\xb8,\x0f\x80\xb1\x83\xe00A\x1eC\x89\x83P\xfc$.\x13\x83\xf1|L,\xc9\r\x83\xb0\xb5\x82\xe4\xe8\x06\x9c\x07\xa0\x99\x1d\x07>\x82\x8fp0t@\xca\x10\xe4\xe8\x0f\x92\x14?\x06\xf8\x84\x88C\x81\n49A\xc6\xe3\x1cG\x03\xb0\xb8\x13\n\xc2d\xf8\x18\xf9`\xb3\xc0e `\xa6\x8c\xc3\x81 0&\x1e\x1c8\xd3\x01\xb0&@\xf4\x0b\xc3B\x1f\x852&`@\xc9\xcb\x01\xec\x11(@\xfa\x044\xe0pL\x8c\x1d\x07i\x03\x16\xc8\x04#\xe8\xc6\x9a\x0b\x1a\x03\xe0v\x06\x05\xcf\x1e\xbcX1qf\x00\xf8?\x04\xfc\x0ct\'\x8a\x80q\xc2:&\x06\xc0\x1f\x05\x0f\x98@\xae\x01\x7f\xc0\x07\xff\x00\x0e\xfe\x00\x03\xdf\x80\x03\xef\x80\x1b\xf1\xc2\x00\xe7\xe0\x18\xfc\xe0!\xfc\x80<\xfc@\x0e~\x00?>\x00\x0f\xfe\x00\x1f\xff\x00>\xf0\x07\xfc\x00~\x10?\xff\x00?8\x0e|\x01\x87\x0c\xfc\xc7\x00>\x04\x0f>\x1f\x0f\x0f\x1f\x0f\x02\x83\x87\xcf\x03\x87\x0f?\xc0\x07\x9e`?\xc0\x03\xfe\x00?\xe0w\xe1\xc0\xfe\xe0\xc3\xe0\x01\xdf\xf8\x03\x07\x00~p\x00|8\x18\xfe\x0c\x1ex\x1c|>\x0e\x1f\x1e\x1e>\x00\x7f\x83\x07\xdb\x87\x83\x07\xc7\x07\x10q\xff\x00?\xe2\x01\xe0\xc1\xc3\xe1\x00\x7f\xc0\x05\xf0 \xf8\xf0p\xfexy\xf8\x02?\x0c\x8f\x03\x0f\x9f\xe0\xc1\xc7\x87\x03\xc3\xc3\xb0\xe1\xe1\xc1\xe3\xe0q\xf0\x00\xfcp|\x0c>8\x0e\x1cp\xc3\xc7\x03\x81\xc1\xc7\xe7\x00\x0f\xc7\x87\x19\t\xef\xc43\xe0\xc1\xfc\xf8p\xf0x\xf8\xf0a\xc7\x00\x1f\xf8\x01|\xf8\xf0xp<|\xce\x0e!\x83\xcf\x08\x07\x8f\x08\xc1\x87\x8f\x80\xc7\xe3\x00\x07\xf8\xe0\xef\x009\xf7\x80\x0e\xf8\xe1\xe3\xf8!\x9f\xc0\xff\x03\xf8\x07\xc0\x1f\xf8\xc4\x04\xfc\xc4\xc1\xbc\x87\xf0\x0f\xc0\x7f\x05\xe0%\xec\xc0>\x84G\xf0\x8e\x03\xf8\x03\xfb\xc0\x19\xf8\x07\x9c\x0c\x17\xf8\x07\xe0\x1f\xa1\xfc\x0f\xfc\x01\xf0?\x00\xfe\x03\xf0\x1f\x00\xfd\x00\xff\x88\r\xf9\x01\xff\x00p\x07\xc0>B\xf3\r\xc4\x7f\x80\xfc\x07\xf0^\xc0?\x00x?\x81\xff\x01\xf8\x01\xc3\xe8\x0c\xe4d\x8f\xe4\x0f\xf0\x07\xf0\xc2\x1f\x00\x7f\xc0o\x80~\x03\xf8\x07\xf0?\xc0x\x0f\x82\x07\xfe"wp\x02v\x03\xfe\x00\xfeg\x00|\xc7\xf1\x8e\xc6;\xe0?\x84\xf3\x19\xd8\x03\x99\xfc\t\xb8\x0f\xf8\x00\x9d$a\xf9\r\x00\xfd\x03\xf0\x1f\x90?\x01\xf8\x1f\xd0\x0f\xf87\x01\xf8\x07\xf0\x0f\xc0?\x00\xfe\x03\xf8\x0f\xc0?\x00\xfa\x03\xf0\x0f\x80\xff\x01\xb8\x07\xf0\x01\xfc\x01\xbc\x80\x13\x1e\x00\x7f\xe1@\x7f\xa0\x7f\xb0\x00?\xc0\x1f\xc08\x0f\xf0\x1f\x80\xff\x01\xfc\x03\xf1~\x01\xfe\x01\xf0\xff\x00\x7f\xc0\x1d\x07\xf0\x0f\xc0~\x06\xe0\x07\xe0\x0f\xf8\x06\xc1\xfe\x01\xfc\x03\xe0\x0f\x00\xfc'

# time_table = [
#     [162, 167, 167, 127, 128],
#     [226, 60, 60, 0, 0],
#     [225, 60, 59, 0, 0],
#     [200, 0, 0, 54, 55],
#     [199, 0, 0, 54, 54]
# ]
time_table = [
    b"\xa2\xa7\xa7\x7f\x80",
    b"\xe2<<\x00\x00",
    b"\xe1<;\x00\x00",
    b"\xc8\x00\x0067",
    b"\xc7\x00\x0066",
]

# // mouth formants (F1) 5..29
# mouth_formants_5_29 = bytes([
#     0, 0, 0, 0, 0, 10,
#     14, 19, 24, 27, 23, 21, 16, 20, 14, 18, 14, 18, 18,
#     16, 13, 15, 11, 18, 14, 11, 9, 6, 6, 6
# ])
mouth_formants_5_29 = b"\x00\x00\x00\x00\x00\n\x0e\x13\x18\x1b\x17\x15\x10\x14\x0e\x12\x0e\x12\x12\x10\r\x0f\x0b\x12\x0e\x0b\t\x06\x06\x06"

# // throat formants (F2) 5..29
# throat_formants_5_29 = bytes([
#     255, 255,
#     255, 255, 255, 84, 73, 67, 63, 40, 44, 31, 37, 45, 73, 49,
#     36, 30, 51, 37, 29, 69, 24, 50, 30, 24, 83, 46, 54, 86
# ])
throat_formants_5_29 = (
    b"\xff\xff\xff\xff\xffTIC?(,\x1f%-I1$\x1e3%\x1dE\x182\x1e\x18S.6V"
)

# // there must be no zeros in this 2 tables
# // formant 1 frequencies (mouth) 48..53
# mouth_formants_48_53 = bytes([
#     19, 27, 21, 27, 18, 13
# ])
mouth_formants_48_53 = b"\x13\x1b\x15\x1b\x12\r"

# // formant 2 frequencies (throat) 48..53
# throat_formants_48_53 = bytes([
#     72, 39, 31, 43, 30, 34
# ])
throat_formants_48_53 = b"H'\x1f+\x1e\""


class Renderer:
    """Renderer takes the phoneme parameters and renders sound waveform.

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
        self.speed = speed
        self.pitch = pitch
        self.mouth = mouth
        self.throat = throat
        self.sing_mode = sing_mode

        self.buffer_size = buffer_size
        self.debug = debug

        self.freq1data = bytearray(
            [
                0x00, 0x13, 0x13, 0x13, 0x13, 0x0a, 0x0e, 0x12,
                0x18, 0x1a, 0x16, 0x14, 0x10, 0x14, 0x0e, 0x12,
                0x0e, 0x12, 0x12, 0x10, 0x0c, 0x0e, 0x0a, 0x12,
                0x0e, 0x0a, 0x08, 0x06, 0x06, 0x06, 0x06, 0x11,
                0x06, 0x06, 0x06, 0x06, 0x0e, 0x10, 0x09, 0x0a,
                0x08, 0x0a, 0x06, 0x06, 0x06, 0x05, 0x06, 0x00,
                0x12, 0x1a, 0x14, 0x1a, 0x12, 0x0c, 0x06, 0x06,
                0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
                0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
                0x06, 0x0a, 0x0a, 0x06, 0x06, 0x06, 0x2c, 0x13,
            ]
        )

        self.freq2data = bytearray(
            [
                0x00, 0x43, 0x43, 0x43, 0x43, 0x54, 0x48, 0x42,
                0x3e, 0x28, 0x2c, 0x1e, 0x24, 0x2c, 0x48, 0x30,
                0x24, 0x1e, 0x32, 0x24, 0x1c, 0x44, 0x18, 0x32,
                0x1e, 0x18, 0x52, 0x2e, 0x36, 0x56, 0x36, 0x43,
                0x49, 0x4f, 0x1a, 0x42, 0x49, 0x25, 0x33, 0x42,
                0x28, 0x2f, 0x4f, 0x4f, 0x42, 0x4f, 0x6e, 0x00,
                0x48, 0x26, 0x1e, 0x2a, 0x1e, 0x22, 0x1a, 0x1a,
                0x1a, 0x42, 0x42, 0x42, 0x6e, 0x6e, 0x6e, 0x54,
                0x54, 0x54, 0x1a, 0x1a, 0x1a, 0x42, 0x42, 0x42,
                0x6d, 0x56, 0x6d, 0x54, 0x54, 0x54, 0x7f, 0x7f,
            ]
        )

        self.phoneme_index_output = bytearray(60)
        self.stress_output = bytearray(60)
        self.phoneme_length_output = bytearray(60)

        self.pitches = bytearray(256)

        self.frequency1 = bytearray(256)
        self.frequency2 = bytearray(256)
        self.frequency3 = bytearray(256)

        self.amplitude1 = bytearray(256)
        self.amplitude2 = bytearray(256)
        self.amplitude3 = bytearray(256)

        self.sampled_consonant_flag = bytearray(256)

        self.old_time_table_index = 0

        self.buffer_pos = 0
        self.buffer = bytearray(self.buffer_size)
        self.buffer_end = 0

        self.config()

    def _print_output(self, flag, f1, f2, f3, a1, a2, a3, p):
        print("===========================================")
        print("Final data for speech output:\n")
        print(" flags ampl1 freq1 ampl2 freq2 ampl3 freq3 pitch")
        print("------------------------------------------------")
        i = 0
        while i < 255:
            print(
                f"{flag[i]:5} {a1[i]:5} {f1[i]:5} {a2[i]:5} {f2[i]:5} {a3[i]:5} {f3[i]:5} {p[i]:5}"
            )
            i += 1
        print("===========================================")

    # // Create a rising or falling inflection 30 frames prior to
    # // index X. A rising inflection is used for questions, and
    # // a falling inflection is used for statements.
    def _add_inflection(self, inflection, pos):
        # // store the location of the punctuation
        end = pos

        if pos < 30:
            pos = 0
        else:
            pos -= 30

        # // FIXME: Explain this fix better, it's not obvious
        # // ML : A =, fixes a problem with invalid pitch with '.'
        a = self.pitches[pos]
        while a == 127:
            pos = (pos + 1) & 0xFF
            a = self.pitches[pos]

        while pos != end:
            # // add the inflection direction
            a = (a + inflection) & 0xFF

            # // set the inflection
            self.pitches[pos] = a

            pos = (pos + 1) & 0xFF
            while (pos != end) and (self.pitches[pos] == 255):
                pos = (pos + 1) & 0xFF

    # // ASSIGN PITCH CONTOUR
    # //
    # // This subtracts the F1 frequency from the pitch to create a
    # // pitch contour. Without this, the output would be at a single
    # // pitch level (monotone).
    def _assign_pitch_contour(self):
        for i in range(256):
            # // subtract half the frequency of the formant 1.
            # // this adds variety to the voice
            self.pitches[i] = (self.pitches[i] - (self.frequency1[i] >> 1)) & 0xFF

    # // RESCALE AMPLITUDE
    # //
    # // Rescale volume from a linear scale to decibels.
    # //
    def _rescale_amplitude(self):
        for i in range(255, -1, -1):
            self.amplitude1[i] = amplitude_rescale[self.amplitude1[i]]
            self.amplitude2[i] = amplitude_rescale[self.amplitude2[i]]
            self.amplitude3[i] = amplitude_rescale[self.amplitude3[i]]

    # // CREATE FRAMES
    # //
    # // The length parameter in the list corresponds to the number of frames
    # // to expand the phoneme to. Each frame represents 10 milliseconds of time.
    # // So a phoneme with a length of 7 = 7 frames = 70 milliseconds duration.
    # //
    # // The parameters are copied from the phoneme to the frame verbatim.
    # //
    def _create_frames(self):
        x = 0
        for i in range(256):
            # // get the phoneme at the index
            phoneme = self.phoneme_index_output[i]

            # // if terminal phoneme, exit the loop
            if phoneme == 255:
                break

            if phoneme == PHONEME_PERIOD:
                self._add_inflection(RISING_INFLECTION, x)
            elif phoneme == PHONEME_QUESTION:
                self._add_inflection(FALLING_INFLECTION, x)

            # // get the stress amount (more stress = higher pitch)
            temp_stress = self.stress_output[i] + 1
            temp_stress = (
                len(tab47492) - 1 if temp_stress >= len(tab47492) else temp_stress
            )
            phase1 = tab47492[temp_stress]

            # // get number of frames to write
            phase2 = self.phoneme_length_output[i]

            # // copy from the source to the frames list
            # do-while loop
            flag_loop_init = True
            while (phase2 != 0) or flag_loop_init:
                flag_loop_init = False

                self.frequency1[x] = self.freq1data[phoneme]  # // F1 frequency
                self.frequency2[x] = self.freq2data[phoneme]  # // F2 frequency
                self.frequency3[x] = freq3data[phoneme]  # // F3 frequency
                self.amplitude1[x] = ampl1data[phoneme]  # // F1 amplitude
                self.amplitude2[x] = ampl2data[phoneme]  # // F2 amplitude
                self.amplitude3[x] = ampl3data[phoneme]  # // F3 amplitude
                self.sampled_consonant_flag[x] = sampled_consonant_flags[
                    phoneme
                ]  # // phoneme data for sampled consonants
                self.pitches[x] = (self.pitch + phase1) & 0xFF  # // pitch
                x += 1
                phase2 -= 1

    def _output(self, index, a):
        self.buffer_pos += time_table[self.old_time_table_index][index]
        self.old_time_table_index = index

        # // write a little bit in advance
        self.buffer_end = self.buffer_pos // 50
        for k in range(5):
            self.buffer[self.buffer_end + k] = (a & 15) * 16

    def _render_voiced_sample(self, hi, off, phase1):
        # do-while loop
        flag_loop_init_1 = True
        while (phase1 != 0) or flag_loop_init_1:
            flag_loop_init_1 = False

            bit = 8
            sample = sample_table[hi + off]

            # do-while loop
            flag_loop_init_2 = True
            while (bit != 0) or flag_loop_init_2:
                flag_loop_init_2 = False

                if (sample & 128) != 0:
                    self._output(3, 26)
                else:
                    self._output(4, 6)

                sample = (sample << 1) & 0xFF
                bit = (bit - 1) & 0xFF

            off = (off + 1) & 0xFF
            phase1 = (phase1 + 1) & 0xFF

        return off

    def _render_unvoiced_sample(self, hi, off, m):
        # do-while loop
        flag_loop_init_1 = True
        while (off != 0) or flag_loop_init_1:
            flag_loop_init_1 = False

            bit = 8
            sample = sample_table[hi + off]

            # do-while loop
            flag_loop_init_2 = True
            while (bit != 0) or flag_loop_init_2:
                flag_loop_init_2 = False

                if (sample & 128) != 0:
                    self._output(2, 5)
                else:
                    self._output(1, m)

                sample = (sample << 1) & 0xFF
                bit = (bit - 1) & 0xFF

            off = (off + 1) & 0xFF

    # // -------------------------------------------------------------------------
    # //Code48227
    # // Render a sampled sound from the sampleTable.
    # //
    # //   Phoneme   Sample Start   Sample End
    # //   32: S*    15             255
    # //   33: SH    257            511
    # //   34: F*    559            767
    # //   35: TH    583            767
    # //   36: /H    903            1023
    # //   37: /X    1135           1279
    # //   38: Z*    84             119
    # //   39: ZH    340            375
    # //   40: V*    596            639
    # //   41: DH    596            631
    # //
    # //   42: CH
    # //   43: **    399            511
    # //
    # //   44: J*
    # //   45: **    257            276
    # //   46: **
    # //
    # //   66: P*
    # //   67: **    743            767
    # //   68: **
    # //
    # //   69: T*
    # //   70: **    231            255
    # //   71: **
    # //
    # // The SampledPhonemesTable[] holds flags indicating if a phoneme is
    # // voiced or not. If the upper 5 bits are zero, the sample is voiced.
    # //
    # // Samples in the sampleTable are compressed, with bits being converted to
    # // bytes from high bit to low, as follows:
    # //
    # //   unvoiced 0 bit   -> X
    # //   unvoiced 1 bit   -> 5
    # //
    # //   voiced 0 bit     -> 6
    # //   voiced 1 bit     -> 24
    # //
    # // Where X is a value from the table:
    # //
    # //   { 0x18, 0x1A, 0x17, 0x17, 0x17 };
    # //
    # // The index into this table is determined by masking off the lower
    # // 3 bits from the SampledPhonemesTable:
    # //
    # //        index = (SampledPhonemesTable[i] & 7) - 1;
    # //
    # // For voices samples, samples are interleaved between voiced output.
    def _render_sample(self, m: bytearray, consonant_flag, n):
        # // mem49 == current phoneme's index

        # // mask low three bits and subtract 1 get value to
        # // convert 0 bits on unvoiced samples.
        hibyte = ((consonant_flag & 7) - 1) & 0xFF

        # // determine which offset to use from table { 0x18, 0x1A, 0x17, 0x17, 0x17 }
        # // T, S, Z                0          0x18
        # // CH, J, SH, ZH          1          0x1A
        # // P, F*, V, TH, DH       2          0x17
        # // /H                     3          0x17
        # // /X                     4          0x17

        hi = hibyte * 256
        # // voiced sample?
        pitchl = consonant_flag & 248
        if pitchl == 0:
            # // voiced phoneme: Z*, ZH, V*, DH
            pitchl = self.pitches[n] >> 4
            m[0] = self._render_voiced_sample(hi, m[0], pitchl ^ 255)
        else:
            self._render_unvoiced_sample(hi, pitchl ^ 255, tab48426[hibyte])

    def _combine_glottal_and_formants(self, phase1, phase2, phase3, y):
        tmp = mult_table[sinus[phase1] | self.amplitude1[y]]
        tmp += mult_table[sinus[phase2] | self.amplitude2[y]]
        tmp += (
            1 if tmp > 255 else 0
        )  # // if addition above overflows, we for some reason add one;
        tmp += mult_table[rectangle[phase3] | self.amplitude3[y]]
        tmp += 136
        tmp >>= 4  # // Scale down to 0..15 range of C64 audio.

        self._output(0, tmp & 0xF)

    # // PROCESS THE FRAMES
    # //
    # // In traditional vocal synthesis, the glottal pulse drives filters, which
    # // are attenuated to the frequencies of the formants.
    # //
    # // SAM generates these formants directly with sin and rectangular waves.
    # // To simulate them being driven by the glottal pulse, the waveforms are
    # // reset at the beginning of each glottal pulse.
    # //
    def _process_frames(self, k):
        speedcounter = 72
        phase1 = 0
        phase2 = 0
        phase3 = 0
        m = bytearray(1)

        y = 0

        glottal_pulse = self.pitches[0]
        n = glottal_pulse - (glottal_pulse >> 2)  # // glottal_pulse * 0.75

        while k:
            flags = self.sampled_consonant_flag[y]

            # // unvoiced sampled phoneme?
            if flags & 248:
                self._render_sample(m, flags, y)
                # // skip ahead two in the phoneme buffer
                y = (y + 2) & 0xFF
                k = (k - 2) & 0xFF
                speedcounter = self.speed
            else:
                self._combine_glottal_and_formants(phase1, phase2, phase3, y)

                speedcounter = (speedcounter - 1) & 0xFF
                if speedcounter == 0:
                    y = (y + 1) & 0xFF  # //go to next amplitude
                    # // decrement the frame count
                    k = (k - 1) & 0xFF
                    if k == 0:
                        return

                    speedcounter = self.speed

                glottal_pulse = (glottal_pulse - 1) & 0xFF

                if glottal_pulse != 0:
                    # // not finished with a glottal pulse

                    n = (n - 1) & 0xFF
                    # // within the first 75% of the glottal pulse?
                    # // is the count non-zero and the sampled flag is zero?
                    if (n != 0) or (flags == 0):
                        # // reset the phase of the formants to match the pulse
                        phase1 = (phase1 + self.frequency1[y]) & 0xFF
                        phase2 = (phase2 + self.frequency2[y]) & 0xFF
                        phase3 = (phase3 + self.frequency3[y]) & 0xFF
                        continue

                    # // voiced sampled phonemes interleave the sample with the
                    # // glottal pulse. The sample flag is non-zero, so render
                    # // the sample for the phoneme.
                    self._render_sample(m, flags, y)

            glottal_pulse = self.pitches[y]
            n = glottal_pulse - (glottal_pulse >> 2)  # // mem44 * 0.75

            # // reset the formant wave generators to keep them in
            # // sync with the glottal pulse
            phase1 = 0
            phase2 = 0
            phase3 = 0

    # //written by me because of different table positions.
    # // mem[47] = ...
    # // 168=pitches
    # // 169=frequency1
    # // 170=frequency2
    # // 171=frequency3
    # // 172=amplitude1
    # // 173=amplitude2
    # // 174=amplitude3
    def _read(self, p, y):
        if p == 168:
            return self.pitches[y]
        elif p == 169:
            return self.frequency1[y]
        elif p == 170:
            return self.frequency2[y]
        elif p == 171:
            return self.frequency3[y]
        elif p == 172:
            return self.amplitude1[y]
        elif p == 173:
            return self.amplitude2[y]
        elif p == 174:
            return self.amplitude3[y]

        print("Error reading to tables")
        return 0

    def _write(self, p, y, value):
        if p == 168:
            self.pitches[y] = value
        elif p == 169:
            self.frequency1[y] = value
        elif p == 170:
            self.frequency2[y] = value
        elif p == 171:
            self.frequency3[y] = value
        elif p == 172:
            self.amplitude1[y] = value
        elif p == 173:
            self.amplitude2[y] = value
        elif p == 174:
            self.amplitude3[y] = value
        else:
            print("Error writing to tables")

    # // linearly interpolate values
    def _interpolate(self, width, table, frame, m):
        sign = m < 0
        remainder = abs(m) % width
        # Note: there is difference between C and Python on `a // b` when the result is negative
        # Need workaround `int(a/b) & 0xFF`
        div = int(m / width) & 0xFF

        error = 0
        pos = width
        val = (self._read(table, frame) + div) & 0xFF

        pos = (pos - 1) & 0xFF
        while pos:
            error = (error + remainder) & 0xFF
            if error >= width:
                # // accumulated a whole integer error, so adjust output
                error = (error - width) & 0xFF
                if sign:
                    val = (val - 1) & 0xFF
                elif val:
                    val = (val + 1) & 0xFF  # // if input is 0, we always leave it alone

            frame = (frame + 1) & 0xFF
            self._write(table, frame, val)  # // Write updated value back to next frame.
            val = (val + div) & 0xFF

            pos = (pos - 1) & 0xFF

    def _interpolate_pitch(self, pos, m, phase3):
        # // unlike the other values, the pitches[] interpolates from
        # // the middle of the current phoneme to the middle of the
        # // next phoneme

        # // half the width of the current and next phoneme
        cur_width = self.phoneme_length_output[pos] // 2
        next_width = self.phoneme_length_output[pos + 1] // 2
        # // sum the values
        width = (cur_width + next_width) & 0xFF
        pitch = self.pitches[next_width + m] - self.pitches[m - cur_width]
        self._interpolate(width, 168, phase3, pitch)

    # // CREATE TRANSITIONS
    # //
    # // Linear transitions are now created to smoothly connect the
    # // end of one sustained portion of a phoneme to the following
    # // phoneme.
    # //
    # // To do this, three tables are used:
    # //
    # //  Table         Purpose
    # //  =========     ==================================================
    # //  blendRank     Determines which phoneme's blend values are used.
    # //
    # //  blendOut      The number of frames at the end of the phoneme that
    # //                will be used to transition to the following phoneme.
    # //
    # //  blendIn       The number of frames of the following phoneme that
    # //                will be used to transition into that phoneme.
    # //
    # // In creating a transition between two phonemes, the phoneme
    # // with the HIGHEST rank is used. Phonemes are ranked on how much
    # // their identity is based on their transitions. For example,
    # // vowels are and diphthongs are identified by their sustained portion,
    # // rather than the transitions, so they are given low values. In contrast,
    # // stop consonants (P, B, T, K) and glides (Y, L) are almost entirely
    # // defined by their transitions, and are given high rank values.
    # //
    # // Here are the rankings used by SAM:
    # //
    # //     Rank    Type                         Phonemes
    # //     2       All vowels                   IY, IH, etc.
    # //     5       Diphthong endings            YX, WX, ER
    # //     8       Terminal liquid consonants   LX, WX, YX, N, NX
    # //     9       Liquid consonants            L, RX, W
    # //     10      Glide                        R, OH
    # //     11      Glide                        WH
    # //     18      Voiceless fricatives         S, SH, F, TH
    # //     20      Voiced fricatives            Z, ZH, V, DH
    # //     23      Plosives, stop consonants    P, T, K, KX, DX, CH
    # //     26      Stop consonants              J, GX, B, D, G
    # //     27-29   Stop consonants (internal)   **
    # //     30      Unvoiced consonants          /H, /X and Q*
    # //     160     Nasal                        M
    # //
    # // To determine how many frames to use, the two phonemes are
    # // compared using the blendRank[] table. The phoneme with the
    # // higher rank is selected. In case of a tie, a blend of each is used:
    # //
    # //      if blendRank[phoneme1] ==  blendRank[phomneme2]
    # //          // use lengths from each phoneme
    # //          outBlendFrames = outBlend[phoneme1]
    # //          inBlendFrames = outBlend[phoneme2]
    # //      else if blendRank[phoneme1] > blendRank[phoneme2]
    # //          // use lengths from first phoneme
    # //          outBlendFrames = outBlendLength[phoneme1]
    # //          inBlendFrames = inBlendLength[phoneme1]
    # //      else
    # //          // use lengths from the second phoneme
    # //          // note that in and out are SWAPPED!
    # //          outBlendFrames = inBlendLength[phoneme2]
    # //          inBlendFrames = outBlendLength[phoneme2]
    # //
    # // Blend lengths can't be less than zero.
    # //
    # // Transitions are assumed to be symetrical, so if the transition
    # // values for the second phoneme are used, the inBlendLength and
    # // outBlendLength values are SWAPPED.
    # //
    # // For most of the parameters, SAM interpolates over the range of the last
    # // outBlendFrames-1 and the first inBlendFrames.
    # //
    # // The exception to this is the Pitch[] parameter, which is interpolates the
    # // pitch from the CENTER of the current phoneme to the CENTER of the next
    # // phoneme.
    # //
    # // Here are two examples. First, For example, consider the word "SUN" (S AH N)
    # //
    # //    Phoneme   Duration    BlendWeight    OutBlendFrames    InBlendFrames
    # //    S         2           18             1                 3
    # //    AH        8           2              4                 4
    # //    N         7           8              1                 2
    # //
    # // The formant transitions for the output frames are calculated as follows:
    # //
    # //     flags ampl1 freq1 ampl2 freq2 ampl3 freq3 pitch
    # //    ------------------------------------------------
    # // S
    # //    241     0     6     0    73     0    99    61   Use S (weight 18) for transition instead of AH (weight 2)
    # //    241     0     6     0    73     0    99    61   <-- (OutBlendFrames-1) = (1-1) = 0 frames
    # // AH
    # //      0     2    10     2    66     0    96    59 * <-- InBlendFrames = 3 frames
    # //      0     4    14     3    59     0    93    57 *
    # //      0     8    18     5    52     0    90    55 *
    # //      0    15    22     9    44     1    87    53
    # //      0    15    22     9    44     1    87    53
    # //      0    15    22     9    44     1    87    53   Use N (weight 8) for transition instead of AH (weight 2).
    # //      0    15    22     9    44     1    87    53   Since N is second phoneme, reverse the IN and OUT values.
    # //      0    11    17     8    47     1    98    56 * <-- (InBlendFrames-1) = (2-1) = 1 frames
    # // N
    # //      0     8    12     6    50     1   109    58 * <-- OutBlendFrames = 1
    # //      0     5     6     5    54     0   121    61
    # //      0     5     6     5    54     0   121    61
    # //      0     5     6     5    54     0   121    61
    # //      0     5     6     5    54     0   121    61
    # //      0     5     6     5    54     0   121    61
    # //      0     5     6     5    54     0   121    61
    # //
    # // Now, consider the reverse "NUS" (N AH S):
    # //
    # //     flags ampl1 freq1 ampl2 freq2 ampl3 freq3 pitch
    # //    ------------------------------------------------
    # // N
    # //     0     5     6     5    54     0   121    61
    # //     0     5     6     5    54     0   121    61
    # //     0     5     6     5    54     0   121    61
    # //     0     5     6     5    54     0   121    61
    # //     0     5     6     5    54     0   121    61
    # //     0     5     6     5    54     0   121    61   Use N (weight 8) for transition instead of AH (weight 2)
    # //     0     5     6     5    54     0   121    61   <-- (OutBlendFrames-1) = (1-1) = 0 frames
    # // AH
    # //     0     8    11     6    51     0   110    59 * <-- InBlendFrames = 2
    # //     0    11    16     8    48     0    99    56 *
    # //     0    15    22     9    44     1    87    53   Use S (weight 18) for transition instead of AH (weight 2)
    # //     0    15    22     9    44     1    87    53   Since S is second phoneme, reverse the IN and OUT values.
    # //     0     9    18     5    51     1    90    55 * <-- (InBlendFrames-1) = (3-1) = 2
    # //     0     4    14     3    58     1    93    57 *
    # // S
    # //   241     2    10     2    65     1    96    59 * <-- OutBlendFrames = 1
    # //   241     0     6     0    73     0    99    61
    def _create_transitions(self):
        m = 0
        pos = 0
        while True:
            phoneme = self.phoneme_index_output[pos]
            next_phoneme = self.phoneme_index_output[pos + 1]

            if next_phoneme == 255:
                break  # // 255 == end_token

            # // get the ranking of each phoneme
            next_rank = blend_rank[next_phoneme]
            rank = blend_rank[phoneme]

            # // compare the rank - lower rank value is stronger
            if rank == next_rank:
                # // same rank, so use out blend lengths from each phoneme
                phase1 = out_blend_length[phoneme]
                phase2 = out_blend_length[next_phoneme]
            elif rank < next_rank:
                # // next phoneme is stronger, so us its blend lengths
                phase1 = in_blend_length[next_phoneme]
                phase2 = out_blend_length[next_phoneme]
            else:
                # // current phoneme is stronger, so use its blend lengths
                # // note the out/in are swapped
                phase1 = out_blend_length[phoneme]
                phase2 = in_blend_length[phoneme]

            m = (m + self.phoneme_length_output[pos]) & 0xFF

            speedcounter = (m + phase2) & 0xFF
            phase3 = (m - phase1) & 0xFF
            transition = (phase1 + phase2) & 0xFF

            if (((transition - 2) & 0xFF) & 128) == 0:
                table = 169
                self._interpolate_pitch(pos, m, phase3)
                while table < 175:
                    # // tables:
                    # // 168  pitches[]
                    # // 169  frequency1
                    # // 170  frequency2
                    # // 171  frequency3
                    # // 172  amplitude1
                    # // 173  amplitude2
                    # // 174  amplitude3

                    value = self._read(table, speedcounter) - self._read(table, phase3)
                    self._interpolate(transition, table, phase3, value)

                    table = (table + 1) & 0xFF

            pos = (pos + 1) & 0xFF

        # // add the length of this phoneme
        return (m + self.phoneme_length_output[pos]) & 0xFF

    # // RENDER THE PHONEMES IN THE LIST
    # //
    # // The phoneme list is converted into sound through the steps:
    # //
    # // 1. Copy each phoneme <length> number of times into the frames list,
    # //    where each frame represents 10 milliseconds of sound.
    # //
    # // 2. Determine the transitions lengths between phonemes, and linearly
    # //    interpolate the values across the frames.
    # //
    # // 3. Offset the pitches by the fundamental frequency.
    # //
    # // 4. Render the each frame.
    def _render_batch(self):
        if self.phoneme_index_output[0] == 255:
            return  # //exit if no data

        self._create_frames()
        t = self._create_transitions()

        if not self.sing_mode:
            self._assign_pitch_contour()

        self._rescale_amplitude()

        if self.debug:
            self._print_output(
                self.sampled_consonant_flag,
                self.frequency1,
                self.frequency2,
                self.frequency3,
                self.amplitude1,
                self.amplitude2,
                self.amplitude3,
                self.pitches,
            )

        self._process_frames(t)

    # //return = hibyte(mem39212*mem39213) <<  1
    def _trans(self, a, b):
        return (((a * b) >> 8) << 1) & 0xFF

    # /*
    #     SAM's voice can be altered by changing the frequencies of the
    #     mouth formant (F1) and the throat formant (F2). Only the voiced
    #     phonemes (5-29 and 48-53) are altered.
    # */
    def config(
        self,
        speed: int | None = None,
        pitch: int | None = None,
        mouth: int | None = None,
        throat: int | None = None,
        sing_mode: bool | None = None,
    ):
        """Configure renderer parameters.

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
        """

        if speed is not None:
            self.speed = speed
        if pitch is not None:
            self.pitch = pitch
        if mouth is not None:
            self.mouth = mouth
        if throat is not None:
            self.throat = throat
        if sing_mode is not None:
            self.sing_mode = sing_mode

        new_frequency = 0

        pos = 5
        # // recalculate formant frequencies 5..29 for the mouth (F1) and throat (F2)
        while pos != 30:
            # // recalculate mouth frequency
            initial_frequency = mouth_formants_5_29[pos]
            if initial_frequency != 0:
                new_frequency = self._trans(self.mouth, initial_frequency)

            self.freq1data[pos] = new_frequency

            # // recalculate throat frequency
            initial_frequency = throat_formants_5_29[pos]
            if initial_frequency != 0:
                new_frequency = self._trans(self.throat, initial_frequency)

            self.freq2data[pos] = new_frequency

            pos += 1

        # // recalculate formant frequencies 48..53
        pos = 0
        while pos < 6:
            # // recalculate F1 (mouth formant)
            initial_frequency = mouth_formants_48_53[pos]
            new_frequency = self._trans(self.mouth, initial_frequency)
            self.freq1data[pos + 48] = new_frequency

            # // recalculate F2 (throat formant)
            initial_frequency = throat_formants_48_53[pos]
            new_frequency = self._trans(self.throat, initial_frequency)
            self.freq2data[pos + 48] = new_frequency

            pos += 1

    def render(
        self,
        processor: Processor,
    ) -> bool:
        """Render sound waveform.

        When it is successful, the audio data is stored in `self.buffer`.
        And the length of the valid data is stored in `self.buffer_end`.

        Args:
            processor:
                A `Processor` instance that has output parameters prepared.

        Returns:
            Whether the sound waveform are rendered successfully.
        """

        self.buffer_end = self.buffer_pos = 0  # Reset buffer end and position
        srcpos = 0  # // Position in source
        destpos = 0  # // Position in output

        while True:
            A = processor.phoneme_index[srcpos]
            self.phoneme_index_output[destpos] = A

            if A == 255:
                self._render_batch()
                return True
            elif A == 254:
                self.phoneme_index_output[destpos] = 255
                self._render_batch()
                destpos = 0
            elif A == 0:
                pass
            else:
                self.phoneme_length_output[destpos] = processor.phoneme_length[srcpos]
                self.stress_output[destpos] = processor.stress[srcpos]
                destpos = (destpos + 1) & 0xFF

            srcpos = (srcpos + 1) & 0xFF
