# tenet
TExtual traiNing Examples from daTa

# News
- 2023-08 Research paper [Generation of Training Examples for Tabular Natural Language Inference](https://github.com/dbunibas/tenet/blob/main/TENET_CR_SIGMOD_2024.pdf) Accepted to SIGMOD 2024

# Demonstration Video
[![Coming Soon](https://img.youtube.com/vi/TtqKymy18-o/maxresdefault.jpg)](https://youtu.be/TtqKymy18-o)

# User Interface Execution
To ease the execution we use [Docker](https://www.docker.com/get-started/) and [Angular](https://angular.io/).
1. Execute the engine. Go to the compose folder:
   - In tenet_engine/data rename the config.json.TEMPLATE with config.json
   - Edit config.json according to the configuration properties presented in the Configuration Section
   - Go to the compose folder and build the images:
     ```shell
     docker-compose up --build
     ```
2. Execute the backend. Go to the backend folder:
   ```shell
     gradlew quarkusDev
     ```
3. Execute the frontend. Go to the frontend folder:
   ```shell
     ng serve
     ```
4. Open the application at http://localhost:4200/. The current username is admin and password tenet! you could change it by connecting to the Mongo DB instance deployed with docker.

# Configuration
The configuration can be done through the config.json file. It consists of three main sections:
1. Negative Table Generation contains the different strategies to use to generate negative evidence through an error injection process.
  - addRows (removeRows) = 'True' or 'False' if new rows should be added (rows to be removed) to generate the negative table
  - rowsToAdd (rowsToRemoce) = the number of new rows to add (remove)
  - strategy = "ActiveDomain" or "LMGenerator". With ActiveDomain values for new rows are extracted from the ActiveDomain, instead by using "LMGenerator" it uses a PLM to generate the values.
2. Sentence Generation contains the allowed semantic-queries to use and that could be discovered through the searching process, and also the comparison operator to use. Available values for operations are: "lookup", "comparison", "filter", "min", "max", "count", "sum", "avg", "grouping", "ranked", "percentage", "combined". While values for comparison are "<", ">", "=".
3. Text generation Language Model configuration.
  - "api_key" should contains your ChatGPT API key or your TogetherAI API key
  - "languageModel" specifies the LM to use to generate the sentences. Values are: "ChatGPT", "MistralOllama" or "MistralTogetherAi". In the case of MistralOllama the api_key is not required but the model should be executed by using [Ollama](https://ollama.com/)
  - "address" allows to set up the address of the Ollama server


# Engine Only Execution

1. Make sure you have an OPEN-AI Key to execute the workflow.
2. Install requirements (pip install -r requirements.txt)
3. Create a Postgres database with the following configuration:
   - dbname = "tenet"
   - user and passw = "pguser"
   - Notice: you can change the values in src/queryExecutor/PostgresExecutor.py
4. An example of the execution of the system is in test/TestTenet.py
   - Given a relational table as input
   - And the evidence (a set of cells selected by the user), ad input (but optionally)
   - Generate positive and negative examples according the relational table and the provided evidence.

Data Folder contains the generated training dataset and the full pipeline for training the target applications (Tenet submission.7z).
To train and test target applications unzip the file and follow the readme per each application.


# Citation
@article{TenetSigmod,
  author = {Jean-Flavien, Bussotti and Enzo, Veltri and Donatello, Santoro and Paolo, Papotti},
  title = {{Generation of Training Examples for Tabular Natural Language Inference}},
  publisher = {Association for Computing Machinery},
  journal = {Proc. ACM Manag. Data},
  year = {2023},
  doi = {10.1145/3626730},
}


