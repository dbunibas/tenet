#from pandasql import sqldf
import pandas as pd
import duckdb

#pysqldf = lambda q: sqldf(q, globals())

def run(query, table, attrMapping):
    df_table = create_df(table)
    results = duckdb.sql(query).df()
    results = results.rename(columns=attrMapping)
    return results

def create_df(table):
    #table = [[elt[0]] + elt[1][:] for elt in enumerate(table)]
    df = pd.DataFrame(table.toDict())
    numAttr = len(table.schema)
    df.insert(loc=0, column='key',value=df.index)
    #df.columns = ['key'] + ['a' + str(i) for i in range(0, numAttr - 1)]
    df.columns = ['key'] + ['a' + str(i) for i in range(0, numAttr)]
    return df




