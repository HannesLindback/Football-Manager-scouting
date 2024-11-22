from typing import Dict
from football_manager_scouting.backend.preprocess_data import Preprocess
from football_manager_scouting.backend.server import Interact, Setup
from tqdm import tqdm

def insert_data_to_database(
                    db_login: Dict[str, str],
                    path: str,
                    season: int,
                    total: int = None,
                    n: int = 50000) -> None:
    """
    Inserts the data of an RTF file generated from Football Manager into a database.
    
    The file is assumed to be of the raw format directly from FM,
    where all data points are divided into cells separated with |
    and each row is separated by one line like: | -- |. The first row should
    consist of headers with the name of the category.
    
    Processes the RTF file, categorizes data based on the given JSON mapping,
    and inserts the data.

    Parameters:
    ----------
    db_login : Dict[str, str]
        Dictionary containing login credentials for the database connection.
        Should contain the keys: 'user', 'password', 'host' (both host and port) and 'database'.
    path : str
        The file path to the RTF file containing the FM data.
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
    
    engine = Setup.create_engine(**db_login)
    interact = Interact(engine)
    
    args = {'season': season}
    args.update(db_login)
    process = Preprocess(**args)
    
    print('Inserting entries...')
    
    read_rtf_file = process.read_rtf_file
    insert = interact.insert
    commit = interact.commit
    
    count = 0
    for tables in tqdm(read_rtf_file(path), desc='Entry', total=total):
        _tables = tables.copy()
        
        player = _tables['Player']
        del _tables['Player']

        insert(tables=_tables, player_table=player)        

        if n is not None and count % n == 0 and count != 0:
            commit(verbose=True)
        
        count += 1
            
    commit(verbose=True)
