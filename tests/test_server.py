from football_manager_scouting.backend.server import Setup, Interact
from football_manager_scouting.backend.tables import (Player, PlayerInfo, Attributes, Stats, Ca, Contract, Base,
                    Position, Division, Foot, Nat, Club, Eligible)
from football_manager_scouting.backend.errors import UnexpecteTableNameError, NoPlayerFoundError, UnexpectedColumnNameError
from sqlalchemy.engine import Connection
from sqlalchemy import MetaData, text
import pytest


engine = Setup.create_engine(
            user='postgres',
            password='root',
            host='localhost:5432',
            database='playerstest'
        )
interact = Interact(engine)
Base.metadata.drop_all(engine)


def test_create_engine():
    connection = engine.connect()
    
    # Test that the database exists.
    assert isinstance(connection, Connection)

def test_create():
    
    # Test that it raises ValueError when given arguments of the wrong type.
    with pytest.raises(ValueError):
        interact.create('true', verbose='true')
        interact.create(1, verbose=False)
        interact.create(False, verbose='true')
    
    # Retrieve the table relations imported to server.py and in tables.py.
    interact.create(drop=True, verbose=False)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    tables = set([table.__tablename__ for table in (Player, PlayerInfo, Attributes, Stats, Ca, Contract,
                Position, Division, Foot, Nat, Club, Eligible)])
    created_tables = set(metadata.tables.keys())
    
    # Verify that the engine in server.py has the expected table relations.
    assert tables == created_tables

