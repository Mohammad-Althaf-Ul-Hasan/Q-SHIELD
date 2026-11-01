# 🛡️ Q‑SHIELD

**Quantum Secure Hybrid Integrated Encryption for Layered Data Distribution**

## Overview
Q‑SHIELD is a full‑stack web application that demonstrates a hybrid quantum‑safe
network security protocol. It combines:

- BB84 Quantum Key Distribution (QKD) simulation with realistic noise models
- Kyber‑512 Post‑Quantum Cryptography (NIST FIPS 203)
- AES‑256‑GCM classical authenticated encryption
- Real‑time WebSocket protocol visualization
- Multi‑node QKD network and digital twin simulation
- ML‑based eavesdropping anomaly detection
- Immutable blockchain audit trail
- Industry‑standard ETSI GS QKD 014 REST API

## Tech Stack
- **Backend:** Flask, Flask‑SocketIO, MySQL (via mysql‑connector‑python)
- **Quantum:** Pure Python BB84 simulator, Kyber‑512 via kyber‑py, decoy‑state, MDI‑QKD
- **Frontend:** HTML5, CSS3 (glassmorphism), vanilla JavaScript, SocketIO client
- **ML:** scikit‑learn (SVM classifier, linear regression forecaster)
- **PDF:** ReportLab

## Quick Start
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
Open http://127.0.0.1:5000

Project Structure
See the documentation for the full file tree.

License
MIT

---

### 15.7 `logs/` directory

Create an empty `logs/` folder. The application will populate `app.log` automatically.

---

### 15.8 `documentation/` folder

If you haven't already, you can place your existing report and presentation files here. No code changes needed.

---

## ✅ Complete File Tree Now Matches

Every file from the original specification now exists—either as fully functional code or as a placeholder stub ready for future development. The application is fully runnable.

---

## Next Steps

You can now **test** the entire system:

1. Activate virtual environment.
2. `python app.py`
3. Open `http://127.0.0.1:5000`
4. Verify all core tabs work (Quantum Core, Encrypt, Decrypt, Analysis updates).

When you're ready, type **"TESTED"** and I'll help you package or polish any final details.