import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text


def getDBConnection(user_uenc, pw_uenc, host, port, dbname):
    connection = psycopg2.connect(user=user_uenc, password=pw_uenc, host=host, port=port, database=dbname)
    return connection


def getEngine(username, password, address, port, dbName):
    connectionString = "postgresql://" + str(username) + ":" + str(password) + "@" + str(address) + ":" + str(
        port) + "/" + str(dbName)
    engine = create_engine(connectionString)
    return engine


def run(query, table, attrMapping):
    df_table = create_df(table)
    ## TODO: change
    user = "pguser"
    passw = "pguser"
    host = "tenet-postgres"
    port = 5432
    dbname = "tenet"
    db = getEngine(user, passw, host, port, dbname)
    conn = db.connect()
    # converting data to sql
    df_table.to_sql('df_table', conn, if_exists='replace', index=False)
    ## execute query
    result = conn.execute(text(query))
    # r = result.fetchall()
    # return
    results = pd.DataFrame(result.fetchall())
    # results = pd.read_sql(query, db)
    results = results.copy()
    results = results.rename(columns=attrMapping)
    results.columns = ensureUniqueColumnNames(results)
    ## close connections
    conn.close()
    db.dispose()
    return results


def ensureUniqueColumnNames(results: pd.DataFrame):
    exploredCols = []
    occurrencesCounter = {}
    for column in results.columns:
        if column in exploredCols:
            try:
                occurrence = occurrencesCounter[column]
            except KeyError:
                occurrence = 0
            occurrence += 1
            occurrencesCounter[column] = occurrence
            column += "_" + str(occurrence)
        exploredCols.append(column)
    return exploredCols


def create_df(table):
    df = pd.DataFrame(table.toDict())
    numAttr = len(table.schema)
    df.insert(loc=0, column='key', value=df.index)
    df.columns = ['key'] + ['a' + str(i) for i in range(0, numAttr)]
    return df
