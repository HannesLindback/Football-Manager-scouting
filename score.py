from collections import defaultdict
import math

class Score:
    """Class for scoring the player according to the statistics."""

    def __init__(self, all_stats) -> None:
        self.mean, self.std  = self._normal(all_stats,
                                            n_stats=len(all_stats[0]))

    def __call__(self, stats, e=0.0000001):
        """Calculates the scores of one single player.
        
        For each statistic i of a player p:
        calculate the Z-score against the mean and standard deviation of
        each player in datasets' value for that statistic.
        
        Then, normalize each Z-score with tanh.
        
        The tanh-normalized Z-score is that player's score for that statistic."""
        
        Z = [(x - self.mean[i]) / (self.std[i] + e)
             for i, x in enumerate(stats)]
        
        t = [math.tanh(x)*10 for x in Z]
        
        weighted = [round(stat, 2)
                    for i, stat in enumerate(t)]
        
        return weighted
    
    def _normal(self, div_stats, n_stats):
        """Calculate the normal distribution of each statistic."""
        
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
