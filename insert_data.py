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
        
        process = Preprocess(season=season, user=self.user, password=self.password, port=self.port)
        
        print('Inserting entries...')
        
        read_rtf_file = process.read_rtf_file
        insert = self.source_connection.insert
        commit = self.source_connection.commit
        
        count = 0
        for tables in tqdm(read_rtf_file(path, json_path), desc='Entry', total=total):
            _tables = tables.copy()
            
            player = _tables['Player']
            del _tables['Player']

            insert(tables=_tables, player_table=player)        

            if n is not None and count % n == 0 and count != 0:
                commit(verbose=True)
            
            count += 1
                
        commit(verbose=True)
