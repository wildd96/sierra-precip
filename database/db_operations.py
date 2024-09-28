from google.cloud.sql.connector import Connector
import sqlalchemy

class Database:
    def __init__(self, project_id, region, instance_name, db_user, db_pass, db_name):
        self.connector = Connector()
        self.connection_params = {
            "project_id": project_id,
            "region": region,
            "instance_name": instance_name,
            "user": db_user,
            "password": db_pass,
            "db": db_name
        }
        self.engine = None

    def _get_conn(self):
        return self.connector.connect(
            f"{self.connection_params['project_id']}:{self.connection_params['region']}:{self.connection_params['instance_name']}",
            "pymysql",
            user=self.connection_params['user'],
            password=self.connection_params['password'],
            db=self.connection_params['db']
        )

    def connect(self):
        if not self.engine:
            self.engine = sqlalchemy.create_engine(
                "mysql+pymysql://",
                creator=self._get_conn,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            print(f"Created engine: {self.engine}")
        return self.engine

    def execute_query(self, query):
        engine = self.connect()
        with engine.connect() as connection:
            result = connection.execute(sqlalchemy.text(query))
            return result.fetchall()

    def pull_table(self, table_name):
        query = f"SELECT * FROM {table_name}"
        return self.execute_query(query)

    def query(self, query):
        return self.execute_query(query)

    def close(self):
        if self.engine:
            self.engine.dispose()
            self.engine = None
            print("Connection pool closed")