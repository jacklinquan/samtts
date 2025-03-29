"""SAMTTS Processor

Processor takes phonemes and prepares output parameters.
"""

from __future__ import annotations


stress_input_table = bytes([
    ord(item)
    for item
    in [
        '*', '1', '2', '3', '4', '5', '6', '7', '8'
    ]
])

sign_input_table1 = bytes([
    ord(item)
    for item
    in [
        ' ', '.', '?', ',', '-', 'I', 'I', 'E',
        'A', 'A', 'A', 'A', 'U', 'A', 'I', 'E',
        'U', 'O', 'R', 'L', 'W', 'Y', 'W', 'R',
        'L', 'W', 'Y', 'M', 'N', 'N', 'D', 'Q',
        'S', 'S', 'F', 'T', '/', '/', 'Z', 'Z',
        'V', 'D', 'C', '*', 'J', '*', '*', '*',
        'E', 'A', 'O', 'A', 'O', 'U', 'B', '*',
        '*', 'D', '*', '*', 'G', '*', '*', 'G',
        '*', '*', 'P', '*', '*', 'T', '*', '*',
        'K', '*', '*', 'K', '*', '*', 'U', 'U',
        'U'
    ]
])

sign_input_table2 = bytes([
    ord(item)
    for item
    in [
        '*', '*', '*', '*', '*', 'Y', 'H', 'H',
        'E', 'A', 'H', 'O', 'H', 'X', 'X', 'R',
        'X', 'H', 'X', 'X', 'X', 'X', 'H', '*',
        '*', '*', '*', '*', '*', 'X', 'X', '*',
        '*', 'H', '*', 'H', 'H', 'X', '*', 'H',
        '*', 'H', 'H', '*', '*', '*', '*', '*',
        'Y', 'Y', 'Y', 'W', 'W', 'W', '*', '*',
        '*', '*', '*', '*', '*', '*', '*', 'X',
        '*', '*', '*', '*', '*', '*', '*', '*',
        '*', '*', '*', 'X', '*', '*', 'L', 'M',
        'N'
    ]
])


# Ind  | phoneme |  flags   |
# -----|---------|----------|
# 0    |   *     | 00000000 |
# 1    |  .*     | 00000000 |
# 2    |  ?*     | 00000000 |
# 3    |  ,*     | 00000000 |
# 4    |  -*     | 00000000 |

# VOWELS
# 5    |  IY     | 10100100 |
# 6    |  IH     | 10100100 |
# 7    |  EH     | 10100100 |
# 8    |  AE     | 10100100 |
# 9    |  AA     | 10100100 |
# 10   |  AH     | 10100100 |
# 11   |  AO     | 10000100 |
# 17   |  OH     | 10000100 |
# 12   |  UH     | 10000100 |
# 16   |  UX     | 10000100 |
# 15   |  ER     | 10000100 |
# 13   |  AX     | 10100100 |
# 14   |  IX     | 10100100 |

# DIPHTONGS
# 48   |  EY     | 10110100 |
# 49   |  AY     | 10110100 |
# 50   |  OY     | 10110100 |
# 51   |  AW     | 10010100 |
# 52   |  OW     | 10010100 |
# 53   |  UW     | 10010100 |


# 21   |  YX     | 10000100 |
# 20   |  WX     | 10000100 |
# 18   |  RX     | 10000100 |
# 19   |  LX     | 10000100 |
# 37   |  /X     | 01000000 |
# 30   |  DX     | 01001000 |


# 22   |  WH     | 01000100 |


# VOICED CONSONANTS
# 23   |  R*     | 01000100 |
# 24   |  L*     | 01000100 |
# 25   |  W*     | 01000100 |
# 26   |  Y*     | 01000100 |
# 27   |  M*     | 01001100 |
# 28   |  N*     | 01001100 |
# 29   |  NX     | 01001100 |
# 54   |  B*     | 01001110 |
# 57   |  D*     | 01001110 |
# 60   |  G*     | 01001110 |
# 44   |  J*     | 01001100 |
# 38   |  Z*     | 01000100 |
# 39   |  ZH     | 01000100 |
# 40   |  V*     | 01000100 |
# 41   |  DH     | 01000100 |

# unvoiced CONSONANTS
# 32   |  S*     | 01000000 |
# 33   |  SH     | 01000000 |
# 34   |  F*     | 01000000 |
# 35   |  TH     | 01000000 |
# 66   |  P*     | 01001011 |
# 69   |  T*     | 01001011 |
# 72   |  K*     | 01001011 |
# 42   |  CH     | 01001000 |
# 36   |  /H     | 01000000 |

# 43   |  **     | 01000000 |
# 45   |  **     | 01000100 |
# 46   |  **     | 00000000 |
# 47   |  **     | 00000000 |


