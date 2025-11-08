#!/bin/bash
# CHIKA VPS Install Script - ALL IN ONE!
# Usage: curl -fsSL https://raw.githubusercontent.com/USER/REPO/main/scripts/vps-install.sh | bash

set -e

echo "🚀 CHIKA VPS Installation"
echo "========================="

# Update system
echo "📦 Updating system..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo "📦 Installing: Nginx, PostgreSQL, Python 3.11, Git..."
sudo apt install -y nginx postgresql postgresql-contrib python3.11 python3.11-venv python3-pip git certbot python3-certbot-nginx

# Create chika user
echo "👤 Creating chika user..."
sudo useradd -m -s /bin/bash chika || true

# Clone repo
echo "📥 Cloning CHIKA repo..."
sudo -u chika git clone https://github.com/ruipedro-pinheiro/CHIKA.git /home/chika/app

# Setup Python venv
echo "🐍 Setting up Python environment..."
cd /home/chika/app/backend
sudo -u chika python3.11 -m venv venv
sudo -u chika venv/bin/pip install -r requirements.txt

# Setup PostgreSQL
echo "🗄️ Setting up PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE chika;" || true
sudo -u postgres psql -c "CREATE USER chika WITH PASSWORD 'chika_secure_pass_2025';" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE chika TO chika;" || true

# Create .env file template
echo "⚙️ Creating .env file..."
cat > /home/chika/app/backend/.env << 'ENVEOF'
DATABASE_URL=postgresql://chika:chika_secure_pass_2025@localhost/chika
GMAIL_APP_PASSWORD=REPLACE_WITH_YOUR_GMAIL_APP_PASSWORD
GMAIL_USER=REPLACE_WITH_YOUR_EMAIL
GOOGLE_API_KEY=REPLACE_WITH_YOUR_GOOGLE_API_KEY
OPENAI_API_KEY=REPLACE_WITH_YOUR_OPENAI_API_KEY
ENVEOF
sudo chown chika:chika /home/chika/app/backend/.env

echo ""
echo "⚠️  IMPORTANT: Edit /home/chika/app/backend/.env with real API keys!"
echo "   Then: sudo systemctl restart chika"

# Create systemd service
echo "🔧 Creating systemd service..."
sudo cat > /etc/systemd/system/chika.service << 'SERVICEEOF'
[Unit]
Description=CHIKA Backend
After=network.target postgresql.service

[Service]
Type=simple
User=chika
WorkingDirectory=/home/chika/app/backend
Environment="PATH=/home/chika/app/backend/venv/bin"
ExecStart=/home/chika/app/backend/venv/bin/uvicorn main_simple:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo cat > /etc/nginx/sites-available/chika << 'NGINXEOF'
server {
    listen 80;
    server_name _;
    
    # Frontend
    location / {
        root /home/chika/app/frontend;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Admin
    location /waitlist/admin {
        proxy_pass http://localhost:8000/waitlist/admin;
        proxy_set_header Host $host;
    }
}
NGINXEOF
sudo ln -sf /etc/nginx/sites-available/chika /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Start services
echo "▶️ Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable chika
sudo systemctl start chika
sudo systemctl restart nginx

# Show status
echo ""
echo "✅ INSTALLATION COMPLETE!"
echo "========================="
echo "Backend: http://YOUR_VPS_IP/api/health"
echo "Frontend: http://YOUR_VPS_IP"
echo "Waitlist: http://YOUR_VPS_IP/api/waitlist/count"
echo ""
echo "📝 Next steps:"
echo "1. Point your domain to this VPS IP"
echo "2. Run: sudo certbot --nginx -d yourdomain.com"
echo "3. Migrate DB: pg_dump render_db | psql chika"
echo ""
echo "🔍 Useful commands:"
echo "  sudo systemctl status chika    # Check backend"
echo "  sudo journalctl -u chika -f    # Live logs"
echo "  sudo nginx -t                  # Test nginx config"
