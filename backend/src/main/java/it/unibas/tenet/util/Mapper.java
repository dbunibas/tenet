package it.unibas.tenet.util;

import org.modelmapper.ModelMapper;
import org.modelmapper.convention.MatchingStrategies;

import java.util.ArrayList;
import java.util.List;

public class Mapper {

    private final static ModelMapper mapper = new ModelMapper();

    static {
        mapper.getConfiguration()
                .setMatchingStrategy(MatchingStrategies.STRICT)
                .setSkipNullEnabled(true);
    }

    public static void map(Object source, Object dest) {
        mapper.map(source, dest);
    }

    public static <D> D map(Object source, final Class<D> destType) {
        return mapper.map(source, destType);
    }

    public static <S, D> List<D> map(final List<S> source, final Class<D> destType) {
        List<D> dest = new ArrayList<D>();
        for (S element : source) {
            if (element == null) {
                continue;
            }
            dest.add(mapper.map(element, destType));
        }
        return dest;
    }
}
