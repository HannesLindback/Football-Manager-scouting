from football_manager_scouting.category_mappings.categories import STATS, ATTRIBUTES
from football_manager_scouting.backend.score import Score
from football_manager_scouting.backend.request_data import Request
import csv
from typing import Dict


def _create_index(data, header, file) -> None:
    """
    Scores players based on their statistics and writes the results to a CSV file.

    This function extracts player statistics, calculates scores using the 
    `Score` class, and writes the scores along with player information to a 
    specified CSV file. It formats player information, including minutes played 
    and position, and constructs rows for the CSV output.

    Parameters
    ----------
    data : dict
        A dictionary where each key is a player identifier and each value 
        contains the player's statistics and information.
    header : list
        A list of column headers to include in the CSV file.
    file : str
        The name of the CSV file to write the player scores to.

    Returns
    -------
    None
        The function does not return any value but writes the output to a file.
    """
    
    stats = [list(entry['Stats'].values()) for entry in data.values()]
    score = Score(all_stats=[*stats])

    with open(file, 'w', encoding='utf-8', newline='') as outf:
        
        writer = csv.writer(outf, delimiter=',')
        writer.writerow(['Score'] + header)
        
        for player_data in data.values():
            player_data['PlayerInfo']['mins'] = round(player_data['PlayerInfo']['mins']/90, 2)
            player_data['PlayerInfo']['position'] = ' '.join(player_data['PlayerInfo']['position']) \
                                                    if isinstance(player_data['PlayerInfo']['position'], (tuple, list)) \
                                                    else player_data['PlayerInfo']['position']
            row = [0]

            for cat, vals in player_data.items():
                if cat == 'Stats':
                    scores = score(vals.values())
                    row.extend(scores)
                    row[0] = sum(scores)
                else:
                    row.extend(list(vals.values()))
        
            writer.writerow(row)


def _postprocess(data, cats):
    """
    Processes player data by filtering out unwanted statistics and generating a header.

    This function removes unwanted statistics from the player data based on the 
    specified categories and constructs a header list for the remaining data. 
    It uses helper functions to filter out unwanted categories and generate the 
    final header.

    Parameters
    ----------
    data : dict
        A dictionary containing player data, where each key is a player identifier 
        and each value contains statistics and other information.
    cats : dict
        A dictionary specifying the categories to retain in the player data.

    Returns
    -------
    tuple
        A tuple containing two elements:
        - dict: The processed player data with unwanted statistics removed.
        - list: The generated header list reflecting the retained statistics.
    """
    
    def remove_unwanted_data(data, filter_cats):
        for uid, records in data.items():
            for cat in filter_cats:
                data[uid][cat] = {key:val for key, val in records[cat].items()
                                  if key in filter_cats[cat]}
        return data

    def get_header(data):
        header = []
        for entry in data.values():
            for table_name in entry.values():
                header.extend(list(table_name.keys()))
            return header

    data = remove_unwanted_data(data, cats)
    header = [header if header != 'mins' else '90s' 
              for header in get_header(data)]
    
    return data, header


def create_index(db_login: Dict[str, str],
          category: str = 'all',
          position: str = None,
          mins: str = 0,
          division: str = None) -> None:
    """
    Creates an index of FM players specifying how each player compares to the
    other players based on the statistics of each player.
    
    Retrieves player data from the database based on the specified filters,
    scores the player based on his statistics, and saves the results to a CSV file.

    Args:
        db_login (Dict[str, str]): Dictionary containing login credentials for the database connection.
            Should contain the keys: 'user', 'password', 'host' (both host and port) and 'database'.
        category (str, optional): Statistical category to filter the data. Can be 'all' or a position. 
            Supported positions are listed in categories.STATS. Default is 'all'.
        position (str, optional): Comma-separated list of positions to filter players by (e.g., 'FW,MF').
            Default is None, which includes all positions.
        mins (str, optional): Minimum minutes played filter for the player data. Default is 0.
        division (str, optional): Division to filter players by. Default is None.

    Returns:
        None: Writes the filtered player data to a CSV file named after the category.

    Example:
        index(
            db_login={'user': 'username', 'password': 'password', 'host': 'localhost:5432', 'database': 'database'},
            category='DC',
            position='DC',
            mins=500,
            division=None
        )
    """
    
    request = Request(**db_login)
    
    file = f'./{category}.csv'
    
    position = [pos.strip() for pos in position.split(',')] if position else None
    
    filter = {'pos': position, 'mins': mins, 'division': division}
    
    data = request.fetch_all(filter=filter)
    
    cats = {'Stats': set(STATS[category]),
            'Attributes': set(ATTRIBUTES[category])}
    
    data, header = _postprocess(data, cats)
    
    print('Creating player index...')
    
    _create_index(data, header, file)

    print(f'Finished! Data saved to file {file}')
