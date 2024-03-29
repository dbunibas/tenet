from pydantic import BaseModel


class HeaderDTO(BaseModel):
    name: str
    type: str | None


class CellDTO(BaseModel):
    header: HeaderDTO
    value: str | int | float
    row: int
    column: int


class EvidenceDTO(BaseModel):
    cells: list[CellDTO] = []
    negative: bool = False


class TableDTO(BaseModel):
    headers: list[HeaderDTO] = []
    cells: list[CellDTO] = []

    def getCells(self, idList: list[int]):
        cells: list[CellDTO] = []
        for cell in self.cells:
            if cell.cellId in idList:
                cells.append(cell)
        return cells


class TableEvidenceDTO(BaseModel):
    name: str
    table: TableDTO
    userEvidence: EvidenceDTO


class EvidenceToGenerateDTO(BaseModel):
    name: str
    table: TableDTO
    userEvidence: EvidenceDTO
    positiveNumber: int
    negativeNumber: int
    negativeTable: TableDTO | None


class GeneratedEvidenceDTO(BaseModel):
    evidence: list[EvidenceDTO]
    negativeTable: TableDTO | None


class SemanticQueryDTO(BaseModel):
    name: str
    query: str


class SentenceToGenerateDTO(BaseModel):
    name: str
    table: TableDTO
    evidence: EvidenceDTO
    sentenceType: SemanticQueryDTO
    sentenceNumber: int


class ExportRequestDTO(BaseModel):
    name: str
    table: TableDTO
    userEvidence: EvidenceDTO
    positiveNumber: int
    negativeNumber: int
    sentencesNumber: int


class ExportSentencesDTO(BaseModel):
    evidence: EvidenceDTO
    sentences: list[str] | list[None] | None
    table: TableDTO
    prompt: str
    operation: SemanticQueryDTO
    negative: bool
