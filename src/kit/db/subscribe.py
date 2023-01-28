import os
import sqlite3 as sqlite

from typing import List, Tuple, Set, Union, Mapping

class Subscribe:
    ANY_ID = -1
    ANY_CONTENT = '-1'
    ANY_EXTRA = ''
    ANY_VALUES = (ANY_ID, ANY_CONTENT, ANY_EXTRA)
    COLUMN_NAMES = ('id', 'content', 'extra')

    def __init__(self, db_name : str):
        self.file = os.path.join('database', db_name)

        if not os.path.exists(self.file):
            self.db = sqlite.connect(self.file)
            self.db.execute('CREATE TABLE data (id INTEGER, content TEXT, extra TEXT)')
            self.db.commit()
        else:
            self.db = sqlite.connect(self.file)
            
        
    def __del__(self):
        self.db.close()


    def add(self, data : Tuple[int, str, str] | Tuple[int, str]):
        if len(data) == 2:
            data = (data[0], data[1], '')
        
        self.db.execute('INSERT INTO data VALUES (?, ?, ?)', data)
        self.db.commit()

    
    def eval_specifier(self, data : Tuple[int, str, str] | Tuple[int, str] | Mapping[str, Union[int, str]]) -> Tuple[int, str, str]:
        if isinstance(data, Mapping):
            # if len(data) == 0:
            #     raise ValueError('Please specify at least one value')
            
            return tuple(data.get(name) if name in data else any_value for name, any_value in zip(self.COLUMN_NAMES, self.ANY_VALUES)) # type: ignore baka!

        elif len(data) == 2:
            return (data[0], data[1], self.ANY_EXTRA)
        
        else:
            return data

    
    def remove(self, specifier : Tuple[int, str, str] | Tuple[int, str] | Mapping[str, Union[int, str]]):
        specifier = self.eval_specifier(specifier)

        specs : List[str] = []
        params = []
        for name, any_value, value in zip(self.COLUMN_NAMES, self.ANY_VALUES, specifier):
            if value != any_value:
                specs.append(f'{name} = ?')
                params.append(value)
        
        if len(specs) == 0:
            raise ValueError('Please specify at least one value')

        self.db.execute('DELETE FROM data WHERE ' + ' AND '.join(specs), params)
        self.db.commit()
    
    def query(self, specifier : Tuple[int, str, str] | Tuple[int, str] | Mapping[str, Union[int, str]]) -> List[Tuple[int, str, str]]:
        specifier = self.eval_specifier(specifier)

        specs : List[str] = []
        params = []
        for name, any_value, value in zip(self.COLUMN_NAMES, self.ANY_VALUES, specifier):
            if value != any_value:
                specs.append(f'{name} = ?')
                params.append(value)
        
        # if len(specs) == 0:
        #     raise ValueError('Please specify at least one value')

        if len(specs) == 0:
            return self.db.execute('SELECT * FROM data').fetchall()
        
        return self.db.execute('SELECT * FROM data WHERE ' + ' AND '.join(specs), params).fetchall()

        # with open('log.txt', 'w') as f:
        #     f.write(str(lst))
    
    def __contains__(self, specifier : Tuple[int, str, str] | Tuple[int, str] | Mapping[str, Union[int, str]]) -> bool:
        return len(self.query(specifier)) > 0