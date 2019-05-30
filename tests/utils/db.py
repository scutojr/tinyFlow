import mongoengine as me
import mongoengine.connection as connection


def connect(host='mongo_test_server', port=27017, db='test', alias=connection.DEFAULT_CONNECTION_NAME):
    """
    :return: connection object
    """
    return me.connect(db, host=host, port=port)


def disconnect(alias=None, conn=None):
    """
    WARN: make no effect, the connection to mongo is not closed after
          calling this method according to the monitoring data of 'ss -t'
    """
    if conn:
        conn.close()
    elif alias:
        connection.disconnect(alias=alias)


def drop(*doc_cls):
    for cls in doc_cls:
        cls.drop_collection()
