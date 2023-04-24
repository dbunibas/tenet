class IOperator:
    def checkSemantic(self, evidence, database) -> bool:
        """Check if the semantic of the operator applies to the evidence"""
        pass

    def printOperator(self, evidence, database, attributes=None) -> str:
        """Generate the operator for the languageModel"""
        pass

    def linearizeEvidence(self, evidence) -> str:
        """Generate evidence linearization"""
        #TODO: maybe use a dict as extra parameter, or pass a linearizationObj and use it
        linerizedTable = "Table: " + evidence.tableName + "\n"
        lineSeparator = "-"*12 + "\n"
        linerizedTable += lineSeparator
        headers = evidence.headers
        headerNames = evidence.getHeaderNames()
        headerLine = " | ".join(headerNames) + "\n"
        linerizedTable += headerLine
        linerizedTable += lineSeparator
        for row in evidence.orderedRows:
            cellValues = []
            for header in headerNames:
                cell = row[header]
                value = ""
                if cell is not None:
                    value = cell.value
                cellValues.append(cell)
            rowLine = " | ".join(cellValues) + "\n"
            linerizedTable += rowLine
        linerizedTable += lineSeparator + "\n" # add another endline
        return linerizedTable