def test_insert():
    # Test that the function raises exception when given a tables dict with unexpected tablenames.
    with pytest.raises(UnexpecteTableNameError):
        tables = {'playerinfo': ({'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 1}, {'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 2}, {'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 3}, {'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 4}),
                    'Contract': {'beginDate': 2027, 'expiryDate': 2031, 'extension': 0, 'wage': 765000, 'releaseClauseFee': 0, 'value': 77535945}}
        player_table = {'name': 'blabla', 'uid': '2345', 'season': '23'}
        interact.insert(tables, player_table)    
    
    # Test that the function raises exception when given a table dict with unexpected column names.
    with pytest.raises(UnexpectedColumnNameError):
        tables = {'PlayerInfo': ({'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 1}, {'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 2}, {'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 3}, {'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 4}),
                    'Contract': {'bbeginDate': 2027, 'expiryDate': 2031, 'extension': 0, 'wage': 765000, 'releaseClauseFee': 0, 'value': 77535945}}
        player_table = {'name': 'blabla', 'uid': '2345', 'season': '23'}
        interact.insert(tables, player_table)
    
    with pytest.raises(UnexpectedColumnNameError):
        tables = {'PlayerInfo': ({'aage': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 1}, {'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 2}, {'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 3}, {'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 4}),
                    'Contract': {'beginDate': 2027, 'expiryDate': 2031, 'extension': 0, 'wage': 765000, 'releaseClauseFee': 0, 'value': 77535945}}
        player_table = {'name': 'blabla', 'uid': '2345', 'season': '23'}
        interact.insert(tables, player_table)

    with pytest.raises(UnexpectedColumnNameError):
        tables = {'PlayerInfo': ({'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 1}, {'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 2}, {'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 3}, {'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 4}),
                    'Contract': {'beginDate': 2027, 'expiryDate': 2031, 'extension': 0, 'wage': 765000, 'releaseClauseFee': 0, 'value': 77535945}}
        player_table = {'nname': 'blabla', 'uid': '2345', 'season': '23'}
        interact.insert(tables, player_table)

    # Test that elements are correctly added to the session.
    
    lookup_tables = {
        'Club': ['Mainz 05', 'Bnei Furadis', 'AB', 'Start', 'Hammarby', 'Odd', 'Lyngby', 'Slagelse', 'Steinkjer', 'Frigg', 'HamKam', 'Stord', 'Jerv', 'RS Waremme', 'FC Haka', 'Kongsvinger', 'Grorud'],
        'Division': ['Norwegian Fourth Division Telemark', '3F Superliga', 'Danish Zealand Series', 'Norwegian Fourth Division Trøndelag 1', 'Norwegian Third Division Group 3', 'Norwegian Fourth Division Hordaland 2', 'Norwegian First Division', 'Belgian Second Amateur Division C', 'Finnish Premier League', 'Dutch Reserve Competition Eerste Divisie', 'Ligue 2 BKT', 'Italian Serie D Grp. C', 'Dutch Eerste Klasse Zaterdag D', 'Bundesliga 2', 'Norwegian Fourth Division Østfold', 'Brazilian National First Division', 'Norwegian Fourth Division Hordaland 1', 'Norwegian Fourth Division Sunnmøre', 'Norwegian Second Division Group 1', 'Spanish Second Division', 'United States Soccer Leagues Division One'],
        'Foot': ['Very Strong', 'Reasonable', '-', 'Weak', 'Strong', 'Fairly Strong', 'Very Weak'],
        'Nat': ['NED', 'ISR', 'DEN', 'NOR', 'BEL', 'FIN', 'FRA', 'ITA', 'MAR', 'BRA', 'ESP', 'TRI', 'ENG', 'USA', 'AFG', 'ROU'],
        'Eligible': ['Yes', 'No'],
        'Position': ['ML', 'MC', 'AML', 'AMC', 'DR', 'GK', 'STC', 'DC', 'MR', 'AMR', 'DL', 'DM', 'WBR', 'WBL']
    }
    
    for table, vals in lookup_tables.items():
        for val in vals:
            interact.get_lookup_id(table, (table.lower(), val))
    
    playerinfo = [{'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 1}]
    contract = {'beginDate': 2027, 'expiryDate': 2031, 'extension': 0, 'wage': 765000, 'releaseClauseFee': 0, 'value': 77535945}
    attributes = {"cor": "7", "cro": "15", "dri": "12", "fin": "10", "fir": "18", "fre": "14", "hea": "9", "lon": "16", "lth": "8", "mar": "6", "pas": "17", "pen": "4", "tck": "11", "tec": "19", "agg": "13", "ant": "12", "bra": "5", "cmp": "16", "cnt": "20", "decisions": "8", "det": "14", "fla": "3", "ldr": "11", "otb": "10", "pos": "9", "tea": "18", "vis": "15", "wor": "7", "acc": "17", "agi": "19", "bal": "12", "jum": "8", "natF": "13", "pac": "14", "sta": "10", "strength": "20", "aer": "11", "cmd": "15", "com": "16", "ecc": "4", "han": "9", "kic": "8", "oneVsOne": "6", "pun": "7", "ref": "18", "tro": "14", "thr": "13"}
    ca = {'ca': 126}
    stats = {'aerA': 2.2, 'hdrsW': 4.2, 'blk': 3.3, 'clr': 4.4, 'tckC': 1.6, 'presA': 2.3, 'presC': 4.3, 'interceptions': 3.1, 'sprints': 4.9, 'possLost': 3.7, 'possWon': 2.3, 'drb': 0.2, 'opCrsA': 3.4, 'opCrsC': 2.7, 'psA': 4.2, 'psC': 1.2, 'prPasses': 1.0, 'opKp': 0.8, 'chC': 0.4, 'xa': 0.3, 'shot': 3.5, 'sht': 2.0, 'npXg': 1.9}
    tables =   {'Stats': stats,
                'PlayerInfo': playerinfo,
                'Attributes': attributes,
                'Contract': contract,
                'Ca': ca}
    player_table = {'name': 'blabla', 'uid': '1', 'season': '23'}
    
    interact.insert(tables, player_table)

    inserted = [player_table] + playerinfo + [stats] + [contract] + [ca] + [attributes]
    expected_values = [val for table in inserted for val in table.values()]

    found_values = []
    for new, inserted_table in zip(interact.session.new, inserted):
        for key in inserted_table:
            found_values.append(getattr(new, key))

    assert expected_values == found_values
    
    remove_all_rows()
    
def test_get_lookup_id():
    # Test that the function raises exception when given a tables dict with unexpected tablenames.
    with pytest.raises(UnexpecteTableNameError):
        interact.get_lookup_id('position', ('position', 'MC'))
    
    # Test that the function raises exception when given a table dict with unexpected column names.
    with pytest.raises(UnexpectedColumnNameError):
        interact.get_lookup_id('Position', ('Position', 'MC'))
    
    # Test that non-existing ID:s are added to lookup table.
    id1 = interact.get_lookup_id('Position', ('position', 'MC'))
    id2 = interact.get_lookup_id('Position', ('position', 'MC'))
    assert id1 == id2
    
    remove_all_rows()
    
def test_select():
    interact.create(drop=True, verbose=False)

    ################################ SETUP ################################
    
    lookup_tables = {
        'Club': ['Mainz 05', 'Bnei Furadis', 'AB', 'Start', 'Hammarby', 'Odd', 'Lyngby', 'Slagelse', 'Steinkjer', 'Frigg', 'HamKam', 'Stord', 'Jerv', 'RS Waremme', 'FC Haka', 'Kongsvinger', 'Grorud'],
        'Division': ['Norwegian Fourth Division Telemark', '3F Superliga', 'Danish Zealand Series', 'Norwegian Fourth Division Trøndelag 1', 'Norwegian Third Division Group 3', 'Norwegian Fourth Division Hordaland 2', 'Norwegian First Division', 'Belgian Second Amateur Division C', 'Finnish Premier League', 'Dutch Reserve Competition Eerste Divisie', 'Ligue 2 BKT', 'Italian Serie D Grp. C', 'Dutch Eerste Klasse Zaterdag D', 'Bundesliga 2', 'Norwegian Fourth Division Østfold', 'Brazilian National First Division', 'Norwegian Fourth Division Hordaland 1', 'Norwegian Fourth Division Sunnmøre', 'Norwegian Second Division Group 1', 'Spanish Second Division', 'United States Soccer Leagues Division One'],
        'Foot': ['Very Strong', 'Reasonable', '-', 'Weak', 'Strong', 'Fairly Strong', 'Very Weak'],
        'Nat': ['NED', 'ISR', 'DEN', 'NOR', 'BEL', 'FIN', 'FRA', 'ITA', 'MAR', 'BRA', 'ESP', 'TRI', 'ENG', 'USA', 'AFG', 'ROU'],
        'Eligible': ['Yes', 'No'],
        'Position': ['ML', 'MC', 'AML', 'AMC', 'DR', 'GK', 'STC', 'DC', 'MR', 'AMR', 'DL', 'DM', 'WBR', 'WBL']
    }
    
    for table, vals in lookup_tables.items():
        for val in vals:
            interact.get_lookup_id(table, (table.lower(), val))

    playerinfo = [{'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 37, 'division': 1, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 1}]
    contract = {'beginDate': 2027, 'expiryDate': 2031, 'extension': 0, 'wage': 765000, 'releaseClauseFee': 0, 'value': 77535945}
    attributes = {"cor": "7", "cro": "15", "dri": "12", "fin": "10", "fir": "18", "fre": "14", "hea": "9", "lon": "16", "lth": "8", "mar": "6", "pas": "17", "pen": "4", "tck": "11", "tec": "19", "agg": "13", "ant": "12", "bra": "5", "cmp": "16", "cnt": "20", "decisions": "8", "det": "14", "fla": "3", "ldr": "11", "otb": "10", "pos": "9", "tea": "18", "vis": "15", "wor": "7", "acc": "17", "agi": "19", "bal": "12", "jum": "8", "natF": "13", "pac": "14", "sta": "10", "strength": "20", "aer": "11", "cmd": "15", "com": "16", "ecc": "4", "han": "9", "kic": "8", "oneVsOne": "6", "pun": "7", "ref": "18", "tro": "14", "thr": "13"}
    ca = {'ca': 126}
    stats = {'aerA': 2.2, 'hdrsW': 4.2, 'blk': 3.3, 'clr': 4.4, 'tckC': 1.6, 'presA': 2.3, 'presC': 4.3, 'interceptions': 3.1, 'sprints': 4.9, 'possLost': 3.7, 'possWon': 2.3, 'drb': 0.2, 'opCrsA': 3.4, 'opCrsC': 2.7, 'psA': 4.2, 'psC': 1.2, 'prPasses': 1.0, 'opKp': 0.8, 'chC': 0.4, 'xa': 0.3, 'shot': 3.5, 'sht': 2.0, 'npXg': 1.9}
    tables = {'Stats': stats,
                'PlayerInfo': playerinfo,
                'Attributes': attributes,
                'Contract': contract,
                'Ca': ca}
    player_table = {'name': 'blabla', 'uid': '1', 'season': '23'}

    interact.insert(tables, player_table)

    playerinfo2 = [{'age': 30, 'rightfoot': 2, 'leftfoot': 3, 'mins': 45, 'division': 2, 'club': 3, 'nat': 2, 'eligible': 2, 'position': 5}, {'age': 30, 'rightfoot': 2, 'leftfoot': 3, 'mins': 45, 'division': 2, 'club': 3, 'nat': 2, 'eligible': 2, 'position': 6}, {'age': 30, 'rightfoot': 2, 'leftfoot': 3, 'mins': 45, 'division': 2, 'club': 3, 'nat': 2, 'eligible': 2, 'position': 7}, {'age': 30, 'rightfoot': 2, 'leftfoot': 3, 'mins': 45, 'division': 2, 'club': 3, 'nat': 2, 'eligible': 2, 'position': 8}]
    contract2 = {'beginDate': 2025, 'expiryDate': 2030, 'extension': 1, 'wage': 800000, 'releaseClauseFee': 500000, 'value': 80000000}
    attributes2 = {"cor": "5", "cro": "18", "dri": "16", "fin": "13", "fir": "7", "fre": "19", "hea": "12", "lon": "11", "lth": "9", "mar": "8", "pas": "14", "pen": "10", "tck": "6", "tec": "20", "agg": "15", "ant": "8", "bra": "17", "cmp": "13", "cnt": "12", "decisions": "10", "det": "9", "fla": "11", "ldr": "7", "otb": "16", "pos": "18", "tea": "15", "vis": "12", "wor": "14", "acc": "19", "agi": "6", "bal": "9", "jum": "13", "natF": "10", "pac": "8", "sta": "20", "strength": "7", "aer": "18", "cmd": "14", "com": "13", "ecc": "12", "han": "6", "kic": "17", "oneVsOne": "9", "pun": "16", "ref": "19", "tro": "14", "thr": "11"}
    ca2 = {'ca': 40}
    stats2 = {'aerA': 3.3, 'hdrsW': 2.7, 'blk': 3.5, 'clr': 1.3, 'tckC': 1.1, 'presA': 3.2, 'presC': 0.4, 'interceptions': 5.0, 'sprints': 2.3, 'possLost': 1.2, 'possWon': 0.0, 'drb': 1.4, 'opCrsA': 3.5, 'opCrsC': 3.9, 'psA': 0.4, 'psC': 2.3, 'prPasses': 3.2, 'opKp': 2.4, 'chC': 3.2, 'xa': 0.2, 'shot': 3.4, 'sht': 2.7, 'npXg': 2.3}
    tables2 = {'Stats': stats2,
                'PlayerInfo': playerinfo2,
                'Attributes': attributes2,
                'Contract': contract2,
                'Ca': ca2}
    player_table2 = {'name': 'blablabla', 'uid': '2', 'season': '24'}
    interact.insert(tables2, player_table2)
    
    playerinfo3 = [{'age': 24, 'rightfoot': 1, 'leftfoot': 2, 'mins': 105, 'division': 20, 'club': 1, 'nat': 1, 'eligible': 1, 'position': 2}]
    contract3 = {'beginDate': 2025, 'expiryDate': 2030, 'extension': 1, 'wage': 800000, 'releaseClauseFee': 500000, 'value': 80000000}
    attributes3 = {"cor": "5", "cro": "18", "dri": "16", "fin": "13", "fir": "7", "fre": "19", "hea": "12", "lon": "11", "lth": "9", "mar": "8", "pas": "14", "pen": "10", "tck": "6", "tec": "20", "agg": "15", "ant": "8", "bra": "17", "cmp": "13", "cnt": "12", "decisions": "10", "det": "9", "fla": "11", "ldr": "7", "otb": "16", "pos": "18", "tea": "15", "vis": "12", "wor": "14", "acc": "19", "agi": "6", "bal": "9", "jum": "13", "natF": "10", "pac": "8", "sta": "20", "strength": "7", "aer": "18", "cmd": "14", "com": "13", "ecc": "12", "han": "6", "kic": "17", "oneVsOne": "9", "pun": "16", "ref": "19", "tro": "14", "thr": "11"}
    ca3 = {'ca': 130}
    stats3 = {'aerA': 3.3, 'hdrsW': 2.7, 'blk': 3.5, 'clr': 1.3, 'tckC': 1.1, 'presA': 3.2, 'presC': 0.4, 'interceptions': 5.0, 'sprints': 2.3, 'possLost': 1.2, 'possWon': 0.0, 'drb': 1.4, 'opCrsA': 3.5, 'opCrsC': 3.9, 'psA': 0.4, 'psC': 2.3, 'prPasses': 3.2, 'opKp': 2.4, 'chC': 3.2, 'xa': 0.2, 'shot': 3.4, 'sht': 2.7, 'npXg': 2.3}
    tables3 = {'Stats': stats3,
                'PlayerInfo': playerinfo3,
                'Attributes': attributes3,
                'Contract': contract3,
                'Ca': ca3}
    player_table3 = {'name': 'blablablabla', 'uid': '3', 'season': '25'}

    interact.insert(tables3, player_table3)
    
    interact.commit()
    
    ###### Test position filter ######
    
    # Expects 0 players and NoPlayerFoundError to be raised
    with pytest.raises(NoPlayerFoundError):
        _, _ = _select_helper(['AML'])
            
    # Expects only players with position 1 (ML)
    _select_tst_helper(expected_positions={1}, expected_uids={'1'}, raw_positions=['ML'])

    # Expects players with positions 1 (ML) and 2 (MC)
    _select_tst_helper(expected_positions={1, 2}, expected_uids={'1', '3'}, raw_positions=['ML', 'MC'])
    
    # Expects players with positions 1 (ML) and 2 (MC) and 5, 6, 7, 8 (DR, GK, STC, DC)
    _select_tst_helper(expected_positions={1, 2, 5, 6, 7, 8}, expected_uids={'1', '2', '3'}, raw_positions=['ML', 'MC', 'DR', 'GK', 'STC', 'DC'])
    
    ###### Test mins filter ######
    
    # Expect no players and NoPlayerFoundError to be raised
    with pytest.raises(NoPlayerFoundError):
        _, _ = _select_helper(mins=2000000)
    
    # Expect players with more than 0 mins
    _select_tst_helper(expected_uids={'1', '2', '3'}, mins=0)
    
    # Expect players with more than 40 mins
    _select_tst_helper(expected_uids={'2', '3'}, mins=40)
    
    # Expect players with less than 100 mins
    # ---
    
    ###### Test name filter ######
    
    # Expect no players and NoPlayerFoundError to be raised
    with pytest.raises(NoPlayerFoundError):
        _, _ = _select_helper(name='x')
    
    # Expect all players
    _select_tst_helper(expected_uids={'1', '2', '3'}, name=None)
    
    # Expect player called 'blablablabla'
    _select_tst_helper(expected_uids={'3'}, name=['blablablabla'])
    
    # Expect player called 'blabla' or 'blablabla'
    _select_tst_helper(expected_uids={'1', '2'}, name=['blabla', 'blablabla'])
    
    ###### Test division filter ######
    
    # Expect no players and NoPlayerFoundError to be raised
    with pytest.raises(NoPlayerFoundError):
        _, _ = _select_helper(division='x')
    
    # Expect all players
    _select_tst_helper(expected_uids={'1', '2', '3'}, division=None)
    
    # Expect player 3
    _select_tst_helper(expected_uids={'3'}, division='Spanish Second Division')
    
    # Expect player 1 and 3
    _select_tst_helper(expected_uids={'1', '3'}, division=['Spanish Second Division', 'Norwegian Fourth Division Telemark'])
    
    ###### Test min_ca filter ######
    # Expect no players and NoPlayerFoundError to be raised
    with pytest.raises(NoPlayerFoundError):
        _, _ = _select_helper(min_ca=201)
    
    # Expect all players
    _select_tst_helper(expected_uids={'1', '2', '3'}, min_ca=0)
    
    # Expect player 1 and 3
    _select_tst_helper(expected_uids={'1', '3'}, min_ca=100)
    
    ###### Test eligible filter ######
    # Expect all players
    _select_tst_helper(expected_uids={'1', '2', '3'}, eligible=None)
    
    # Expect player 1 and 3
    _select_tst_helper(expected_uids={'1', '3'}, eligible='Yes')
    
    # Expect player 2
    _select_tst_helper(expected_uids={'2'}, eligible='No')
    
    ###### Test season filter ######
    # Expect all players
    _select_tst_helper(expected_uids={'1', '2', '3'}, season=None)
    
    # Expect player 1 and 3
    _select_tst_helper(expected_uids={'1', '3'}, season=['23', '25'])
    
    # Expect player 2
    _select_tst_helper(expected_uids={'2'}, season='24')


    remove_all_rows()


def _select_tst_helper(expected_positions=None, expected_uids=None, raw_positions=None,
                        mins=0, name=None, division=None, min_ca=0, eligible=None, season=None):
    found_positions, found_uids = _select_helper(pos=raw_positions, mins=mins, name=name,
                                                division=division, min_ca=min_ca, eligible=eligible, season=season)
    
    if expected_positions:
        assert found_positions == expected_positions, f'Expected values {expected_positions}, but found values {found_positions}'
    
    assert found_uids == expected_uids, f'Expected values {expected_uids}, but found values {found_uids}'

def _select_helper(pos=None, mins=0, name=None, division=None, min_ca=0, eligible=None, season=None):
    res = [row for row in interact.select(pos=pos, mins=mins, name=name, division=division, min_ca=min_ca, eligible=eligible, season=season)]
    
    positions, players = set(), set()
    
    for _, tables_of_player in res:
        for table_of_player in tables_of_player:
    
            positions.add(table_of_player.PlayerInfo.position)
            players.add(table_of_player.Player.uid)
    
    return positions, players


def remove_all_rows():
    interact.session.flush()
    table_names = ('stats', '"playerInfo"', 'attributes', 'contract', 'ca', 'player', 'foot', 'position', 'club', 'nat', 'division', 'eligible')
    query = text(f'TRUNCATE TABLE {', '.join(table_names)} RESTART IDENTITY CASCADE;')
    interact.session.execute(query)
    interact.session.commit()