from fastapi import APIRouter

from src.api.services.TenetService import TenetService

from src.api.model.DTO import EvidenceDTO, EvidenceToGenerateDTO, ExportRequestDTO, ExportSentencesDTO, \
    GeneratedEvidenceDTO, SemanticQueryDTO, SentenceToGenerateDTO, TableEvidenceDTO

tenetResource = APIRouter()

tenetService = TenetService()


@tenetResource.get("/up")
async def up() -> str:
    return "Server is up"


@tenetResource.post("/evidence/generateSQL")
def getSQLQuery(tableEvidenceDTO: TableEvidenceDTO) -> str:
    return tenetService.generateSQL(tableEvidenceDTO)


@tenetResource.post("/evidence/generateEvidence")
def generateEvidence(evidenceToGenerateDTO: EvidenceToGenerateDTO):
    return tenetService.generateEvidence(evidenceToGenerateDTO)


@tenetResource.post("/evidence/findSemanticQueries")
def findSemanticQueries(tableEvidenceDTO: TableEvidenceDTO) -> list[SemanticQueryDTO]:
    return tenetService.findSemanticQueries(tableEvidenceDTO)


@tenetResource.post("/evidence/generateSentences")
def generateSentences(generateDTO: SentenceToGenerateDTO) -> list[str]:
    return tenetService.generateSentences(generateDTO)


@tenetResource.post("/evidence/exportSentences")
def exportSentences(exportRequestDTO: ExportRequestDTO):
    return tenetService.exportExamples(exportRequestDTO)
