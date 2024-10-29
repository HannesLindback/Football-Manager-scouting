import unittest, random
from unittest.mock import patch
from preprocess_data import Preprocess


class TestPreprocess(unittest.TestCase):
    ITERATIONS = 100
    
    def setUp(self):
        self.process = Preprocess(season=27, division_id=100, club_id=200, nat_id=300)

    def test_split_positions(self):
        pos_strings = ['M/AM (LC)', 'GK', 'D (R)', 'M/AM (C), ST (C)', 'D (LC), DM', 'D (RC)', 'D (RL), WB (R)']
        expected_positions = (['ML', 'MC', 'AML', 'AMC'], ['GK'], ['DR'], ['MC', 'AMC', 'STC'],
                              ['DL', 'DC', 'DM'], ['DR', 'DC'], ['DR', 'DL', 'WBR'])
        
        for pos_string, expected in zip(pos_strings, expected_positions):
            result = self.process._split_positions(pos_string)
            self.assertEqual(result, expected)

    def test_format_high_values(self):
        values = ['41M\xa0kr', '13B\xa0kr', '250K\xa0kr', '34\xa0kr']
        expected_values = [41000000, 13000000000, 250000, 34]
        for value, expected in zip(values, expected_values):
            result = self.process._format_high_values(value)
            self.assertEqual(result, expected)

    def test_obfuscate_asking_price(self):
        for _ in range(TestPreprocess.ITERATIONS):
            asking_price = random.randrange(0, 1000000000)
            n = random.randrange(2, 10)
            obfuscated_price = self.process._obfuscate_asking_price(asking_price, n=n)
            self.assertTrue((asking_price/n) <= obfuscated_price <= (asking_price*n))

    def test_encode_lookup_tables(self):
        tables = {'position': ['GK', 'DC'], 'rightfoot': 'Strong', 'eligible': 'Yes'}
        encoded_tables = self.process._encode_lookup_tables(tables)
        
        self.assertEqual(encoded_tables['position'], [0, 1])  # GK, DC
        self.assertEqual(encoded_tables['rightfoot'], 5)  # 'Strong'
        self.assertEqual(encoded_tables['eligible'], 1)  # 'Yes'
        
    def test_clean(self):
        Player = {'name': 'Kalle'}
        PlayerInfo = {'age': '22', 'position': 'M/AM (LC)', 'mins': '1\xa0434'}
        Contract = {'beginDate': '01-01-2022', 'expiryDate': '-', 'extension': '',
                    'wage': '765\xa0000\xa0kr p/m', 'ap': '1.35M\xa0kr', 'releaseClauseFee': '7.5M\xa0kr'}
        
        stats = [val.strip() for val in
                'Aer A/90 | Hdrs W/90 | Blk/90 | Clr/90 | Tck/90 | Pres A/90 | Pres C/90 | Int/90 | Sprints/90 | Poss Lost/90 | Poss Won/90 | Drb/90 | OP-Crs A/90 | OP-Crs C/90 | Ps A/90 | Ps C/90 | Pr passes/90 | OP-KP/90 | Ch C/90 | xA/90 | Shot/90 | ShT/90 | NP-xG/90'.split('|')
                ]
        vals = [random.random() for i in range(len(stats))]
        insert_vals = vals.copy()
        insert_vals[4] = '-'
        vals[4] = 0.0
        Stats = {stat: val for stat, val in zip(stats, insert_vals)}
        
        cleaned_data = self.process._clean(Player=Player,
                                           PlayerInfo=PlayerInfo,
                                           Contract=Contract,
                                           Stats=Stats)
        
        self.assertEqual(cleaned_data['Player']['name'], 'Kalle')
        self.assertEqual(cleaned_data['PlayerInfo']['age'], 22)
        self.assertEqual(cleaned_data['PlayerInfo']['mins'], 1434)
        self.assertEqual(cleaned_data['PlayerInfo']['position'], ['ML', 'MC', 'AML', 'AMC'])
        
        self.assertEqual(cleaned_data['Contract']['beginDate'], 2022)
        self.assertEqual(cleaned_data['Contract']['expiryDate'], 0)
        self.assertEqual(cleaned_data['Contract']['extension'], 0)
        self.assertEqual(cleaned_data['Contract']['wage'], 765000)
        self.assertTrue((1350000/2) <= cleaned_data['Contract']['value'] <= (1350000*2))
        self.assertEqual(cleaned_data['Contract']['releaseClauseFee'], 7500000)
        self.assertIs(cleaned_data['Contract'].get('ap'), None)
        
        self.assertEqual(list(cleaned_data['Stats'].values()), vals)
        breakpoint


if __name__ == '__main__':
    unittest.main()
