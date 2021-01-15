from mysql import connector


class ConnectionError(Exception):
    pass


class CredentialsError(Exception):
    pass


class SQLError(Exception):
    pass


class UseDatabase():
    def __init__(self, config: dict) -> None:
        self.db_config = config

    def __enter__(self) -> 'cursor':
        try:
            self.cnx = connector.connect(**self.db_config)
            self.cursor = self.cnx.cursor(buffered=True)
            print('db connected')
            return self.cursor
        except connector.errors.InterfaceError as err:
            raise ConnectionError(err)
        except connector.errors.ProgrammingError as err:
            raise CredentialsError(err)

    def __exit__(self, exc_type, exc_value, ex_trace) -> None:
        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()
        print('db disconnected')
        if exc_type is connector.errors.ProgrammingError:
            raise SQLError(exc_value)
        elif exc_type:
            raise exc_type(exc_value)
