from typing import Any
from collections import defaultdict


class Players(dict):
    """
    A custom dictionary subclass to manage player data, allowing for specific unpacking of values 
    upon item assignment.

    Attributes:
    ----------
    _iterable : tuple
        A tuple defining the structure of the player data, defaulting to ('position',).
    
    Methods:
    -------
    __setitem__(key: Any, value: dict) -> None
        Assigns a value to a key in the dictionary, unpacking the value before storing.
    __getitem__(key: Any) -> Any
        Retrieves the value associated with the specified key from the dictionary.
    """
    
    __slots__ = '_iterable'
    
    def __init__(self, iterable=('position',), *args, **kwargs):
        """
        Initializes a Players instance.

        Parameters:
        ----------
        iterable : tuple, optional
            A tuple defining the structure of the player data. 
            Defaults to ('position',).
        *args : variable length argument list
            Additional positional arguments to pass to the base dictionary.
        **kwargs : arbitrary keyword arguments
            Additional keyword arguments to pass to the base dictionary.
        """
        
        super(Players, self).__init__(*args, **kwargs)
        self._iterable = iterable
        
    def __setitem__(self, key: Any, value: dict) -> None:
        """
        Sets the value for a specified key in the dictionary.

        The value is unpacked using the `unpack_tables` method before assignment.

        Parameters:
        ----------
        key : Any
            The key under which the value is stored.
        value : dict
            The value to be stored, which will be unpacked before assignment.

        Returns:
        -------
        None
        """
        
        value = self.unpack_tables(value)
                
        return super().__setitem__(key, value)
    
    def __getitem__(self, key: Any) -> Any:
        """
        Retrieves the value for a specified key from the dictionary.

        Parameters:
        ----------
        key : Any
            The key whose value is to be retrieved.

        Returns:
        -------
        Any
            The value associated with the specified key.
        """
        
        return super().__getitem__(key)
    
    def unpack_tables(self, rows):
        """
        Unpacks rows of data into a structured dictionary format.

        This method processes each row and organizes the data by table names,
        allowing for easy access and manipulation of the data.

        Parameters:
        ----------
        rows : iterable
            An iterable of rows, where each row contains data for multiple tables.

        Returns:
        -------
        dict
            A dictionary where each key is a table name and each value is another 
            dictionary containing column names and their corresponding values.
        """
        
        def add_table_columns():
            """
            Adds column values from a given table instance to the structured dictionary.

            This method retrieves the values for each column in the specified table,
            handling both regular and lookup columns. It organizes the data into the
            appropriate table structure within the provided `tables` dictionary.

            Parameters:
            ----------
            table : object
                An instance of a table class containing the data to be unpacked.
            tables : defaultdict
                A defaultdict used to store the unpacked table data, organized by table names.
            """
            
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
    
    