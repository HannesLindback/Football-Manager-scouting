import argparse
from soccerplots.radar_chart import Radar
from categories import Categories
from request_data import Request
from collections import defaultdict
from errors import MultiplePlayersFoundError
from player import Players
from typing import List, Tuple, Dict


def create_radar_chart(ranges: List[Tuple[float, float]],
           params: List[str],
           comparison: List[float],
           player_stats: List[float],
           name: str,
           age: str,
           mins: str,
           comp_name: str) -> None:
    """
    Creates and saves a radar chart comparing player statistics.

    This function generates a radar chart using the provided player statistics 
    and comparison statistics. It formats the chart's title and subtitle based 
    on the player's information and saves the chart as an image file.

    Parameters
    ----------
    ranges : List[Tuple[float, float]]
        A list of tuples indicating the min and max ranges for each statistic 
        displayed on the radar chart.
    params : List[str]
        A list of parameter names corresponding to the statistics being plotted.
    comparison : List[float]
        A list of comparison values for the statistics to visualize against the 
        player's statistics.
    player_stats : List[float]
        A list of the player's statistics to be displayed on the radar chart.
    name : str
        The name of the player being compared.
    age : str
        The age of the player being compared.
    mins : str
        The number of minutes the player has played.
    comp_name : str
        The name of the player or average being used for comparison.
    
    Returns
    -------
    None
        The function does not return any value but saves the radar chart image.
    """
    
    values = [player_stats, comparison]

    title = dict(
    title_name=f'{name}',     
    title_color='#B6282F',
    subtitle_name=f'Age: {age}',      
    subtitle_color='#B6282F',
    title_name_2=f'90s: {round(mins/90, 2)}',    
    title_color_2='#B6282F',
    subtitle_name_2=f'Compared to: {comp_name}',    
    subtitle_color_2='#344D94',
    title_fontsize=18,             
    subtitle_fontsize=15,          
    title_fontsize_2=14,              
    subtitle_fontsize_2=12            
)
    radar = Radar(fontfamily="Ubuntu")
    fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values, 
                               radar_color=['#B6282F', '#344D94'], alphas=[0.8, 0.6], 
                               title=title, dpi=500, compare=True, filename='spider.jpg')
    

def get_ranges(all_stats: Dict[str, List[float]]) -> List[tuple[float, float]]:
    """
    Calculates the min and max ranges for each statistic from the provided data.

    This function generates a list of tuples representing the minimum and 
    maximum values for each statistic in the provided dictionary. 
    Special handling is applied for the 'possLost' statistic to reverse its 
    range since a lower value is preferred.

    Parameters
    ----------
    all_stats : Dict[str, List[float]]
        A dictionary where keys are statistic names and values are lists of 
        corresponding values for different players.

    Returns
    -------
    List[Tuple[float, float]]
        A list of tuples containing the min and max values for each statistic.
    """
    
    ranges = [(min(all_stats[stat]), max(all_stats[stat]))
              # The lower the category possLost is the better,
              # therefore reverse the order of this category's ranges
              if stat != 'possLost' else (max(all_stats[stat]), min(all_stats[stat]))
              for stat in all_stats]
    
    return ranges


def average_stats(all_stats: Dict[str, List[float]]) -> List[float]:
    """
    Calculates the average values for each statistic in the provided data.

    Parameters
    ----------
    all_stats : Dict[str, List[float]]
        A dictionary where keys are statistic names and values are lists of 
        corresponding values for different players.

    Returns
    -------
    List[float]
        A list of average values for each statistic.
    """
    
    return [sum(stat)/len(stat) for stat in all_stats.values()]


def get_stats(data: Players[Dict[str, Dict[str, str | float]]], filter_cats: set[str]) -> Dict[str, list[float]]:
    """
    Extracts statistics for players based on specified categories.

    This function filters the statistics of players in the provided data 
    according to the specified categories and compiles them into a 
    dictionary.

    Parameters
    ----------
    data : Players[str, Dict[Dict[str, str | float]]]
        A collection of player data where each player's statistics are stored 
        in a dictionary format.
    filter_cats : set[str]
        A set of category names to filter the statistics.

    Returns
    -------
    Dict[str, List[float]]
        A dictionary where keys are the filtered statistic names and values 
        are lists of corresponding statistics for the players.
    """
    
    stats = defaultdict(list)
    
    for records in data.values():
        player_stats: Dict[str, float] = records['Stats']
        for key, val in player_stats.items():
            if key in filter_cats:
                stats[key].append(val)
                
    return dict(stats)


def spider(args, categories, request):
    """
    Generates a radar chart comparison for a specified player and category.

    This function fetches player data based on command-line arguments, retrieves 
    relevant statistics, and creates a radar chart comparing the player's stats 
    with either another player or the average of players in the same category.

    Parameters
    ----------
    args : argparse.Namespace
        The command-line arguments containing player search filters and database 
        connection information.
    categories : Categories
        An object containing the statistics categories for filtering.
    request : Request
        An instance of the Request class for fetching player data from the database.

    Returns
    -------
    None
        The function does not return any value but generates a radar chart.
    """
    
    position = [pos.strip() for pos in args.position.split(',')] if args.position else None
    category = categories.stats[args.category]

    login = {'user':  args.user, 'password': args.password,
             'port': args.port, 'database': args.database}
    
    player_filter = {'pos': position, 'mins':args.mins,
                     'name': args.name, 'division': args.division}

    results: Players[dict[dict[str, str | int | float]]] = \
        request.fetch_all(login=login, filter=player_filter)

    if len(results) > 1:
        raise MultiplePlayersFoundError('Multiple players found!')
    
    player: dict[dict[str, str | int | float]] = next(iter(results.values()))
    player_stats: list[float] = list(player['Stats'].values())
        
    players_from_division_filter  = {'pos': position,
                                     'mins': args.mins,
                                     'division': player['PlayerInfo']['division']}

    players_from_division: Players[dict[dict[str, str | int | float]]] = \
        request.fetch_all(login=login, filter=players_from_division_filter)

    if len(players_from_division) <= 15:
        print(f'Only {len(players_from_division)} players in database!')
        
    stats_of_players_from_division = get_stats(players_from_division, set(category))

    ranges = get_ranges(stats_of_players_from_division)
    
    if args.comparison != 'average':
        comp_player_filter = {'pos': position,
                              'name': args.comparison,
                              'mins': args.mins}
        
        comp_player = next(iter(request.fetch_all(login=login, filter=comp_player_filter).values()))
        comparison = [comp_player['Stats'][stat] for stat in category]

    else:
        comparison: list[float] = average_stats(stats_of_players_from_division)
    
    create_radar_chart(ranges=ranges,
           params=category,
           comparison=comparison,
           player_stats=player_stats,
           name=player['Player']['name'],
           mins=player['PlayerInfo']['mins'],
           age=player['PlayerInfo']['age'],
           comp_name=args.comparison)


if __name__ == '__main__':    
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', type=str)
    ap.add_argument('--category', type=str)
    ap.add_argument('--position', type=str)
    ap.add_argument('--division', type=str)
    ap.add_argument('--comparison', type=str)
    ap.add_argument('--mins', type=int)
    ap.add_argument('--user', type=str)
    ap.add_argument('--password', type=str)
    ap.add_argument('--port', type=str)
    ap.add_argument('--database', type=str)
    args = ap.parse_args()

    categories = Categories()
    request = Request()

    spider(args, categories, request)
