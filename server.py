from process_data import Process
from tables import Player, PlayerInfo, Attributes, Stats, Ca, Contract, Base
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy import select, create_engine, and_
from tqdm import tqdm
from collections import defaultdict


class Setup:
    
    def __init__(self):
        pass
    
    def create_engine(self, user, password, host, database):
        """Get the SQLalchemy engine."""
        
        url = f'postgresql+psycopg2://{user}:{password}@{host}/{database}'
        engine = create_engine(url)
        return engine


class Interact:
    """Class for interacting with an SQL database using Sqlalchemy's ORM."""
    
    def __init__(self, engine, main_table='Player') -> None:
        self.engine = engine
        self.ORM_tables = {'Player': Player,
                           'playerInfo': PlayerInfo,
                           'stats': Stats,
                           'attributes': Attributes,
                           'contract': Contract,
                           'ca': Ca}
        self.main_table_name = main_table
        self.records = None
    
    def create(self):
        """Create a database."""
        
        print('Creating database')
        Base.metadata.create_all(self.engine)
        print('Database created.')
        
    def insert(self, path='data.rtf'):
        """Insert records into a database using Sqlalchemy's ORM and the
        data gathered in process_data.py."""
        
        process = Process()
        process(path)
        
        tables = ['Player', 'playerInfo', 'stats',
                  'attributes', 'contract', 'ca']
        
        with Session(self.engine) as session:
            for id in tqdm(process.data, desc='Adding datapoints to database'):
                for table in tables:
                    
                    ORM_table = self.ORM_tables[table]
                    
                    data = process.data[id][table]
                    
                    for entry in data:
                        new_entry = ORM_table(**entry)
                        
                        session.add(new_entry)
            
            print('Commiting entries...')
            session.commit()
            print('All entries commited.')

    def select(self,
               pos: str,
               mins: int,
               name: str=None,
               division: str=None,
               table_names: tuple=(),
               min_ca: int=100):
        
        """Selects records from the database and adds them to a defaultdict.
        """
        
        def ands():
            """Builds the 'AND' condition of the 'WHERE' clause."""
            
            ands = []
            ands.append(Ca.ca >= min_ca)
            ands.append(PlayerInfo.eligible == 'Yes')
            ands.append(PlayerInfo.mins >= mins)
            
            if pos:
                ands.append(PlayerInfo.position.in_(pos))
            if division:
                ands.append(PlayerInfo.division == division)
            if name:
                ands.append(Player.name == name)
                
            return and_(*ands)


        self.records = defaultdict(dict)
        
        table_names = ['Player', 'playerInfo', 'ca'] + list(table_names)
        
        with Session(self.engine) as session:

            conditions = ands()
            
            query = select(Player).join(Player._playerInfo).join(Player._ca) \
                    .options(selectinload(Player._playerInfo)) \
                    .filter(conditions)
                                
            results = session.execute(query)
            
            for row in results.mappings():
                
                UID = getattr(row['Player'], 'UID')
                
                for table_name in table_names:
            
                    self._add_records(row, table_name, UID)
                    
        return self.records


    def _add_records(self, row, table_name, UID):
        """Retrieve a record from the database and add it to the defaultdict."""
        
        def get_table():
            """Get the ORM Declarative mapping table."""
            
            if table_name == self.main_table_name:
                table = row[table_name]
            else:
                table = getattr(row[self.main_table_name], '_'+table_name)
            return table
        
        def get_data():
            if isinstance(table, InstrumentedList):
                data = self._collapse_list(table, columns)
            elif not isinstance(table, InstrumentedList):
                data = {field:getattr(table, field) for field in columns}    
            return data
                
        ORM_table = self.ORM_tables[table_name]
        columns = [table for table in vars(ORM_table) if table[0] != '_']
        
        table = get_table()        
        
        data = get_data()
                    
        self.records[UID][table_name] = data
        
    def _collapse_list(self, obj, table_fields):
        data = {}
        positions = []
        
        for obj_i in obj:
            for field in table_fields:
                
                val = getattr(obj_i, field)
                
                data[field] = val
                
                if field == 'position':
                    positions.append(val)
                
        if positions:
            data['position'] = ', '.join(positions)

        return data
