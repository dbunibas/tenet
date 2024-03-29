# tenet
TExtual traiNing Examples from daTa

# News
- 2023-08 Research paper [Generation of Training Examples for Tabular Natural Language Inference](https://github.com/dbunibas/tenet/blob/main/TENET_CR_SIGMOD_2024.pdf) Accepted to SIGMOD 2024

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


