from typing import Any
from collections import defaultdict


class Players(dict):

    __slots__ = '_iterable'
    
    def __init__(self, iterable=('position',), *args, **kwargs):
        super(Players, self).__init__(*args, **kwargs)
        self._iterable = iterable
        
    def __setitem__(self, key: Any, value: dict) -> None:
        value = self.unpack_tables(value)
                
        return super().__setitem__(key, value)
    
    def __getitem__(self, key: Any) -> Any:
        return super().__getitem__(key)
    
    def unpack_tables(self, rows):
        
        def add_table_columns():
            table_name = table.__tablename__[0].upper() + table.__tablename__[1:]
            
            get_column_value = lambda table, col_name: getattr(table, col_name, None)
            
            get_lookup_column_value = lambda table, col_name: \
                getattr(getattr(table, col_name.capitalize()), col_name)
                
            get_lookup_column_value_with_annoying_name = lambda table, col_name: \
                getattr(getattr(table, col_name.capitalize()), 'foot')
            
            lookup_tables = set([attr.lower() for attr in dir(table) if attr[0].isupper()])
            
            col_names = [col_name for col_name in table.__table__.columns.keys()
                         if not col_name.startswith('_')]
            
            for col_name in col_names:
                
                if col_name in lookup_tables:
                    
                    try:
                        val = get_lookup_column_value(table, col_name)
                    
                    except AttributeError:
                        val = get_lookup_column_value_with_annoying_name(table, col_name)
                
                else:
                    val = get_column_value(table, col_name)
                
                if col_name in self._iterable:
                    iterable_value = tables[table_name].get(col_name, [])
                    val = iterable_value + [val]
                
                tables[table_name][col_name] = val  
                    
        tables = defaultdict(dict)
        for row in rows:
            for table in row:
                add_table_columns()
                
        return dict(tables)
        