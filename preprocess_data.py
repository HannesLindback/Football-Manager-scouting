import re, random, itertools, json
from collections import defaultdict
from typing import Generator, Iterable, Dict, List, Tuple


class Preprocess:
    
    CORRECT_COLUMN_HEADERS =  \
            {
            'aer a/90': 'aerA',
            'hdrs w/90': 'hdrsW',
            'blk/90': 'blk',
            'clr/90': 'clr',
            'tck/90': 'tckC',
            'pres a/90': 'presA',
            'pres c/90': 'presC',
            'int/90': 'interceptions',
            'sprints/90': 'sprints',
            'poss lost/90': 'possLost',
            'poss won/90': 'possWon',
            'drb/90': 'drb',
            'op-crs a/90': 'opCrsA',
            'op-crs c/90': 'opCrsC',
            'ps a/90': 'psA',
            'ps c/90': 'psC',
            'pr passes/90': 'prPasses',
            'op-kp/90': 'opKp',
            'ch c/90': 'chC',
            'xa/90': 'xa',
            'shot/90': 'shot',
            'sht/90': 'sht',
            'np-xg/90': 'npXg',
            'dec': 'decisions',
            '1v1': 'oneVsOne',
            'l th': 'lth',
            'natf': 'natF',
            'right foot': 'rightfoot',
            'left foot': 'leftfoot',
            'begins': 'beginDate',
            'expires': 'expiryDate',
            'opt ext by club': 'extension',
            'min fee rls': 'releaseClauseFee',
            'str': 'strength'
            }
    
    def __init__(self,
                 season: int = None,
                 division_id: int = 0,
                 club_id: int = 0,
                 nat_id: int = 0) -> None:
        """Class for preprocessing a Football Manager rtf-file."""
        
        self._id: Generator[int] = (i for i in itertools.count())
        self._season             = season
        
        self.lookup_tables = {
            'Division': {},
            'Club': {},
            'Nat': {},
        }
        self._lookup_tables_of_player = defaultdict(dict)
        self.Position      = {pos: id for id, pos in enumerate('GK DC DR DL WBR DM WBL MR MC ML AMR AMC AML STC'.split())}
        self.Foot          = {'-': 0, 'Very Weak': 1, 'Weak': 2, 'Reasonable': 3, 'Fairly Strong': 4, 'Strong': 5, 'Very Strong': 6}
        self.Eligible      = {'No': 0, 'Yes': 1}
        
        self._Division_id: Generator[int]  = (i+division_id for i in itertools.count())
        self._Club_id: Generator[int]      = (i+club_id for i in itertools.count())
        self._Nat_id: Generator[int]       = (i+nat_id for i in itertools.count())
        
    def __call__(self, path: str, json_path: str):
        """
        Preprocesses the data of an RTF file generated from Football Manager.
        
        The file is assumed to be of the raw format directly from FM,
        where all data points are divided into cells separated with |
        and each row is separated by one line like: | -- |. The first row should
        consist of headers with the name of the category.
        
        Needs a JSON file mapping the each header to a wider category.
        E.g. xA/90 -> Stats and cor -> Attributes.
        
        Processes the RTF file, categorizes data based on the given JSON mapping,
        and yields the structured tables for one row, corresponding to the information of one player.

        Parameters:
        ----------
        path : str
            The file path to the RTF file containing the FM data.
        json_path : str
            The file path to a JSON file containing the mapping of column headers to data categories.
            NOTE: Removing individual mappings will almost definitely cause errors.
                  Only remove entire categories at once! Adding things is fine though.

        Yields:
        -------
        tuple
            A tuple containing:
            - tables : dict
                A dictionary of categorized tables, where keys are categories and values are dictionaries
                of formatted column headers and associated values.
                Each dictionary corresponds to one single player.
            - lookup_tables : dict
                A dictionary of lookup tables, generated based on specific "PlayerInfo" processing rules.
                A bit clunky. Should be rewritten.

        Notes:
        ------
        - The function loads a category mapping from the specified JSON file.
        - Tables are initialized based on unique categories, excluding "Unused" entries.
        - Special handling is applied to 'PlayerInfo' for encoding lookup tables and processing positional data.
        """
        
        with open(json_path) as json_file:
            category_map = json.load(json_file)
        
        tables: Dict[str, dict] = {category: {} for category in set(category_map.values())
                                   if category != "Unused"}
        
        for line in self._read_rtf_file(path):
            
            for column_header, value in line.items():
                
                category = category_map[column_header]
                
                if category != 'Unused':
                    column_header = self._format_header(column_header)
                    
                    try:
                        tables[category][column_header] = value
                    
                    except TypeError:
                        
                        if isinstance(tables[category], Iterable):
                            tables[category] = {}
                            tables[category][column_header] = value
                        else:
                            raise TypeError
                        
                    except KeyError:
                        tables[category].setdefault(column_header, value)
        
            self._clean(**tables)
        
            if 'PlayerInfo' in tables:
                tables['PlayerInfo'].update(self._encode_lookup_tables(tables['PlayerInfo']))
                tables['PlayerInfo'] = self._breakout_positions(tables['PlayerInfo'])
            
            lookup_tables = dict(self._lookup_tables_of_player)
            self._lookup_tables_of_player = defaultdict(dict)
        
            yield tables, lookup_tables
    
    def _read_rtf_file(self, path: str):
        """
        Reads content from a RTF file generated from Football Manager.
        Extracts column headers, and processes each line to yield formatted content.

        Parameters:
        ----------
        path : str
            The file path to the RTF document to be read.

        Yields:
        -------
        str
            A formatted line of content from the RTF file after applying necessary transformations.
        """

        with open(path, 'r', encoding='utf-8') as fhand:

            column_headers = self._get_column_headers(fhand.readline())
            
            for line in fhand:
                
                if self._is_content(line):
                    
                    line = self._format_line(line, column_headers)
                    
                    yield line
                    

    def _clean(self,
               Player: Dict[str, str] = None,
               PlayerInfo: Dict[str, str] = None,
               Stats: Dict[str, str] = None,
               Attributes: Dict[str, str] = None,
               Contract: Dict[str, str] = None,
               Ca: Dict[str, str] = None) -> None:
        """
        Cleans and formats data within specified tables (dictionaries) to ensure consistent data types
        and structures for further processing.

        Parameters:
        ----------
        Player : dict, optional
            Dictionary containing player-specific data.
        PlayerInfo : dict, optional
            Dictionary with player information, including age, position, and minutes played.
        Stats : dict, optional
            Dictionary of player statistics, where keys are stat names and values are numbers.
        Attributes : dict, optional
            Dictionary for general attributes related to the player.
        Contract : dict, optional
            Dictionary containing player contract details, such as wage, value, and contract dates.
        Ca : dict, optional
            Dictionary containing player "ca" (current ability) details.

        Returns:
        -------
        dict
            The cleaned dictionaries with updated data values as per specified formatting rules.
        """
        
        def clean_player_table():
            try:
                Player['season'] = self._season
            except KeyError:
                pass
            
        def clean_playerInfo_table():
            try:
                PlayerInfo['age']        = int(PlayerInfo['age'])
            except KeyError:
                pass
            
            try:
                PlayerInfo['position']   = self._split_positions(PlayerInfo['position'])
            except KeyError:
                pass
            
            try:
                PlayerInfo['mins']       = self._make_int(PlayerInfo['mins']) \
                                           if PlayerInfo['mins'] != '-' else 0
            except KeyError:
                pass
            
        def clean_stats_table():
            for key, val in Stats.items():
                Stats[key] = float(val) if val != '-' else 0.0
            
        def clean_contract_table():
            try:
                Contract['beginDate']        = int(Contract['beginDate'][-4:]) \
                                               if Contract['beginDate'] != '-' else 0
            except KeyError:
                pass
            
            try:
                Contract['expiryDate']       = int(Contract['expiryDate'][-4:]) \
                                               if Contract['expiryDate'] != '-' else 0
            except KeyError:
                pass
            
            try:
                Contract['extension']        = int(Contract['extension']) \
                                               if Contract['extension'] != '' else 0
            except KeyError:
                pass
            
            try:
                Contract['wage']             = self._make_int(Contract['wage']) \
                                               if Contract['wage'] != '-' and Contract['wage'] != 'N/A' else 0
            except KeyError:
                pass
            
            try:
                Contract['value']            = self._obfuscate_asking_price(
                                               self._format_high_values(Contract['ap']))
            except KeyError:
                pass
            
            try:
                Contract['releaseClauseFee'] = self._format_high_values(Contract['releaseClauseFee']) \
                                               if Contract['releaseClauseFee'] != '-' else 0
            except KeyError:
                pass
            
            try:
                del Contract['ap']
            except KeyError:
                pass
            
        def clean_ca_table():
            try:
                Ca['ca'] = int(Ca['ca'])
            except KeyError:
                pass

        if Player:
            clean_player_table()
        if PlayerInfo:
            clean_playerInfo_table()
        if Stats:
            clean_stats_table()
        if Contract:
            clean_contract_table()
        if Ca:
            clean_ca_table()
             
    @staticmethod
    def _split_positions(pos_string: str) -> List[str]:
        """Helper function for splitting Football Manager's position strings
        to something more managable.
        
        Example:
            arg:
                pos_string: str = 'M/AM (LC)
            returns:
                processed_positions: list = ['ML', 'MC', 'AML', 'AMC']"""
            
        raw_positions = pos_string.split(', ')
        processed_positions = []

        for raw_pos in raw_positions:
            sides = list(''.join(re.findall(r'\((.*?)\)', raw_pos)))
            positions = re.search(r'[A-Z]{1,2}(/([A-Z]){1,2})*', raw_pos).group(0).split('/')

            combined = []
            for pos in positions:
                if sides:
                    for side in sides:
                        combined.append(pos+side)
                else:
                    combined.append(pos)

            processed_positions.extend(combined)

        return processed_positions

    @staticmethod
    def _breakout_positions(table: Dict[str, str | int])-> Tuple[Dict[str, str | int]]:
        """If a player can play at several positions,
        breaks out the list of positions so that there is one position per row."""
        
        new_tables = []
        for i in range(len(table['position'])):
            new_table = table.copy()
            new_table['position'] = table['position'][i]
            new_tables.append(new_table)

        return tuple(new_tables)

    def _encode_lookup_tables(self, tables: Dict[str, str | int]) -> Dict[str, int]:
        """
        Encodes the provided tables dictionary by mapping each value to a unique ID
        and updates lookup tables accordingly.
        
        The database should not contain free text except for names etc. Therefore this 
        function replaces club, division, positions eligibility and footedness with an ID.

        Parameters:
        ----------
        tables : dict
            Dictionary where keys are table names and values are either strings or integers representing
            data entries for each table.

        Returns:
        -------
        tables
            The modified tables dictionary with values replaced by their corresponding encoded IDs
            based on predefined lookup mappings.

        Notes:
        ------
        - Each table entry is processed based on its type:
        - `position`: Converted to a list of position IDs.
        - `rightfoot` and `leftfoot`: Mapped to IDs from the `Foot` lookup.
        - `eligible`: Mapped to IDs from the `Eligible` lookup.
        - All other tables: Processed with `add_column_id` to assign unique IDs from
            a lookup table and update `self._lookup_tables_of_player`.
        - Helper functions within `_encode_lookup_tables` include:
        - `add_column_id`: Adds a unique column ID for values not already in the lookup table.
        - `add_position_id`: Maps a list of positions to corresponding position IDs.
        """
        
        def add_column_id(val: str, table_name: str) -> int:
            """Returns the row id of the given column."""

            if self.lookup_tables.get(table_name) is not None:
                
                if not val in self.lookup_tables[table_name]:
                    id = next(getattr(self, f'_{table_name}_id'))

                    self.lookup_tables[table_name][val] = id
                    self.lookup_tables[table_name][table_name.lower()] = val
                    self.lookup_tables[table_name]['id'] = id

                    self._lookup_tables_of_player[table_name][table_name.lower()] = val
                    self._lookup_tables_of_player[table_name]['id'] = id

                return self.lookup_tables[table_name][val]
        
        def add_position_id(positions: list[str]) -> list[int]:
            """Returns the position ids for the positions in the row."""
            
            return [self.Position[pos] for pos in positions]
    
        for table in tables:
            if table == 'position':
                val = add_position_id(tables[table])
            elif table in {'rightfoot', 'leftfoot'}:
                val = self.Foot[tables[table]]
            elif table == 'eligible':
                val = self.Eligible[tables[table]]
            else:
                val = add_column_id(tables[table], table.capitalize())
            
            if val is not None:
                tables[table] = val
        
        return tables

    @staticmethod
    def _format_high_values(val: str) -> float:
        """Helper function for formatting raw values.
        
        Example:
            arg:
                val: str = '41M\xa0kr'
            returns:
                float = 41000000.0"""
                
        letter = '\xa0k'
        n = 1
        if 'K' in val:
            n = 1000
            letter = 'K'
        elif 'M' in val:
            n = 1000000
            letter = 'M'
        elif 'B' in val:
            n = 1000000000
            letter = 'B'
        
        return float(val[:val.find(letter)]) * n
    
    @staticmethod
    def _obfuscate_asking_price(asking_price: int, n=2) -> int:
        """Revealing the asking price of a player directly would make the game
        too easy. This method sets the asking price to a random number within
        a range of the true number."""
        
        obfuscated = round(random.randrange(int(asking_price/n),
                                            int(asking_price*n))) \
                     if asking_price != 0 else 0
                     
        return int(obfuscated)

    @staticmethod
    def _make_int(val) -> int:
        """Helper method for making ints of string values with unicode chars."""
        return int(''.join(re.findall(r'\d+', val)))
    
    @staticmethod
    def _clean_line(line: str) -> list[str]:
        """Returns a list with the elements in the line."""
        
        return line.strip().rstrip('\n').strip('|').split('|')
    
    @staticmethod
    def _is_content(line: str) -> bool:
        """Returns True if line is content. I.e. not row border or blankspace."""
        
        return line != '\n' and line[3] != '-'
    
    def _format_line(self, line: str, column_headers: list[str]) -> dict[str, str]:
        """Returns a dict with the column header as key and the cell content as value."""
        
        line = {column_header: elem.strip()
                for column_header, elem in
                zip(column_headers, self._clean_line(line))}
        return line

    def _get_column_headers(self, header_line: str) -> list[str]:
        """Returns a list of all headers in file."""
        
        return [header.strip() for header in self._clean_line(header_line)]

    def _format_header(self, header: str) -> str:
        """Returns a formatted header that is valid for SQL"""
        
        return self.CORRECT_COLUMN_HEADERS.get(header.lower(), header.lower())
