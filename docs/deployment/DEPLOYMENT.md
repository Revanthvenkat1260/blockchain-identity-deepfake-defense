# Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Node.js 16+
- Python 3.9+
- PostgreSQL
- Ethereum Wallet (MetaMask)
- Polygon RPC endpoint

## Environment Setup

### 1. Configure Environment Variables

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@db:5432/deepfake_defense

# Flask
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Blockchain
WEB3_PROVIDER_URL=https://rpc-mumbai.maticvigil.com
PRIVATE_KEY=your-wallet-private-key
CONTRACT_ADDRESSES={
  "identityManager": "0x...",
  "assetManager": "0x...",
  "accessControl": "0x...",
  "auditTrail": "0x..."
}

# IPFS
IPFS_API_URL=https://ipfs.infura.io:5001

# Machine Learning
GPU_ENABLED=true
DEVICE=cuda
```

## Deployment Methods

### Method 1: Docker Compose (Recommended)

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Verify services
docker-compose ps
```

### Method 2: Manual Deployment

#### Backend API

```bash
cd backend
pip install -r requirements.txt
gunicorn -w 4 -b 0.0.0.0:5000 api.app:app
```

#### Smart Contracts

```bash
cd backend/smart-contracts
npm install
npx hardhat run scripts/deploy.js --network polygon
```

#### Desktop Application

```bash
cd desktop-app
npm install
npm run build
npm run start
```

## Database Setup

```bash
# Create database
creatdb deepfake_defense

# Run migrations
alembic upgrade head
```

## Smart Contract Deployment

### Step 1: Configure Hardhat

Update `hardhat.config.js` with your RPC endpoint and private key.

### Step 2: Deploy Contracts

```bash
cd backend/smart-contracts

# Compile
npx hardhat compile

# Test
npx hardhat test

# Deploy to Polygon Mumbai (testnet)
npx hardhat run scripts/deploy.js --network polygonMumbai

# Deploy to Polygon Mainnet
npx hardhat run scripts/deploy.js --network polygon
```

### Step 3: Verify Contracts

```bash
npx hardhat verify --network polygon <CONTRACT_ADDRESS> <CONSTRUCTOR_ARGS>
```

## Monitoring & Logging

### Logs

```bash
# View backend logs
docker-compose logs -f backend

# View blockchain logs
docker-compose logs -f blockchain
```

### Health Checks

```bash
# API health
curl http://localhost:5000/health

# Database
psql -U user -d deepfake_defense -c "SELECT 1"

# Blockchain
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` files
2. **Private Keys**: Use secure key management (AWS Secrets Manager, etc.)
3. **SSL/TLS**: Enable HTTPS in production
4. **Rate Limiting**: Configure API rate limits
5. **Database**: Use strong passwords and IP whitelisting
6. **Firewall**: Restrict access to necessary ports only

## Scaling

### Horizontal Scaling

```yaml
services:
  backend:
    deploy:
      replicas: 3
```

### Load Balancing

```bash
# Using Nginx
upstream backend {
  server backend-1:5000;
  server backend-2:5000;
  server backend-3:5000;
}
```

### Caching

```bash
# Redis for session and cache
docker-compose up -d redis
```

## Troubleshooting

### API Won't Start

```bash
# Check logs
docker-compose logs backend

# Verify database connection
psql $DATABASE_URL
```

### Blockchain Connection Issues

```bash
# Test RPC endpoint
curl -X POST $WEB3_PROVIDER_URL \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

### Image Processing Fails

```bash
# Verify ML dependencies
python -c "import torch; import tensorflow; print('OK')"

# Check GPU availability
nvidia-smi
```

## Backup & Recovery

### Database Backup

```bash
pg_dump $DATABASE_URL > backup.sql
```

### Restore

```bash
psql $DATABASE_URL < backup.sql
```

## Updates & Maintenance

### Update Dependencies

```bash
# Python
pip install --upgrade -r requirements.txt

# Node
npm update
```

### Contract Upgrades

Use UUPS pattern for contract upgrades:

```bash
npx hardhat run scripts/upgrade.js --network polygon
```

## Support

For deployment issues, refer to:
- [Backend README](../backend/README.md)
- [Smart Contracts Guide](../docs/blockchain/SMART_CONTRACTS.md)
- [Architecture Documentation](../docs/architecture/ARCHITECTURE.md)
