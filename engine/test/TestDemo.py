import unittest

from src.api.ConfigSingleton import ConfigSingleton
from src import Constants
from src.Tenet import Tenet
from src.model.RelationalTable import Table, Header, Cell, Database, Evidence
import os
import csv
import json

from EvidenceEncoder import EvidenceEncoder


class TestDemo(unittest.TestCase):

    def attributes_to_header(self, attributes):
        headers = []
        for attribute in attributes:
            header = Header(attribute)
            headers.append(header)
        return headers

    def create_table(self, attributes, table_name, rows):
        headers = self.attributes_to_header(attributes)
        table = Table(table_name, headers)
        for row in rows:
            cells = []
            for i in range(len(attributes)):
                cell = Cell(row[i], headers[i])
                cells.append(cell)
            table.addRow(cells)
        return table

    def create_example(self, generated_example, table_data, labelValue):
        example = {}
        example["headers"] = table_data["headers"]
        example["rows"] = table_data["rows"]
        example["claim"] = generated_example["sentences"]
        example["evidence"] = generated_example["evidence"]
        example["label"] = labelValue
        return example

    def test_generate(self):
        folder_path = "/Users/enzoveltri/Desktop/tenet-demo/tabular-fact-checking/annotated_tables/"

        ## LOCATION
        evLocation1 = Evidence("locations")
        cell0_0 = Cell("Akrar", Header("Town/Village"))
        cell0_0.setPos([0, 0])
        cell0_1 = Cell(28, Header("Population"))
        cell0_1.setPos([0, 1])
        evLocation1.addRow([cell0_0, cell0_1])
        cell1_0 = Cell("Argir", Header("Town/Village"))
        cell1_0.setPos([1, 0])
        cell1_1 = Cell(1907, Header("Population"))
        cell1_1.setPos([1, 1])
        evLocation1.addRow([cell1_0, cell1_1])
        evLocation1.build()

        evLocation2 = Evidence("locations")
        cell0_0 = Cell("Glyvrar", Header("Town/Village"))
        cell0_0.setPos([16, 0])
        cell0_1 = Cell("Eysturoy", Header("Island"))
        cell0_1.setPos([16, 1])
        evLocation2.addRow([cell0_0, cell0_1])
        cell1_0 = Cell("Hellur", Header("Town/Village"))
        cell1_0.setPos([22, 0])
        cell1_1 = Cell("Eysturoy", Header("Island"))
        cell1_1.setPos([22, 1])
        evLocation2.addRow([cell1_0, cell1_1])
        evLocation2.build()

        evLocation3 = Evidence("locations")
        cell0_0 = Cell("Glyvrar", Header("Town/Village"))
        cell0_0.setPos([16, 0])
        cell0_1 = Cell("Eysturoy", Header("Island"))
        cell0_1.setPos([16, 4])
        cell0_2 = Cell(421, Header("Population"))
        cell0_2.setPos([16, 1])
        evLocation3.addRow([cell0_0, cell0_1, cell0_2])
        cell1_0 = Cell("Hellur", Header("Town/Village"))
        cell1_0.setPos([22, 0])
        cell1_1 = Cell("Eysturoy", Header("Island"))
        cell1_1.setPos([22, 4])
        cell1_2 = Cell(26, Header("Population"))
        cell1_2.setPos([22, 1])
        evLocation3.addRow([cell1_0, cell1_1, cell1_2])
        evLocation3.build()

        ## FILM ROLE
        evFilmRole = Evidence("film_roles")
        cell0_0 = Cell(1991, Header("Year"))
        cell0_0.setPos([0, 0])
        cell0_1 = Cell("Let Him Have It", Header("Title"))
        cell0_1.setPos([0, 1])
        evFilmRole.addRow([cell0_0, cell0_1])
        cell1_0 = Cell(1992, Header("Year"))
        cell1_0.setPos([1, 0])
        cell1_1 = Cell("Death and the Compass", Header("Title"))
        cell1_1.setPos([1, 1])
        evFilmRole.addRow([cell1_0, cell1_1])
        evFilmRole.build()

        ## COMIC ISSUES
        evComicIssues = Evidence("comic_issues")
        cell0_0 = Cell("The Name of the Game", Header("Title"))
        cell0_0.setPos([0, 0])
        cell0_1 = Cell(152, Header("TPB page number"))
        cell0_1.setPos([0, 4])
        evComicIssues.addRow([cell0_0, cell0_1])
        cell1_0 = Cell("Get Some", Header("Title"))
        cell1_0.setPos([1, 0])
        cell1_1 = Cell(192, Header("TPB page number"))
        cell1_1.setPos([1, 4])
        evComicIssues.addRow([cell1_0, cell1_1])
        evComicIssues.build()

        ## CHATEAU DETAILS
        ecChateauDetails = Evidence("chateau_details")
        cell0_0 = Cell("Château de Champtocé", Header("Name"))
        cell0_0.setPos([4, 0])
        cell0_1 = Cell("Ruins", Header("Condition"))
        cell0_1.setPos([4, 2])
        ecChateauDetails.addRow([cell0_0, cell0_1])
        cell1_0 = Cell("Château de Pouancé", Header("Name"))
        cell1_0.setPos([9, 0])
        cell1_1 = Cell("Ruins", Header("Condition"))
        cell1_1.setPos([9, 2])
        ecChateauDetails.addRow([cell1_0, cell1_1])
        cell2_0 = Cell("Château de la Turmelière", Header("Name"))
        cell2_0.setPos([11, 0])
        cell2_1 = Cell("Ruins", Header("Condition"))
        cell2_1.setPos([11, 2])
        ecChateauDetails.addRow([cell2_0, cell2_1])
        ecChateauDetails.build()

        ## MOTORCYCLE RACING TEAM
        evMotorcycleRacingTeam = Evidence("motorcycle_racing_team")
        cell0_0 = Cell("Camel Yamaha Team", Header("Team"))
        cell0_0.setPos([0, 0])
        cell0_1 = Cell("Colin Edwards", Header("Rider"))
        cell0_1.setPos([0, 5])
        evMotorcycleRacingTeam.addRow([cell0_0, cell0_1])
        cell1_0 = Cell("Camel Yamaha Team", Header("Team"))
        cell1_0.setPos([1, 0])
        cell1_1 = Cell("Valentino Rossi", Header("Rider"))
        cell1_1.setPos([1, 5])
        evMotorcycleRacingTeam.addRow([cell1_0, cell1_1])
        evMotorcycleRacingTeam.build()

        ## OLYMPIC MEDALIST
        evOlympitMedalist = Evidence("olimpyc_medalist")
        cell0_0 = Cell("Japan (JPN)", Header("Nation"))
        cell0_0.setPos([0, 1])
        cell0_1 = Cell(9, Header("Gold"))
        cell0_1.setPos([0, 2])
        evOlympitMedalist.addRow([cell0_0, cell0_1])
        cell1_0 = Cell("Iran (IRI)", Header("Nation"))
        cell1_0.setPos([1, 1])
        cell1_1 = Cell(1, Header("Gold"))
        cell1_1.setPos([1, 2])
        evOlympitMedalist.addRow([cell1_0, cell1_1])
        evOlympitMedalist.build()

        ## PLAYER_CAREER_OVERVIEW
        evPlayerCareerOverview = Evidence("player_career_overview")
        cell0_0 = Cell("Berrick Barnes", Header("Name"))
        cell0_0.setPos([3, 0])
        cell0_1 = Cell("NRL", Header("Top rugby league level"))
        cell0_1.setPos([3, 2])
        evPlayerCareerOverview.addRow([cell0_0, cell0_1])
        cell1_0 = Cell("Willie Carne", Header("Name"))
        cell1_0.setPos([5, 0])
        cell1_1 = Cell("NRL", Header("Top rugby league level"))
        cell1_1.setPos([5, 2])
        evPlayerCareerOverview.addRow([cell1_0, cell1_1])
        evPlayerCareerOverview.build()

        tablesManualEvidence = ["locations",
                                "film_roles",
                                "comic_issues",
                                "chateau_details",
                                "motorcycle_racing_team",
                                "olympic_medalists",
                                "player_career_overview"
                                ]

        manualEvidences = {
            "locations": [evLocation1, evLocation2, evLocation3],
           # "locations": [evLocation1],
            "film_roles": [evFilmRole],
            "comic_issues": [evComicIssues],
            "chateau_details": [ecChateauDetails],
            "motorcycle_racing_team": [evMotorcycleRacingTeam],
            "olympic_medalists": [evOlympitMedalist],
            "player_career_overview": [evPlayerCareerOverview]
        }

        # Get the list of files in the folder_path
        file_list = os.listdir(folder_path)
        # Filter for CSV files
        csv_files = [f for f in file_list if f.endswith('.csv')]

        database_manual = Database("WikiTables")
        tables_data_manual = {}

        # Process each CSV file
        for csv_file in csv_files:
            tableName = csv_file.split(".")[0]
            if tableName not in tablesManualEvidence: continue
            file_path = os.path.join(folder_path, csv_file)
            print(f"Processing file: {csv_file}")
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                # Read the header row
                header = next(reader)
                print("Headers:", header)
                # Read the remaining rows
                rows = list(reader)
                print("Number of rows:", len(rows))
                # print("First 5 rows:", rows[:5]) # Uncomment to see sample rows
                table = self.create_table(header, tableName, rows)
                database_manual.addTable(table)
                tables_data_manual[tableName] = {"headers": header, "rows": rows}
            print("-" * 20)

        database_manual.inferTypes()

        operations = [Constants.OPERATION_COMPARISON, Constants.OPERATION_FILTER, Constants.OPERATION_COUNT,
                      Constants.OPERATION_SUM, Constants.OPERATION_AVG]
        comparisons = [Constants.OPERATOR_SAME, Constants.OPERATOR_LT, Constants.OPERATOR_GT]
        config = ConfigSingleton()
        config.CONFIG_TENET_API_KEY = "4c71843b6e8a2e87c3d1ee2a8ac682ff01f66f6bbb97491dae8635ee7a92354d"
        config.CONFIG_TENET_LANGUAGE_MODEL = "ExaoneTogetherAi"
        seed = config.SEED
        addRows = config.NEGATIVE_TABLE_GENERATION_ADD_ROWS
        rowsToAdd = config.NEGATIVE_TABLE_GENERATION_ROWS_TO_ADD
        removeRows = config.NEGATIVE_TABLE_GENERATION_REMOVE_ROWS
        rowsToRemove = config.NEGATIVE_TABLE_GENERATION_ROWS_TO_REMOVE
        bestEvidences = config.CONFIG_TENET_BEST_EVIDENCES
        rateLimit = config.CONFIG_TENET_RATE_LIMIT
        sleepTime = config.CONFIG_TENET_SLEEP_TIME
        address = config.CONFIG_TENET_ADDRESS
        strategy = Constants.STRATEGY_ACTIVE_DOMAIN
        languageModel = config.CONFIG_TENET_LANGUAGE_MODEL
        useLM = False

        bestEvidences = 10
        tenet = Tenet(database_manual, seed, operations, comparisons, bestEvidences=bestEvidences,
                      sentencesPerExample=3, languageModel=languageModel, rateLimit=rateLimit,
                      sleepTime=sleepTime, address=address)
        tenet.disableLanguageModel()

        numEvidence = 5
        exampleManual = []
        for tableName in tablesManualEvidence:
            table = database_manual.getTableByName(tableName)
            #print(table)
            evidences = manualEvidences[tableName]
            print(evidences)
            for evidenceSel in evidences:
                print(evidenceSel)
                positiveExamples = tenet.generatePositiveExamples(tableName, evidenceSel, numEvidence)
                negativeExamples = tenet.generateNegativeExamples(tableName, evidenceSel, numEvidence, addRows,
                                                                  rowsToAdd,
                                                                  removeRows, rowsToRemove, strategy, useLM=useLM)
                if len(positiveExamples) > 0:
                    for p in positiveExamples:
                        print("***** POSITIVES *****")
                        example = self.create_example(p, tables_data_manual[tableName], "support")
                        print(example["evidence"])
                        exampleManual.append(example)
                if len(negativeExamples) > 0:
                    for n in negativeExamples:
                        # print("***** NEGATIVES *****")
                        example = self.create_example(n, tables_data_manual[tableName], "refute")
                        exampleManual.append(example)

        json_string = json.dumps(exampleManual, indent=4, cls=EvidenceEncoder)

        # Write the JSON string to a file
        with open(folder_path + 'example_train_manual.json', 'w') as f:
            f.write(json_string)
