# Mathematical Model & Algorithms

## 1. Feature Normalization — Z-Score Standardization

Each raw feature is normalized using StandardScaler before feeding into the autoencoder:

$$
x'_i = \frac{x_i - \mu_i}{\sigma_i}
$$

Where:
- `x_i` = raw feature value
- `μ_i` = mean of feature `i` across all samples
- `σ_i` = standard deviation of feature `i`
- `x'_i` = normalized feature value (zero mean, unit variance)

---

## 2. Autoencoder Architecture

### Encoder

$$
h_1 = \text{ReLU}(W_1 \cdot x + b_1) \quad \text{where } W_1 \in \mathbb{R}^{32 \times 15}
$$

$$
z = \text{ReLU}(W_2 \cdot h_1 + b_2) \quad \text{where } W_2 \in \mathbb{R}^{16 \times 32}
$$

### Decoder

$$
h_3 = \text{ReLU}(W_3 \cdot z + b_3) \quad \text{where } W_3 \in \mathbb{R}^{32 \times 16}
$$

$$
\hat{x} = W_4 \cdot h_3 + b_4 \quad \text{where } W_4 \in \mathbb{R}^{15 \times 32}
$$

### ReLU Activation Function

$$
\text{ReLU}(a) = \max(0, a)
$$

### Summary

```
Input(15) → Linear(32) → ReLU → Linear(16) → ReLU → Linear(32) → ReLU → Linear(15) → Output
         |_________ Encoder __________|  |__________ Decoder __________|
```

---

## 3. Loss Function — Mean Squared Error (MSE)

The autoencoder is trained to minimize the reconstruction error:

$$
\mathcal{L}(\theta) = \frac{1}{N} \sum_{i=1}^{N} \| x_i - \hat{x}_i \|^2 = \frac{1}{N} \sum_{i=1}^{N} \frac{1}{d} \sum_{j=1}^{d} (x_{ij} - \hat{x}_{ij})^2
$$

Where:
- `N` = number of training samples (67,238)
- `d` = feature dimension (15)
- `x_i` = original input vector
- `x̂_i` = reconstructed output vector
- `θ` = all learnable parameters (W₁, b₁, W₂, b₂, W₃, b₃, W₄, b₄)

### Optimizer — Adam

$$
m_t = \beta_1 m_{t-1} + (1 - \beta_1) g_t
$$

$$
v_t = \beta_2 v_{t-1} + (1 - \beta_2) g_t^2
$$

$$
\theta_{t+1} = \theta_t - \frac{\alpha}{\sqrt{\hat{v}_t} + \epsilon} \hat{m}_t
$$

Where: `α = 0.001`, `β₁ = 0.9`, `β₂ = 0.999`, `ε = 10⁻⁸`

---

## 4. Anomaly Detection — Per-Sample Reconstruction Error

For each weekly feature vector, the reconstruction error is computed as:

$$
e_i = \frac{1}{d} \sum_{j=1}^{d} (x_{ij} - \hat{x}_{ij})^2
$$

A sample is flagged as **anomalous** if:

$$
\text{Anomaly}(i) = \begin{cases} 1 & \text{if } e_i > \tau \\ 0 & \text{otherwise} \end{cases}
$$

Where the threshold `τ` is the 99th percentile:

$$
\tau = P_{99}(\{e_1, e_2, \ldots, e_N\})
$$

**Result:** 673 anomalous weeks out of 67,238 total (≈ 1%).

---

## 5. User-Level Risk Scoring

Each user's overall risk score is the average reconstruction error across all their weekly vectors:

$$
R_u = \frac{1}{|W_u|} \sum_{w \in W_u} e_w
$$

Where:
- `R_u` = risk score for user `u`
- `W_u` = set of all weekly feature vectors for user `u`
- `e_w` = reconstruction error for week `w`

### User Classification

$$
\text{Class}(u) = \begin{cases} \text{CONFIRMED THREAT} & \text{if } R_u \geq P_{99}(\{R_1, \ldots, R_M\}) \\ \text{SUSPICIOUS} & \text{if } R_u \geq P_{95}(\{R_1, \ldots, R_M\}) \\ \text{NORMAL} & \text{otherwise} \end{cases}
$$

Where `M = 1,000` (total users).

---

## 6. XAI — Feature Deviation Analysis

For a flagged user `u`, the contribution of each feature `j` is computed as:

$$
C_j^{(u)} = \frac{|\bar{x}_j^{(u)} - \bar{x}_j^{(\text{global})}|}{|\bar{x}_j^{(\text{global})}|}
$$

