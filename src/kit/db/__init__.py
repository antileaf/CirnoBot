import nonebot
import sqlite3 as sqlite

from typing import List, Tuple, Set, Union, Mapping

from . import subscribe as subscribe

'''
class DB:
    def __init__(self, db_name : str, types : List[Tuple[str, type]]):
        for name, t in types:
            if not t in [str, int, float]:
                raise TypeError(f'Invalid type: {t}')

        self.file = db_name
        self.types = types
        
        self.db = sqlite.connect(self.file)
        
    def __del__(self):
        self.db.close()
    
    def type_check(self, data : List[Union[str, int, float]] | Mapping[str, Union[str, int, float]]):
        if len(data) != len(self.types):
            return False

        if isinstance(data, Mapping):
            for k, t in self.types:
                if not k in data or not isinstance(data[k], t):
                    return False
        
        else:
            for i, t in enumerate(data):
                if not isinstance(t, self.types[i][1]):
                    return False
        
        return True
        
    def add(self, data : List[Union[str, int, float]] | Mapping[str, Union[str, int, float]]):
        if not self.type_check(data):
            raise TypeError(f'Invalid type: expected {self.types}')
        
        self.db.execute('INSERT INTO data VALUES ({})'.format(', '.join(['?'] * len(self.types))), data)
        self.db.commit()
    
    def remove(self, data : List[Union[str, int, float]] | Mapping[str, Union[str, int, float]]):
        if not self.type_check(data):
            raise TypeError(f'Invalid type: expected {self.types}')
        
        self.db.execute('DELETE FROM data WHERE {}'.format(' AND '.join([f'{k} = ?' for k, _ in self.types])), data)
        self.db.commit()
'''