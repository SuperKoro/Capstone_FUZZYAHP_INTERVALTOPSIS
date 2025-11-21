# Expert Aggregation Methods trong Project

## Tổng Quan

Project này sử dụng **2 phương pháp khác nhau** để kết hợp (aggregate) ý kiến của nhiều chuyên gia (experts):

1. **Fuzzy AHP**: Sử dụng **Fuzzy Geometric Mean** (trung bình hình học mờ)
2. **Interval TOPSIS**: Sử dụng **Arithmetic Mean** (trung bình số học)

---

## 1. Fuzzy AHP - Fuzzy Geometric Mean

### 📍 File Implementation
[`algorithms/fuzzy_ahp.py`](file:///G:/anti/supplier_selection_app/algorithms/fuzzy_ahp.py#L50-L96) - Method `fuzzy_geometric_mean()`

### 🎯 Mục Đích
Kết hợp các ma trận so sánh cặp (pairwise comparison matrices) từ nhiều chuyên gia để tạo ra một ma trận đồng thuận (consensus matrix).

### 📐 Công Thức

Cho K chuyên gia với ma trận fuzzy comparison, mỗi phần tử được biểu diễn bởi Triangular Fuzzy Number (TFN): `(l, m, u)` (lower, middle, upper).

**Weighted Geometric Mean** được tính như sau:

```
Aggregated_ij = (l_ij, m_ij, u_ij)

Trong đó:
l_ij = (l₁^ω₁) × (l₂^ω₂) × ... × (lₖ^ωₖ)
m_ij = (m₁^ω₁) × (m₂^ω₂) × ... × (mₖ^ωₖ)
u_ij = (u₁^ω₁) × (u₂^ω₂) × ... × (uₖ^ωₖ)

ω₁ + ω₂ + ... + ωₖ = 1.0 (expert weights)
```

Nếu không có expert weights (hoặc weights bằng nhau), sử dụng **standard geometric mean** với ω = 1/K.

### 💻 Code Implementation

```python
@staticmethod
def fuzzy_geometric_mean(fuzzy_matrices: List[np.ndarray], 
                        expert_weights: Optional[List[float]] = None) -> np.ndarray:
    """
    Calculate fuzzy geometric mean of multiple fuzzy comparison matrices
    
    Args:
        fuzzy_matrices: List of fuzzy matrices, each is (n, n, 3) where last dim is (l, m, u)
        expert_weights: Optional list of expert weights (must sum to 1.0)
        
    Returns:
        Aggregated fuzzy matrix (n, n, 3)
    """
    n_experts = len(fuzzy_matrices)
    n_criteria = fuzzy_matrices[0].shape[0]
    
    # Handle weights
    if expert_weights is None or len(expert_weights) != n_experts:
        weights = [1.0 / n_experts] * n_experts  # Equal weights
    else:
        weights = expert_weights
    
    aggregated = np.zeros((n_criteria, n_criteria, 3))
    
    for i in range(n_criteria):
        for j in range(n_criteria):
            if i == j:
                aggregated[i, j] = [1, 1, 1]  # Diagonal elements
            else:
                # Collect fuzzy values across experts
                l_values = [matrix[i, j, 0] for matrix in fuzzy_matrices]
                m_values = [matrix[i, j, 1] for matrix in fuzzy_matrices]
                u_values = [matrix[i, j, 2] for matrix in fuzzy_matrices]
                
                # Weighted geometric mean
                aggregated[i, j, 0] = np.prod([l ** w for l, w in zip(l_values, weights)])
                aggregated[i, j, 1] = np.prod([m ** w for m, w in zip(m_values, weights)])
                aggregated[i, j, 2] = np.prod([u ** w for u, w in zip(u_values, weights)])
    
    return aggregated
```

### 🔍 Workflow trong Project

1. Mỗi expert tạo ma trận pairwise comparison trong AHP tab
2. Khi tính toán weights, method `FuzzyAHP.calculate_weights()` được gọi:
   ```python
   # Step 1: Aggregate expert judgments using weighted fuzzy geometric mean
   aggregated_matrix = cls.fuzzy_geometric_mean(fuzzy_matrices, expert_weights)
   
   # Step 2: Calculate fuzzy weights
   fuzzy_weights = cls.calculate_fuzzy_weights(aggregated_matrix)
   
   # Step 3: Defuzzify to get crisp weights
   crisp_weights = cls.defuzzify(fuzzy_weights)
   ```

### ✅ Tại Sao Dùng Geometric Mean?

- **Bảo toàn tính chất reciprocal**: Nếu expert 1 đánh giá A/B = 3, thì B/A = 1/3. Geometric mean bảo toàn tính chất này.
- **Phù hợp với multiplicative scale**: AHP sử dụng scale từ 1/9 đến 9 (multiplicative).
- **Consistency**: Geometric mean tạo ma trận có CR (Consistency Ratio) thấp hơn so với arithmetic mean.

---

## 2. Interval TOPSIS - Arithmetic Mean

### 📍 File Implementation
[`algorithms/interval_topsis.py`](file:///G:/anti/supplier_selection_app/algorithms/interval_topsis.py#L22-L43) - Method `aggregate_expert_ratings()`

### 🎯 Mục Đích
Kết hợp các decision matrices (performance ratings) từ nhiều chuyên gia để tạo ra một decision matrix đồng thuận.

### 📐 Công Thức

Cho K chuyên gia với decision matrices, mỗi phần tử là interval: `[lower, upper]`.

**Arithmetic Mean** được tính như sau:

```
Aggregated_ij = [avg(lower₁, lower₂, ..., lowerₖ), avg(upper₁, upper₂, ..., upperₖ)]

Trong đó:
avg(lower₁, ..., lowerₖ) = (lower₁ + lower₂ + ... + lowerₖ) / K
avg(upper₁, ..., upperₖ) = (upper₁ + upper₂ + ... + upperₖ) / K
```

### 💻 Code Implementation

```python
@staticmethod
def aggregate_expert_ratings(expert_matrices: List[np.ndarray]) -> np.ndarray:
    """
    Aggregate ratings from multiple experts using Arithmetic Mean
    
    Args:
        expert_matrices: List of decision matrices (one per expert)
                        Each matrix is (m, n, 2) where last dim is [lower, upper]
                        
    Returns:
        Aggregated decision matrix (m, n, 2)
    """
    if not expert_matrices:
        raise ValueError("No expert matrices to aggregate")
        
    # Stack matrices along a new axis: (k, m, n, 2)
    stacked = np.stack(expert_matrices)
    
    # Calculate mean along the first axis (experts)
    aggregated = np.mean(stacked, axis=0)
    
    return aggregated
```

### 🔍 Workflow trong Project

1. Mỗi expert chọn linguistic ratings trong TOPSIS Rating tab
2. Mỗi linguistic rating được convert thành interval (ví dụ: "Good" → [5, 7])
3. Khi calculate ranking, method `calculate_ranking()` thực hiện:

```python
# Collect matrices for each expert
expert_matrices = []
for expert in self.experts:
    ratings = database.get_topsis_ratings(project_id, expert['id'])
    
    # Build matrix for this expert (m alternatives × n criteria × 2)
    matrix = np.zeros((n_alternatives, n_criteria, 2))
    
    for i, alt in enumerate(alternatives):
        for j, crit in enumerate(criteria):
            matrix[i, j] = [rating_lower, rating_upper]
    
    expert_matrices.append(matrix)

# Aggregate ratings from all experts
aggregated_matrix = IntervalTOPSIS.aggregate_expert_ratings(expert_matrices)

# Calculate TOPSIS ranking using aggregated matrix
CC, results = IntervalTOPSIS.rank_alternatives(aggregated_matrix, weights, is_benefit)
```

### ✅ Tại Sao Dùng Arithmetic Mean?

- **Simple và intuitive**: Performance ratings là additive scale (0-10).
- **Phù hợp với interval data**: Arithmetic mean bảo toàn đặc tính của intervals.
- **Equal treatment**: Tất cả experts có trọng số bằng nhau (hiện tại không support expert weights trong TOPSIS).

---

## 3. So Sánh Hai Phương Pháp

| Tiêu chí | Fuzzy AHP | Interval TOPSIS |
|----------|-----------|-----------------|
| **Aggregation Method** | Fuzzy Geometric Mean | Arithmetic Mean |
| **Input Data Type** | Triangular Fuzzy Numbers (TFN) | Interval Numbers |
| **Scale Type** | Multiplicative (1/9 to 9) | Additive (0 to 10) |
| **Expert Weights** | Supported | Not supported (equal weights) |
| **Purpose** | Criteria weighting | Alternative rating |
| **Preserve Property** | Reciprocal property | Interval bounds |
| **Complexity** | Higher (3 values per element) | Lower (2 values per element) |

---

## 4. Expert Management trong Project

### Cách Tạo và Quản Lý Experts

1. **Tạo experts**: Trong AHP tab, phần "Expert Management"
2. **Assign weights**: Mỗi expert có weight (phải tổng = 1.0)
3. **Input comparisons**: Mỗi expert nhập pairwise comparisons riêng
4. **Input ratings**: Mỗi expert nhập performance ratings riêng trong TOPSIS tab

### Database Schema

**Experts Table:**
```sql
CREATE TABLE experts (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    name TEXT NOT NULL,
    weight REAL DEFAULT 0.0
)
```

**Expert Data:**
- AHP comparisons: `pairwise_comparisons` table có `expert_id` column
- TOPSIS ratings: `topsis_ratings` table có `expert_id` column

---

## 5. Ví Dụ Minh Họa

### Ví Dụ 1: Fuzzy AHP Aggregation

**3 experts đánh giá tiêu chí A so với B:**

| Expert | Linguistic | TFN (l, m, u) | Weight |
|--------|------------|---------------|--------|
| Expert 1 | Moderately important | (2, 3, 4) | 0.5 |
| Expert 2 | Strongly important | (4, 5, 6) | 0.3 |
| Expert 3 | Equally important | (1, 1, 1) | 0.2 |

**Aggregated TFN:**
```
l = (2^0.5) × (4^0.3) × (1^0.2) = 2.38
m = (3^0.5) × (5^0.3) × (1^0.2) = 2.82
u = (4^0.5) × (6^0.3) × (1^0.2) = 3.36

Result: (2.38, 2.82, 3.36)
```

### Ví Dụ 2: TOPSIS Aggregation

**3 experts đánh giá Supplier X trên Criterion "Quality":**

| Expert | Linguistic | Interval [l, u] |
|--------|-----------|-----------------|
| Expert 1 | Good | [5, 7] |
| Expert 2 | Very Good | [7, 9] |
| Expert 3 | Fair | [3, 5] |

**Aggregated Interval:**
```
lower = (5 + 7 + 3) / 3 = 5.0
upper = (7 + 9 + 5) / 3 = 7.0

Result: [5.0, 7.0]
```

---

## 6. Code Files Liên Quan

1. **Fuzzy AHP:**
   - [`algorithms/fuzzy_ahp.py`](file:///G:/anti/supplier_selection_app/algorithms/fuzzy_ahp.py) - Core algorithm
   - [`algorithms/hierarchical_ahp.py`](file:///G:/anti/supplier_selection_app/algorithms/hierarchical_ahp.py) - Hierarchical extension
   - [`gui/ahp_tab.py`](file:///G:/anti/supplier_selection_app/gui/ahp_tab.py) - UI for expert input

2. **Interval TOPSIS:**
   - [`algorithms/interval_topsis.py`](file:///G:/anti/supplier_selection_app/algorithms/interval_topsis.py) - Core algorithm
   - [`gui/topsis_tab.py`](file:///G:/anti/supplier_selection_app/gui/topsis_tab.py) - UI for expert input

3. **Database:**
   - [`database/db_manager.py`](file:///G:/anti/supplier_selection_app/database/db_manager.py) - Expert and rating storage

---

## 7. Tóm Tắt

✅ **Fuzzy AHP** combine experts bằng **Geometric Mean có weighted** để:
   - Tạo consensus pairwise comparison matrix
   - Bảo toàn reciprocal property
   - Hỗ trợ expert weights khác nhau

✅ **Interval TOPSIS** combine experts bằng **Arithmetic Mean** để:
   - Tạo consensus decision matrix
   - Simple và intuitive
   - Tất cả experts có trọng số bằng nhau

Cả hai phương pháp đều cho phép nhiều experts tham gia quyết định, tạo ra kết quả đồng thuận và khách quan hơn so với chỉ có một expert.
