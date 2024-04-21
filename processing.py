from collections import defaultdict
from server import Interact
from server import Setup, Interact


class Process:
    """Class for processing and categorizing the data."""
    
    def __init__(self, user, password, port, database):
        setup = Setup()
        engine = setup.create_engine(user,
                                     password,
                                     port,
                                    database=database)
        self.interact = Interact(engine)
    
    def __call__(self, stat_cat, attr_cat, position, mins, tables):
        """Retrieves data from the SQL-database."""
        
        print('Retrieving requested records...')
        
        data = self.interact.select(table_names=tables,
                                    pos=position,
                                    mins=mins)
        
        data = self._get_category_data(data, stat_cat, attr_cat)
        
        all_stats = self._get_all_stats(data)
        
        header = [header if header != 'mins' else '90s' 
                  for header in self._get_header(data)]
        return data, all_stats, header
    
    def _get_category_data(self, data, stat_cat, attr_cat):
        
        for UID, record in data.items():
            stats = {}
            attributes = {}
            
            for stat, value in record['stats'].items():
                if stat in stat_cat:
                    stats[stat] = value
            data[UID]['stats'] = stats
            
            for attr, value in record['attributes'].items():
                if attr in attr_cat:
                    attributes[attr] = value
            data[UID]['attributes'] = attributes
        
        return data
    
    def _get_all_stats(self, data):
        all_stats = []
        
        for record in data.values():
            all_stats.append(list(record['stats'].values()))
        
        return all_stats
    
    def _get_header(self, data):
        header = []
        for entry in data.values():
            for table_name in entry.values():
                header.extend(list(table_name.keys()))
            return header