Where:
- `x̄_j^(u)` = average value of feature `j` across all weeks of user `u`
- `x̄_j^(global)` = average value of feature `j` across all users (global mean)
- `C_j^(u)` = relative deviation (contribution score) for feature `j`

Features are ranked by `C_j` in descending order; the top 8 are reported.

---

## 7. Graph Analysis — PageRank Centrality

For the email/file/USB interaction network, node importance is computed using PageRank:

$$
PR(v) = \frac{1 - d}{N} + d \sum_{u \in B(v)} \frac{PR(u)}{L(u)}
$$

Where:
- `PR(v)` = PageRank score of node `v`
- `B(v)` = set of nodes with edges pointing to `v`
- `L(u)` = number of outgoing edges from node `u`
- `d` = damping factor (default 0.85)
- `N` = total number of nodes in the graph

---

## 8. Per-User Activity Node Risk Classification

Each weekly activity node in the per-user graph is assigned a risk level:

$$
\text{Risk}(w) = \begin{cases} \text{HIGH (red)} & \text{if } w \in A_u \text{ and } e_w > 0.001 \\ \text{MEDIUM (orange)} & \text{if } w \in A_u \text{ or } \frac{h_w}{n_w} > 0.4 \\ \text{LOW (green)} & \text{otherwise} \end{cases}
$$

Where:
- `A_u` = set of anomalous weeks for user `u`
- `e_w` = reconstruction error for week `w`
- `h_w` = after-hours event count in week `w`
- `n_w` = total event count in week `w`

---

## Algorithm 1: Autoencoder-Based Anomaly Detection

```
ALGORITHM: Insider Threat Detection via Autoencoder

Input:  Weekly feature matrix X ∈ ℝ^(N×d), N=67,238, d=15
Output: Set of anomalous weeks A, user risk scores R

1.  NORMALIZE X using StandardScaler → X'
2.  INITIALIZE Autoencoder with random weights θ
3.  FOR epoch = 1 to 50 DO
4.      FOR each mini-batch B ⊂ X' (batch_size=256) DO
5.          Compute reconstructions: X̂_B = Decoder(Encoder(X_B))
6.          Compute loss: L = (1/|B|) Σ ||x - x̂||²
7.          Update θ via Adam optimizer: θ ← θ - α·∇L
8.      END FOR
9.  END FOR
10. FOR each sample x'_i ∈ X' DO
11.     Compute reconstruction error: e_i = (1/d) Σ(x'_ij - x̂_ij)²
12. END FOR
13. SET threshold τ = 99th percentile of {e_1, ..., e_N}
14. SET A = {i : e_i > τ}     ▹ 673 anomalous weeks
15. FOR each user u DO
16.     R_u = mean({e_w : w ∈ weeks(u)})
17. END FOR
18. CLASSIFY users by percentile of R_u
19. RETURN A, R
```

---

## Algorithm 2: XAI Feature Contribution Ranking

```
ALGORITHM: Deviation-Based Explainability

Input:  Flagged user u, weekly features database
Output: Top-K contributing features with deviation scores

1.  FETCH all weekly vectors for user u → {w_1, ..., w_T}
2.  COMPUTE user average: x̄_j^(u) = (1/T) Σ w_t[j]  for each feature j
3.  SAMPLE 5,000 vectors from global database
4.  COMPUTE global average: x̄_j^(global) for each feature j
5.  FOR each feature j = 1 to d DO
6.      C_j = |x̄_j^(u) - x̄_j^(global)| / |x̄_j^(global)|
7.  END FOR
8.  SORT features by C_j in descending order
9.  RETURN top K=8 features with (feature_name, user_value, global_avg, C_j)
```

---

## Summary of Key Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Input dimension (d) | 15 | Number of behavioral + psychometric features |
| Encoder layers | 15 → 32 → 16 | Two hidden layers with ReLU |
| Latent dimension | 16 | Compressed representation size |
| Decoder layers | 16 → 32 → 15 | Symmetric to encoder |
| Learning rate (α) | 0.001 | Adam optimizer |
| Epochs | 50 | Training iterations |
| Batch size | 256 | Mini-batch SGD |
| Anomaly threshold | 99th percentile | Top 1% reconstruction errors |
| Threat threshold | 99th percentile of users | Top 1% risk scores |
| Suspicious threshold | 95th percentile of users | Top 5% risk scores |
| PageRank damping (d) | 0.85 | Default NetworkX value |
| XAI top-K features | 8 | Features reported per user |
| Total samples (N) | 67,238 | Weekly feature vectors |
| Total users (M) | 1,000 | Monitored employees |
