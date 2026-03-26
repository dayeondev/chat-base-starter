package com.casablanca.repository;

import com.casablanca.entity.InterestCompany;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface InterestCompanyRepository extends JpaRepository<InterestCompany, Long> {
    List<InterestCompany> findByUserIdOrderByCreatedAtDesc(Long userId);
    boolean existsByUserIdAndCompanyCode(Long userId, String companyCode);
    void deleteByUserIdAndId(Long userId, Long id);
}
