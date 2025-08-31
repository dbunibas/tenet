import json
from src.model.RelationalTable import Evidence


class EvidenceEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Evidence):
            # Convert Evidence object to its string representation
            evidenceString = str(obj)
            tokens = evidenceString.split("\n")
            rows = []
            for token in tokens:
                row = token.split("|")[:-1]
                if (len(row) > 0): rows.append(row)
            return rows
        # Let the base class default method raise the TypeError for other types
        return json.JSONEncoder.default(self, obj)