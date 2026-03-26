package com.casablanca.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class InterestCompanyResponse {
    private Long id;
    private Long companyRefId;
    private String companyCode;
    private String companyName;
    private LocalDateTime createdAt;
}
