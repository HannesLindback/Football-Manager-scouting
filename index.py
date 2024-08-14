import argparse
from categories import Categories
from score import Score
from request_data import Request
import csv


def index(data, header, file) -> None:
    """Scores players and writes the scores to csv-file."""
    
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
    """Processes and categorizes the data in a presentable manner."""
    
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
    ap.add_argument('--filename', type=str, default='data')
    ap.add_argument('--category', type=str, default='WB')
    ap.add_argument('--position', type=str, default='ML')
    ap.add_argument('--mins', type=int, default=449)
    ap.add_argument('--season', type=int, default=27)
    ap.add_argument('--user', type=str, default='postgres')
    ap.add_argument('--password', type=str, default='root')
    ap.add_argument('--port', type=str, default='localhost:5432')
    ap.add_argument('--database', type=str, default='players')
    args = ap.parse_args()

    categories = Categories()
    request = Request()
    
    file = f'/home/hantan/FM/files/{args.category}.csv'
    
    position = [pos.strip() for pos in args.position.split(',')] if args.position else None
    
    login = {'user':  args.user, 'password': args.password,
             'port': args.port, 'database': args.database}
    
    filter = {'pos': position, 'mins':args.mins, 'name': None,
              'division': None}
    
    data = request.fetch_all(login=login, filter=filter)
    
    cats = {'Stats': set(categories.stats[args.category]),
            'Attributes': set(categories.attributes[args.category])}
    
    data, header = postprocess(data, cats)
    
    print('Creating player index...')
    
    index(data, header, file)

    print(f'Finished! Data saved to file {file}')