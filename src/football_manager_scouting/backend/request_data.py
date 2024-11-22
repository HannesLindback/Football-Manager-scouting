from collections import defaultdict
from football_manager_scouting.backend.server import Setup, Interact
from football_manager_scouting.backend.player import Players
from football_manager_scouting.backend.tables import Player, Division, Club, Nat
from typing import Dict


class Request:
    """
    A class to handle database requests related to player data.

    Provides methods to connect to a database, fetch player data, 
    and retrieve lookup tables for various attributes such as division, club, 
    and nationality. Uses the `Players` class to organize and store the 
    player records retrieved from the database.
    """

    def __init__(self,
                 user: str,
                 password: str,
                 host: str,
                 database: str) -> None:
        """
        Initializes the Request object and creates an instance of Players.

        Attributes
        ----------
        players : Players
            An instance of the Players class to store player records.
        """
        
        self.players = Players()
        engine = Setup.create_engine(user, password, host, database)
        self.connection = Interact(engine)

    def fetch_all(self,
                  filter={}) -> Players:
        """
        Retrieves all player records from the database based on the given filter.

        This method retrieves records and stores them in the players attribute.

        Parameters
        ----------
        filter : dict, optional
            A dictionary of filters to apply when retrieving records.
        login : dict, optional
            A dictionary containing login credentials if the connection is not provided.
        connection : Interact, optional
            An existing database connection. If None, a new connection will be established.

        Returns
        -------
        Players
            An instance of the Players class containing all fetched player records.
        """
        
        print('Retrieving records from database...')
        
        for uid, tables in self.connection.select(**filter):
            self.players[uid] = tables
        
        return self.players
    
    def iterator(self,
                 filter={},
                 ):
        """
        Returns an iterator for fetching player records from the database.

        This method retrieves records one at a time, yielding unpacked player 
        data using the unpack_tables method.

        Parameters
        ----------
        filter : dict, optional
            A dictionary of filters to apply when retrieving records.
        login : dict, optional
            A dictionary containing login credentials if the connection is not provided.
        connection : Interact, optional
            An existing database connection. If None, a new connection will be established.

        Yields
        ------
        dict
            An unpacked dictionary of player data for each record retrieved.
        """
        
        print('Retrieving records from database...')
        
        for _, tables in self.connection.select(**filter):
            yield self.players.unpack_tables(tables)
    
    def fetch_lookup_tables(self) -> Dict[str, str | int]:
        """
        Retrieves lookup table IDs for divisions, clubs, and nationalities.

        Collects and organizes the IDs of various lookup tables 
        and returns them as a dict.

        Parameters
        ----------
        connection : Interact
            An existing database connection used to fetch lookup tables.

        Returns
        -------
        defaultdict
            A dictionary containing the IDs of divisions, clubs, and nationalities.
        """
        
        print('Retrieving lookup tables IDs...')
        
        tables = defaultdict(dict)
        for _, row in self.connection.select(**{'columns': (Player, Division, Club, Nat)}):
            (division, club, nat) = row[0]
            tables['Division'][division.division] = division.id
            tables['Club'][club.club] = club.id
            tables['Nat'][nat.nat] = nat.id
                
        return dict(tables)