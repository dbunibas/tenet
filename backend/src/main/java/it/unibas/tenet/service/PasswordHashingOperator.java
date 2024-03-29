package it.unibas.tenet.service;

import jakarta.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

@Singleton
@Slf4j
public class PasswordHashingOperator {

    public String md5Hash(String password) {
        try {
            java.security.MessageDigest digest = java.security.MessageDigest.getInstance("MD5");
            byte[] hash = digest.digest(password.getBytes());
            String hashString = "";
            for (int i = 0; i < hash.length; i++) {
                hashString += Integer.toHexString(
                        (hash[i] & 0xFF) | 0x100
                ).toLowerCase().substring(1, 3);
            }
            log.debug("HASHED PASSWORD: {}", hashString);
            return hashString;

        } catch (Exception ex) {
            throw new IllegalArgumentException("Failed to hash");
        }
    }
}
