# Getting Started Guide

## Quick Start (5 minutes)

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker (optional but recommended)
- Git

### Step 1: Clone Repository

```bash
git clone https://github.com/Revanthvenkat1260/blockchain-identity-deepfake-defense.git
cd blockchain-identity-deepfake-defense
```

### Step 2: Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start Flask API
flask run
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000
```

### Step 3: Deploy Smart Contracts

```bash
cd backend/smart-contracts

# Install dependencies
npm install

# Configure Hardhat
cp .env.example .env
# Add your PRIVATE_KEY and RPC endpoint

# Deploy to Polygon Mumbai (testnet)
npx hardhat run scripts/deploy.js --network polygonMumbai
```

**Expected Output:**
```
IdentityManager deployed to: 0x...
AssetManager deployed to: 0x...
AccessControlManager deployed to: 0x...
AuditTrail deployed to: 0x...
```

### Step 4: Run Desktop Application

```bash
cd desktop-app

# Install dependencies
npm install

# Start in development mode
npm start
```

**Expected Output:**
Desktop app window opens with UI

## 🎯 Core Features Walkthrough

### Feature 1: Image Encryption

```bash
# Using the desktop app:
1. Click "Encrypt" tab
2. Drag and drop image
3. Click "Start Encryption"
4. Receive encryption ID and pixel signature
```

**Or via API:**

```bash
curl -X POST http://localhost:5000/api/v1/images/encrypt \
  -F "image=@photo.jpg" \
  -F "did=did:polygon:user123" \
  -H "Authorization: Bearer <token>"
```

### Feature 2: Deepfake Detection

```bash
# Using the desktop app:
1. Click "Verify" tab
2. Upload image to analyze
3. Click "Analyze Image"
4. Receive deepfake detection results
```

**Or via API:**

```bash
curl -X POST http://localhost:5000/api/v1/verify/deepfake \
  -F "image=@suspicious.jpg" \
  -H "Authorization: Bearer <token>"
```

### Feature 3: Blockchain Integration

```bash
# Register identity:
curl -X POST http://localhost:5000/api/v1/blockchain/register-identity \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "did": "did:polygon:user123",
    "public_key": "0x...",
    "metadata": "User Profile"
  }'

# Mint NFT asset:
curl -X POST http://localhost:5000/api/v1/blockchain/mint-asset \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "owner_did": "did:polygon:user123",
    "asset_uri": "ipfs://QmExample",
    "pixel_signature": "0x...",
    "encryption_algorithm": "AES-256-CBC"
  }'
```

## 🐳 Docker Deployment

### Quick Docker Setup

```bash
# Build and start all services
docker-compose up -d

# View running services
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Services running:**
- Backend API: `http://localhost:5000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## 📚 Project Structure

```
blockchain-identity-deepfake-defense/
├── backend/                          # Python Flask backend
│   ├── core/                         # Core functionality
│   │   ├── encryption/              # AES-256 encryption module
│   │   ├── detection/               # Deepfake detection ML models
│   │   ├── verification/            # Image integrity verification
│   │   └── blockchain/              # Web3 integration
│   ├── api/                         # Flask REST API routes
│   │   ├── routes/                  # API endpoint definitions
│   │   └── app.py                   # Main Flask application
│   ├── smart-contracts/             # Solidity contracts
│   │   ├── contracts/               # Smart contract code
│   │   ├── scripts/                 # Deployment scripts
│   │   └── hardhat.config.js        # Hardhat configuration
│   └── requirements.txt             # Python dependencies
├── desktop-app/                      # Electron + React app
│   ├── src/
│   │   ├── components/              # React components
│   │   ├── App.js                   # Main app component
│   │   └── App.css                  # Styling
│   ├── public/
│   │   ├── electron.js              # Main Electron process
│   │   └── preload.js               # Preload script
│   └── package.json                 # Node dependencies
├── docs/                            # Documentation
│   ├── architecture/                # System design
│   ├── api/                         # API documentation
│   ├── blockchain/                  # Smart contract guide
│   ├── deployment/                  # Deployment instructions
│   └── security/                    # Security guidelines
└── README.md                        # Project overview
```

## 🔧 Configuration

### Backend Configuration

Create `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/deepfake_defense

# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Blockchain
WEB3_PROVIDER_URL=https://rpc-mumbai.maticvigil.com
PRIVATE_KEY=your-wallet-private-key

# IPFS
IPFS_API_URL=https://ipfs.infura.io:5001
```

### Smart Contracts Configuration

Create `backend/smart-contracts/.env`:

```bash
PRIVATE_KEY=your-wallet-private-key
POLYGONSCAN_API_KEY=your-polygonscan-key
```

## ✅ Testing

### Backend Tests

```bash
cd backend

# Run unit tests
pytest

# Run with coverage
pytest --cov=core
```

### Smart Contract Tests

```bash
cd backend/smart-contracts

# Run contract tests
npx hardhat test

# Generate coverage
npx hardhat coverage
```

## 🚀 Development Workflow

### 1. Make Changes

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes to code
```

### 2. Test Locally

```bash
# Backend tests
cd backend && pytest

# Contract tests
cd backend/smart-contracts && npx hardhat test

# API testing
curl http://localhost:5000/health
```

### 3. Commit & Push

```bash
git add .
git commit -m "Add: description of changes"
git push origin feature/my-feature
```

### 4. Create Pull Request

- Go to GitHub
- Create PR with description
- Wait for CI/CD checks
- Merge after approval

## 🐛 Troubleshooting

### Issue: Database Connection Error

```bash
# Check if PostgreSQL is running
psql --version

# Verify connection string in .env
# Format: postgresql://user:password@host:port/database

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Issue: Blockchain Connection Failed

```bash
# Verify RPC endpoint is accessible
curl -X POST https://rpc-mumbai.maticvigil.com \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

# Check private key format (should be 0x...)
echo $PRIVATE_KEY
```

### Issue: ML Model Loading Fails

```bash
# Check if PyTorch/TensorFlow installed
python -c "import torch; print(torch.__version__)"

# Verify GPU availability
python -c "import torch; print(torch.cuda.is_available())"

# Download model weights
cd backend/core/detection
python -c "import torchvision.models as models; models.efficientnet_b0(pretrained=True)"
```

## 📖 Additional Resources

- [Architecture Documentation](docs/architecture/ARCHITECTURE.md)
- [API Documentation](docs/api/API.md)
- [Smart Contracts Guide](docs/blockchain/SMART_CONTRACTS.md)
- [Deployment Guide](docs/deployment/DEPLOYMENT.md)
- [Security Best Practices](docs/security/SECURITY.md)

## 💬 Community & Support

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Email**: support@deepfakedefense.com

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Follow code style guidelines
4. Add tests for new features
5. Submit a pull request

## 🎉 Next Steps

1. ✅ Deploy to testnet
2. ✅ Run test scenarios
3. ✅ Verify all features working
4. ✅ Review security checklist
5. ✅ Deploy to mainnet

Happy coding! 🚀
