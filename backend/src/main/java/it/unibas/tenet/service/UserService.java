package it.unibas.tenet.service;

import it.unibas.tenet.dao.UserRepository;
import it.unibas.tenet.model.User;
import it.unibas.tenet.model.dto.frontend.UserDTO;
import it.unibas.tenet.util.JWTUtil;
import it.unibas.tenet.util.Mapper;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import lombok.extern.slf4j.Slf4j;

@ApplicationScoped
@Slf4j
public class UserService {

    @Inject
    private UserRepository userRepository;

    @Inject
    private PasswordHashingOperator passwordHashingOperator;

    public UserDTO login(UserDTO loginUser) {
        log.debug("Attempting login from user {}", loginUser.getUsername());
        User user = userRepository.findByUsername(loginUser.getUsername());
        log.warn("PASSWORD HASH {}", passwordHashingOperator.md5Hash(loginUser.getPassword()));
        if (user == null) {
            throw new IllegalArgumentException("Username not found");
        }
        if (!passwordHashingOperator.md5Hash(loginUser.getPassword()).equals(user.getPassword())) {
            throw new IllegalArgumentException("Wrong password");
        }
        UserDTO userDTO = Mapper.map(user, UserDTO.class);
        userDTO.setPassword(null);
        userDTO.setAuthToken(JWTUtil.generateToken(userDTO.getUsername()));
        log.debug("Login authorized {}", userDTO.getId());
        return userDTO;
    }

}
