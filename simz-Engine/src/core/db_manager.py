import os
import json
from typing import Dict, List, Any, Union, Optional
from pathlib import Path
import duckdb


class DBManager:
    """
    DBManager handles the DuckDB database operations for simulation runs.
    """
    
    def __init__(self, file_manager=None):
        """
        Initialize the DBManager with an optional FileManager instance.
        
        Args:
            file_manager: Optional FileManager instance to use for file operations.
                         If None, the DBManager will operate directly on files.
        """
        self.file_manager = file_manager
    
    def initialize_db(self, db_path: Union[str, Path]) -> duckdb.DuckDBPyConnection:
        """
        Initialize a DuckDB database for a simulation run.
        
        Args:
            db_path: Path to the database file
            
        Returns:
            DuckDB connection
        """
        db_path = Path(db_path)
        db_path.parent.mkdir(exist_ok=True, parents=True)
        
        # Create the database connection
        conn = duckdb.connect(str(db_path))
        
        # Initialize base tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS simulation_metadata (
                id VARCHAR PRIMARY KEY,
                name VARCHAR,
                description VARCHAR,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                status VARCHAR,
                parameters VARCHAR
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS simulation_events (
                id VARCHAR PRIMARY KEY,
                event_time DOUBLE,
                entity_id VARCHAR,
                event_type VARCHAR,
                event_data VARCHAR,
                processed BOOLEAN DEFAULT FALSE
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS simulation_entities (
                id VARCHAR PRIMARY KEY,
                entity_type VARCHAR,
                name VARCHAR,
                properties VARCHAR,
                created_at DOUBLE,
                updated_at DOUBLE
            )
        """)
        
        return conn
    
    def create_run_db(self, project_name: str, run_id: str) -> Path:
        """
        Create a new DuckDB database for a simulation run.
        
        Args:
            project_name: Name of the project
            run_id: ID of the run
            
        Returns:
            Path to the created database file
            
        Raises:
            ValueError: If the project or run doesn't exist
        """
        if self.file_manager is None:
            raise ValueError("FileManager is required to create a run database.")
        
        project_path = self.file_manager.get_project_path(project_name)
        run_path = project_path / "Run" / run_id
        
        if not run_path.exists():
            raise ValueError(f"Run '{run_id}' does not exist in project '{project_name}'.")
        
        db_path = run_path / f"{run_id}.db"
        
        # Initialize the database
        conn = self.initialize_db(db_path)
        
        # Add initial metadata
        run_config = {
            "project_name": project_name,
            "run_id": run_id,
            "status": "initialized"
        }
        
        conn.execute("""
            INSERT INTO simulation_metadata 
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?)
        """, (run_id, f"Run {run_id}", "", "initialized", json.dumps(run_config)))
        
        conn.close()
        
        return db_path
    
    def get_db_connection(self, db_path: Union[str, Path]) -> duckdb.DuckDBPyConnection:
        """
        Get a connection to a DuckDB database.
        
        Args:
            db_path: Path to the database file
            
        Returns:
            DuckDB connection
            
        Raises:
            FileNotFoundError: If the database file doesn't exist
        """
        db_path = Path(db_path)
        
        if not db_path.exists():
            raise FileNotFoundError(f"Database file '{db_path}' does not exist.")
        
        return duckdb.connect(str(db_path))
    
    def get_run_db_connection(self, project_name: str, run_id: str) -> duckdb.DuckDBPyConnection:
        """
        Get a connection to a run's DuckDB database.
        
        Args:
            project_name: Name of the project
            run_id: ID of the run
            
        Returns:
            DuckDB connection
            
        Raises:
            ValueError: If the project or run doesn't exist
            FileNotFoundError: If the database file doesn't exist
        """
        if self.file_manager is None:
            raise ValueError("FileManager is required to get a run database connection.")
        
        project_path = self.file_manager.get_project_path(project_name)
        run_path = project_path / "Run" / run_id
        
        if not run_path.exists():
            raise ValueError(f"Run '{run_id}' does not exist in project '{project_name}'.")
        
        db_path = run_path / f"{run_id}.db"
        
        return self.get_db_connection(db_path)
    
    def add_entity(self, conn: duckdb.DuckDBPyConnection, entity_id: str, 
                  entity_type: str, name: str, properties: Dict) -> None:
        """
        Add a new entity to the simulation.
        
        Args:
            conn: DuckDB connection
            entity_id: Unique ID for the entity
            entity_type: Type of the entity
            name: Name of the entity
            properties: Properties of the entity as a dictionary
            
        Raises:
            ValueError: If an entity with the same ID already exists
        """
        # Check if entity already exists
        result = conn.execute(
            "SELECT COUNT(*) FROM simulation_entities WHERE id = ?", 
            (entity_id,)
        ).fetchone()[0]
        
        if result > 0:
            raise ValueError(f"Entity with ID '{entity_id}' already exists.")
        
        current_time = conn.execute("SELECT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)").fetchone()[0]
        
        conn.execute("""
            INSERT INTO simulation_entities 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entity_id, 
            entity_type, 
            name, 
            json.dumps(properties),
            current_time,
            current_time
        ))
    
    def update_entity(self, conn: duckdb.DuckDBPyConnection, entity_id: str, 
                     properties: Dict) -> None:
        """
        Update an entity's properties.
        
        Args:
            conn: DuckDB connection
            entity_id: ID of the entity to update
            properties: New properties of the entity as a dictionary
            
        Raises:
            ValueError: If the entity doesn't exist
        """
        # Check if entity exists
        result = conn.execute(
            "SELECT COUNT(*) FROM simulation_entities WHERE id = ?", 
            (entity_id,)
        ).fetchone()[0]
        
        if result == 0:
            raise ValueError(f"Entity with ID '{entity_id}' does not exist.")
        
        current_time = conn.execute("SELECT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)").fetchone()[0]
        
        conn.execute("""
            UPDATE simulation_entities 
            SET properties = ?, updated_at = ?
            WHERE id = ?
        """, (json.dumps(properties), current_time, entity_id))
    
    def get_entity(self, conn: duckdb.DuckDBPyConnection, entity_id: str) -> Dict[str, Any]:
        """
        Get an entity's information.
        
        Args:
            conn: DuckDB connection
            entity_id: ID of the entity to get
            
        Returns:
            Entity information as a dictionary
            
        Raises:
            ValueError: If the entity doesn't exist
        """
        result = conn.execute("""
            SELECT id, entity_type, name, properties, created_at, updated_at 
            FROM simulation_entities 
            WHERE id = ?
        """, (entity_id,)).fetchone()
        
        if result is None:
            raise ValueError(f"Entity with ID '{entity_id}' does not exist.")
        
        return {
            "id": result[0],
            "entity_type": result[1],
            "name": result[2],
            "properties": json.loads(result[3]),
            "created_at": result[4],
            "updated_at": result[5]
        }
    
    def add_event(self, conn: duckdb.DuckDBPyConnection, event_id: str, 
                 event_time: float, entity_id: str, event_type: str, 
                 event_data: Dict) -> None:
        """
        Add a new event to the simulation.
        
        Args:
            conn: DuckDB connection
            event_id: Unique ID for the event
            event_time: Time of the event
            entity_id: ID of the entity associated with the event
            event_type: Type of the event
            event_data: Data associated with the event as a dictionary
            
        Raises:
            ValueError: If an event with the same ID already exists
        """
        # Check if event already exists
        result = conn.execute(
            "SELECT COUNT(*) FROM simulation_events WHERE id = ?", 
            (event_id,)
        ).fetchone()[0]
        
        if result > 0:
            raise ValueError(f"Event with ID '{event_id}' already exists.")
        
        conn.execute("""
            INSERT INTO simulation_events 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            event_id, 
            event_time, 
            entity_id, 
            event_type, 
            json.dumps(event_data),
            False
        ))
    
    def get_events(self, conn: duckdb.DuckDBPyConnection, 
                  start_time: Optional[float] = None, 
                  end_time: Optional[float] = None,
                  entity_id: Optional[str] = None,
                  event_type: Optional[str] = None,
                  processed: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Get events from the simulation based on filters.
        
        Args:
            conn: DuckDB connection
            start_time: Optional start time filter
            end_time: Optional end time filter
            entity_id: Optional entity ID filter
            event_type: Optional event type filter
            processed: Optional processed status filter
            
        Returns:
            List of events as dictionaries
        """
        query = """
            SELECT id, event_time, entity_id, event_type, event_data, processed 
            FROM simulation_events 
            WHERE 1=1
        """
        params = []
        
        if start_time is not None:
            query += " AND event_time >= ?"
            params.append(start_time)
        
        if end_time is not None:
            query += " AND event_time <= ?"
            params.append(end_time)
        
        if entity_id is not None:
            query += " AND entity_id = ?"
            params.append(entity_id)
        
        if event_type is not None:
            query += " AND event_type = ?"
            params.append(event_type)
        
        if processed is not None:
            query += " AND processed = ?"
            params.append(processed)
        
        query += " ORDER BY event_time ASC"
        
        results = conn.execute(query, params).fetchall()
        
        return [
            {
                "id": row[0],
                "event_time": row[1],
                "entity_id": row[2],
                "event_type": row[3],
                "event_data": json.loads(row[4]),
                "processed": row[5]
            }
            for row in results
        ]
    
    def mark_event_processed(self, conn: duckdb.DuckDBPyConnection, event_id: str) -> None:
        """
        Mark an event as processed.
        
        Args:
            conn: DuckDB connection
            event_id: ID of the event to mark as processed
            
        Raises:
            ValueError: If the event doesn't exist
        """
        result = conn.execute(
            "SELECT COUNT(*) FROM simulation_events WHERE id = ?", 
            (event_id,)
        ).fetchone()[0]
        
        if result == 0:
            raise ValueError(f"Event with ID '{event_id}' does not exist.")
        
        conn.execute("""
            UPDATE simulation_events 
            SET processed = TRUE
            WHERE id = ?
        """, (event_id,))
    
    def create_custom_table(self, conn: duckdb.DuckDBPyConnection, 
                           table_name: str, columns: List[Dict[str, str]]) -> None:
        """
        Create a custom table in the simulation database.
        
        Args:
            conn: DuckDB connection
            table_name: Name of the table to create
            columns: List of column definitions, each a dictionary with 'name' and 'type' keys
            
        Raises:
            ValueError: If the table already exists
        """
        # Check if table already exists
        result = conn.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name = ?
        """, (table_name,)).fetchone()[0]
        
        if result > 0:
            raise ValueError(f"Table '{table_name}' already exists.")
        
        # Create the table
        columns_sql = ", ".join([f"{col['name']} {col['type']}" for col in columns])
        conn.execute(f"CREATE TABLE {table_name} ({columns_sql})")
    
    def insert_data(self, conn: duckdb.DuckDBPyConnection, 
                   table_name: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        """
        Insert data into a table.
        
        Args:
            conn: DuckDB connection
            table_name: Name of the table to insert into
            data: Dictionary or list of dictionaries with column names as keys and values to insert
            
        Raises:
            ValueError: If the table doesn't exist
        """
        # Check if table exists
        result = conn.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_name = ?
        """, (table_name,)).fetchone()[0]
        
        if result == 0:
            raise ValueError(f"Table '{table_name}' does not exist.")
        
        # Convert single dictionary to list
        if isinstance(data, dict):
            data = [data]
        
        # Get column names from the first dictionary
        if not data:
            return
        
        columns = list(data[0].keys())
        placeholders = ", ".join(["?" for _ in columns])
        columns_str = ", ".join(columns)
        
        # Insert each row
        for row in data:
            values = [row.get(col) for col in columns]
            conn.execute(f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})", values)
    
    def query_data(self, conn: duckdb.DuckDBPyConnection, query: str, 
                  params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a custom query on the database.
        
        Args:
            conn: DuckDB connection
            query: SQL query to execute
            params: Optional parameters for the query
            
        Returns:
            Query results as a list of dictionaries
        """
        if params is None:
            params = []
        
        result = conn.execute(query, params)
        
        # Get column names
        description = result.description
        column_names = [desc[0] for desc in description]
        
        # Fetch rows and convert to dictionaries
        rows = result.fetchall()
        
        return [
            {column_names[i]: value for i, value in enumerate(row)}
            for row in rows
        ] 