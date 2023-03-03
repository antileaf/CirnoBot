import enum
import string

from typing import Dict, List, Optional, Set, Tuple

class Character(enum.Enum):
    Error = -1

    Sol = 0
    So = Sol

    Ky = 1

    May = 2
    Ma = May

    Axl = 3
    Ax = Axl

    Chipp = 4
    Ch = Chipp

    Potemkin = 5
    Po = Potemkin
    
    Faust = 6
    Fa = Faust

    Millia = 7
    Mi = Millia

    Zato_1 = 8
    Zato1 = Zato_1
    Zato = Zato_1
    Za = Zato_1

    Ramlethal = 9
    Ram = Ramlethal
    Ra = Ramlethal

    Leo = 10
    Le = Leo

    Nagoriyuki = 11
    Nago = Nagoriyuki
    Na = Nagoriyuki

    Giovanna = 12
    Gi = Giovanna

    Anji = 13

    I_No = 14
    Ino = I_No
    INo = I_No

    Goldlewis = 15
    Go = Goldlewis

    Jack_O = 16
    Jacko = Jack_O
    JackO = Jack_O
    Jko = Jack_O

    Happy_Chaos = 17
    Ha = Happy_Chaos
    Happy = Happy_Chaos

    Baiken = 18
    Ba = Baiken

    Testament = 19
    Te = Testament

    Bridget = 20
    Br = Bridget

    Sin = 21
    Si = Sin


full_name_tbl : Dict[Character, str] = {
    Character.Error : 'Error',
    Character.Sol : 'Sol Badguy',
    Character.Ky : 'Ky Kiske',
    Character.May : 'May',
    Character.Axl : 'Axl Low',
    Character.Chipp : 'Chipp Zanuff',
    Character.Potemkin : 'Potemkin',
    Character.Faust : 'Faust',
    Character.Millia : 'Millia Rage',
    Character.Zato_1 : 'Zato-1',
    Character.Ramlethal : 'Ramlethal Valentine',
    Character.Leo : 'Leo Whitefang',
    Character.Nagoriyuki : 'Nagoriyuki',
    Character.Giovanna : 'Giovanna',
    Character.Anji : 'Anji Mito',
    Character.I_No : 'I-No',
    Character.Goldlewis : 'Goldlewis',
    Character.Jack_O : 'Jack-O',
    Character.Happy_Chaos : 'Happy Chaos',
    Character.Baiken : 'Baiken',
    Character.Testament : 'Testament',
    Character.Bridget : 'Bridget',
    Character.Sin : 'Sin Kiske'
}

# such tricks are useful!
full_name_reversed_tbl : Dict[str, Character] = { v : k for k, v in full_name_tbl.items() }


short_name_tbl = {
    Character.Error : 'Error',
    Character.Sol : 'Sol',
    Character.Ky : 'Ky',
    Character.May : 'May',
    Character.Axl : 'Axl',
    Character.Chipp : 'Chipp',
    Character.Potemkin : 'Potemkin',
    Character.Faust : 'Faust',
    Character.Millia : 'Millia',
    Character.Zato_1 : 'Zato',
    Character.Ramlethal : 'Ramlethal',
    Character.Leo : 'Leo',
    Character.Nagoriyuki : 'Nagoriyuki',
    Character.Giovanna : 'Giovanna',
    Character.Anji : 'Anji',
    Character.I_No : 'I-No',
    Character.Goldlewis : 'Goldlewis',
    Character.Jack_O : 'Jack-O',
    Character.Happy_Chaos : 'Happy Chaos',
    Character.Baiken : 'Baiken',
    Character.Testament : 'Testament',
    Character.Bridget : 'Bridget',
    Character.Sin : 'Sin'
}

short_name_reversed_tbl : Dict[str, Character] = { v : k for k, v in short_name_tbl.items() }


two_letter_name_tbl : Dict[Character, List[str]] = {
    Character.Error : ['Error'],
    Character.Sol : ['so'],
    Character.Ky : ['ky'],
    Character.May : ['ma'],
    Character.Axl : ['ax'],
    Character.Chipp : ['ch'],
    Character.Potemkin : ['po'],
    Character.Faust : ['fa'],
    Character.Millia : ['mi'],
    Character.Zato_1 : ['za'],
    Character.Ramlethal : ['ra'],
    Character.Leo : ['le'],
    Character.Nagoriyuki : ['na'],
    Character.Giovanna : ['gi'],
    Character.Anji : ['an'],
    Character.I_No : ['in'],
    Character.Goldlewis : ['go'],
    Character.Jack_O : ['jc', 'jk'],
    Character.Happy_Chaos : ['ha', 'hc'],
    Character.Baiken : ['ba'],
    Character.Testament : ['te'],
    Character.Bridget : ['br', 'bi'],
    Character.Sin : ['si']
}


aliases_tbl : Dict[Character, Set[str]] = {
    Character.Error : set(),
    Character.Sol : {'Sol Badguy', 'Sol'},
    Character.Ky : {'Ky Kiske', 'Ky'},
}
