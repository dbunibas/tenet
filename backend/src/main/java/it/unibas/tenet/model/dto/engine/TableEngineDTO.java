package it.unibas.tenet.model.dto.engine;

import it.unibas.tenet.model.Cell;
import it.unibas.tenet.model.Header;
import java.util.ArrayList;
import java.util.List;
import lombok.Data;

@Data
public class TableEngineDTO {

    private List<Header> headers = new ArrayList<>();

    private List<Cell> cells = new ArrayList<>();

}
