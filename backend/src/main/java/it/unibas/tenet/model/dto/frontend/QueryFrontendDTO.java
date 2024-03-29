package it.unibas.tenet.model.dto.frontend;

import lombok.Data;

@Data
public class QueryFrontendDTO {

    private String sql;

    public QueryFrontendDTO(String sql) {
        this.sql = sql;
    }

}