# 55   |  **     | 01001110 |
# 56   |  **     | 01001110 |
# 58   |  **     | 01001110 |
# 59   |  **     | 01001110 |
# 61   |  **     | 01001110 |
# 62   |  **     | 01001110 |
# 63   |  GX     | 01001110 |
# 64   |  **     | 01001110 |
# 65   |  **     | 01001110 |
# 67   |  **     | 01001011 |
# 68   |  **     | 01001011 |
# 70   |  **     | 01001011 |
# 71   |  **     | 01001011 |
# 73   |  **     | 01001011 |
# 74   |  **     | 01001011 |
# 75   |  KX     | 01001011 |
# 76   |  **     | 01001011 |
# 77   |  **     | 01001011 |


# SPECIAL
# 78   |  UL     | 10000000 |
# 79   |  UM     | 11000001 |
# 80   |  UN     | 11000001 |
# 31   |  Q*     | 01001100 |

FLAG_PLOSIVE = 0x0001
FLAG_STOPCONS = 0x0002  # /* stop consonant */
FLAG_VOICED = 0x0004
# /* 0x08 */
FLAG_DIPTHONG = 0x0010
FLAG_DIP_YX = 0x0020  # /* dipthong ending with YX */
FLAG_CONSONANT = 0x0040
FLAG_VOWEL = 0x0080
FLAG_PUNCT = 0x0100
# /* 0x200 */
FLAG_ALVEOLAR = 0x0400
FLAG_NASAL = 0x0800
FLAG_LIQUIC = 0x1000  # /* liquic consonant */
FLAG_FRICATIVE = 0x2000

flags = [
    0x8000 , 0xC100 , 0xC100 , 0xC100 , 0xC100 , 0x00A4 , 0x00A4 , 0x00A4 ,
    0x00A4 , 0x00A4 , 0x00A4 , 0x0084 , 0x0084 , 0x00A4 , 0x00A4 , 0x0084 ,
    0x0084 , 0x0084 , 0x0084 , 0x0084 , 0x0084 , 0x0084 , 0x0044 , 0x1044 ,
    0x1044 , 0x1044 , 0x1044 , 0x084C , 0x0C4C , 0x084C , 0x0448 , 0x404C ,

    0x2440 , 0x2040 , 0x2040 , 0x2440 , 0x0040 , 0x0040 , 0x2444 , 0x2044 ,
    0x2044 , 0x2444 , 0x2048 , 0x2040 , 0x004C , 0x2044 , 0x0000 , 0x0000 ,
    0x00B4 , 0x00B4 , 0x00B4 , 0x0094 , 0x0094 , 0x0094 , 0x004E , 0x004E ,

    0x004E , 0x044E , 0x044E , 0x044E , 0x004E , 0x004E , 0x004E , 0x004E ,
    0x004E , 0x004E , 0x004B , 0x004B , 0x004B , 0x044B , 0x044B , 0x044B ,
    0x004B , 0x004B , 0x004B , 0x004B , 0x004B , 0x004B , 0x0080 , 0x00C1 ,
    0x00C1
]

phoneme_stressed_length_table = bytes([
    0x00 , 0x12 , 0x12 , 0x12 , 8 ,0xB , 9 ,0xB ,
    0xE ,0xF ,0xB , 0x10 ,0xC , 6 , 6 ,0xE ,
    0xC ,0xE ,0xC ,0xB , 8 , 8 ,0xB ,0xA ,
    9 , 8 , 8 , 8 , 8 , 8 , 3 , 5 ,
    2 , 2 , 2 , 2 , 2 , 2 , 6 , 6 ,
    8 , 6 , 6 , 2 , 9 , 4 , 2 , 1 ,
    0xE ,0xF ,0xF ,0xF ,0xE ,0xE , 8 , 2 ,
    2 , 7 , 2 , 1 , 7 , 2 , 2 , 7 ,
    2 , 2 , 8 , 2 , 2 , 6 , 2 , 2 ,
    7 , 2 , 4 , 7 , 1 , 4 , 5 , 5
])

phoneme_length_table = bytes([
    0 , 0x12 , 0x12 , 0x12 , 8 , 8 , 8 , 8 ,
    8 ,0xB , 6 ,0xC ,0xA , 5 , 5 ,0xB ,
    0xA ,0xA ,0xA , 9 , 8 , 7 , 9 , 7 ,
    6 , 8 , 6 , 7 , 7 , 7 , 2 , 5 ,
    2 , 2 , 2 , 2 , 2 , 2 , 6 , 6 ,
    7 , 6 , 6 , 2 , 8 , 3 , 1 , 0x1E ,
    0xD ,0xC ,0xC ,0xC ,0xE , 9 , 6 , 1 ,
    2 , 5 , 1 , 1 , 6 , 1 , 2 , 6 ,
    1 , 2 , 8 , 2 , 2 , 4 , 2 , 2 ,
    6 , 1 , 4 , 6 , 1 , 4 , 0xC7 , 0xFF
])

