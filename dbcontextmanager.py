from mysql import connector


class UseDatabase():
    def __init__(self, config: dict) -> None:
        self.db_config = config

    def __enter__(self) -> 'cursor':
        self.cnx = connector.connect(**self.db_config)
        self.cursor = self.cnx.cursor(buffered=True)
        print('db connected')
        return self.cursor

    def __exit__(self, exc_type, exc_value, ex_trace) -> None:
        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()
        print('db disconnected')
