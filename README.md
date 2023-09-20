# tenet
TExtual traiNing Examples from daTa

# News
- 2023-08 Research paper [Generation of Training Examples for Tabular Natural Language Inference](https://github.com/dbunibas/tenet/blob/main/TENET_SIGMOD.pdf) Accepted to SIGMOD 2024 

# Execution

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
  journal = {Proceedings of the ACM on Management of Data},
  title = {{Generation of Training Examples for Tabular Natural Language Inference}},
  year = {2024}
}
