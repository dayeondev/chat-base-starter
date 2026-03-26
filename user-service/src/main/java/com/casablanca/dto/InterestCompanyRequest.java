package com.casablanca.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class InterestCompanyRequest {
    private Long companyRefId;

    @NotBlank(message = "Company code is required")
    private String companyCode;

    @NotBlank(message = "Company name is required")
    private String companyName;
}
