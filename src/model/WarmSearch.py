from src import Constants
from src.LoggedDecorators import timed
from src.model.ISearchStrategy import ISearchStrategy
from src.model.RelationalTable import Evidence, Cell
from src.queryExecutor.InMemoryExecutor import run as runInMemory
from src.queryExecutor.PostgresExecutor import run as runPostgres
import re
import pandas as pd


class WarmSearch(ISearchStrategy):

    def __init__(self):
        super().__init__()

    def setSeed(self, seed):
        super().setSeed(seed)

    def findEvidences(self, table, numExamples, evidence):
        if evidence is None: return None ## TODO: return an exception?
        if table is None: return None
        graph = self.getGraph(evidence, table)
        query, attrMapping = self.createQuery(graph, table)
        evidences = self.executeQuery(query, table, attrMapping, numExamples, evidence)
        return evidences

    #@timed
    def createQuery(self, graph, table, tableName="df_table", limit=800): ## tableName is fixed for duckDB
        attrMapping = {}
        nb_nodes = len(graph.keys())
        pairs_node_srow = []
        for elt in graph.keys():
            graph[elt]['visited'] = False
            res = set([elt] + graph[elt]['same_row'])
            if not res in pairs_node_srow:
                pairs_node_srow += [res]
        pairs_node_srow_en = list(enumerate(pairs_node_srow))
        txt_select = 'SELECT '
        pairs_visited = []
        txt_where = ' WHERE '
        txt_from = ' FROM '
        # FROM
        for elt in pairs_node_srow_en:
            txt_from += tableName + ' as t' + str(elt[0]) + ', '
        txt_from = txt_from[:-2]
        # WHERE
        next_not_visited = self.pick_next_not_visited(graph)
        while not next_not_visited == None:
            # print(next_not_visited)
            elt = graph[next_not_visited]
            graph[next_not_visited]['visited'] = True
            # print(pairs_node_srow)
            # print(pairs_node_srow_en)
            # [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
            conv_nnv_to_var = [x[0] for x in pairs_node_srow_en if next_not_visited in x[1]][0]
            this_cell_txt = 't' + str(conv_nnv_to_var) + '.a' + str(elt['position'][1])
            this_attr_type = table.schema[elt['position'][1]].type
            this_attr_name = table.schema[elt['position'][1]].name
            attrMapping['a'+ str(elt['position'][1])] = this_attr_name
            this_cell_txt_k = 't' + str(conv_nnv_to_var) + '.key'
            this_cell_txt_k_old = 't' + str(next_not_visited) + '.key'
            txt_select += this_cell_txt + ', ' + this_cell_txt_k + ', '

            # txt_select+=this_cell_txt+', '
            for u in elt['relation']:
                conv_u_to_var = [x[0] for x in pairs_node_srow_en if u[0] in x[1]][0]
                other_cell_txt = 't' + str(conv_u_to_var) + '.a' + str(graph[u[0]]['position'][1])
                other_attr_type = table.schema[graph[u[0]]['position'][1]].type
                other_attr_name = table.schema[graph[u[0]]['position'][1]].name
                other_cell_txt_k = 't' + str(conv_u_to_var) + '.key'
                other_cell_txt_k_old = 't' + str(u[0]) + '.key'
                if ([this_cell_txt_k_old, other_cell_txt_k_old] in pairs_visited):
                    continue
                pairs_visited += [[this_cell_txt_k_old, other_cell_txt_k_old],
                                  [other_cell_txt_k_old, this_cell_txt_k_old]]

                rel_txt = ''
                if u[1] == 'eq' or u[1] == '=':
                    rel_txt = '='
                if u[1] == '<':
                    rel_txt = '<'
                if u[1] == '>':
                    rel_txt = '>'
                if u[1] == 'diff':
                    rel_txt = '<>'
                if not rel_txt == '' and (this_attr_type == other_attr_type):
                    txt_where += this_cell_txt + rel_txt + other_cell_txt + ' and '
                # if u[0] in elt['same_row']:
                #    txt_where+= this_cell_txt_k+'='+other_cell_txt_k+' and '
                # elif next_not_visited>u[0]:
                # ========================= I ADDED <> instead of > because didn t work otherwise
                #   txt_where+= this_cell_txt_k+'<>'+other_cell_txt_k+' and '
            if True:  # (len(elt['relation'])==0):
                next_not_visited = self.pick_next_not_visited(graph)
        if txt_where == ' WHERE ':
            txt_where = ""
        else:
            txt_where = txt_where[:-5]
        txt_select = txt_select[:-2]
        return txt_select + txt_from + txt_where + ' LIMIT ' + str(limit), attrMapping

    #@timed
    def getGraph(self, evidence, table):
        cellPos = []
        for row in evidence.rows:
            for cell in row:
                cellPos.append(cell.pos)
        graph = dict()
        for i in range(len(cellPos)):
            graph[i] = dict()
            graph[i]['visited'] = False
            graph[i]['position'] = cellPos[i]
            graph[i]['relation'] = []
            graph[i]['same_row'] = []
            graph[i]['same_col'] = []
            for t in range(len(cellPos)):
                if t == i:
                    continue
                graph[i]['relation'] += [[t, self.get_comp2(table, cellPos[i], cellPos[t])]]
                if cellPos[i][0] == cellPos[t][0]:
                    graph[i]['same_row'] += [t]
                if cellPos[i][1] == cellPos[t][1]:
                    graph[i]['same_col'] += [t]
        return graph

    #@timed
    def executeQuery(self, query, table, attrMapping, maxExamples, evidence, shuffle=False):
        #print("*** Query:", query)
        df = None
        if evidence.getNumberOfCells() > 10 or len(table.rows) > 50:
            df = runPostgres(query, table, attrMapping)
        else:
            df = runInMemory(query, table, attrMapping)
        # df.drop(list(df.filter(regex='key')), axis=1, inplace=True) ## drop key columns
        result = None
        if shuffle:
            if self.seed is not None:
                result = df.sample(n=maxExamples, random_state=self.seed)
            else:
                result = df.sample(n=maxExamples)
        else:
            result = df.head(maxExamples)
        select = query.split("FROM")[0].replace("SELECT", "").strip()
        ts = re.findall("t[0-9]+", select)
        atts = select.split(",")
        ts = [a for i, a in enumerate(ts) if not i % 2]
        atts = [a for i, a in enumerate(atts) if not i % 2]
        columns = result.columns
        evidences = []
        for index, row in result.iterrows():
            evidence = Evidence(table.tableName)
            maxIndex = len(attrMapping)
            counter = 0
            prevT = ""
            rowEvidence = []
            for attr, key in self.pairwise(columns):
                currentT = ts[counter]
                currentAttr = atts[counter].replace(currentT, "").replace(".", "").strip()
                if currentT != prevT:
                    if len(rowEvidence) != 0:
                        evidence.addRow(rowEvidence)
                    rowEvidence = []
                cellValue = row[attr]
                rowProvenance = row[key]
                attributeName = attrMapping[currentAttr]
                attribute = table.getAttribute(attributeName)
                # attribute = table.schema[counter % maxIndex]
                attrPos = counter % maxIndex
                cell = Cell(cellValue, attribute)
                cell.setPos([rowProvenance, attrPos])
                rowEvidence.append(cell)
                prevT = currentT
                counter += 1
            if len(rowEvidence) > 0:
                evidence.addRow(rowEvidence)
            evidence.build()
            evidences.append(evidence)
        return evidences

    def get_comp2(self, table, elt_i, elt2_i):
        # equality, inf, sup,...
        #elt_v = table[elt_i[0]][elt_i[1]]
        elt_c = table.getCellByPos(elt_i[0], elt_i[1])
        elt_v = elt_c.value
        # print(elt2_i)
        #elt2_v = table[elt2_i[0]][elt2_i[1]]
        elt2_c = table.getCellByPos(elt2_i[0], elt2_i[1])
        elt2_v = elt2_c.value
        comp = ''
        if elt_c.header.type == Constants.NUMERICAL and elt2_c.header.type == Constants.NUMERICAL:
        #if elt_v.replace('.', '', 1).isdigit() and elt2_v.replace('.', '', 1).isdigit():
            if float(elt_v) < float(elt2_v):
                comp = '<'
            elif float(elt_v) - float(elt2_v) < 1e-5:
                comp = '='
            else:
                comp = '>'
        else:
            if elt_v == elt2_v:
                comp = 'eq'
            else:
                comp = 'diff'
        return comp

    def pick_next_not_visited(self, graph):
        for elt in graph.keys():
            if graph[elt]['visited'] == False: return elt
        return None

    def create_df_nok(self, table):
        #table = [elt[1][:] for elt in enumerate(table)]
        df = pd.DataFrame(table.toDict())
        numAttr = len(table.schema)
        df.columns = ['a' + str(i) for i in range(0, numAttr)]
        return df

    def pairwise(self, iterable):
        "s -> (s0, s1), (s2, s3), (s4, s5), ..."
        a = iter(iterable)
        return zip(a, a)
