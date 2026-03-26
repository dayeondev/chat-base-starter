package com.casablanca.service;

import com.casablanca.config.JwtUtil;
import com.casablanca.dto.*;
import com.casablanca.entity.InterestCompany;
import com.casablanca.entity.User;
import com.casablanca.exception.ResourceNotFoundException;
import com.casablanca.exception.UserAlreadyExistsException;
import com.casablanca.repository.InterestCompanyRepository;
import com.casablanca.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final InterestCompanyRepository interestCompanyRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    @Transactional
    public AuthResponse register(RegisterRequest request) {
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new UserAlreadyExistsException("Username already exists");
        }
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new UserAlreadyExistsException("Email already exists");
        }

        User user = new User();
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        user.setPassword(passwordEncoder.encode(request.getPassword()));

        user = userRepository.save(user);

        String token = jwtUtil.generateToken(user.getUsername(), user.getId());
        return new AuthResponse(token, user.getUsername(), user.getEmail());
    }

    public AuthResponse login(LoginRequest request) {
        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> new ResourceNotFoundException("User not found"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new RuntimeException("Invalid password");
        }

        String token = jwtUtil.generateToken(user.getUsername(), user.getId());
        return new AuthResponse(token, user.getUsername(), user.getEmail());
    }

    public User getUserByUsername(String username) {
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new ResourceNotFoundException("User not found"));
    }

    public User getUserById(Long userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + userId));
    }

    @Transactional
    public InterestCompanyResponse addInterest(Long userId, InterestCompanyRequest request) {
        if (interestCompanyRepository.existsByUserIdAndCompanyCode(userId, request.getCompanyCode())) {
            throw new RuntimeException("Company already in interests");
        }

        InterestCompany interest = new InterestCompany();
        interest.setUserId(userId);
        interest.setCompanyRefId(request.getCompanyRefId());
        interest.setCompanyCode(request.getCompanyCode());
        interest.setCompanyName(request.getCompanyName());

        interest = interestCompanyRepository.save(interest);
        return mapToResponse(interest);
    }

    public List<InterestCompanyResponse> getInterests(Long userId) {
        return interestCompanyRepository.findByUserIdOrderByCreatedAtDesc(userId)
                .stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    @Transactional
    public void deleteInterest(Long userId, Long id) {
        interestCompanyRepository.deleteByUserIdAndId(userId, id);
    }

    private InterestCompanyResponse mapToResponse(InterestCompany interest) {
        return new InterestCompanyResponse(
                interest.getId(),
                interest.getCompanyRefId(),
                interest.getCompanyCode(),
                interest.getCompanyName(),
                interest.getCreatedAt()
        );
    }
}
