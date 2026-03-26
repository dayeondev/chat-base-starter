package com.casablanca.gateway.filter;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.factory.AbstractGatewayFilterFactory;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Mono;

import java.util.UUID;

@Component("RequestId")
public class RequestIdFilter extends AbstractGatewayFilterFactory<Object> {

    private static final Logger log = LoggerFactory.getLogger(RequestIdFilter.class);
    private static final String REQUEST_ID_HEADER = "X-Request-ID";

    @Override
    public String name() {
        return "RequestId";
    }

    @Override
    public GatewayFilter apply(Object config) {
        return (exchange, chain) -> {
            ServerHttpRequest request = exchange.getRequest();
            final String requestId = request.getHeaders().getFirst(REQUEST_ID_HEADER);

            // Generate Request ID if not present
            final String finalRequestId = (requestId == null || requestId.isEmpty()) 
                ? UUID.randomUUID().toString() 
                : requestId;

            // Log incoming request
            log.info("[{}] {} {} from {}",
                finalRequestId,
                request.getMethod(),
                request.getURI().getPath(),
                getClientIp(request)
            );

            // Add Request ID to response header for client tracing
            final ServerHttpResponse response = exchange.getResponse();
            response.getHeaders().set(REQUEST_ID_HEADER, finalRequestId);

            // Propagate Request ID to downstream services
            ServerHttpRequest mutatedRequest = request.mutate()
                    .header(REQUEST_ID_HEADER, finalRequestId)
                    .build();

            final long startTime = System.currentTimeMillis();

            return chain.filter(exchange.mutate().request(mutatedRequest).build())
                    .doFinally(signalType -> {
                        long duration = System.currentTimeMillis() - startTime;
                        int status = response.getStatusCode() != null ?
                            response.getStatusCode().value() : 0;
                        log.info("[{}] {} {} - {} ({}ms)",
                            finalRequestId,
                            request.getMethod(),
                            request.getURI().getPath(),
                            status,
                            duration
                        );
                    });
        };
    }

    private String getClientIp(ServerHttpRequest request) {
        String ip = request.getHeaders().getFirst("X-Forwarded-For");
        if (ip == null || ip.isEmpty()) {
            ip = request.getHeaders().getFirst("X-Real-IP");
        }
        if (ip == null || ip.isEmpty()) {
            ip = request.getRemoteAddress() != null ?
                request.getRemoteAddress().getAddress().getHostAddress() : "unknown";
        }
        return ip;
    }
}
