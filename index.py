import argparse
from categories import Categories
from score import Score
from request_data import Request
import csv


def index(data, header, file) -> None:
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


def postprocess(data, cats):
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


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--filename', type=str)
    ap.add_argument('--category', type=str)
    ap.add_argument('--position', type=str)
    ap.add_argument('--mins', type=int)
    ap.add_argument('--season', type=int)
    ap.add_argument('--user', type=str)
    ap.add_argument('--password', type=str)
    ap.add_argument('--port', type=str)
    ap.add_argument('--database', type=str)
    args = ap.parse_args()

    categories = Categories()
    request = Request()
    
    file = f'./{args.category}.csv'
    
    position = [pos.strip() for pos in args.position.split(',')] if args.position else None
    
    login = {'user':  args.user, 'password': args.password,
             'port': args.port, 'database': args.database}
    
    filter = {'pos': position, 'mins': args.mins, 'name': None,
              'division': None}
    
    data = request.fetch_all(login=login, filter=filter)
    
    cats = {'Stats': set(categories.stats[args.category]),
            'Attributes': set(categories.attributes[args.category])}
    
    data, header = postprocess(data, cats)
    
    print('Creating player index...')
    
    index(data, header, file)

    print(f'Finished! Data saved to file {file}')