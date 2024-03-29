package it.unibas.tenet.model;

import java.util.ArrayList;
import java.util.List;
import lombok.Data;

@Data
public class ExportedEvidence {

    List<Cell> cells = new ArrayList<>();
}
