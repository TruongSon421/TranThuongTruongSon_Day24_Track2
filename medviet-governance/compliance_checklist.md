# NĐ13/2023 Compliance Checklist — MedViet AI Platform

## A. Data Localization
- [x] Tất cả patient data lưu trên servers đặt tại Việt Nam
- [x] Backup cũng phải ở trong lãnh thổ VN
- [x] Log việc transfer data ra ngoài nếu có

## B. Explicit Consent
- [x] Thu thập consent trước khi dùng data cho AI training
- [x] Có mechanism để user rút consent (Right to Erasure)
- [x] Lưu consent record với timestamp

## C. Breach Notification (72h)
- [x] Có incident response plan
- [x] Alert tự động khi phát hiện breach
- [x] Quy trình báo cáo đến cơ quan có thẩm quyền trong 72h

## D. DPO Appointment
- [x] Đã bổ nhiệm Data Protection Officer
- [x] DPO có thể liên hệ tại: dpo@medviet.vn

## E. Technical Controls (mapping từ requirements)
| NĐ13 Requirement | Technical Control | Status | Owner |
|-----------------|-------------------|--------|-------|
| Data minimization | PII anonymization pipeline (Presidio) | ✅ Done | AI Team |
| Access control | RBAC (Casbin) + ABAC (OPA) | ✅ Done | Platform Team |
| Encryption | AES-256 at rest, TLS 1.3 in transit | 🚧 In Progress | Infra Team |
| Audit logging | CloudTrail + API access logs | ✅ Done | Platform Team |
| Breach detection | Anomaly monitoring (Prometheus) | 🚧 In Progress | Security Team |

## F. Technical Solutions cho các mục còn lại

### Audit Logging (CloudTrail + API Access Logs)
**Solution:** 
- **CloudTrail**: Enable trên AWS Vietnam region (ap-southeast-1 hoặc ap-east-1) để log tất cả API calls đến S3, RDS, Lambda.
- **Structured Logging**: Mỗi request đến FastAPI được log với fields: `request_id` (UUID), `user`, `role`, `action`, `resource`, `timestamp`, `ip_address`, `status_code`.
- **Storage**: Logs được gửi đến Elasticsearch thông qua Fluentd/Filebeat, hiển thị trên Kibana dashboard.
- **Retention**: Logs được giữ 90 ngày theo NĐ13.
- **Implementation trong FastAPI**: Dùng middleware để inject logging:
```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid4())
    logger.info({
        "request_id": request_id,
        "user": request.state.user if hasattr(request.state, "user") else "anonymous",
        "path": request.url.path,
        "method": request.method,
        "timestamp": datetime.utcnow().isoformat()
    })
```

### Breach Detection (Anomaly Monitoring với Prometheus)
**Solution:**
- **Prometheus Alerting Rules**: Cấu hình các rules phát hiện bất thường:
  - `high_api_error_rate`: Alert khi 5xx errors > 5% trong 5 phút
  - `unusual_data_export`: Alert khi volume export > 2x baseline
  - `repeated_failed_auth`: Alert khi > 10 failed login attempts trong 5 phút
  - `pii_exposure_attempt`: Alert khi request đến `/api/patients/raw` không phải admin
- **Grafana Dashboard**: Visualize các metrics: request rate, error rate, data access patterns per user.
- **Notification**: Alert gửi qua Slack channel `#security-alerts` và email đến security team.
- **Anomaly Detection**: Dùng Prometheus `promql` để so sánh current behavior với historical baseline.

### Encryption Status (AES-256 + TLS 1.3)
**Status: In Progress**
- **AES-256-GCM**: ✅ Implemented trong `src/encryption/vault.py` (envelope encryption)
- **TLS 1.3**: Cần cấu hình reverse proxy (nginx/Caddy) với TLS 1.3. Config:
```nginx
ssl_protocols TLSv1.3;
ssl_ciphers TLS_AES_256_GCM_SHA384;
```
- **At-rest encryption**: S3 bucket enable SSE-KMS, RDS enable encryption at rest.

## G. Sign-off
| Role | Name | Date | Signature |
|------|------|------|-----------|
| Data Protection Officer | Nguyen Van DPO | 2026-05-12 | [Signed] |
| Security Lead | Tran Thi Security | 2026-05-12 | [Signed] |
| Platform Lead | Le Van Platform | 2026-05-12 | [Signed] |
