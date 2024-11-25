from football_manager_scouting.index import create_index
from football_manager_scouting.insert_data import insert_data_to_database
from football_manager_scouting.backend.server import Interact, Setup
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker


db_login = {
    'user': 'postgres',
    'password': 'root',
    'host': 'localhost:5432',
    'database': 'playerstest'
}


def remove_all_rows():
    engine = Setup.create_engine(
            user='postgres',
            password='root',
            host='localhost:5432',
            database='playerstest'
        )

    interact = Interact(engine)
    interact.session.flush()
    table_names = ('stats', '"playerInfo"', 'attributes', 'contract', 'ca', 'player', 'foot', 'position', 'club', 'nat', 'division', 'eligible')
    query = text(f'TRUNCATE TABLE {', '.join(table_names)} RESTART IDENTITY CASCADE;')
    interact.session.execute(query)
    interact.session.commit()


def get_records(column, lookup_join='', where_filter='', query=None):
    engine = Setup.create_engine(
            user='postgres',
            password='root',
            host='localhost:5432',
            database='playerstest'
        )

    Session = sessionmaker(bind=engine)
    session = Session()

    if not query:
        part_1 = f'SELECT player.name, {column} FROM player JOIN "playerInfo" ON "playerInfo"."_playerID" = player._id'
        where = where_filter if where_filter else ''

        query = f'{part_1} {lookup_join} {where};'

    return session.execute(text(query)).all()

    
def parse_csv(file):
    with open(file, 'r', encoding='utf-8') as fhand:
        fhand.readline()
        
        data = []
        
        for line in fhand:
            _, name, _, season, _, position, _,_, nineties, division, _ = line.split(',', 10)
            data.append({'name': name, 'season': season, 'position': position, 'mins': float(nineties)*90, 'division': division})
            
    return data

def test_setup():
    remove_all_rows()

    data_path = './data/test_data.rtf'

    insert_data_to_database(db_login=db_login, path=data_path, season='24')
    insert_data_to_database(db_login=db_login, path=data_path, season='25')


def test_zero_filters():
    create_index(db_login=db_login, category='all', file='zero.csv')
    results = get_records(column='player.uid')
    found = set([d['name'] for d in parse_csv('zero.csv')])
    assert set([res[0] for res in results]) == found

def test_pos_filters():
    create_index(db_login=db_login, category='all', position='ML', file='position.csv')
    results = get_records(column='position.position', lookup_join='JOIN position ON "playerInfo".position = position.id', where_filter="WHERE position.position = 'ML'")
    found = [(d['name'], set(d['position'].split())) for d in parse_csv('position.csv')]
    assert all([exp_name == found_name and exp_pos in found_poss for (exp_name, exp_pos), (found_name, found_poss) in zip(results, found)])
    
def test_min_filters():
    create_index(db_login=db_login, category='all', mins=64, file='mins.csv')
    results = get_records(column='"playerInfo".mins', where_filter='WHERE "playerInfo".mins >= 64')
    found = [(d['name'], round(d['mins'])) for d in parse_csv('mins.csv')]
    assert set(results) == set(found)

def test_division_filters():
    create_index(db_login=db_login, category='all', division=('Ligue 2 BKT', 'Norwegian First Division'), file='division.csv')
    results = get_records(column='division.division', lookup_join='JOIN division ON "playerInfo".division = division.id', where_filter="WHERE division.division IN ('Ligue 2 BKT', 'Norwegian First Division')")
    found = [(d['name'], d['division']) for d in parse_csv('division.csv')]
    assert set(results) == set(found)
    
def test_season_filters():
    create_index(db_login=db_login, category='all', season='24', file='season.csv')
    results = get_records(column='player.season', where_filter="WHERE player.season = '24'")
    found = [(d['name'], d['season']) for d in parse_csv('season.csv')]
    assert set(results) == set(found)
    
def test_all_filters():
    create_index(db_login=db_login, category='all', position='AML', mins=100, division='Bundesliga 2', season='25', file='all.csv')
    query = """
            SELECT player.name, position.position, "playerInfo".mins, division.division, player.season
            FROM player
            JOIN "playerInfo"
            ON "playerInfo"."_playerID" = player._id
            JOIN position
            ON "playerInfo".position = position.id
            JOIN division
            ON "playerInfo".division = division.id
            WHERE position.position = 'AML' AND "playerInfo".mins >= 100 AND division.division = 'Bundesliga 2' and player.season = '25';
            """
            
    results = get_records(column='', query=query)
    found = [(d['name'], d['season'], d['position'].split(), round(d['mins']), d['division']) for d in parse_csv('all.csv')]
    vals = []
    for (found_name, found_season, found_pos, found_mins, found_div), \
        (exp_name, exp_season, exp_pos, exp_mins, exp_div) in zip(found, results):
        vals.append((found_name == exp_name, found_season == exp_season, exp_pos in found_pos,
                     found_mins == exp_mins, found_div == exp_div))
    assert all(vals)
