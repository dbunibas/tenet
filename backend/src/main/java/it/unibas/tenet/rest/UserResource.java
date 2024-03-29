package it.unibas.tenet.rest;

import io.smallrye.common.constraint.NotNull;
import it.unibas.tenet.model.dto.frontend.UserDTO;
import it.unibas.tenet.service.UserService;
import jakarta.annotation.security.PermitAll;
import jakarta.enterprise.context.RequestScoped;
import jakarta.inject.Inject;
import jakarta.validation.Valid;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@RequestScoped
@Path("/users")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class UserResource {

    @Inject
    private UserService userService;

    @POST
    @Path("/login")
    @PermitAll
    public UserDTO login(@NotNull @Valid UserDTO loginUser) {
        return userService.login(loginUser);
    }

}
