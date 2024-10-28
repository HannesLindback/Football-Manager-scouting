import math

class Score:
    """Class for scoring the player according to the statistics."""


    def __init__(self, all_stats) -> None:
        #       1          2        3       4         5         6          7          8        9          10        11          12           13        14       15        16       17       18                     
        # | Aerial/90 | Blk/90 | Clr/90 | Tck/90 | Pres/90 | Int/90 | Sprints/90 | Poss/90 | Drb/90 | OP-Crs/90 | Ps/90 | Pr passes/90 | OP-KP/90 | Ch C/90 | xA/90 | Shot/90 | ShT/90 | NP-xG/90 | Name                 | Mins  | Age | Position          | Inf | Rec     | 

        # 'def', 'press', 'running', 'possession', 'dribbles', 'crossing', 'passing', 'chances', 'attacking'

        self.weights = {'DC': [1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        'WB': [2, 1, 1, 3, 4, 4, 5, 3, 4, 5, 3, 4, 4, 5, 5, 1, 1, 1],
                        'IWB': [3, 3, 3, 3, 3, 3, 1, 3, 2, 2, 5, 6, 6, 6, 7, 2, 2, 2], 
                        'YB': [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
                        'WB': [1, 1, 1, 1, 1, 1, 3, 2, 5, 5, 3, 4, 5, 5, 5, 1, 1, 1], 
                        'DM': [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0], 
                        'MC': [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
                        'AM': [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1],
                        'YM': [1, 1, 1, 2, 3, 3, 3, 2, 4, 2, 1, 3, 4, 4, 5, 3, 3, 5], 
                        'W': [1, 1, 1, 1, 2, 2, 4, 3, 4, 4, 2, 3, 5, 5, 5, 2, 2, 3],
                        'STC': [1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1]}
        
        self.mean, self.std  = self._normal(all_stats,
                                            n_stats=len(all_stats[0]))
        

    def __call__(self, stats, e=0.0000001):
        """Calculates the scores of one single player.
        
        tanh()
        
        First weighs scores after the averages of the entire dataset,
        then weighs scores according to importance for the position."""
        
        Z = [(x - self.mean[i]) / (self.std[i] + e)
             for i, x in enumerate(stats)]
        
        t = [math.tanh(x)*10 for x in Z]
        
        #weighted = [round(stat * self.weights[category][i], 2)
        #            for i, stat in enumerate(t)]
        
        weighted = [round(stat, 2)
                    for i, stat in enumerate(t)]
        
        return weighted
    
    def _normal(self, div_stats, n_stats):
        mean_stats = [0] * n_stats
        for player_stat in div_stats:
            for i in range(len(player_stat)):
                mean_stats[i] += player_stat[i]
        mean_stats = [mean_stats[i] / len(div_stats)
                for i in range(len(mean_stats))]
        
        summed_squares = [0] * n_stats
        for player_stat in div_stats:
            for i in range(len(player_stat)):
                summed_squares[i] += (player_stat[i] - mean_stats[i]) ** 2
        
        std_devs = [math.sqrt(summed_squares[i]/len(div_stats))
                    for i in range(len(summed_squares))]
        
        return mean_stats, std_devs
