from tables import (Player, PlayerInfo, Attributes, Stats, Ca, Contract, Base,
                    Position, Division, Foot, Nat, Club, Eligible)
from sqlalchemy.orm import Session
from sqlalchemy import select, create_engine, and_, func
from tqdm import tqdm


class Setup:
    
    @classmethod
    def create_engine(self, user, password, host, database):
        url = f'postgresql+psycopg2://{user}:{password}@{host}/{database}'
        engine = create_engine(url)
        return engine


class Interact:

    def __init__(self, engine) -> None:
        self.engine = engine
        self.session = Session(engine)

    def commit(self, close=True):
        print('Commiting entries...')
        self.session.commit()
        if close:
            self.session.close()
        print('All entries commited to database!')

    def create(self, drop=False):
        if self.engine.url.database == 'historic':
            inp = input("Du är påväg att fucka med den historiska databasen, är du säker på att du vill fortsätta??\n")
            
            if inp.lower() != 'yes':
                exit()
        
        print('Creating database...')
        if drop:
            Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        print('Database created.')

    def insert(self,
               tables: dict=None,
               lookup_tables: dict=None,
               player_table: dict=None) -> None:
        
        def add_tables():
            player = Player(**player_table)
            
            for table_name, table in tables.items():
                table_obj = global_vars[table_name]
                
                if not isinstance(table, (tuple, list)):
                    table_obj(_player=player, **table)

                else:
                    for t in table:
                        table_obj(_player=player, **t)
        
            self.session.add(player)
        
        def add_lookup_tables():
            for table_name, table in lookup_tables.items():
                table_obj = global_vars[table_name]
                
                if not isinstance(table, (tuple, list)):
                    self.session.add(table_obj(**table))
                    
                else:
                    for t in table:
                        self.session.add(table_obj(**t))
        
        global_vars = globals()
        
        if tables:
            add_tables()
        
        if lookup_tables:
            add_lookup_tables()

    def select(self,
               pos=None,
               mins: int=0,
               name: str=None,
               division: str=None,
               min_ca: int=0,
               eligible: int=None,
               season: int=None,
               columns = (Player._id, Player, PlayerInfo,
                          Ca, Contract, Stats, Attributes)):

        def ands(pos, name, division, eligible):
            ands = []
            ands.append(Ca.ca >= min_ca)
            ands.append(PlayerInfo.mins >= mins)

            if pos:
                pos = [res[0] for res in self.session.query(Position.id) \
                            .filter(Position.position.in_(pos)).all()]

                ands.append(Player._id.in_(select(Player._id).join(PlayerInfo).filter(PlayerInfo.position.in_(pos))))

            if division:

                if not isinstance(division, (tuple, list)):
                    division = [division]

                division_id = [res[0] for res in self.session.query(Division.id) \
                               .filter(Division.division.in_(division)).all()]

                ands.append(PlayerInfo.division.in_(division_id))

            if name:
                ands.append(Player.name.in_(name if isinstance(name, (tuple, list)) else [name]))

            if eligible is not None:
                eligible_id = [res[0] for res in self.session.query(Eligible.id) \
                               .filter(Eligible.eligible == eligible).all()][0]
                
                ands.append(PlayerInfo.eligible == eligible_id)

            if season is not None:
                ands.append(Player.season == season)

            return and_(*ands)

        n_rows = self.session.query(func.count(Player._id)) \
                             .join(PlayerInfo).join(Ca) \
                             .filter(ands(pos, name, division, eligible)) \
                             .scalar()

        
        results = self.session.query(*columns) \
                              .join(PlayerInfo, PlayerInfo._playerID == Player._id) \
                              .join(Ca, Ca._playerID == Player._id) \
                              .join(Contract, Contract._playerID == Player._id) \
                              .join(Attributes, Attributes._playerID == Player._id) \
                              .join(Stats, Stats._playerID == Player._id) \
                              .join(Division, PlayerInfo.division == Division.id) \
                              .join(Club, PlayerInfo.club == Club.id) \
                              .join(Nat, PlayerInfo.nat == Nat.id) \
                              .join(Eligible, PlayerInfo.eligible == Eligible.id) \
                              .filter(ands(pos, name, division, eligible)) \
                              .order_by(Player._id) \

        results = self.session.execute(results)

        first_row = next(results)
        previous_id = first_row.Player._id
        
        rows = [first_row[1:]]
        
        for row in tqdm(results, desc='Processing rows', total=n_rows):
            current_id = row.Player._id
            
            if current_id != previous_id:
                yield row.Player.uid, rows
                rows = []
                previous_id = current_id

            rows.append(row[1:])


if __name__ == '__main__':
    engine = Setup.create_engine('postgres',
                                 'root',
                                 'localhost:5432',
                                 database='players')
    
    interact = Interact(engine)
    
    # interact.create(drop=True)
    
    # tables = {
    #     'Position': [],
    #     'Foot': [],
    #     'Eligible': [
    #         {'eligible': 'Yes', 'id': 1}, {'eligible': 'No', 'id': 0}]
    #           }
    
    
    # for id, pos in enumerate('GK DC DR DL WBR DM WBL MR MC ML AMR AMC AML STC'.split()):
    #     tables['Position'].append({'position': pos, 'id': id})
        
    # for id, strength in enumerate('-,Very Weak,Weak,Reasonable,Fairly Strong,Strong,Very Strong'.split(',')):
    #     tables['Foot'].append({'foot': strength, 'id': id})

    # interact.insert(lookup_tables=tables)
    # interact.commit()