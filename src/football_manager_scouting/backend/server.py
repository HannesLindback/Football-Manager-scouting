from typing import Dict, Tuple, Iterable
from football_manager_scouting.backend.tables import (Player, PlayerInfo, Attributes, Stats, Ca, Contract, Base,
                    Position, Division, Foot, Nat, Club, Eligible)
from football_manager_scouting.backend.errors import NoPlayerFoundError, UnexpecteTableNameError, UnexpectedColumnNameError
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy import select, create_engine, and_, func, inspect
from sqlalchemy.exc import OperationalError
from tqdm import tqdm

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

        Raises:
        ------
        OperationError
            If the specified database does not exist.
            
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
        
        try:
            engine.connect()
            
        except OperationalError:
            stmnt = f'Error: Database {database} does not exist! An empty database must be created before use.'
            raise OperationalError(statement=stmnt, params=None, orig=OperationalError)
        
        return engine


class Interact:

    TABLE_NAMES = ('player', 'playerInfo', 'attributes', 'stats',
                   'ca', 'contract', 'position', 'division', 'foot',
                   'nat', 'club', 'eligible')

    def __init__(self, engine) -> None:
        self.engine = engine
        self.session = Session(engine)
        
        self._check_if_tables_not_exist()

    def _check_if_tables_not_exist(self):
        if not all([inspect(self.engine).has_table(table_name)
                    for table_name in self.TABLE_NAMES]):
            print("Table relation not found")
            self.create(drop=False)
                
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
               drop: bool = False,
               verbose: bool = True) -> None:
        """
        Creates the database schema by generating all tables from ORM models, with an option to drop existing tables.

        Parameters:
        ----------
        drop : bool, optional
            If set to `True`, drops all existing tables in the database before creating new ones. Default is `False`.

        Raises:
        ------
        ValueError
            If given an argument of the wrong type.

        Notes:
        ------
        - Uses `Base.metadata.create_all` to generate tables defined by ORM models in the metadata.
        - Drops all tables if `drop` is set to `True` using `Base.metadata.drop_all`.
        """

        if not isinstance(drop, bool):
            raise ValueError(f'Expected argument `drop` to be of type bool but got {type(drop)} instead.')
        if not isinstance(verbose, bool):
            raise ValueError(f'Expected argument `verbose` to be of type bool but got {type(verbose)} instead.')

        if verbose:
            print('Creating database...')

        if drop:
            Base.metadata.drop_all(self.engine)

        Base.metadata.create_all(self.engine)

        if verbose:
            print('Database created.')

    def insert(self,
               tables: Dict[str, Dict[str, str | float] |
                                 Iterable[Dict[str, int]]],
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

        Raises:
        ------
        UnexpecteTableNameError
            If given a table name not import from tables.py.
        UnexpectedColumnNameError
            If given a column name not present in the table mapping.

        Notes:
        ------
        - The method constructs player and table objects using the imported ORM models.
        - Player records are added to the session before committing, enabling batch insertion.
        """
        
        global_vars = globals()
        
        try:
            player = Player(**player_table)
        except TypeError:
            expected_cols = ', '.join([column.name for column in Player.__table__.columns if not column.name.startswith('_')])
            found_cols = ', '.join(list(player_table.keys()))
            raise UnexpectedColumnNameError(f"Unexpected mapped column!\nExpected columns: {expected_cols},\nbut found columns: {found_cols}")
        
        for table_name, table in tables.items():
            
            try:
                table_obj = global_vars[table_name]
            except KeyError:
                raise UnexpecteTableNameError(f"Cannot find ORM table mapping with the name `{table_name}`.")
            
            if not isinstance(table, (tuple, list)):
                try:
                    table_obj(_player=player, **table)
                except TypeError:
                    expected_cols = ', '.join([column.name for column in table_obj.__table__.columns if not column.name.startswith('_')])
                    found_cols = ', '.join(list(table.keys()))
                    raise UnexpectedColumnNameError(f"Unexpected mapped column!\nExpected columns: {expected_cols},\nbut found columns: {found_cols}")

            else:
                for t in table:
                    try:
                        table_obj(_player=player, **t)
                    except TypeError:
                        expected_cols = ', '.join([column.name for column in table_obj.__table__.columns if not column.name.startswith('_')])
                        found_cols = ', '.join(list(t.keys()))
                        raise UnexpectedColumnNameError(f"Unexpected mapped column!\nExpected columns: {expected_cols},\nbut found columns: {found_cols}")
        
        self.session.add(player)

            
    def get_lookup_id(self,
                      lookup_table_name: str,
                      lookup: Tuple[str, str]):
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

        Raises:
        ------
        UnexpecteTableNameError
            If given a table name not import from tables.py.
        UnexpectedColumnNameError
            If given a column name not present in the table mapping.

        Example:
            To get or create an entry in table `Division` where the column `division` has the value
            'First Division', call:
            
            ```
            division_id = lookup_tables("Division", ("division", "First Division"))
            ```
        """
        
        global_vars = globals()
        
        try:
            lookup_table_obj = global_vars[lookup_table_name]
        except KeyError:
            raise UnexpecteTableNameError(f"Cannot find ORM table mapping with the name `{lookup_table_name}`.")
        
        # Get the lookup column from the table. E.g. the position column from the Position table.
        try:
            lookup_column_obj = getattr(lookup_table_obj, lookup[0])
        except AttributeError:
            expected_cols = ', '.join([column.name for column in lookup_table_obj.__table__.columns if not column.name.startswith('_') and not column.name == 'id'])
            raise UnexpectedColumnNameError(f'Unexpected mapped column!\nExpected columns: {expected_cols},\nbut found column: {lookup[0]}')
        
        id = self.session.query(lookup_table_obj.id).filter(lookup_column_obj == lookup[1]).first()
        
        if id is None:
            try:
                entry = lookup_table_obj(**{lookup[0]: lookup[1]})
            except TypeError:
                expected_cols = ', '.join([column.name for column in lookup_table_obj.__table__.columns if not column.name.startswith('_') and not column.name == 'id'])
                raise UnexpectedColumnNameError(f'Unexpected mapped column!\nExpected columns: {expected_cols},\nbut found column: {lookup[0]}')
            
            self.session.add(entry)
            self.commit()
        
            id = self.session.query(lookup_table_obj.id).filter(lookup_column_obj == lookup[1]).first()

        return id[0]

    def select(self,
               pos: Iterable[str] = None,
               mins: int = 0,
               name: Iterable[str] | str = None,
               division: Iterable[str] | str = None,
               min_ca: int = 0,
               eligible: str = None,
               season: Iterable[int] = None,
               columns = (Player, PlayerInfo,
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
                ands.append(Player.season.in_(season if isinstance(season, (tuple, list)) else [season]))

            return and_(*ands)

        n_rows = self.session.query(func.count(Player._id)) \
                             .join(PlayerInfo).join(Ca) \
                             .filter(ands(pos, name, division, eligible)) \
                             .scalar()

        results_query = select(*columns) \
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
                  .order_by(Player._id)

        results = self.session.execute(results_query)

        if n_rows == 0:
            raise NoPlayerFoundError('No players found with the given filters.')

        rows_of_one_player = []
        row = next(results)
        current_id = row.Player.uid
        rows_of_one_player.append(row)
        
        # Iterate through all retrieved rows.
        with tqdm(total=n_rows, desc='Processing rows') as pbar: 
            while row:

                try:
                    row = next(results)
                except StopIteration:
                    yield row.Player.uid, rows_of_one_player
                    break
                
                pbar.update()
                
                next_id = row.Player.uid

                # Yield the current rows if the next row is of a new player and start over.
                if current_id != next_id:
                    yield current_id, rows_of_one_player
                    rows_of_one_player = []
                    current_id = next_id

                rows_of_one_player.append(row)
