# 🚀 Deployment Guide - Green Cloud VM Placement System

## Quick Deployment Options

### 🐍 **Option 1: Direct Python Deployment (Recommended for Development)**

#### Prerequisites
- Python 3.10+ installed
- pip package manager
- Modern web browser

#### Steps
1. **Clone and Setup**
   ```bash
   git clone https://github.com/Abiram289/Green-cloud.git
   cd Green-cloud
   pip install -r requirements.txt
   ```

2. **Launch Application**
   ```bash
   python start_webapp.py
   ```

3. **Access Application**
   - 🌐 **Web Interface**: http://localhost:5000
   - ⚡ **Auto-opens browser** with welcome screen

---

### 🐳 **Option 2: Docker Deployment (Recommended for Production)**

#### Prerequisites
- Docker installed and running
- Docker Compose (optional, for full stack)

#### Simple Docker Deployment
```bash
# Build and run container
docker build -t green-cloud .
docker run -p 5000:5000 green-cloud

# Access at: http://localhost:5000
```

#### Full Stack with Docker Compose
```bash
# Launch complete infrastructure
docker-compose up -d

# Access services:
# - Web App: http://localhost:5000
# - Grafana: http://localhost:3000 (admin/admin_change_me)
# - Prometheus: http://localhost:9090
# - PostgreSQL: localhost:5432
```

#### Docker Management Commands
```bash
# View logs
docker-compose logs -f green-cloud-app

# Scale application
docker-compose up --scale green-cloud-app=3

# Update application
docker-compose build green-cloud-app
docker-compose up -d green-cloud-app

# Stop services
docker-compose down

# Clean up (including volumes)
docker-compose down -v
```

---

### ☁️ **Option 3: Cloud Deployment**

#### AWS EC2 / Azure VM / GCP Compute
```bash
# SSH into your cloud instance
ssh -i your-key.pem ubuntu@your-server-ip

# Install Docker (Ubuntu example)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Clone and deploy
git clone https://github.com/Abiram289/Green-cloud.git
cd Green-cloud
docker-compose up -d

# Configure firewall/security groups:
# - Allow port 5000 (Web App)
# - Allow port 80/443 (if using Nginx)
```

#### Kubernetes Deployment
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: green-cloud-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: green-cloud
  template:
    metadata:
      labels:
        app: green-cloud
    spec:
      containers:
      - name: green-cloud
        image: green-cloud:latest
        ports:
        - containerPort: 5000
---
apiVersion: v1
kind: Service
metadata:
  name: green-cloud-service
spec:
  selector:
    app: green-cloud
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

```bash
kubectl apply -f k8s-deployment.yaml
```

---

### 🌐 **Option 4: Heroku Deployment**

#### Setup
```bash
# Install Heroku CLI
# Create Heroku app
heroku create your-green-cloud-app

# Add buildpack
heroku buildpacks:set heroku/python

# Create Procfile
echo "web: python start_webapp.py" > Procfile

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku master
```

---

## 🔧 Configuration Options

### Environment Variables
```bash
# Flask Configuration
export FLASK_ENV=production
export FLASK_DEBUG=false
export SECRET_KEY=your_secret_key_here

# Database (if using PostgreSQL)
export DATABASE_URL=postgresql://user:pass@localhost:5432/greencloud

# Redis (if using caching)
export REDIS_URL=redis://localhost:6379

# Port Configuration
export PORT=5000
```

### Production Settings
```python
# config.py
import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False
    TESTING = False
    DATABASE_URI = os.environ.get('DATABASE_URL')
    REDIS_URL = os.environ.get('REDIS_URL')
```

---

## 🛡️ Security Considerations

### Production Checklist
- [ ] **Change default passwords** in docker-compose.yml
- [ ] **Set strong SECRET_KEY** for Flask sessions
- [ ] **Configure HTTPS** with SSL certificates
- [ ] **Set up firewall rules** to restrict access
- [ ] **Enable authentication** for production use
- [ ] **Configure backup strategy** for data
- [ ] **Monitor logs** for security events

### SSL/HTTPS Setup
```nginx
# nginx.conf example
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://green-cloud-app:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📊 Monitoring & Logging

### Built-in Monitoring
- **Health Checks**: Available at `/health`
- **Metrics**: Built into web interface
- **Logs**: Application logs to stdout

### External Monitoring (Docker Compose)
- **Prometheus**: Metrics collection (port 9090)
- **Grafana**: Visualization dashboards (port 3000)
- **Log aggregation**: Centralized logging

### Custom Monitoring Setup
```python
# Add to app.py for custom metrics
from prometheus_client import Counter, Histogram
import time

REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')

@app.before_request
def before_request():
    REQUEST_COUNT.inc()
    g.start_time = time.time()

@app.after_request
def after_request(response):
    REQUEST_LATENCY.observe(time.time() - g.start_time)
    return response
```

---

## 🔄 Updates & Maintenance

### Application Updates
```bash
# Pull latest changes
git pull origin master

# Docker deployment update
docker-compose build green-cloud-app
docker-compose up -d green-cloud-app

# Python deployment update
pip install -r requirements.txt
# Restart application server
```

### Backup Strategy
```bash
# Backup application data
docker-compose exec postgres pg_dump -U greencloud greencloud > backup.sql

# Backup models and results
tar -czf backup-$(date +%Y%m%d).tar.gz models/ results/ data/
```

### Health Monitoring
```bash
# Check application health
curl http://localhost:5000/api/system_status

# Monitor container status
docker ps
docker stats

# View application logs
docker-compose logs -f green-cloud-app
```

---

## 🎯 Performance Optimization

### Production Tuning
```python
# Use Gunicorn for production
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

### Resource Scaling
```yaml
# docker-compose.yml - Resource limits
services:
  green-cloud-app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### Caching Setup
```python
# Add Redis caching for better performance
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.cached(timeout=300)
def get_system_stats():
    # Cached for 5 minutes
    return calculate_stats()
```

---

## ❓ Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9
```

**Docker Issues**
```bash
# Clean up Docker resources
docker system prune -a

# Rebuild containers
docker-compose build --no-cache
```

**Permission Issues**
```bash
# Fix file permissions
sudo chown -R $(whoami) .
chmod +x start_webapp.py
```

**Memory Issues**
```bash
# Monitor memory usage
docker stats
free -h

# Increase swap space if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📞 Support

### Getting Help
- 📧 **GitHub Issues**: Report bugs and request features
- 📚 **Documentation**: Check README and guides
- 💬 **Community**: Join discussions on GitHub

### Deployment Support
For enterprise deployment assistance:
- 🏢 **Professional Support**: Available for production deployments
- 🔧 **Custom Configuration**: Tailored setup for specific requirements
- 📈 **Performance Tuning**: Optimization for large-scale deployments

---

## 🎉 Success Checklist

After deployment, verify these work:
- [ ] **Web interface loads** at configured URL
- [ ] **Dashboard displays data** correctly
- [ ] **VM placement requests** work
- [ ] **Tenant management** accessible
- [ ] **Audit logs** are generated
- [ ] **Reports** can be generated
- [ ] **Health checks** pass
- [ ] **Logs** are being written
- [ ] **Performance** is acceptable

---

**🚀 Your Green Cloud VM Placement System is ready for production!**