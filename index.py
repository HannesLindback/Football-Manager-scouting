import argparse
from categories import Categories
from processing import Process
from score import Score
import csv
import sys


class Index:
    """Driver class for scoring players and writing the scores to csv-file."""

    def __init__(self, data, all_stats, header, file) -> None:
        score = Score(all_stats)
    
        with open(file, 'w', encoding='utf-8', newline='') as outf:
            
            writer = csv.writer(outf, delimiter=',')
            writer.writerow(['Score'] + header)
            
            for player_data in data.values():
                player_data['playerInfo']['mins'] = round(player_data['playerInfo']['mins']/90, 2)
                row = [0]
                
                for table, columns in player_data.items():
                    if table == 'stats':
                        scores = score(columns.values())
                        row.extend(scores)
                        row[0] = sum(scores)
                    else:
                        row.extend(list(columns.values()))
            
                writer.writerow(row)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--filename', type=str)
    ap.add_argument('--category', type=str)
    ap.add_argument('--position', type=str)
    ap.add_argument('--mins', type=int)
    ap.add_argument('--user', type=str)
    ap.add_argument('--password', type=str)
    ap.add_argument('--port', type=str)
    ap.add_argument('--database', type=str)
    args = ap.parse_args()

    categories = Categories()
    process = Process(args.user, args.password, args.port, args.database)
    
    file = f'files/{args.category}.csv'
    
    tables = ('stats', 'contract', 'attributes')
    position = [pos.strip() for pos in args.position.split(',')]
    stat_cat = categories.stats[args.category]
    attr_cat = categories.attributes[args.category]
    
    data, all_stats, header = process(stat_cat, attr_cat, position, args.mins, tables)
    
    print('Creating player index...')
    
    Index(data, all_stats, header, file)

    print(f'Finished! Data saved to file {file}')