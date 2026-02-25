# Ambulance Fleet Management System

Production-grade ambulance fleet management system with GPS tracking, preset location auto-detection, fixed/distance tariff billing, and live tracking.

## Prerequisites

- Ubuntu 22.04 LTS (or similar)
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

## Ubuntu Setup Instructions

### 1. Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm postgresql redis-server
```

### 2. Node.js (recommend nvm for specific version)

```bash
# Using NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Or use nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 20
nvm use 20
```

### 3. PostgreSQL Setup

```bash
sudo -u postgres psql -c "CREATE USER ambulance WITH PASSWORD 'ambulance_secret';"
sudo -u postgres psql -c "CREATE DATABASE ambulance_fleet OWNER ambulance;"
```

### 4. Redis Setup

```bash
# Redis runs by default on localhost:6379
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 5. Python Virtualenv Setup

```bash
cd ambulance-system/backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 6. Environment Configuration

```bash
cp ../.env.example .env
# Edit .env with your DATABASE_URL, REDIS_URL, SECRET_KEY
```

### 7. Initialize Database and Seed Data

```bash
cd backend
source venv/bin/activate
python scripts/seed_data.py
```

### 8. Run Backend

```bash
cd backend
source venv/bin/activate
python run.py
```

Backend runs on http://localhost:9322

### 9. Build and Run Driver Frontend

```bash
cd frontend/driver
npm install
npm run build
npx serve -s dist -l 5175
```

Driver app runs on http://localhost:5175

### 10. Build and Run Admin Frontend

```bash
cd frontend/admin
npm install
npm run build
npx serve -s dist -l 5176
```

Admin app runs on http://localhost:5176

---

## Systemd Service Setup

Copy service files to systemd:

```bash
sudo cp deployment/systemd/*.service /etc/systemd/system/
```

Edit paths in service files if your installation directory differs from `/opt/ambulance-system`.

Create application user:

```bash
sudo useradd -r -s /bin/false ambulance
sudo mkdir -p /opt/ambulance-system
sudo chown -R ambulance:ambulance /opt/ambulance-system
```

Install `serve` globally for frontend services:

```bash
sudo npm install -g serve
```

Update ExecStart in driver/admin services to use `serve` directly if needed:

```bash
ExecStart=/usr/bin/serve -s dist -l 5175
```

Enable and start services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ambulance-backend ambulance-driver ambulance-admin
sudo systemctl start ambulance-backend ambulance-driver ambulance-admin
sudo systemctl status ambulance-backend
```

---

## Cloudflare Tunnel Setup

1. Install cloudflared:

```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

2. Login and create tunnel:

```bash
cloudflared tunnel login
cloudflared tunnel create ambulance-system
```

3. Copy tunnel ID and credentials path. Edit `deployment/cloudflare/config.yml`:

```yaml
tunnel: <YOUR_TUNNEL_ID>
credentials-file: /home/ubuntu/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: api.yourdomain.com
    service: http://localhost:9322
  - hostname: driver.yourdomain.com
    service: http://localhost:5175
  - hostname: admin.yourdomain.com
    service: http://localhost:5176
  - service: http_status:404
```

4. Create DNS records for api, driver, admin subdomains in Cloudflare Dashboard (CNAME to <tunnel-id>.cfargotunnel.com).

5. Run tunnel:

```bash
cloudflared tunnel --config deployment/cloudflare/config.yml run
```

---

## .env.example

```
DATABASE_URL=postgresql://ambulance:ambulance_secret@localhost:5432/ambulance_fleet
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=change_this_to_long_random_string_in_production
```

---

## API Endpoints

- `POST /auth/login` - Driver login
- `POST /auth/admin-login` - Admin login
- `GET /preset-locations/nearby` - Auto-detect preset location by lat/lng
- `GET /preset-destinations/by-source/{id}` - Destinations for preset location
- `POST /trips` - Create trip
- `POST /trips/{id}/start` - Start trip
- `POST /trips/{id}/end` - End trip (calculates distance, billing, creates invoice)
- `POST /gps/update` - GPS location update (every 5 seconds)
- `GET /gps/vehicles/live` - Live vehicle locations

---

## Default Seed Credentials

- **Driver:** Phone +1234567890 / Password driver123
- **Admin:** Username admin / Password admin123

Run `python scripts/seed_data.py` to create these. The admin user is created even if org data already exists.
