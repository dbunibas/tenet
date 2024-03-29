from src.model.RelationalTable import Cell, Evidence, Header, Table
from src.api.model.DTO import CellDTO, EvidenceDTO, ExportSentencesDTO, HeaderDTO, SemanticQueryDTO, TableDTO

import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class Mapper:
    def tableFromDTOMapper(self, tableDTO: TableDTO, tableName: str):
        headers = []
        for headerDTO in tableDTO.headers:
            header = Header(headerDTO.name)
            if headerDTO.type is not None:
                header.type = headerDTO.type
            headers.append(header)
        cells = tableDTO.cells
        table = Table(tableName, headers)
        rows = {}
        for cell in cells:
            if rows.get(cell.row) == None:
                rows[cell.row] = []
            rows[cell.row].append(Cell(cell.value, headers[cell.column], [cell.row, cell.column]))
        for newRow in list(rows.values()):
            table.addRow(newRow)
        return table

    def evidenceFromDTOMapper(self, evidenceDTO: EvidenceDTO, tableName: str):
        evidence = Evidence(tableName)
        cells = evidenceDTO.cells
        rows = {}
        for cell in cells:
            row = cell.row
            if rows.get(row) == None:
                rows[row] = []
            rows[row].append(Cell(cell.value, cell.header, [cell.row, cell.column]))
        evidence.rows = list(rows.values())
        evidence.build()
        return evidence

    def cellToDTO(self, cell: Cell, row: int, col: int):
        return CellDTO(
            header=HeaderDTO(name=cell.header.name, type=cell.header.type),
            value=cell.value,
            row=row,
            column=col
        )

    def evidenceToDTOMapper(self, evidence: Evidence, negative=False):
        evidenceDTO: EvidenceDTO = EvidenceDTO()
        cells: list[CellDTO] = []
        currentRow = 0
        for row in evidence.rows:
            currentCol = 0
            for cell in row:
                cellDTO = self.cellToDTO(cell, currentRow, currentCol)
                cells.append(cellDTO)
                currentCol += 1
            currentRow += 1
        evidenceDTO.cells = cells
        evidenceDTO.negative = negative
        return evidenceDTO

    def tableToDTOMapper(self, table: Table):
        tableDTO = TableDTO()
        tableDTO.headers = table.schema
        currentRow = 0
        for row in table.rows:
            col = 0
            for cell in row:
                cellDTO = self.cellToDTO(cell, currentRow, col)
                tableDTO.cells.append(cellDTO)
                col += 1
            currentRow += 1
        return tableDTO

    def exportSentencesToDTO(self, evidence, sentences: list[str], table, prompt: str, operation: SemanticQueryDTO,
                             negative: bool):
        return ExportSentencesDTO(
            evidence=self.evidenceToDTOMapper(evidence, negative),
            sentences=sentences,
            table=self.tableToDTOMapper(table),
            prompt=prompt,
            operation=operation,
            negative=negative
        )
