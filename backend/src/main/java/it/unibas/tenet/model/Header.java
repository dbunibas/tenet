package it.unibas.tenet.model;

import lombok.Data;
import lombok.NoArgsConstructor;
import org.bson.types.ObjectId;

@Data
@NoArgsConstructor
public class Header {

    public Header(String name) {
        this.name = name;
    }

    private String name;
    private String type;

}
