package it.unibas.tenet.rest;

import jakarta.annotation.security.PermitAll;
import jakarta.enterprise.context.RequestScoped;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Path("")
@RequestScoped
@PermitAll
public class UpResource {

    @Path("/test")
    @GET
    @Produces(MediaType.TEXT_PLAIN)
    public String testUp() {
        return "Server is up";
    }

}
