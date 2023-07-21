import pandas as pd
import psycopg2
from sqlalchemy import create_engine

def getDBConnection(user_uenc, pw_uenc, host, port, dbname) :
    connection = psycopg2.connect(user = user_uenc, password = pw_uenc, host = host, port = port, database = dbname)
    return connection

def getEngine(username, password, address, port, dbName):
    connectionString = "postgresql://"+str(username) +":"+ str(password) + "@"+str(address) + ":" + str(port) +"/" + str(dbName)
    engine = create_engine(connectionString)
    return engine

def run(query, table, attrMapping):
    df_table = create_df(table)
    ## TODO: Change with your postgres config
    user = "pguser"
    passw = "pguser"
    host = "localhost"
    port = 5432
    dbname = "tenet"
    db = getEngine(user, passw, host, port, dbname)
    conn = db.connect()
    # converting data to sql
    df_table.to_sql('df_table', conn, if_exists='replace', index=False)
    ## execute query
    results = pd.read_sql(query, db)
    results = results.copy()
    results = results.rename(columns=attrMapping)
    ## close connections
    conn.close()
    db.dispose()
    return results


def create_df(table):
    df = pd.DataFrame(table.toDict())
    numAttr = len(table.schema)
    df.insert(loc=0, column='key',value=df.index)
    df.columns = ['key'] + ['a' + str(i) for i in range(0, numAttr)]
    return df