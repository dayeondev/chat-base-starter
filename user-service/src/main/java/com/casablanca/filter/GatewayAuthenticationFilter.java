package com.casablanca.filter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Collections;

@Component
public class GatewayAuthenticationFilter extends OncePerRequestFilter {

    private static final Logger log = LoggerFactory.getLogger(GatewayAuthenticationFilter.class);

    @Value("${app.gateway.secret}")
    private String gatewaySecret;

    private static final String GATEWAY_SECRET_HEADER = "X-Gateway-Secret";
    private static final String USER_ID_HEADER = "X-User-Id";
    private static final String USERNAME_HEADER = "X-Username";

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {

        String userIdHeader = request.getHeader(USER_ID_HEADER);
        String usernameHeader = request.getHeader(USERNAME_HEADER);
        String gatewaySecretHeader = request.getHeader(GATEWAY_SECRET_HEADER);

        // If headers are present, validate they come from the gateway
        if (userIdHeader != null && usernameHeader != null) {
            // Validate gateway secret - this is sufficient to verify the request comes from our gateway
            if (!gatewaySecret.equals(gatewaySecretHeader)) {
                log.warn("GatewayAuthenticationFilter: Invalid gateway secret from {}", request.getRemoteAddr());
                response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Invalid gateway secret");
                return;
            }

            log.debug("GatewayAuthenticationFilter: Valid gateway secret, authenticating user");

            // Parse and validate user ID
            Long userId;
            try {
                userId = Long.valueOf(userIdHeader);
            } catch (NumberFormatException e) {
                response.sendError(HttpServletResponse.SC_BAD_REQUEST, "Invalid user ID format");
                return;
            }

            // All checks passed - set authentication
            String username = usernameHeader;
            UsernamePasswordAuthenticationToken authentication =
                new UsernamePasswordAuthenticationToken(
                    userId,
                    null,
                    Collections.singletonList(new SimpleGrantedAuthority("ROLE_USER"))
                );
            authentication.setDetails(username);

            SecurityContextHolder.getContext().setAuthentication(authentication);
        }

        filterChain.doFilter(request, response);
    }
}
