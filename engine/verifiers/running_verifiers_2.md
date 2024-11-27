# Training FEVEROUS and TabFact Verifiers

Once the examples are generated, two distinct paths allow training the **FEVEROUS** and **TabFact** verifiers on them.

## FEVEROUS

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/wenhuchen/Table-Fact-Checking.git
   ```

2. **Prepare the Dataset:**
   - Create a folder named `datasets` and place all the CSV files of the tables in it.
   
3. **Create the Database:**
   - Run the `create_db` notebook. This will create a database containing your tables.
   - Execute the following command:
     ```bash
     database/create_wiki_db --db_path . --wiki_path ./readyfordb --wiki_name new_db.db
     ```

4. **Replace the Training File:**
   - Replace the `train.jsonl` file in the `data` directory with a new JSONL file containing your own claims. The file should have one dictionary per row, with each dictionary corresponding to one example.

   Example of a dictionary:
   ```json
   {
       "evidence": [{
           "content": ["1903 Norwegian Football Cup_header_cell_1_0_0", "1903 Norwegian Football Cup_header_cell_1_0_2"],
           "context": {
               "1903 Norwegian Football Cup_header_cell_1_0_0": ["1903 Norwegian Football Cup_title", "1903 Norwegian Football Cup_section_0"],
               "1903 Norwegian Football Cup_header_cell_1_0_2": ["1903 Norwegian Football Cup_title", "1903 Norwegian Football Cup_section_0"]
           }
       }],
       "id": 10791,
       "claim": "The Semi-finals of the 1903 Norwegian Football Cup were played between 6 teams.",
       "label": "REFUTES",
       "challenge": "Numerical Reasoning"
   }
   ```

   - **Details for Fields:**
     - `evidence > content`: List all the cell IDs used as evidence for the claims.
     - `context`: Provide a key for each element in `content` with its corresponding context. Use the table title in the format `NAMEOFTABLE_title`, where `NAMEOFTABLE` corresponds to the relevant CSV file in `/datasets`.
     - The structure of the cell ID is `NAMEOFTABLE_cell_0_ROWID_COLID`, where `ROWID` and `COLID` denote the row and column indices of the cell within the table.
     - Update the `claim` and `label` fields with the correct ones for the new claims.

5. **Run the End-to-End Pipeline:**
   ```bash
   python3 examples/baseline.py --split dev --doc_count 5 --sent_count 5 --tab_count 3 \
   --config_path_cell_retriever src/feverous/baseline/retriever/config_roberta.json \
   --config_path_verdict_predictor src/feverous/baseline/predictor/config_roberta_old.json \
   --db_path new_db.db
   ```

   For more details on running the pipeline, refer to the repository documentation.

---

## TabFact

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/wenhuchen/Table-Fact-Checking.git
   ```

2. **Prepare the Dataset:**
   - Add each table as an individual file in the folder `data/all_csv`.

3. **Update the Training IDs:**
   - Modify the `train_id.json` file in the `data` directory to contain a list of all table IDs used for training.

4. **Replace the Claims:**
   - Replace the claims in `tokenized_data/train_examples.json` with the newly generated ones.
   - The file should be a dictionary where the keys are table IDs, and the values are lists with three elements:
     1. A list of claims corresponding to the table.
     2. A list of labels for the claims (0 or 1).
     3. The title of the table.

   Example format:
   ```json
   "2-1859269-1.html.csv": [
       [
           "During the third round of the Turkish Cup, there were no new entries.",
           "The highest number of winners from a previous round in the Turkish Cup was 54 in Round 3.",
           "The Süper Lig was the most common league to win a round in the Turkish Cup.",
           "The lowest number of new entries concluding a round in the Turkish Cup was 5.",
           "Round 1 of the Turkish Cup began with 156 competitors, and the final round was completed by only 2 teams.",
           "There were new entries for the first 4 rounds of the Turkish Cup.",
           "The highest number of winners from a previous round in the Turkish Cup was 59 in Round 3.",
           "The TFF Third League was the most common league to win a round in the Turkish Cup.",
           "2 was the lowest number of new entries concluding a round in the Turkish Cup.",
           "From Round 1 to the final round, there were 4 clubs remaining to complete the round."
       ],
       [
           1,
           1,
           1,
           1,
           1,
           0,
           0,
           0,
           0,
           0
       ],
       "Turkish Cup"
   ]
   ```

5. **Launch Training:**
   Follow the instructions provided in the repository for training and testing:
   [Table-Fact-Checking Documentation](https://github.com/wenhuchen/Table-Fact-Checking/tree/master?tab=readme-ov-file#start-from-scratch-data-preprocessing).


---
## Using the paper generated datasets 

The following generated datasets used in the submission can be used directly in the previous pipelines:
- [GeneratedDatasetsForTargetApplications.zip](https://github.com/dbunibas/tenet/blob/main/engine/data/GeneratedDatasetsForTargetApplications.zip)
- [dataForFeverousNotebook.zip](https://github.com/dbunibas/tenet/blob/main/engine/data/revision/feverous/dataForFeverousNotebook.zip)