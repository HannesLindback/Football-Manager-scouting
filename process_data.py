import re
import random
import json
from collections import defaultdict
import itertools

class Process:

    def __init__(self):
        """Processes an rtf-file containing information and statistics
        on player from Football manager."""
        
        self.data = defaultdict(lambda: defaultdict(list))

        self.id = (i for i in itertools.count())
    
    def __call__(self, path, stats_range=(0,22), attr_range=(23,69),
                 ctr_range=(70,75), nat_team_range=(76,78), ca_range=(79,79),
                 player_range=(80,81), info_range=(82,91)):
        """Iterates through the file.
        
        Cleans data, groups the values into different categories and adds them
        to a defaultdict which can later be used to add data to a database."""
        
        with open(path, 'r', encoding='utf-8') as fhand:
            for _ in range(8): fhand.readline()
            
            headers = [header.strip() for header in fhand.readline().split('|')][1:-3]
            
            for line in fhand:
                if line != '\n' and line[3] != '-':
                    line        = line.rstrip('\n').split('|')[1:-3]
                    
                    player      = self.group_values(headers, line, player_range)
                    player_info = self.group_values(headers, line, info_range)
                    stats       = self.group_values(headers, line, stats_range)
                    attributes  = self.group_values(headers, line, attr_range)
                    ctr         = self.group_values(headers, line, ctr_range)
                    ca          = self.group_values(headers, line, ca_range)
                    
                    self.add_data(player, player_info, stats, attributes,
                               ctr, ca, id=next(self.id))
    
    def group_values(self, headers, line, range):
        """Groups values into categories."""
        
        correct_headers =  {'aer a/90': 'aerA',
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
                            'uid': 'UID',
                            'right foot': 'rightFoot',
                            'left foot': 'leftFoot',
                            'begins': 'beginDate',
                            'expires': 'expiryDate',
                            'opt ext by club': 'extension',
                            'min fee rls': 'releaseClauseFee',
                            'str': 'strength'}
        
        group = {correct_headers.get(header.lower(), header.lower()):val.strip()
                 for header, val in zip(headers[range[0]:range[1]+1],
                                        line[range[0]:range[1]+1])}
        return group
    
    def add_data(self, *group, id):
        """Adds data to the dict."""
        
        table_names = ('Player', 'playerInfo', 'stats',
                       'attributes', 'contract', 'ca')
                
        for dirty_group, table_name in zip(group, table_names):
            cleaned_group = self._clean(dirty_group, table_name, id)

            if cleaned_group.get('position', None):
                cleaned_group = self._breakout_positions(cleaned_group)

            if not isinstance(cleaned_group, list):
                self.data[id][table_name].append(cleaned_group)
            else:
                self.data[id][table_name].extend(cleaned_group)
            
    def _clean(self, group, group_name, id):
        """Explicitly cleans the raw data into a better format for storing in the database."""
        
        if group_name == 'Player':
            group['_id'] = id
            
        elif group_name == 'ca':
            group['ca'] = int(group['ca'])
            
            group['_playerID'] = id
            
        elif group_name == 'contract':
            group['beginDate'] = int(group['beginDate'][-4:]) \
                                 if group['beginDate'] != '-' else 0
                
            group['expiryDate'] = int(group['expiryDate'][-4:]) \
                                  if group['expiryDate'] != '-' else 0
                
            group['extension'] = int(group['extension']) \
                                 if group['extension'] != '' else 0

            group['wage'] = self._make_int(group['wage']) \
                            if group['wage'] != '-' and group['wage'] != 'N/A' else 0
            
            group['value'] = self._obfuscate(self._format_high_values(group['ap']))
            
            del group['ap']
            
            group['releaseClauseFee'] = self._format_high_values(group['releaseClauseFee']) \
                                      if group['releaseClauseFee'] != '-' else 0
                                             
            group['_playerID'] = id
            
        elif group_name == 'playerInfo':
            group['age'] = int(group['age'])
            
            group['position'] = self._split_positions(group['position'])
            
            group['mins'] = self._make_int(group['mins']) \
                            if group['mins'] != '-' else 0
            
            group['_playerID'] = id
            
        elif group_name == 'nat_team':
            group['team'] = int(group['team']) \
                            if group['team'] != '' else 0
            
            group['caps'] = int(group['caps']) \
                            if group['caps'] != '-' else 0
            
            group['yth apps'] = int(group['yth apps']) \
                                if group['yth apps'] != '-' else 0
            
            group['_playerID'] = id
            
        elif group_name == 'stats':
            for key, val in group.items():
                group[key] = float(val) \
                             if val != '-' else 0.0
                
            group['_playerID'] = id
            
        elif group_name == 'attributes':
            group['natF'] = group['nat']
            
            del group['nat']
            
            group['_playerID'] = id
            
        return group
            
    def _split_positions(self, position_indicator):
        raw_positions = position_indicator.split(', ')
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
        
    def _format_high_values(self, val: str):
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
        
    def _obfuscate(self, val):
        return round(random.randrange(int(val/2), int(val*2))) if val != 0 else 0

    def _breakout_positions(self, group):
        new_dict = []
        for i, pos in enumerate(group['position']):
            tempdict = group.copy()
            tempdict['position'] = pos
            new_dict.append(tempdict)
        return new_dict
    
    def _make_int(self, val):
        return int(''.join(re.findall(r'\d+', val)))

if __name__ == '__main__':
    path = 'data.rtf'
    process = Process()
    process._split_positions('GK')
    process(path, season='26-27', primary_key='player')
    x = process.player_data['43298994']['player']['name']
    breakpoint
