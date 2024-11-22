import re, random
from typing import Iterable, Dict, List, Tuple
from football_manager_scouting.backend.server import Setup, Interact
from football_manager_scouting.category_mappings.category_map import CATEGORY_MAP


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
                 season: int,
                 user: str,
                 password: str,
                 host: str,
                 database: str
                 ) -> None:
        """Class for preprocessing data from Football Manager."""
        
        self._season = season
        
        self.lookup_tables = {
            'division': 'division',
            'club': 'club',
            'nat': 'nat',
            'rightfoot': 'foot',
            'leftfoot': 'foot',
            'eligible': 'eligible'
        }

        engine = Setup.create_engine(user, password, host, database)
    
        interact = Interact(engine)
        self.get_lookup_id = interact.get_lookup_id
    
    def read_rtf_file(self, path: str):
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

        Yields:
        -------
        tables : dict
            A dictionary of categorized tables, where keys are categories and values are dictionaries
            of formatted column headers and associated values.
            Each dictionary corresponds to one single player.
        """

        tables: Dict[str, Dict[str, int | float | str]] = \
            {category: {} for category in set(CATEGORY_MAP.values())
             if category != "Unused"}

        with open(path, 'r', encoding='utf-8') as fhand:

            column_headers = self._get_column_headers(fhand.readline())
            
            for line in fhand:
                
                if self._is_content(line):
                    
                    line = self._format_line(line, column_headers)
                    
                    for column_header, value in line.items():
                
                        category = CATEGORY_MAP[column_header]
                        
                        if category != 'Unused':
                            column_header = self._format_header(column_header)
                            
                            
                            try:
                                tables[category][column_header] = value
                            
                            # Avoid the broken out PlayerInfo that is tuple.
                            except TypeError:
                                
                                if isinstance(tables[category], Iterable):
                                    tables[category] = {}
                                    tables[category][column_header] = value
                                else:
                                    raise TypeError
                                
                            except KeyError:
                                tables[category].setdefault(column_header, value)
        
                    self._clean(**tables)
                    
                    try:
                        
                        tables['PlayerInfo'] = self._encode_string_names(tables['PlayerInfo'])
                        
                        tables['PlayerInfo'] = self._breakout_positions(tables['PlayerInfo'])
                    except KeyError:
                        pass
                    
                    yield tables

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
    
    def _encode_positions(self, positions: list[str]) -> list[int]:
        """
        Encodes a list of string positions to unique int ids.
        """
        
        position_ids = []
        for pos in positions:
            id = self.get_lookup_id('Position', ('position', pos))
            position_ids.append(id)
        
        return position_ids
    
    def _breakout_positions(
                            self,
                            playerInfo: Dict[str, str | int]
                            ) -> Tuple[Dict[str, str | int]]:
        """
        Breaks out the position a player can play at from a string
        with multimple positions to atomic strings with one position per string.
        
        Returns a tuple containing the playerInfo dict, but with one position per dict in the tuple.
        
        Parameters:
        ----------
        playerInfo
            The playerinfo table.

        Returns:
        -------
        tables
            A tuple of dicts containing one position per dict with the other values copied.
        """
        
        positions = self._split_positions(playerInfo.pop('position'))
        
        positions = self._encode_positions(positions)
        
        tables = []
        for i in range(len(positions)):
            tables.append(playerInfo.copy())
            tables[i]['position'] = positions[i]

        return tuple(tables)

    @staticmethod
    def _split_positions(pos_string: str) -> List[str]:
        """
        Helper function for splitting Football Manager's position strings
        to something more managable.
        
        For example a position string like: 'M/AM (LC) would be split to the list: ['ML', 'MC', 'AML', 'AMC']
        """
        
        raw_positions = pos_string.split(', ')
        
        processed_positions = []
        for raw_pos in raw_positions:
            
            # Finds the lateral marker, e.g. R, C or L (right, center, left).
            lateral_markers = list(''.join(re.findall(r'\((.*?)\)', raw_pos)))
            
            # Finds the position without the lateral marker, e.g. GK, D, WB, DM, M, AM, ST
            # (Goalkeeper, Defender, Wing back, Midfielder, Attacking midfielder, Striker)
            positions = re.search(r'[A-Z]{1,2}(/([A-Z]){1,2})*', raw_pos).group(0).split('/')

            # Combines the position with the lateral marker to form positions like:
            # AM (LC) -> AML, AMC; D/M (LC) -> DL, DC, ML, MC.
            combined = []
            for pos in positions:
                if lateral_markers:
                    for lateral_marker in lateral_markers:
                        combined.append(pos+lateral_marker)
                else:
                    combined.append(pos)

            processed_positions.extend(combined)

        return processed_positions

    def _encode_string_names(self, playerInfo: Dict[str, str | int]) -> Dict[str, str | int]:
        """Encodes loose string names with int IDs.
        
        Encodes the columns that have lookup tables with int ids.
        Also updates the lookup table for new names.
        """
        
        for column, val in playerInfo.items():
            
            if self.lookup_tables.get(column):
                id = self.get_lookup_id(self.lookup_tables[column].capitalize(), 
                                                 (self.lookup_tables[column], val))
                playerInfo[column] = id
        
        return playerInfo

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
