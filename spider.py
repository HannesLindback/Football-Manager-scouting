import argparse
from soccerplots.radar_chart import Radar
from categories import Categories
from request_data import Request
from collections import defaultdict


def spider(ranges, params, comparison, player_stats, name, age, mins, comp_name):
    values = [player_stats, comparison]

    title = dict(
    title_name=f'{name}',     ## title on left side
    title_color='#B6282F',
    subtitle_name=f'Age: {age}',      ## subtitle on left side
    subtitle_color='#B6282F',
    title_name_2=f'90s: {round(mins/90, 2)}',    ## title on right side
    title_color_2='#B6282F',
    subtitle_name_2=f'Compared to: {comp_name}',    ## subtitle on right side
    subtitle_color_2='#344D94',
    title_fontsize=18,             ## same fontsize for both title
    subtitle_fontsize=15,          ## same fontsize for both subtitle
    title_fontsize_2=14,              ## fontsize for right-title
    subtitle_fontsize_2=12            ## fontsize for right-subtitle
)
    radar = Radar(fontfamily="Ubuntu")
    fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                               radar_color=['#B6282F', '#344D94'], alphas=[0.8, 0.6], 
                               title=title, dpi=500, compare=True, filename='spider.jpg')
    

def get_ranges(all_stats):
    ranges = [(min(all_stats[stat]), max(all_stats[stat]))
              # The lower the category possLost is the better,
              # therefore reverse the order of this category's ranges
              if stat != 'possLost' else (max(all_stats[stat]), min(all_stats[stat]))
              for stat in all_stats]
    
    return ranges


def average_stats(all_stats):
    return [sum(stat)/len(stat) for stat in all_stats.values()]


def get_stats(data, filter_cats):
    stats = defaultdict(list)
    
    for records in data.values():
        for key, val in records['Stats'].items():
            if key in filter_cats:
                stats[key].append(val)
                
    return stats


if __name__ == '__main__':    
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', type=str, default="Paolo Gozzi")
    ap.add_argument('--category', type=str, default='DC')
    ap.add_argument('--position', type=str, default='DC')
    ap.add_argument('--division', type=str, default=None)
    ap.add_argument('--comparison', type=str, default='average')
    ap.add_argument('--mins', type=int, default=449)
    ap.add_argument('--user', type=str, default='postgres')
    ap.add_argument('--password', type=str, default='root')
    ap.add_argument('--port', type=str, default='localhost:5432')
    ap.add_argument('--database', type=str, default='players')
    args = ap.parse_args()

    categories = Categories()

    position = [pos.strip() for pos in args.position.split(',')] if args.position else None
    category = categories.stats[args.category]

    login = {'user':  args.user, 'password': args.password,
             'port': args.port, 'database': args.database}
    
    player_filter = {'pos': position, 'mins':args.mins,
                     'name': args.name, 'division': args.division}

    player = next(iter(Request.retrieve_records(login=login, filter=player_filter).values()))

    players_from_division_filter = {'pos': position,
                                    'mins':args.mins,
                                    'division': player['playerInfo']['division']}

    players_from_division = Request.retrieve_records(login=login,
                                             filter=players_from_division_filter)

    if len(players_from_division) <= 15:
        print(f'Ojoj! Bara {len(players_from_division)} spelare i databasen!')
        
    stats_of_players_from_division = get_stats(players_from_division,
                                               set(category))
    
    ranges = get_ranges(stats_of_players_from_division)
    
    if args.comparison != 'average':
        comp_player_filter = {'pos': position,
                              'name': args.comparison,
                              'mins': args.mins}
        
        comp_player = next(iter(Request.retrieve_records(login=login,
                                       filter=comp_player_filter).values()))
        
        comparison = [comp_player['stats'][stat] for stat in category]

    else:
        comparison = average_stats(stats_of_players_from_division)
    
    spider(ranges=ranges,
           params=category,
           comparison=comparison,
           player_stats=list(player['stats'].values()),
           name=player['player']['name'],
           mins=player['playerInfo']['mins'],
           age=player['layerInfo']['age'],
           comp_name=args.comparison)
    