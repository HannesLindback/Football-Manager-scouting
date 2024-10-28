import re
import random
from collections import defaultdict
import itertools
from typing import Generator


class Preprocess:
    
    def __init__(self,
                 season: int = None,
                 division_id: int = 0,
                 club_id: int = 0,
                 nat_id: int = 0) -> None:
        
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
        
        ##############################
        #Todo: Ta bort:
        # self.Division      = {}
        # self.Club          = {}
        # self.Nat           = {}
        ##############################
        
        self._Division_id: Generator[int]  = (i+division_id for i in itertools.count())
        self._Club_id: Generator[int]      = (i+club_id for i in itertools.count())
        self._Nat_id: Generator[int]       = (i+nat_id for i in itertools.count())
        
    def __call__(self, **kwds: dict[dict]) -> dict:
        tables = kwds
    
        if 'PlayerInfo' in tables:
            tables['PlayerInfo'].update(self._encode_lookup_tables(tables['PlayerInfo']))
            tables['PlayerInfo'] = self._breakout_positions(tables['PlayerInfo'])
            
        lookup_tables = self._lookup_tables_of_player
        self._lookup_tables_of_player = defaultdict(dict)

        return tables, lookup_tables
    
    def from_rtf_file(self, path: str, stats_range=(0,22), attr_range=(23,69),
                  ctr_range=(70,75), nat_team_range=(76,78), ca_range=(79,79),
                  player_range=(80,81), info_range=(82,91)):
        """Reads an rtf-file of players from Football Manager.
        Cleans and structures each row, where one row = one player.
        
        Args:
            path (str): Path to  rtf-file of players from Football Manager.

        Yields:
            tables (dict): A dict with formatted tables per category.
        """
        
        with open(path, 'r', encoding='utf-8') as fhand:
            for _ in range(8): fhand.readline()
            
            headers = [header.strip()
                       for header in fhand.readline().split('|')][1:-3]
            
            for line in fhand:
                if line != '\n' and line[3] != '-':
                    line        = line.rstrip('\n').split('|')[1:-3]
                    
                    tables = \
                        {
                            'Player': self._format_tables(headers, line, player_range),
                            'PlayerInfo': self._format_tables(headers, line, info_range),
                            'Stats': self._format_tables(headers, line, stats_range),
                            'Attributes': self._format_tables(headers, line, attr_range),
                            'Contract': self._format_tables(headers, line, ctr_range),
                            # 'NatTeam': self._format_tables(headers, line, nat_team_range),
                            'Ca': self._format_tables(headers, line, ca_range)
                            }
                    
                    yield self._clean(**tables)

    def _clean(self, Player: dict=None, PlayerInfo: dict=None,
                Stats: dict=None, Attributes: dict=None,
                Contract: dict=None, Ca: dict=None) -> dict:
            """Cleans the values of all tables of one player."""
            
            def clean_player_table():
                # Player['_id']    = id
                Player['season'] = self._season
            
            def clean_playerInfo_table():
                PlayerInfo['age']        = int(PlayerInfo['age'])
                
                PlayerInfo['position']   = self._split_positions(PlayerInfo['position'])
                # PlayerInfo['division']   = self._add_column_id(PlayerInfo['division'], 'Division')
                # PlayerInfo['club']       = self._add_column_id(PlayerInfo['club'], 'Club')
                # PlayerInfo['nat']        = self._add_column_id(PlayerInfo['nat'], 'Nat')
                # PlayerInfo['rightfoot']  = self.Foot[PlayerInfo['rightfoot']]
                # PlayerInfo['leftfoot']   = self.Foot[PlayerInfo['leftfoot']]
                # PlayerInfo['eligible']   = self._add_column_id(PlayerInfo['eligible'], 'Eligible')
                
                PlayerInfo['mins']       = self._make_int(PlayerInfo['mins']) \
                                           if PlayerInfo['mins'] != '-' else 0
                # PlayerInfo['_playerID']  = id
                
            def clean_stats_table():
                for key, val in Stats.items():
                    Stats[key] = float(val) if val != '-' else 0.0
                # Stats['_playerID'] = id
                
            def clean_contract_table():
                Contract['beginDate']        = int(Contract['beginDate'][-4:]) \
                                               if Contract['beginDate'] != '-' else 0
                Contract['expiryDate']       = int(Contract['expiryDate'][-4:]) \
                                               if Contract['expiryDate'] != '-' else 0
                Contract['extension']        = int(Contract['extension']) \
                                               if Contract['extension'] != '' else 0
                Contract['wage']             = self._make_int(Contract['wage']) \
                                               if Contract['wage'] != '-' and Contract['wage'] != 'N/A' else 0
                Contract['value']            = self._obfuscate_asking_price(self._format_high_values(Contract['ap']))
                Contract['releaseClauseFee'] = self._format_high_values(Contract['releaseClauseFee']) \
                                               if Contract['releaseClauseFee'] != '-' else 0
                # Contract['_playerID']        = id
                del Contract['ap']
                
            def clean_attributes_table():
                Attributes['natF'] = Attributes['nat']
                del Attributes['nat']
                # Attributes['_playerID'] = id
                
            def clean_ca_table():
                Ca['ca'] = int(Ca['ca'])
                # Ca['_playerID'] = id

            if Player:
                clean_player_table()
            if PlayerInfo:
                clean_playerInfo_table()
            if Stats:
                clean_stats_table()
            if Contract:
                clean_contract_table()
            if Attributes:
                clean_attributes_table()
            if Ca:
                clean_ca_table()
            
            args = locals()
            return {arg:val for arg, val in args.items() if isinstance(val, dict)}

    @staticmethod
    def _format_tables(columns: list[str],
                       line: list[str],
                       range: tuple[int]) -> dict:
        """Helper method for formatting tables when reading from rtf-file.
        Formats tables to dicts with column names as key.
        Fix the column names of the raw data so that they are valid for SQL."""
        
        correct_column_names =  \
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
            'right foot': 'rightfoot',
            'left foot': 'leftfoot',
            'begins': 'beginDate',
            'expires': 'expiryDate',
            'opt ext by club': 'extension',
            'min fee rls': 'releaseClauseFee',
            'str': 'strength'
            }
        
        table = {correct_column_names.get(column.lower(), column.lower()):val.strip()
                    for column, val in zip(columns[range[0]:range[1]+1],
                                        line[range[0]:range[1]+1])}
        return table
    
    @staticmethod
    def _split_positions(pos_string: str):
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
    def _breakout_positions(table: dict) -> tuple:
        """If a player can play at several positions,
        breaks out the list of positions so that there is one positions per row."""
        
        new_tables = []
        for i in range(len(table['position'])):
            new_table = table.copy()
            new_table['position'] = table['position'][i]
            new_tables.append(new_table)

        return tuple(new_tables)

    def _encode_lookup_tables(self, tables: dict) -> dict:
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


if __name__ == '__main__':
    path = 'data.rtf'
    process = Preprocess(season=27)
    for row in process.from_rtf_file(path):
        process(**row)
