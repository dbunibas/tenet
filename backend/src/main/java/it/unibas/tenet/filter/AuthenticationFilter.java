package it.unibas.tenet.filter;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import it.unibas.tenet.util.JWTUtil;
import jakarta.annotation.Priority;
import jakarta.annotation.security.PermitAll;
import jakarta.ws.rs.Priorities;
import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.container.ContainerRequestFilter;
import jakarta.ws.rs.container.ResourceInfo;
import jakarta.ws.rs.core.Context;
import jakarta.ws.rs.core.HttpHeaders;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.core.SecurityContext;
import jakarta.ws.rs.ext.Provider;
import lombok.extern.slf4j.Slf4j;

import java.io.IOException;
import java.lang.reflect.Method;
import java.security.Principal;

@Provider
@Priority(Priorities.AUTHENTICATION)
@Slf4j
public class AuthenticationFilter implements ContainerRequestFilter {

    private static final String AUTHENTICATION_SCHEME = "Bearer";
    private static final ObjectMapper mapper = new ObjectMapper();
    @Context
    private ResourceInfo resourceInfo;

    @Override
    public void filter(ContainerRequestContext requestContext) throws IOException {
        if (requestContext.getUriInfo().getPath().startsWith("openapi.") || requestContext.getUriInfo().getPath().startsWith("application.wadl")) {
            return;
        }
        if (requestContext.getMethod().equalsIgnoreCase("OPTIONS")) {
            return;
        }
        Class<?> resourceClass = resourceInfo.getResourceClass();
        Method method = resourceInfo.getResourceMethod();
        if (resourceClass.isAnnotationPresent(PermitAll.class) || method.isAnnotationPresent(PermitAll.class)) {
            return;
        }
        String intestazioneAutorizzazione = requestContext.getHeaderString(HttpHeaders.AUTHORIZATION);
        if (!isNotAuthToken(intestazioneAutorizzazione)) {
            stopRequest("Missing auth token", requestContext);
            return;
        }
        String token = intestazioneAutorizzazione.substring(AUTHENTICATION_SCHEME.length()).trim();
        try {
            String emailUtente = JWTUtil.verifyToken(token);
            SecurityContext originalSecurityContext = requestContext.getSecurityContext();
            requestContext.setSecurityContext(new AppSecurityContext(emailUtente, originalSecurityContext.isSecure(), originalSecurityContext.getAuthenticationScheme()));
        } catch (Exception e) {
            log.error("Error during token validation {}", e.getMessage(), e);
            stopRequest("Non valid Auth Token", requestContext);
        }
    }

    private boolean isNotAuthToken(String authorizationHeader) {
        return authorizationHeader != null && authorizationHeader.toLowerCase()
                .startsWith(AUTHENTICATION_SCHEME.toLowerCase() + " ");
    }

    private void stopRequest(String messaggio, ContainerRequestContext requestContext) {
        ObjectNode json = mapper.createObjectNode();
        json.put("error", messaggio);
        requestContext.abortWith(
                Response.status(Response.Status.UNAUTHORIZED)
                        .entity(json.toPrettyString())
                        .build());
    }

    class AppSecurityContext implements SecurityContext {

        private final String username;
        private final boolean secure;
        private final String authenticationScheme;

        public AppSecurityContext(String username, boolean secure, String authenticationScheme) {
            this.username = username;
            this.secure = secure;
            this.authenticationScheme = authenticationScheme;
        }

        @Override
        public Principal getUserPrincipal() {
            return new Principal() {
                @Override
                public String getName() {
                    return username;
                }
            };
        }

        @Override
        public boolean isSecure() {
            return secure;
        }

        @Override
        public String getAuthenticationScheme() {
            return authenticationScheme;
        }

        @Override
        public boolean isUserInRole(String role) {
            return true;
        }

    }
}
