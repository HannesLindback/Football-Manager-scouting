from preprocess_data import Preprocess
from server import Interact, Setup
from request_data import Request
import argparse
from tqdm import tqdm


class Insert:
    
    def __init__(self, user, password, port, database):
        engine = Setup.create_engine(user,
                                     password,
                                     port,
                                     database=database)

        self.user = user
        self.password = password
        self.port = port

        self.source_connection = Interact(engine)

    def _insert_to_database(self, row, process, connection):
        tables, lookup_tables = process(**row)

        player = tables['Player']
        del tables['Player']

        connection.insert(tables=tables, player_table=player, lookup_tables=lookup_tables)

    def insert_from_rtf(self, path, season, total=None):
        process = Preprocess(season=season)

        print('Inserting entries...')
        for row in tqdm(process.from_rtf_file(path), desc='Entry', total=total):
            self._insert_to_database(row, process, self.source_connection)

        self.source_connection.commit()

    def insert_from_database(self):
        target_db = input('Target database name: ')

        engine = Setup.create_engine(self.user,
                                     self.password,
                                     self.port,
                                     database=target_db)
        
        target_connection = Interact(engine)
        request = Request()
        
        lookup_tables = request.fetch_lookup_tables(connection=target_connection)
        division_id = max([id for id in lookup_tables['Division'].values()])
        club_id = max([id for id in lookup_tables['Club'].values()])
        nat_id = max([id for id in lookup_tables['Nat'].values()])
        
        process = Preprocess(division_id=division_id,
                             club_id=club_id,
                             nat_id=nat_id)
        process.lookup_tables.update(lookup_tables)
        
        for row in request.iterator(filter={},
                                    connection=self.source_connection):
            
            self._insert_to_database(row, process, target_connection)
            
        target_connection.commit()
                    
        
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--user', type=str, default='postgres')
    ap.add_argument('--password', type=str, default='root')
    ap.add_argument('--port', type=str, default='localhost:5432')
    ap.add_argument('--database', type=str, default='players')
    ap.add_argument('--from_database', type=bool, default=False)
    ap.add_argument('--from_rtf', type=bool, default=False)
    ap.add_argument('--season', type=int, default=27)
    ap.add_argument('--total', type=int)
    ap.add_argument('--path', type=str, default='/home/hantan/FM/data.rtf')
    args = ap.parse_args()

    insert = Insert(args.user, args.password, args.port, args.database)
    
    if args.from_rtf:
        insert.insert_from_rtf(path=args.path, total=args.total, season=args.season)
    if args.from_database:
        insert.insert_from_database()
    