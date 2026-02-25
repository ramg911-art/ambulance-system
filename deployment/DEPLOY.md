# Deployment Notes

## After Git Pull - Changes Not Reflected

If you pulled new code but the service still runs old behavior:

### 1. Check where the service runs from

```bash
sudo systemctl cat ambulance-system
```

Look at `WorkingDirectory=` – the service runs code from that path. If it points to `/opt/ambulance-system` but your repo is in `/home/ram/ambulance-system`, the service is using old code.

### 2. Fix options

**Option A: Point the service at your repo**

Edit the service file (adjust paths if needed):

```bash
sudo nano /etc/systemd/system/ambulance-system.service
```

Set:
```
WorkingDirectory=/home/ram/ambulance-system/backend
ExecStart=/home/ram/ambulance-system/backend/venv/bin/python run.py
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl restart ambulance-system
```

**Option B: Deploy your repo into the service directory**

If the service expects `/opt/ambulance-system`:

```bash
sudo rsync -av --exclude venv --exclude __pycache__ --exclude .git \
  /home/ram/ambulance-system/ /opt/ambulance-system/
sudo systemctl restart ambulance-system
```

### 3. Rebuild Admin Frontend (if admin changes not visible)

```bash
cd /home/ram/ambulance-system/frontend/admin
npm run build
# If using serve, restart the admin service too
```

### 4. Ensure DB has new tables

The `distance_tariff_config` table is created automatically on first backend startup after the model is added. If it’s missing:

```bash
cd /home/ram/ambulance-system/backend
source venv/bin/activate
python -c "from app.db.session import init_db; init_db(); print('OK')"
```
