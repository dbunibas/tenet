# tenet
**Textual Training Examples from Data**

Tabular data is becoming increasingly important in Natural Language Processing (NLP) tasks, such as Tabular Natural Language Inference (TNLI). Given a table and a hypothesis expressed in NL text, the goal is to assess if the former structured data supports or refutes the latter. We introduce Tenet, for the automatic augmentation and generation of training examples for TNLI. Our approach is built around the intuition that SQL queries are the right tool to achieve variety in the generated examples, both in terms of data variety and reasoning complexity. The first is achieved by evidence-queries that identify cell values over tables according to different data patterns. Once the data for the example is identified, semantic-queries describe the different ways such data can be identified with standard SQL clauses. These rich descriptions are then verbalized as text to create the annotated examples for the TNLI task. The same approach is also extended to create counterfactual examples, i.e., examples where the hypothesis is false, with a method based on injecting errors in the original (clean) table. For all steps, we introduce generic generation algorithms that take as input only the tables. 
Tenet generates human-like examples, which lead to the effective training of several inference models with results comparable to those obtained by training the same models with manually-written examples.

# News
- 2023-08 Research paper [Generation of Training Examples for Tabular Natural Language Inference](https://github.com/dbunibas/tenet/blob/main/TENET_CR_SIGMOD_2024.pdf) Accepted to SIGMOD 2024

# Demonstration Video
[<img src="https://img.youtube.com/vi/TtqKymy18-o/maxresdefault.jpg" width="60%">](https://youtu.be/TtqKymy18-o)


# Requirements
In order to execute the engine, a valid LLM provider need to be specify. The system supports three providers:
1. OpenAI with a valid API key
2. TogheterAI with a valid API key
3. Ollama installed locally, with the [Mistral](https://ollama.com/library/mistral) model 
The configuration of one of these provider need to be specified in the configuration section.

In addition, the following tools are required:
- [Docker](https://www.docker.com/get-started/) - to run the Engine
- [Node](https://nodejs.org/en) (optional) - to run the Web Interface
- [Java](https://www.oracle.com/java/technologies/downloads/) (at least 21) - to run the Web Interface

Is possible to install the requirements via [Brew](https://brew.sh/).
```shell
brew install docker
brew install node
brew install openjdk@21
brew install ollama
```

Then pull the Mistral Model:
```shell
ollama pull mistral
```

# Engine Only Execution

1. Make sure you have an LLM installed on your machine or a API_KEY to execute the workflow.

2. Edit the configuration:
   - In compose/tenet_engine/data rename the config.json.TEMPLATE with config.json (see command below)
   - Edit config.json according to the configuration properties presented in the [Configuration Section](#configuration)
   
  The default configuration uses Ollama executed locally, we can use it simply by renaming the config.json.TEMPLATE. And we can execute the engine without any further configuration.
  
  ```shell
  mv compose/tenet_engine/data/config.json.TEMPLATE compose/tenet_engine/data/config.json
  ```

3. Execute the engine and run the examples
   - Go to the compose folder and build the images:
     ```shell
     cd compose/
     docker-compose up --build -d
     docker exec -it tenet-engine python -m unittest discover -s test -p 'TestTenet.py'
     ```
4. Execute the engine on a custom class. We assume that the previous step has already executed.
    ```shell
     cp ../engine/test/TestTenet.py ./NewTest.py
     docker cp ./TestNew.py tenet-engine:/usr/src/app/test/TestNew.py
     docker exec -it tenet-engine python -m unittest discover -s test -p 'TestNew.py'
     ```
    Using this approach, custom data can be introduced in the NewTest class (we duplicate the file for simplicity) and the workflow executed. For example, the NewTest.py can be edited to change the input data, and the input evidence. Essentially, the input for the classes is as follows:
   - A relational table
   - The evidence (a set of cells selected by the user)
  
# User Interface Execution
To ease the execution we use Docker. We also assume that Java (at least 21) is available on the machine.

1. Execute the engine with the previous commands:
   ```shell
     cd compose/
     docker-compose up --build -d
   ```

3. Execute the backend in a new terminal. Go to the backend folder:
   ```shell
     cd backend/
     gradlew quarkusDev
     ```
4. Execute the frontend in a new terminal. Go to the frontend folder:
   ```shell
     cd frontend/
     ng serve
     ```
5. Open the application at http://localhost:4200/. The current username is admin and password tenet! you could change it by connecting to the Mongo DB instance deployed with docker.

# Configuration
The configuration can be done through the config.json file. It consists of three main sections:
1. `NEGATIVE_TABLE_GENERATION` contains the different strategies to use to generate negative evidence through an error injection process.
  - `addRows` (`removeRows`) = `'True'` or `'False'` if new rows should be added (rows to be removed) to generate the negative table.
  - `rowsToAdd` (`rowsToRemove`) = the number of new rows to add (remove).
  - `strategy` = `"ActiveDomain"` or `"LMGenerator"`. With "ActiveDomain" values for new rows are extracted from the Active Domain, instead by using "LMGenerator" it uses a PLM to generate the values.
2. `SENTENCE_GENERATION` contains the allowed semantic-queries to use and that could be discovered through the searching process, and also the comparison operator to use. Available values for `operations` are: "lookup", "comparison", "filter", "min", "max", "count", "sum", "avg", "grouping", "ranked", "percentage", "combined". While values for `comparisons` are "<", ">", "=".
3. Text generation Language Model configuration `TENET_CONFIG`.
  - `api_key` should contains your ChatGPT API key or your TogetherAI API key-
  - `languageModel` specifies the LM to use to generate the sentences. Values are: `"ChatGPT"`, `"MistralOllama"` or `"MistralTogetherAi"`. In the case of "MistralOllama" the api_key is not required but the model should be executed by using [Ollama](https://ollama.com/).
  - `address` allows to set up the address of the Ollama server, the default configuration contains the default address for Ollama through Docker.




# Citation
```
@article{TenetSigmod,
  author = {Jean-Flavien, Bussotti and Enzo, Veltri and Donatello, Santoro and Paolo, Papotti},
  title = {{Generation of Training Examples for Tabular Natural Language Inference}},
  publisher = {Association for Computing Machinery},
  journal = {Proc. ACM Manag. Data},
  year = {2023},
  doi = {10.1145/3626730},
}
```

