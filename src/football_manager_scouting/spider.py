from soccerplots.radar_chart import Radar
from football_manager_scouting.category_mappings.categories import STATS
from football_manager_scouting.backend.request_data import Request
from collections import defaultdict
from football_manager_scouting.backend.errors import MultiplePlayersFoundError
from football_manager_scouting.backend.player import Players
from typing import List, Tuple, Dict, Iterable


def _create_radar_chart(ranges: List[Tuple[float, float]],
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
                               title=title, dpi=500, compare=True, filename=f'{name}.jpg')
    

def _get_ranges(all_stats: Dict[str, List[float]]) -> List[tuple[float, float]]:
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


def _average_stats(all_stats: Dict[str, List[float]]) -> List[float]:
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


def _get_stats(data: Players[Dict[str, Dict[str, str | float]]], filter_cats: set[str]) -> Dict[str, list[float]]:
    """
    Extracts statistics for players based on specified categories.

    This function filters the statistics of players in the provided data 
    according to the specified categories and compiles them into a 
    dictionary.

    Parameters
    ----------
    data : Players[Dict[Dict[str, str | float]]]
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


def create_spider(db_login: Dict[str, str],
           name: str,
           season: str,
           position: str = None,
           division: str = None,
           mins: int = 0,
           category: str = 'all',
           comparison: str = 'average',
           comparison_division: str | Iterable[str] = None,
           comparison_position: str | Iterable[str] = None,
           comparison_season: int = None
           ) -> None:
    """
    Generates a radar chart ("spider") comparing a specific player's statistics to either
    the average statistics of players in the same division or to another specific player.

    Args:
        db_login (Dict[str, str]): Dictionary containing login credentials for the database connection.
            Should contain the keys: 'user', 'password', 'host' (both host and port) and 'database'.
        name (str): The name of the Player to retrieve data for and display on the radar chart.
        season (int): Which season of the player's data that should be used.
        position (str, optional): String of the position to filter the player by (e.g., 'DC' or 'MC').
            Default is None, which includes all positions.
        division (str, optional): Division of the player to filter by. Default is None.
        mins (int, optional): Minimum number of minutes played by players to be included in the comparison.
            Default is 0.
        category (str, optional): Statistical category to filter the data. Can be 'all' or a position. 
            Supported positions are listed in categories.STATS. Default is 'all'.
        comparison (str, optional): Name of another player to compare to, or 'average' to use the average 
            statistics of players in the same division. Default is 'average'.
        comparison_division (str or iterable of str, optional): The division(s) that should be included in 
            the comparison. If None will use the same division as the named Player. Default is None.
        comparison_position (str or iterable of str, optional): The position(s) that should be included in
            the comparison. If comparison is another player, the compared player's position must be included.
            If None will use the same position as the named Player. Default is None.
        comparison_season (int): Which season that should be used for the comparison. If None will use the
            season specified in argument season.

    Raises:
        MultiplePlayersFoundError: If more than one player is found for the provided `name` filter.

    Returns:
        None: Saves a radar chart comparing the specified player's stats to the chosen comparison data at the location ./spider.jpg.

    Example:
        spider(
            db_login={'user': 'username', 'password': 'password', 'host': 'localhost:5432', 'database': 'database'},
            name='Player A',
            category='DC',
            position='DC',
            mins=500,
            division='Premier League',
            'season': 28,
            'comparison_division': ['Italian Serie A', 'English Premier Division'],
            'comparison': 'Player B',
            'comparison_position': 'DC',
        )
    """

    if division is None and comparison_division is None:
        raise(ValueError('Args division and comparison_division cannot both be None!'))

    if not isinstance(season, str):
        season = str(season)

    request = Request(**db_login)
    
    category = STATS[category]
    
    ###########
    player_filter = {'name': name, 'season': season,
                     'pos': position, 'division': division,
                     'mins': mins}

    player: Players[dict[dict[str, str | int | float]]] = \
        request.fetch_all(filter=player_filter)

    if len(player) > 1:
        raise MultiplePlayersFoundError('Multiple players found! Apply more filters.')

    player: dict[dict[str, str | int | float]] = next(iter(player.values()))  # Extract the sole item of dict.
    player_stats: list[float] = list(player['Stats'].values())
    ###########

    ###########
    comparison_division = comparison_division if comparison_division is not None else division
    comparison_position = comparison_position if comparison_position is not None else position
    comparison_season = comparison_season if comparison_season is not None else season
    
    players_from_division_filter  = {'season': comparison_season,
                                     'pos': comparison_position,
                                     'division': comparison_division,
                                     'mins': mins}

    request.players = Players()  # Inte en bra lösning!

    players_from_division: Players[dict[dict[str, str | int | float]]] = \
        request.fetch_all(filter=players_from_division_filter)

    if len(players_from_division) <= 15:
        print(f'Only {len(players_from_division)} players in database!')

    stats_of_players_from_division = _get_stats(players_from_division, set(category))

    ranges = _get_ranges(stats_of_players_from_division)

    if comparison != 'average':
        request.players = Players()  # Inte en bra lösning!

        comp_player_filter = {'name': comparison,
                              'season': comparison_season,
                              'pos': comparison_position,
                              'division': comparison_division,
                              'mins': mins}

        comp_player = next(iter(request.fetch_all(filter=comp_player_filter).values()))
        comp_name = comp_player['Player']['name']
        comparison = [comp_player['Stats'][stat] for stat in category]

    else:
        comp_name = 'average'
        comparison: list[float] = _average_stats(stats_of_players_from_division)

    _create_radar_chart(
        ranges=ranges,
        params=category,
        comparison=comparison,
        player_stats=player_stats,
        name=player['Player']['name'],
        mins=player['PlayerInfo']['mins'],
        age=player['PlayerInfo']['age'],
        comp_name=comp_name
        )


