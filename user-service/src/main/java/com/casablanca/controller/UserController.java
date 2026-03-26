package com.casablanca.controller;

import com.casablanca.dto.*;
import com.casablanca.entity.User;
import com.casablanca.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(@Valid @RequestBody RegisterRequest request) {
        return ResponseEntity.ok(userService.register(request));
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest request) {
        return ResponseEntity.ok(userService.login(request));
    }

    @GetMapping("/me")
    public ResponseEntity<User> getUserProfile(@RequestHeader("X-User-Id") Long userId) {
        User user = userService.getUserById(userId);
        user.setPassword(null);
        return ResponseEntity.ok(user);
    }

    @PostMapping("/interests")
    public ResponseEntity<InterestCompanyResponse> addInterest(
            @RequestHeader("X-User-Id") Long userId,
            @Valid @RequestBody InterestCompanyRequest request) {
        return ResponseEntity.ok(userService.addInterest(userId, request));
    }

    @GetMapping("/interests")
    public ResponseEntity<List<InterestCompanyResponse>> getInterests(
            @RequestHeader("X-User-Id") Long userId) {
        return ResponseEntity.ok(userService.getInterests(userId));
    }

    @DeleteMapping("/interests/{id}")
    public ResponseEntity<Void> deleteInterest(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable Long id) {
        userService.deleteInterest(userId, id);
        return ResponseEntity.noContent().build();
    }
}
