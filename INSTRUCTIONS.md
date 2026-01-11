# SHIELD AI ML - File Placement Instructions

## ⚠️ IMPORTANT: Do NOT use the `shield_ml` folder I created earlier!

Your existing `shield-ai-ml-main` folder has a better structure. These files fill in the **empty utilities** your existing code needs.

---

## 📁 Where to Put Each File

Copy these files to your `shield-ai-ml-main` folder:

```
shield-ai-ml-main/
├── config/
│   ├── __init__.py          ← REPLACE with: config/__init__.py
│   ├── constants.py          ← REPLACE with: config/constants.py
│   └── settings.py           ← REPLACE with: config/settings.py
│
├── src/
│   ├── api/
│   │   ├── __init__.py       ← REPLACE with: src/api/__init__.py
│   │   ├── endpoints.py      ← REPLACE with: src/api/endpoints.py
│   │   ├── middleware.py     ← REPLACE with: src/api/middleware.py
│   │   ├── schemas.py        ← REPLACE with: src/api/schemas.py
│   │   └── fastapi_server.py ← KEEP YOUR EXISTING FILE (already good!)
│   │
│   └── utils/
│       ├── __init__.py       ← REPLACE with: src/utils/__init__.py
│       ├── logger.py         ← REPLACE with: src/utils/logger.py
│       ├── validators.py     ← REPLACE with: src/utils/validators.py
│       └── config_loader.py  ← REPLACE with: src/utils/config_loader.py
│
├── scripts/
│   └── start_server.py       ← REPLACE with: scripts/start_server.py
│
├── requirements.txt          ← REPLACE with: requirements.txt
└── .env.example              ← REPLACE with: .env.example
```

---

## 🔧 Step-by-Step Instructions

### Step 1: Delete my separate `shield_ml` folder
```bash
# Delete the folder I created (it's not compatible with your structure)
rm -rf shield_ml
```

### Step 2: Copy files to your existing structure
```bash
cd shield-ai-ml-main

# Copy config files
cp /path/to/shield-ai-ml-files/config/__init__.py config/
cp /path/to/shield-ai-ml-files/config/constants.py config/
cp /path/to/shield-ai-ml-files/config/settings.py config/

# Copy utils files
cp /path/to/shield-ai-ml-files/src/utils/__init__.py src/utils/
cp /path/to/shield-ai-ml-files/src/utils/logger.py src/utils/
cp /path/to/shield-ai-ml-files/src/utils/validators.py src/utils/
cp /path/to/shield-ai-ml-files/src/utils/config_loader.py src/utils/

# Copy API files
cp /path/to/shield-ai-ml-files/src/api/__init__.py src/api/
cp /path/to/shield-ai-ml-files/src/api/schemas.py src/api/
cp /path/to/shield-ai-ml-files/src/api/middleware.py src/api/
cp /path/to/shield-ai-ml-files/src/api/endpoints.py src/api/

# Copy scripts
cp /path/to/shield-ai-ml-files/scripts/start_server.py scripts/

# Copy root files
cp /path/to/shield-ai-ml-files/requirements.txt .
cp /path/to/shield-ai-ml-files/.env.example .
```

### Step 3: Fix Import Paths

Your existing files (`risk_calculator.py`, `stalking_detection.py`, etc.) have imports like:
```python
from ...utils.logger import setup_logger
from ...config.constants import RiskLevel
```

These are **relative imports** that work when running from the project root.

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Create .env file
```bash
cp .env.example .env
# Edit .env with your actual values
```

### Step 6: Run the Server
```bash
# Option 1: Using the script
python scripts/start_server.py

# Option 2: Direct uvicorn
uvicorn src.api.fastapi_server:app --reload --host 0.0.0.0 --port 8000

# Option 3: Using Python module
python -m src.api.fastapi_server
```

---

## 🧪 Test the API

Once running, test with:

```bash
# Health check
curl http://localhost:8000/health

# API docs (development only)
open http://localhost:8000/docs
```

---

## ❓ Common Issues

### Import Error: "No module named 'src'"
**Solution:** Run from the `shield-ai-ml-main` directory:
```bash
cd shield-ai-ml-main
python scripts/start_server.py
```

### Import Error: "No module named 'loguru'"
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### "RiskLevel not found"
**Solution:** Make sure you copied `config/constants.py` correctly.

---

## 📝 Files You Should NOT Replace

Keep your existing implementations:
- `src/risk_engine/risk_calculator.py` ← Your existing code is complete!
- `src/anomaly_detection/stalking_detection.py` ← Your existing code is complete!
- `src/api/fastapi_server.py` ← Your existing code is complete!
- `src/decision_agent/*` ← Keep all your decision agent files

---

## 🗑️ Files to Delete

Delete my original folder:
```bash
rm -rf shield_ml
```

This was created before I saw your existing structure and is **not compatible**.
