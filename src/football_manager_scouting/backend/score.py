import math


class Score:
    """
    A class to calculate normalized scores based on player statistics.

    This class computes the mean and standard deviation of given player statistics 
    and provides a method to evaluate a player's score using the calculated 
    mean and standard deviation. The scores are normalized using the hyperbolic 
    tangent function and then scaled.

    Attributes
    ----------
    mean : list of float
        The mean values of the statistics.
    std : list of float
        The standard deviation values of the statistics.

    Parameters
    ----------
    all_stats : list of list of float
        A list containing statistics for all players. Each sublist represents the 
        statistics of an individual player.
    """
    
    def __init__(self,
                 all_stats) -> None:
        """
        Initializes the Score object by computing the mean and standard deviation.

        Parameters
        ----------
        all_stats : list of list of float
            A list containing statistics for all players. Each sublist represents the 
            statistics of an individual player.
        """
        
        self.mean, self.std  = self._normal(all_stats,
                                            n_stats=len(all_stats[0]))
        

    def __call__(self, stats, e=0.0000001):
        """
        Normalizes the given player statistics and computes the weighted score.

        This method takes in player statistics, calculates their z-scores, 
        applies the hyperbolic tangent function, and scales the result.

        Parameters
        ----------
        stats : list of float
            The statistics of a single player to be normalized.
        e : float, optional
            A small value added to the standard deviation to prevent division by zero. 
            Default is 1e-7.

        Returns
        -------
        list of float
            A list of weighted and rounded scores for the input player statistics.
        """
        
        Z = [(x - self.mean[i]) / (self.std[i] + e)
             for i, x in enumerate(stats)]
        
        t = [math.tanh(x)*10 for x in Z]
        
        weighted = [round(stat, 2)
                    for i, stat in enumerate(t)]
        
        return weighted
    
    def _normal(self, all_stats, n_stats):
        """
        Computes the mean and standard deviation for the provided statistics.

        This method calculates the mean and standard deviation of the player 
        statistics from the given data.

        Parameters
        ----------
        div_stats : list of list of float
            A list containing statistics for all players. Each sublist represents 
            the statistics of an individual player.
        n_stats : int
            The number of statistics being analyzed.

        Returns
        -------
        tuple
            A tuple containing two lists: the mean statistics and the standard 
            deviation statistics for the players.
        """
        
        mean_stats = [0] * n_stats
        
        for player_stat in all_stats:
            
            for i in range(len(player_stat)):
                
                mean_stats[i] += player_stat[i]
                
        mean_stats = [mean_stats[i] / len(all_stats) for i in range(len(mean_stats))]
        
        summed_squares = [0] * n_stats
        
        for player_stat in all_stats:
            
            for i in range(len(player_stat)):
                
                summed_squares[i] += (player_stat[i] - mean_stats[i]) ** 2
        
        std_devs = [math.sqrt(summed_squares[i]/len(all_stats))
                    for i in range(len(summed_squares))]
        
        return mean_stats, std_devs
