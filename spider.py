"""Module for creating a radar chart (spider chart) of a player compared to other
players of the same division or of another single player."""


import argparse
from soccerplots.radar_chart import Radar
from categories import Categories
from server import Interact, Setup


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
    

def get_ranges(all_stats, possLost_i):
    ranges = [[float('inf'), 0] for i in range(len(all_stats[0]))]
    
    for stats in all_stats:
        for i, stat in enumerate(stats.values()):
            if stat < ranges[i][0]:
                ranges[i][0] = float(stat)
            if float(stat) > ranges[i][1]:
                ranges[i][1] = float(stat)

    if possLost_i is not None:
        ranges[possLost_i][0], ranges[possLost_i][1]  = ranges[possLost_i][1], ranges[possLost_i][0]

    return ranges


def average_stats(all_stats):
    average_stats = [0] * len(all_stats[0])
    
    for stats in all_stats:
        for i, stat in enumerate(stats.values()):
            average_stats[i] += stat
            
    average_stats = [average_stats[i] / len(all_stats)
                     for i in range(len(average_stats))]

    return average_stats


def get_stats(players_from_division, category):
    all_stats = []
    for UID, record in players_from_division.items():
        stats = {}
        for stat, value in record['stats'].items():
            if stat in category:
                stats[stat] = value
        all_stats.append(stats)
    
    return all_stats

if __name__ == '__main__':    
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', type=str)
    ap.add_argument('--category', type=str)
    ap.add_argument('--position', type=str)
    ap.add_argument('--comparison', type=str)
    ap.add_argument('--mins', type=int)
    ap.add_argument('--user', type=str)
    ap.add_argument('--password', type=str)
    ap.add_argument('--port', type=str)
    ap.add_argument('--database', type=str)
    args = ap.parse_args()

    setup = Setup()
    engine = setup.create_engine(args.user,
                                 args.password,
                                 args.port,
                                 database=args.database)
    interact = Interact(engine)
    categories = Categories()
    
    tables = ('stats',)
    position = [pos.strip() for pos in args.position.split(',')]
    category = categories.stats[args.category]
    
    player = interact.select(table_names=tables,
                             pos=position,
                             name=args.name,
                             mins=args.mins)
    
    division    = [data['playerInfo']['division'] for data in player.values()][0]
    player_stats = [data['stats'][stat] for data in player.values()
                    for stat in category]
    player_name = [data['Player']['name'] for data in player.values()][0]
    player_age  = [data['playerInfo']['age'] for data in player.values()][0]
    player_mins = [data['playerInfo']['mins'] for data in player.values()][0]
    
    players_from_division = interact.select(table_names=tables,
                                            pos=position,
                                            mins=args.mins,
                                            division=division)
    
    if len(players_from_division) <= 15:
        print(f'Ojoj! Bara {len(players_from_division)} spelare i databasen!')
        
    stats_of_players_from_division = get_stats(players_from_division, set(category))
    
    ranges = get_ranges(stats_of_players_from_division)
    
    
    if args.comparison != 'average':
        comp_player = interact.select(table_names=tables,
                                      pos=position,
                                      name=args.comparison,
                                      mins=args.mins)
        comparison = [data['stats'][stat] for data in comp_player.values()
                      for stat in category]
        
    else:
        comparison = average_stats(stats_of_players_from_division)
    
    spider(ranges=ranges,
           params=category,
           comparison=comparison,
           player_stats=player_stats,
           name=player_name,
           mins=player_mins,
           age=player_age,
           comp_name=args.comparison)