PR = 23
PD = 57
PT = 69
BREAK = 254
END = 255


class Processor:
    """Processor takes phonemes and prepares output parameters.
    
    Args:
        debug:
            Set or clear debug flag.
    """
    
    def __init__(self, debug: bool=False):
        self.phoneme_index = bytearray(256)
        self.phoneme_index[255] = 32  # //to prevent buffer overflow
        self.phoneme_length = bytearray(256)
        self.stress = bytearray(256)  # //numbers from 0 to 8
        self.debug = debug


    def _print_phonemes(self):
        print("===========================================")
        print("Internal Phoneme presentation:")
        print()
        print(" idx    phoneme  length  stress")
        print("------------------------------")

        i = 0
        while (self.phoneme_index[i] != 255) and (i < 255):
            if self.phoneme_index[i] < 81:
                print(f" {self.phoneme_index[i]:3}      {chr(sign_input_table1[self.phoneme_index[i]])}{chr(sign_input_table2[self.phoneme_index[i]])}      {self.phoneme_length[i]:3}       {self.stress[i]}")
            else:
                print(f" {self.phoneme_index[i]:3}      ??      {self.phoneme_length[i]:3}       {self.stress[i]}")

            i += 1
        
        print("===========================================")
        print()


    def _insert(self, position: int, mem60: int, mem59: int, mem58: int):
        i = 253  # // ML : always keep last safe-guarding 255
        while i >= position:
            self.phoneme_index[i+1] = self.phoneme_index[i]
            self.phoneme_length[i+1] = self.phoneme_length[i]
            self.stress[i+1] = self.stress[i]
            i -= 1

        self.phoneme_index[position] = mem60
        self.phoneme_length[position] = mem59
        self.stress[position] = mem58


    def _insert_breath(self):
        mem54 = 255
        len = 0
        pos = 0

        index = self.phoneme_index[pos]
        while index != END:
            len = (len + self.phoneme_length[pos]) & 0xFF
            if len < 232:
                if index == BREAK:
                    pass
                elif not (flags[index] & FLAG_PUNCT):
                    if index == 0:
                        mem54 = pos
                else:
                    len = 0
                    pos = (pos+1) & 0xFF
                    self._insert(pos, BREAK, 0, 0)
            else:
                pos = mem54
                self.phoneme_index[pos] = 31  # // 'Q*' glottal stop
                self.phoneme_length[pos] = 4
                self.stress[pos] = 0

                len = 0
                pos = (pos+1) & 0xFF
                self._insert(pos, BREAK, 0, 0)
            
            pos = (pos+1) & 0xFF
            index = self.phoneme_index[pos]
    

    # // Iterates through the phoneme buffer, copying the stress value from
    # // the following phoneme under the following circumstance:

    # //     1. The current phoneme is voiced, excluding plosives and fricatives
    # //     2. The following phoneme is voiced, excluding plosives and fricatives, and
    # //     3. The following phoneme is stressed
    # //
    # //  In those cases, the stress value+1 from the following phoneme is copied.
    # //
    # // For example, the word LOITER is represented as LOY5TER, with as stress
    # // of 5 on the diphtong OY. This routine will copy the stress value of 6 (5+1)
    # // to the L that precedes it.
    def _copy_stress(self):
        # // loop through all the phonemes to be output
        pos = 0
        
        y = self.phoneme_index[pos]
        while y != END:
            # // if CONSONANT_FLAG set, skip - only vowels get stress
            if flags[y] & 64:
                y = self.phoneme_index[(pos+1) & 0xFF]

                # // if the following phoneme is the end, or a vowel, skip
                if (y != END) and ((flags[y] & 128) != 0):
                    # // get the stress value at the next position
                    y = self.stress[(pos+1) & 0xFF]
                    if y and not (y & 128):
                        # // if next phoneme is stressed, and a VOWEL OR ER
                        # // copy stress from next phoneme to this one
                        self.stress[pos] = (y+1) & 0xFF

            pos = (pos+1) & 0xFF
            y = self.phoneme_index[pos]
        

    def _full_match(self, sign1, sign2):
        y = 0

        # do-while loop
        flag_loop_init = True
        while (y != 81) or flag_loop_init:
            flag_loop_init = False

            # // GET FIRST CHARACTER AT POSITION Y IN signInputTable
            # // --> should change name to PhonemeNameTable1
            a = sign_input_table1[y]

            if a == sign1:
                a = sign_input_table2[y]
                # // NOT A SPECIAL AND MATCHES SECOND CHARACTER?
                if (a != ord("*")) and (a == sign2):
                    return y

            y = (y+1) & 0xFF
        
        return None


    def _wild_match(self, sign1):
        y = 0

        # do-while loop
        flag_loop_init = True
        while (y != 81) or flag_loop_init:
            flag_loop_init = False

            if sign_input_table2[y] == ord("*"):
                if sign_input_table1[y] == sign1:
                    return y

            y = (y+1) & 0xFF
        
        return None
        

    # // The input[] buffer contains a string of phonemes and stress markers along
    # // the lines of:
    # //
    # //     DHAX KAET IHZ AH5GLIY. <0x9B>
    # //
    # // The byte 0x9B marks the end of the buffer. Some phonemes are 2 bytes 
    # // long, such as "DH" and "AX". Others are 1 byte long, such as "T" and "Z". 
    # // There are also stress markers, such as "5" and ".".
    # //
    # // The first character of the phonemes are stored in the table signInputTable1[].
    # // The second character of the phonemes are stored in the table signInputTable2[].
    # // The stress characters are arranged in low to high stress order in stressInputTable[].
    # // 
    # // The following process is used to parse the input[] buffer:
    # // 
    # // Repeat until the <0x9B> character is reached:
    # //
    # //        First, a search is made for a 2 character match for phonemes that do not
    # //        end with the '*' (wildcard) character. On a match, the index of the phoneme 
    # //        is added to phonemeIndex[] and the buffer position is advanced 2 bytes.
    # //
    # //        If this fails, a search is made for a 1 character match against all
    # //        phoneme names ending with a '*' (wildcard). If this succeeds, the 
    # //        phoneme is added to phonemeIndex[] and the buffer position is advanced
    # //        1 byte.
    # // 
    # //        If this fails, search for a 1 character match in the stressInputTable[].
    # //        If this succeeds, the stress value is placed in the last stress[] table
    # //        at the same index of the last added phoneme, and the buffer position is
    # //        advanced by 1 byte.
    # //
    # //        If this fails, return a 0.
    # //
    # // On success:
    # //
    # //    1. phonemeIndex[] will contain the index of all the phonemes.
    # //    2. The last index in phonemeIndex[] will be 255.
    # //    3. stress[] will contain the stress value for each phoneme

    # // input[] holds the string of phonemes, each two bytes wide
    # // signInputTable1[] holds the first character of each phoneme
    # // signInputTable2[] holds te second character of each phoneme
    # // phonemeIndex[] holds the indexes of the phonemes after parsing input[]
    # //
    # // The parser scans through the input[], finding the names of the phonemes
    # // by searching signInputTable1[] and signInputTable2[]. On a match, it
    # // copies the index of the phoneme into the phonemeIndexTable[].
    # //
    # // The character <0x9B> marks the end of text in input[]. When it is reached,
    # // the index 255 is placed at the end of the phonemeIndexTable[], and the
    # // function returns with a 1 indicating success.
    def _parser1(self, input_buf):
        position = 0
        srcpos = 0

        sign1 = input_buf[srcpos]
        while sign1 != 155:  # // 155 is end of line marker
            srcpos = (srcpos+1) & 0xFF
            sign2 = input_buf[srcpos]

            match_f = self._full_match(sign1, sign2)
            match_w = self._wild_match(sign1)
            if match_f is not None:
                # // Matched both characters (no wildcards)
                self.phoneme_index[position] = match_f
                position = (position+1) %256
                srcpos = (srcpos+1) & 0xFF  # // Skip the second character of the input as we've matched it
            elif match_w is not None:
                # // Matched just the first character (with second character matching '*'
                self.phoneme_index[position] = match_w
                position = (position+1) %256
            else:
                # // Should be a stress character. Search through the
                # // stress table backwards.
                match_t = 8  # // End of stress table. FIXME: Don't hardcode.
                while (sign1 != stress_input_table[match_t]) and (match_t > 0):
                    match_t -= 1
                
                if match_t == 0:
                    return 0  # // failure
                
                self.stress[(position-1) & 0xFF] = match_t  # // Set stress for prior phoneme

            sign1 = input_buf[srcpos]
        
        self.phoneme_index[position] = END
        return 1
        
        
    # //change phonemelength depedendent on stress
    def _set_phoneme_length(self):
        position = 0
        while self.phoneme_index[position] != 255:
            a = self.stress[position]
            if (a == 0) or ((a&128) != 0):
                self.phoneme_length[position] = phoneme_length_table[self.phoneme_index[position]]
            else:
                self.phoneme_length[position] = phoneme_stressed_length_table[self.phoneme_index[position]]
            
            position += 1

        
    def _code41240(self):
        pos = 0

        while self.phoneme_index[pos] != END:
            index = self.phoneme_index[pos]

            if flags[index] & FLAG_STOPCONS:
                if flags[index] & FLAG_PLOSIVE:
                    x = pos
                    x = (x+1) & 0xFF
                    while not self.phoneme_index[x]:
                        x = (x+1) & 0xFF  # /* Skip pause */
                    
                    a = self.phoneme_index[x]
                    if a != END:
                        if (flags[a] & 8) or (a == 36) or (a == 37):
                            # // '/H' '/X'
                            pos = (pos+1) & 0xFF
                            continue
                
                self._insert((pos+1) & 0xFF, (index+1) & 0xFF, phoneme_length_table[(index+1) & 0xFF], self.stress[pos])
                self._insert((pos+2) & 0xFF, (index+2) & 0xFF, phoneme_length_table[(index+2) & 0xFF], self.stress[pos])
                pos = (pos+2) & 0xFF
            
            pos = (pos+1) & 0xFF


    def _change_rule(self, position, m, descr):
        if self.debug:
            print(f"RULE: {descr}")
        
        self.phoneme_index[position] = 13  # //rule
        self._insert(position+1, m, 0, self.stress[position])


    def _drule(self, string):
        if self.debug:
            print(f"RULE: {string}")


    def _drule_pre(self, descr, x):
        self._drule(descr)
        if self.debug:
            print("PRE")
            print(f"phoneme {x} ({chr(sign_input_table1[self.phoneme_index[x]])}{chr(sign_input_table2[self.phoneme_index[x]])}) length {self.phoneme_length[x]}")


    def _drule_post(self, x):
        if self.debug:
            print("POST")
            print(f"phoneme {x} ({chr(sign_input_table1[self.phoneme_index[x]])}{chr(sign_input_table2[self.phoneme_index[x]])}) length {self.phoneme_length[x]}")


    # // Rewrites the phonemes using the following rules:
    # //
    # //       <DIPTHONG ENDING WITH WX> -> <DIPTHONG ENDING WITH WX> WX
    # //       <DIPTHONG NOT ENDING WITH WX> -> <DIPTHONG NOT ENDING WITH WX> YX
    # //       UL -> AX L
    # //       UM -> AX M
    # //       <STRESSED VOWEL> <SILENCE> <STRESSED VOWEL> -> <STRESSED VOWEL> <SILENCE> Q <VOWEL>
    # //       T R -> CH R
    # //       D R -> J R
    # //       <VOWEL> R -> <VOWEL> RX
    # //       <VOWEL> L -> <VOWEL> LX
    # //       G S -> G Z
    # //       K <VOWEL OR DIPTHONG NOT ENDING WITH IY> -> KX <VOWEL OR DIPTHONG NOT ENDING WITH IY>
    # //       G <VOWEL OR DIPTHONG NOT ENDING WITH IY> -> GX <VOWEL OR DIPTHONG NOT ENDING WITH IY>
    # //       S P -> S B
    # //       S T -> S D
    # //       S K -> S G
    # //       S KX -> S GX
    # //       <ALVEOLAR> UW -> <ALVEOLAR> UX
    # //       CH -> CH CH' (CH requires two phonemes to represent it)
    # //       J -> J J' (J requires two phonemes to represent it)
    # //       <UNSTRESSED VOWEL> T <PAUSE> -> <UNSTRESSED VOWEL> DX <PAUSE>
    # //       <UNSTRESSED VOWEL> D <PAUSE>  -> <UNSTRESSED VOWEL> DX <PAUSE>
    def _rule_alveolar_uw(self, x):
        # // ALVEOLAR flag set?
        if flags[self.phoneme_index[x-1]] & FLAG_ALVEOLAR:
            self._drule("<ALVEOLAR> UW -> <ALVEOLAR> UX")
            self.phoneme_index[x] = 16


    def _rule_ch(self, x):
        self._drule("CH -> CH CH+1")
        self._insert(x+1, 43, 0, self.stress[x])


    def _rule_j(self, x):
        self._drule("J -> J J+1")
        self._insert(x+1, 45, 0, self.stress[x])


    def _rule_g(self, pos):
        # // G <VOWEL OR DIPTHONG NOT ENDING WITH IY> -> GX <VOWEL OR DIPTHONG NOT ENDING WITH IY>
        # // Example: GO
        index = self.phoneme_index[pos+1]

        # // If dipthong ending with YX, move continue processing next phoneme
        if (index != END) and ((flags[index] & FLAG_DIP_YX) == 0):
            # // replace G with GX and continue processing next phoneme
            self._drule("G <VOWEL OR DIPTHONG NOT ENDING WITH IY> -> GX <VOWEL OR DIPTHONG NOT ENDING WITH IY>")
            self.phoneme_index[pos] = 63  # // 'GX'


    def _change(self, pos, val, rule):
        self._drule(rule)
        self.phoneme_index[pos] = val


    def _rule_dipthong(self, p, pf, pos):
        # // <DIPTHONG ENDING WITH WX> -> <DIPTHONG ENDING WITH WX> WX
        # // <DIPTHONG NOT ENDING WITH WX> -> <DIPTHONG NOT ENDING WITH WX> YX
        # // Example: OIL, COW

        # // If ends with IY, use YX, else use WX
        a =  21 if pf & FLAG_DIP_YX else 20  # // 'WX' = 20 'YX' = 21

        # // Insert at WX or YX following, copying the stress
        if a == 20:
            self._drule("insert WX following dipthong NOT ending in IY sound")
        elif a == 21:
            self._drule("insert YX following dipthong ending in IY sound")
        
        self._insert(pos+1, a, 0, self.stress[pos])

        if p == 53:
            # // Example: NEW, DEW, SUE, ZOO, THOO, TOO
            self._rule_alveolar_uw(pos)
        elif p == 42:
            # // Example: CHEW
            self._rule_ch(pos)
        elif p == 44:
            # // Example: JAY
            self._rule_j(pos)


    def _parser2(self):
        pos = 0

        if self.debug:
            print("Parser2")
        
        p = self.phoneme_index[pos]
        while p != END:
            if self.debug:
                print(f"{pos}: {chr(sign_input_table1[p])}{chr(sign_input_table2[p])}")
            
            if p == 0:
                # // Is phoneme pause?
                pos = (pos+1) & 0xFF
                p = self.phoneme_index[pos]
                continue

            pf = flags[p]
            prior = self.phoneme_index[pos-1]

            if pf & FLAG_DIPTHONG:
                self._rule_dipthong(p, pf, pos)
            elif p == 78:
                # // Example: MEDDLE
                self._change_rule(pos, 24, "UL -> AX L")
            elif p == 79:
                # // Example: ASTRONOMY
                self._change_rule(pos, 27, "UM -> AX M")
            elif p == 80:
                # // Example: FUNCTION
                self._change_rule(pos, 28, "UN -> AX N")
            elif (pf & FLAG_VOWEL) and self.stress[pos]:
                # // RULE:
                # //       <STRESSED VOWEL> <SILENCE> <STRESSED VOWEL> -> <STRESSED VOWEL> <SILENCE> Q <VOWEL>
                # // EXAMPLE: AWAY EIGHT
                if not self.phoneme_index[pos+1]:
                    # // If following phoneme is a pause, get next
                    p = self.phoneme_index[pos+2]
                    if (p != END) and (flags[p] & FLAG_VOWEL) and self.stress[pos+2]:
                        self._drule("Insert glottal stop between two stressed vowels with space between them")
                        self._insert(pos+2, 31, 0, 0)  # // 31 = 'Q'
            elif p == PR:
                # // RULES FOR PHONEMES BEFORE R
                if prior == PT:
                    # // Example: TRACK
                    self._change(pos-1, 42, "T R -> CH R")
                elif prior == PD:
                    # // Example: DRY
                    self._change(pos-1, 44, "D R -> J R")
                elif flags[prior] & FLAG_VOWEL:
                    # // Example: ART
                    self._change(pos, 18, "<VOWEL> R -> <VOWEL> RX")
            elif (p == 24) and (flags[prior] & FLAG_VOWEL):
                # // Example: ALL
                self._change(pos, 19, "<VOWEL> L -> <VOWEL> LX")
            elif prior == 60 and p == 32:
                # // 'G' 'S'
                # // Can't get to fire -
                # //       1. The G -> GX rule intervenes
                # //       2. Reciter already replaces GS -> GZ
                self._change(pos, 38, "G S -> G Z")
            elif p == 60:
                self._rule_g(pos)
            else:
                if p == 72:
                    # // 'K'
                    # // K <VOWEL OR DIPTHONG NOT ENDING WITH IY> -> KX <VOWEL OR DIPTHONG NOT ENDING WITH IY>
                    # // Example: COW
                    y = self.phoneme_index[pos+1]
                    # // If at end, replace current phoneme with KX
                    if ((y == END) or (flags[y] & FLAG_DIP_YX) == 0):
                        # // VOWELS AND DIPTHONGS ENDING WITH IY SOUND flag set?
                        self._change(pos, 75, "K <VOWEL OR DIPTHONG NOT ENDING WITH IY> -> KX <VOWEL OR DIPTHONG NOT ENDING WITH IY>")
                        p = 75
                        pf = flags[p]
                
                # // Replace with softer version?
                if (flags[p] & FLAG_PLOSIVE) and (prior == 32):
                    # // 'S'
                    # // RULE:
                    # //      S P -> S B
                    # //      S T -> S D
                    # //      S K -> S G
                    # //      S KX -> S GX
                    # // Examples: SPY, STY, SKY, SCOWL

                    if self.debug:
                        print(f"RULE: S* {chr(sign_input_table1[p])}{chr(sign_input_table2[p])} -> S* {chr(sign_input_table1[p-12])}{chr(sign_input_table2[p-12])}")
                    
                    self.phoneme_index[pos] = p - 12
                elif not (pf & FLAG_PLOSIVE):
                    p = self.phoneme_index[pos]
                    if p == 53:
                        # // Example: NEW, DEW, SUE, ZOO, THOO, TOO
                        self._rule_alveolar_uw(pos)
                    elif p == 42:
                        # // Example: CHEW
                        self._rule_ch(pos)
                    elif p == 44:
                        # // Example: JAY
                        self._rule_j(pos)
                
                if p == 69 or p == 57:
                    # // 'T', 'D'
                    # // RULE: Soften T following vowel
                    # // NOTE: This rule fails for cases such as "ODD"
                    # //       <UNSTRESSED VOWEL> T <PAUSE> -> <UNSTRESSED VOWEL> DX <PAUSE>
                    # //       <UNSTRESSED VOWEL> D <PAUSE>  -> <UNSTRESSED VOWEL> DX <PAUSE>
                    # // Example: PARTY, TARDY
                    if flags[self.phoneme_index[pos-1]] & FLAG_VOWEL:
                        p = self.phoneme_index[pos+1]
                        if not p:
                            p = self.phoneme_index[pos+2]

                        if p == END:
                            break
                        
                        if (p != END) and (flags[p] & FLAG_VOWEL) and not self.stress[pos+1]:
                            self._change(pos, 30, "Soften T or D following vowel or ER and preceding a pause -> DX")

            pos = (pos+1) & 0xFF
            p = self.phoneme_index[pos]


    # // Applies various rules that adjust the lengths of phonemes
    # //
    # //         Lengthen <FRICATIVE> or <VOICED> between <VOWEL> and <PUNCTUATION> by 1.5
    # //         <VOWEL> <RX | LX> <CONSONANT> - decrease <VOWEL> length by 1
    # //         <VOWEL> <UNVOICED PLOSIVE> - decrease vowel by 1/8th
    # //         <VOWEL> <UNVOICED CONSONANT> - increase vowel by 1/2 + 1
    # //         <NASAL> <STOP CONSONANT> - set nasal = 5, consonant = 6
    # //         <VOICED STOP CONSONANT> {optional silence} <STOP CONSONANT> - shorten both to 1/2 + 1
    # //         <LIQUID CONSONANT> <DIPHTONG> - decrease by 2
    def _adjust_lengths(self):
        # // LENGTHEN VOWELS PRECEDING PUNCTUATION
        # //
        # // Search for punctuation. If found, back up to the first vowel, then
        # // process all phonemes between there and up to (but not including) the punctuation.
        # // If any phoneme is found that is a either a fricative or voiced, the duration is
        # // increased by (length * 1.5) + 1

        # // loop index
        x = 0
        index = self.phoneme_index[x]
        while index != END:
            # // not punctuation?
            if (flags[index] & FLAG_PUNCT) == 0:
                x = (x+1) & 0xFF
                index = self.phoneme_index[x]
                continue

            loopIndex = x

            x = (x-1) & 0xFF
            while x and not (flags[self.phoneme_index[x]] & FLAG_VOWEL):
                # // back up while not a vowel
                x = (x-1) & 0xFF
            
            if x == 0:
                break

            # do-while loop
            flag_loop_init = True
            while (x != loopIndex) or flag_loop_init:
                flag_loop_init = False

                # // test for vowel
                index = self.phoneme_index[x]

                # // test for fricative/unvoiced or not voiced
                if (not (flags[index] & FLAG_FRICATIVE)) or (flags[index] & FLAG_VOICED):
                    # //nochmal �berpr�fen
                    a = self.phoneme_length[x]
                    # // change phoneme length to (length * 1.5) + 1
                    self._drule_pre("Lengthen <FRICATIVE> or <VOICED> between <VOWEL> and <PUNCTUATION> by 1.5", x)
                    self.phoneme_length[x] = (a >> 1) + a + 1
                    self._drule_post(x)

                x = (x+1) & 0xFF
            
            x = (x+1) & 0xFF
            index = self.phoneme_index[x]
        
        # // Similar to the above routine, but shorten vowels under some circumstances

        # // Loop through all phonemes
        loopIndex = 0
        index = self.phoneme_index[loopIndex]
        while index != END:
            x = loopIndex

            if flags[index] & FLAG_VOWEL:
                index = self.phoneme_index[loopIndex+1]

                if (index != END) and not (flags[index] & FLAG_CONSONANT):
                    if (index == 18) or (index == 19):
                        # // 'RX', 'LX'
                        index = self.phoneme_index[loopIndex+2]

                        if (index != END) and (flags[index] & FLAG_CONSONANT):
                            self._drule_pre("<VOWEL> <RX | LX> <CONSONANT> - decrease length of vowel by 1", loopIndex)
                            self.phoneme_length[loopIndex] = (self.phoneme_length[loopIndex]-1) & 0xFF
                            self._drule_post(loopIndex)
                else:
                    # // Got here if not <VOWEL>
                    flag = 65 if index == END else flags[index]  # 65 if end marker

                    if not (flag & FLAG_VOICED):
                        # // Unvoiced
                        # // *, .*, ?*, ,*, -*, DX, S*, SH, F*, TH, /H, /X, CH, P*, T*, K*, KX
                        if flag & FLAG_PLOSIVE:
                            # // unvoiced plosive
                            # // RULE: <VOWEL> <UNVOICED PLOSIVE>
                            # // <VOWEL> <P*, T*, K*, KX>
                            self._drule_pre("<VOWEL> <UNVOICED PLOSIVE> - decrease vowel by 1/8th", loopIndex)
                            self.phoneme_length[loopIndex] -= (self.phoneme_length[loopIndex] >> 3)
                            self._drule_post(loopIndex)
                    else:
                        # drule_pre("<VOWEL> <VOICED CONSONANT> - increase vowel by 1/2 + 1", X-1)
                        self._drule_pre("<VOWEL> <VOICED CONSONANT> - increase vowel by 1/2 + 1", x)
                        # // decrease length
                        a = self.phoneme_length[loopIndex]
                        self.phoneme_length[loopIndex] = (a >> 2) + a + 1  # // 5/4*A + 1
                        self._drule_post(loopIndex)
            elif (flags[index] & FLAG_NASAL) != 0:
                # // nasal?
                # // RULE: <NASAL> <STOP CONSONANT>
                # //       Set punctuation length to 6
                # //       Set stop consonant length to 5
                x = (x+1) & 0xFF
                index = self.phoneme_index[x]
                if index != END and (flags[index] & FLAG_STOPCONS):
                    self._drule("<NASAL> <STOP CONSONANT> - set nasal = 5, consonant = 6")
                    self.phoneme_length[x] = 6  # // set stop consonant length to 6
                    self.phoneme_length[x-1] = 5  # // set nasal length to 5
            elif flags[index] & FLAG_STOPCONS:
                # // (voiced) stop consonant?
                # // RULE: <VOICED STOP CONSONANT> {optional silence} <STOP CONSONANT>
                # //       Shorten both to (length/2 + 1)

                # // move past silence
                x = (x+1) & 0xFF
                index = self.phoneme_index[x]
                while index == 0:
                    x = (x+1) & 0xFF
                    index = self.phoneme_index[x]
                
                if (index != END) and (flags[index] & FLAG_STOPCONS):
                    # // FIXME, this looks wrong?
                    # // RULE: <UNVOICED STOP CONSONANT> {optional silence} <STOP CONSONANT>
                    self._drule("<UNVOICED STOP CONSONANT> {optional silence} <STOP CONSONANT> - shorten both to 1/2 + 1")
                    self.phoneme_length[x] = (self.phoneme_length[x] >> 1) + 1
                    self.phoneme_length[loopIndex] = (self.phoneme_length[loopIndex] >> 1) + 1
                    x = loopIndex
            elif flags[index] & FLAG_LIQUIC:
                # // liquic consonant?
                # // RULE: <VOICED NON-VOWEL> <DIPTHONG>
                # //       Decrease <DIPTHONG> by 2
                index = self.phoneme_index[x-1]  # // prior phoneme

                # // FIXME: The debug code here breaks the rule.
                # // prior phoneme a stop consonant>
                # if (flags[index] & FLAG_STOPCONS) != 0:
                self._drule_pre("<LIQUID CONSONANT> <DIPTHONG> - decrease by 2", x)
                
                self.phoneme_length[x] -= 2  # // 20ms
                self._drule_post(x)

            loopIndex = (loopIndex+1) & 0xFF
            index = self.phoneme_index[loopIndex]


    def process(self, input_phonemes: str | bytes | bytearray) -> bool:
        """Process the phonemes and prepare output parameters.

        When it is successful, the output parameters are stored in:
        
        - `self.phoneme_index`
        - `self.phoneme_length`
        - `self.stress`

        Args:
            input_phonemes:
                The input phonemes to process.

        Returns:
            Whether the phonemes are processed successfully.
        """
        
        if isinstance(input_phonemes, str):
            # Convert string to bytes
            input_phonemes = input_phonemes.encode("utf-8")
        elif not isinstance(input_phonemes, (bytes, bytearray)):
            raise Exception("The type of input text must be str, bytes or bytearray.")

        input_phonemes = bytearray(input_phonemes) + bytearray(b"\x9b")
        
        x = 0
        
        if not self._parser1(input_phonemes):
            return False
        
        if self.debug:
            self._print_phonemes()
        
        self._parser2()
        self._copy_stress()
        self._set_phoneme_length()
        self._adjust_lengths()
        self._code41240()

        # do-while loop
        flag_loop_init = True
        while (x != 0) or flag_loop_init:
            flag_loop_init = False
            
            if self.phoneme_index[x] > 80:
                self.phoneme_index[x] = 255
                break  # // error: delete all behind it

            x += 1
        
        self._insert_breath()

        if self.debug:
            self._print_phonemes()
        
        return True
