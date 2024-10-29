from collections import defaultdict
from server import Setup, Interact
from player import Players
from tables import Player, Division, Club, Nat
from typing import Dict


class Request:
    """
    A class to handle database requests related to player data.

    Provides methods to connect to a database, fetch player data, 
    and retrieve lookup tables for various attributes such as division, club, 
    and nationality. Uses the `Players` class to organize and store the 
    player records retrieved from the database.
    """

    def __init__(self) -> None:
        """
        Initializes the Request object and creates an instance of Players.

        Attributes
        ----------
        players : Players
            An instance of the Players class to store player records.
        """
        
        self.players = Players()

    def connect(self,
                user: str,
                password: str,
                port: str,
                database: str) -> Interact:
        """
        Establishes a connection to the database using the provided credentials.

        Parameters
        ----------
        user : str
            The username for database authentication.
        password : str
            The password for database authentication.
        port : str
            The port number to connect to the database.
        database : str
            The name of the database to connect to.

        Returns
        -------
        Interact
            An instance of the Interact class representing the database connection.
        """
        
        engine = Setup.create_engine(user,
                                    password,
                                    port,
                                    database=database)
        
        return Interact(engine)

    def fetch_all(self,
                  filter={},
                  login={},
                  connection: Interact = None) -> Players:
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
        
        connection = self._get_connection_if_none(login, connection)
        
        print('Retrieving records from database...')
        
        for uid, tables in connection.select(**filter):
            self.players[uid] = tables
        
        return self.players
    
    def iterator(self,
                 filter={},
                 login={},
                 connection: Interact = None):
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
        
        connection = self._get_connection_if_none(login, connection)
        
        print('Retrieving records from database...')
        
        for _, tables in connection.select(**filter):
            yield self.players.unpack_tables(tables)
    
    def fetch_lookup_tables(self, connection: Interact) -> Dict[str, str | int]:
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
        for _, row in connection.select(**{'columns': (Player, Division, Club, Nat)}):
            (division, club, nat) = row[0]
            tables['Division'][division.division] = division.id
            tables['Club'][club.club] = club.id
            tables['Nat'][nat.nat] = nat.id
            breakpoint
                
        return dict(tables)
    
    def _get_connection_if_none(self, login, connection):
        return connection if connection else self.connect(**login)
            