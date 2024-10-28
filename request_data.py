from collections import defaultdict
from server import Setup, Interact
from player import Players
from tables import Player, Division, Club, Nat
from errors import NoPlayerFoundError


class Request:

    def __init__(self) -> None:
        self.players = Players()

    def connect(self, user, password, port, database):
        engine = Setup.create_engine(user,
                                    password,
                                    port,
                                    database=database)
        
        return Interact(engine)

    def fetch_all(self, filter={}, login={},
                  connection=None):
        connection = self._get_connection_if_none(login, connection)
        
        print('Retrieving records from database...')
        
        for uid, tables in connection.select(**filter):
            self.players[uid] = tables
        
        return self.players
    
    def iterator(self, filter={}, login={},
                 connection=None):
        connection = self._get_connection_if_none(login, connection)
        
        print('Retrieving records from database...')
        
        for _, tables in connection.select(**filter):
            yield self.players.unpack_tables(tables)
    
    def fetch_lookup_tables(self, connection):
        print('Retrieving lookup tables IDs...')
        
        tables = defaultdict(dict)
        for _, row in connection.select(**{'columns': (Player, Division, Club, Nat)}):
            (division, club, nat) = row[0]
            tables['Division'][division.division] = division.id
            tables['Club'][club.club] = club.id
            tables['Nat'][nat.nat] = nat.id
            breakpoint
                
        return tables
    
    def _get_connection_if_none(self, login, connection):
        return connection if connection else self.connect(**login)
            