import requests
from lxml import etree
import pandas as pd

from typing import Dict, List, Optional, Set, Tuple

tbl = {
    'Sol' : ['sol', 'so', 'sol badguy', '索尔', '索爾', '寸拳', '寸拳人', 'badguy', '索尔巴德凯', '巴德凯', '索尔巴德盖'],
    'Ky' : ['ky', 'ky', 'ky kiske', 'kiske', '凯', '凱', '连王', '第一连王'],
    'May' : ['may', 'ma', '梅伊', '梅', '海豚', '海豚人', 'totsugeki', 'ttgk'],
    'Axl' : ['axl', 'ax', '阿克赛尔', '阿克塞尔', '罗'],
    'Chipp' : ['chipp', 'ch', '奇普', '奇普萨那弗', '忍者', '纸忍', '忍'],
    'Potemkin' : ['potemkin', 'po', '波乔姆金', '波乔姆', '金'],
    'Faust' : ['faust', 'fa', '浮士德', '医生'],
    'Millia' : ['millia', 'mi', '米莉亚', '米莉亚蕾姬'],
    'Zato-1' : ['zato-1', 'za', 'zato1', 'zato', '扎特'],
    'Ramlethal' : ['ramlethal', 'ra', '拉姆', '大剑人'],
    'Leo' : ['leo', 'le', '雷奥', '狮子'],
    'Nagoriyuki' : ['nagoriyuki', 'na', 'nago', '名残雪', '尼哥', '倪哥', '尼'],
    'Giovanna' : ['giovanna', 'gi', '乔凡娜', '狼妹'],
    'Anji' : ['anji', 'an', 'anji mito', 'anjimito', '暗慈', '御津暗慈', '裸男', '眼镜男'],
    'I-No' : ['i-no', 'in', 'ino', '伊诺'],
    'Goldlewis' : ['goldlewis', 'go', '戈德刘易斯', '戈德', '刘易斯', '胖子', '肥仔'],
    'Jack-O\'' : ['jack-o', 'jc', 'jacko', 'jko', 'jk', '婕克欧'],
    'Happy Chaos' : ['happy chaos', 'ha', 'happy', 'hc', '哈皮', '哈批', 'chaos', '手枪男'],
    'Baiken' : ['baiken', 'ba', '梅喧', '大奶人'],
    'Testament' : ['testament', 'te', '泰斯塔门特'],
    'Bridget' : ['bridget', 'br', '布丽姬', '布里姬', '伪娘', '修女', 'bi'],
    'Sin' : ['sin', 'si', '辛']
}

names = ['Sol', 'Ky', 'May', 'Axl', 'Chipp', 'Potemkin', 'Faust', 'Millia', 'Zato-1', 'Ramlethal', 'Leo', 'Nagoriyuki', 'Giovanna', 'Anji', 'I-No', 'Goldlewis', 'Jack-O\'', 'Happy Chaos', 'Baiken', 'Testament', 'Bridget', 'Sin']

short_set = set(v[1].upper() for v in tbl.values())

def get_name(string : str) -> str:
	for k, v in tbl.items():
		if string.lower() in v:
			return k
	
	return ''

def get_short_name(name : str) -> str:
	return tbl[name][1]

def get_cap_short_name(name : str) -> str:
	return tbl[name][1].upper() if name else ''

MATCHUP_URL = 'http://pc.ratingupdate.info/matchups'

def get_win_rate() -> Dict[str, Dict[str, str]]:
	r = requests.get(MATCHUP_URL)
	tree = etree.HTML(r.text) #type: ignore

	tb_str = etree.tostring(tree.xpath('/html/body/section[2]/div/div/div[1]/table')[0]).decode()

	df = pd.read_html(tb_str, encoding='utf-8', header = 0)[0]

	results = list(df.T.to_dict().values())
	
	win_rate : Dict[str, Dict[str, str]] = {}
	for v in results:
		key = get_cap_short_name(v['Unnamed: 0'])

		if key == 'BI':
			key = 'BR' # 我就觉得nm离谱

		win_rate[key] = {}
		for k, v in v.items():
			if k != 'Unnamed: 0':
				win_rate[key][k] = v

	return win_rate