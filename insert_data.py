from preprocess_data import Preprocess
from server import Interact, Setup
from request_data import Request
import argparse
from tqdm import tqdm


class Insert:
    
    def __init__(self,
                 user: str,
                 password: str,
                 port: str,
                 database: str) -> None:
        """
        Initializes a database connection with user credentials and specified parameters.

        Parameters:
        ----------
        user : str
            The username for authenticating the database connection.
        password : str
            The password for authenticating the database connection.
        port : str
            The port number for connecting to the database server.
        database : str
            The name of the database to connect to.

        Attributes:
        -----------
        source_connection : Interact
            An instance of `Interact` that manages interactions with the database using the configured engine.

        Notes:
        ------
        - Sets up a SQLAlchemy engine using `Setup.create_engine` with the provided connection parameters.
        - Initializes `self.source_connection` with an `Interact` instance for handling database operations.
        - Stores the user, password, and port as attributes for potential future use.
        """
        
        engine = Setup.create_engine(user,
                                     password,
                                     port,
                                     database=database)

        self.user = user
        self.password = password
        self.port = port

        self.source_connection = Interact(engine)

    def insert_from_rtf(self,
                        path: str,
                        json_path: str,
                        season: int,
                        total: int = None,
                        n: int = None) -> None:
        """
        Inserts the data of an RTF file generated from Football Manager into a database.
        
        The file is assumed to be of the raw format directly from FM,
        where all data points are divided into cells separated with |
        and each row is separated by one line like: | -- |. The first row should
        consist of headers with the name of the category.
        
        Needs a JSON file mapping the each header to a wider category.
        E.g. xA/90 -> Stats and cor -> Attributes.
        
        Processes the RTF file, categorizes data based on the given JSON mapping,
        and inserts the data.

        Parameters:
        ----------
        path : str
            The file path to the RTF file containing the FM data.
        json_path : str
            The file path to a JSON file containing the mapping of column headers to data categories.
            NOTE: Removing individual mappings will almost definitely cause errors.
                  Only remove entire categories at once! Adding things is fine though.
        season : int
            The season year associated with the entries being processed.
        total : int, optional
            The total number of entries, used to display progress in the insertion process.
        n : int, optional
            After how many entries should commits be done. For a high number of inserts it is
            recommended to commit several times rather than one big final commit. If None will
            perform one commit after all entries have been inserted.
        
        Notes:
        ------
        - Initializes a `Preprocess` instance for handling RTF file data based on the specified season.
        - Uses the `tqdm` library to display progress for each entry insertion.
        - The `source_connection.insert` method is called for each entry, passing tables, player data, and lookup tables.
        - Commits either for every n entry or after all entries have been inserted.
        """
        
        process = Preprocess(season=season)
        
        print('Inserting entries...')
        
        count = 0
        for tables, lookup_tables in tqdm(process(path, json_path), desc='Entry', total=total):
            _tables = tables.copy()
            
            player = _tables['Player']
            del _tables['Player']

            self.source_connection.insert(tables=_tables, player_table=player, lookup_tables=lookup_tables)        

            if n is not None and count % n == 0 and count != 0:
                self.source_connection.commit()
            
            count += 1
                
        self.source_connection.commit()

    def insert_from_database(self):
        """
        Inserts data from a source database to a target database, updating lookup tables and IDs as needed.

        Prompts the user to input the target database name, connects to it, and retrieves required lookup tables.
        Processes each row in the source database, applying necessary transformations and inserting it into the target.

        Notes:
        ------
        - Prompts the user for the target database name and sets up a connection.
        - Retrieves lookup tables and determines the maximum `division_id`, `club_id`, and `nat_id` for
        appropriate ID assignments.
        - Initializes a `Preprocess` instance with updated lookup tables and IDs.
        - Iterates through each row in the source database using a request iterator, transforming and
        inserting each entry into the target database.
        - Commits all entries to the target database after processing is complete.
        """
        
        target_db = input('Target database name: ')

        engine = Setup.create_engine(self.user,
                                     self.password,
                                     self.port,
                                     database=target_db)
        
        target_connection = Interact(engine)
        request = Request()
        
        lookup_tables = request.fetch_lookup_tables(connection=target_connection)
        division_id = max([id for id in lookup_tables['Division'].values()])
        club_id = max([id for id in lookup_tables['Club'].values()])
        nat_id = max([id for id in lookup_tables['Nat'].values()])
        
        process = Preprocess(division_id=division_id,
                             club_id=club_id,
                             nat_id=nat_id)
        process.lookup_tables.update(lookup_tables)
        
        for row in request.iterator(filter={},
                                    connection=self.source_connection):
            
            self._insert_to_database(row, process, target_connection)
            
        target_connection.commit()
