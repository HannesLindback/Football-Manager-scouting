from tables import (Player, PlayerInfo, Attributes, Stats, Ca, Contract, Base,
                    Position, Division, Foot, Nat, Club, Eligible)
from sqlalchemy.orm import Session
from sqlalchemy import select, create_engine, and_, func
from tqdm import tqdm
from errors import NoPlayerFoundError
import sqlalchemy
from sqlalchemy.dialects.postgresql import insert
from typing import Dict, Tuple, Iterable


class Setup:
    
    @classmethod
    def create_engine(self,
                      user: str,
                      password: str,
                      host: str,
                      database: str
                      ) -> sqlalchemy.engine.Engine:
        """
        Creates and returns a SQLAlchemy engine for connecting to a PostgreSQL database.

        Parameters:
        ----------
        user : str
            The username for authenticating the database connection.
        password : str
            The password for authenticating the database connection.
        host : str
            The hostname or IP address of the database server.
        database : str
            The name of the database to connect to.

        Returns:
        -------
        sqlalchemy.engine.Engine
            A SQLAlchemy Engine instance configured to connect to the specified PostgreSQL database.

        Notes:
        ------
        - Uses `psycopg2` as the PostgreSQL driver.
        - Constructs the database URL with the provided credentials and database details.
        """
        
        url = f'postgresql+psycopg2://{user}:{password}@{host}/{database}'
        
        engine = create_engine(url)
        
        return engine


class Interact:

    def __init__(self, engine) -> None:
        self.engine = engine
        self.session = Session(engine)

    def commit(self,
               close: bool = True,
               verbose: bool = False) -> None:
        
        if verbose:
            print('Commiting entries...')
        
        self.session.commit()
        if close:
            self.session.close()
        
        if verbose:
            print('All entries commited to database!')

    def create(self,
               drop: bool = False) -> None:
        """
        Creates the database schema by generating all tables from ORM models, with an option to drop existing tables.

        Parameters:
        ----------
        drop : bool, optional
            If set to `True`, drops all existing tables in the database before creating new ones. Default is `False`.

        Notes:
        ------
        - Uses `Base.metadata.create_all` to generate tables defined by ORM models in the metadata.
        - Drops all tables if `drop` is set to `True` using `Base.metadata.drop_all`.
        """
        
        print('Creating database...')
        if drop:
            Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        print('Database created.')

    def insert(self,
               tables: Dict[str, Dict[str, str | float] | Tuple[Dict[str, int]]],
               player_table: Dict[str, str | int],
               ) -> None:
        """
        Inserts player data and associated tables into the database using the provided ORM models.

        Parameters:
        ----------
        tables : dict
            A dictionary where keys are table names and values are either a dictionary of attributes 
            or a tuple of dictionaries representing individual records to be inserted.
        player_table : dict
            A dictionary of attributes representing the player record to be inserted.

        Notes:
        ------
        - The method constructs player and table objects using the imported ORM models.
        - Player records are added to the session before committing, enabling batch insertion.
        """
       
        global_vars = globals()
        
        player = Player(**player_table)
        
        for table_name, table in tables.items():
            table_obj = global_vars[table_name]
            
            if not isinstance(table, (tuple, list)):
                table_obj(_player=player, **table)

            else:
                for t in table:
                    table_obj(_player=player, **t)
    
        self.session.add(player)
            
    def lookup_tables(self, lookup_table_name: str, lookup: Tuple[str, str]):
        """
        Retrieves the `id` of a row in a specified lookup table where a column matches a given value. 
        If no matching row exists, it inserts a new row with the specified column-value pair and retrieves its `id`.

        Args:
            lookup_table_name (str): The name of the lookup table to query or insert into. This should match
                the name of a table defined in the global scope.
            lookup (Tuple[str, str]): A tuple where the first element is the name of the column to filter by,
                and the second element is the value to match in that column.

        Returns:
            int: The `id` of the row that matches the specified column-value pair, whether found or newly inserted.

        Example:
            To get or create an entry in table `Division` where the column `division` has the value
            'First Division', call:
            
            ```
            division_id = lookup_tables("Division", ("division", "First Division"))
            ```
        """
        
        global_vars = globals()
        
        lookup_table = global_vars[lookup_table_name]
        lookup_column_obj = getattr(lookup_table, lookup[0])
        
        id = self.session.query(lookup_table.id).filter(lookup_column_obj == lookup[1]).first()
        
        if id is None:
            self.session.add(lookup_table(**{lookup[0]: lookup[1]}))
            self.commit()
        
        id = self.session.query(lookup_table.id).filter(lookup_column_obj == lookup[1]).first()[0]

        return id

    def select(self,
               pos: Iterable[str] = None,
               mins: int = 0,
               name: Iterable[str] | str = None,
               division: Iterable[str] | str = None,
               min_ca: int = 0,
               eligible: int = None,
               season: int = None,
               columns = (Player._id, Player, PlayerInfo,
                          Ca, Contract, Stats, Attributes)):
        """
        Retrieves player records from the database based on various filtering criteria.

        Parameters:
        ----------
        pos : iterable of str, optional
            A list or single value of positions to filter players by. 
            If provided, only players in these specified positions will be included.
        mins : int, optional
            The minimum number of minutes played to filter players. Default is 0.
        name : iterable of str or str, optional
            The name(s) of players to filter by. This can be a single name or a list/tuple of names.
        division : iterable of str or str, optional
            The division(s) to filter players by. Can be a single division or a list/tuple of divisions.
        min_ca : int, optional
            The minimum current ability (CA) value to filter players by. Default is 0.
        eligible : int, optional
            The eligibility status to filter players by. If provided, only players matching this status will be selected.
        season : int, optional
            The season year to filter players by. If provided, only players from this specified season will be included.
        columns : tuple, optional
            The columns to retrieve in the query. Defaults to a predefined set of player-related tables.

        Yields:
        -------
        tuple
            A tuple containing the player's unique ID and a list of associated rows for that player.

        Raises:
        ------
        NoPlayerFoundError
            If no players match the specified filtering criteria.

        Notes:
        ------
        - Constructs a dynamic query using SQLAlchemy to filter players based on the provided parameters.
        - Joins various related tables (e.g., PlayerInfo, Ca, Contract, etc.) to retrieve comprehensive player data.
        - Processes results and groups them by player ID, yielding results in a structured format.
        - Utilizes `tqdm` to display progress while processing rows, enhancing user experience.
        """
        
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

        if n_rows == 0:
            raise NoPlayerFoundError('No players found!')

        row = next(results)
        previous_id = row.Player._id
        
        rows = [row[1:]]
        
        for row in tqdm(results, desc='Processing rows', total=n_rows):
            current_id = row.Player._id
            
            if current_id != previous_id:
                yield row.Player.uid, rows
                rows = []
                previous_id = current_id

            rows.append(row[1:])

        if rows:
            yield row.Player.uid, rows