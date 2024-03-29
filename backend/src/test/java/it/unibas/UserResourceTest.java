package it.unibas;

import io.quarkus.test.junit.QuarkusTest;
import org.junit.jupiter.api.Test;

import static io.restassured.RestAssured.given;
import it.unibas.tenet.dao.UserRepository;
import it.unibas.tenet.model.User;
import it.unibas.tenet.service.PasswordHashingOperator;
import jakarta.inject.Inject;

@QuarkusTest
public class UserResourceTest {

    private static final String BASE = "/api/v1";

    @Inject
    private UserRepository userRepository;

    @jakarta.inject.Inject
    private PasswordHashingOperator passwordHashingOperator;

    @Test
    public void loginTest() {
        User mockUser = new User();
        mockUser.setUsername("mock");
        mockUser.setPassword(passwordHashingOperator.md5Hash("mock"));
        userRepository.persist(mockUser);

        given().body("{ \"username\": \"mock\", \"password\": \"wrong password\"}")
                .header("Content-Type", "application/json")
                .when().post(BASE + "/users/login")
                .then()
                .statusCode(400);

        given().body("{ \"username\": \"mock\", \"password\": \"mock\"}")
                .header("Content-Type", "application/json")
                .when().post(BASE + "/users/login")
                .then()
                .statusCode(200);
        userRepository.delete(mockUser);
    }

}
