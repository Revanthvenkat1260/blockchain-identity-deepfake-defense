# System Architecture

## Overview

The blockchain-based identity and deepfake defense platform consists of four major layers:

1. **Identity Layer** - Decentralized Identity Management
2. **Encryption Layer** - Cryptographic Protection
3. **Detection Layer** - AI/Deepfake Detection
4. **Blockchain Layer** - Immutable Recording

## Layer Details

### 1. Identity Layer (DID)

```
User Registration
    ↓
DID Generation (Decentralized Identifier)
    ↓
Private Key Creation + Storage
    ↓
Public Key Registration on Blockchain
    ↓
Identity NFT Minting
```

**Components:**
- DID Registry (Smart Contract)
- Key Management Service
- Identity Verification Module
- RBAC Framework

**Roles:**
- **Admin**: Full system access, contract deployment
- **Manager**: Asset management, user provisioning
- **Auditor**: View-only access to audit logs
- **User**: Image capture and asset ownership

### 2. Encryption Layer

**Image Protection Process:**

```
Original Image
    ↓
Step 1: AES-256 Encryption
    ↓
Step 2: Generate Pixel Signature (SHA-256)
    ↓
Step 3: Steganographic Watermarking
    ↓
Step 4: Create Metadata JSON
    ↓
Encrypted Image + Metadata Package
```

**Key Management:**
- RSA-2048 key pair per user identity
- Private keys stored locally with AES encryption
- Public keys registered on blockchain
- Session keys for image-specific encryption

### 3. Detection Layer

**AI/Deepfake Detection Pipeline:**

```
Monitoring Systems (Parallel)
    ├── Network Monitor
    │   └── Detects API calls to AI services
    ├── Clipboard Monitor
    │   └── Tracks image data copying
    ├── File System Monitor
    │   └── Watches temp file creation
    └── ML Analyzer
        └── Analyzes pixel changes

If Threat Detected
    ↓
Escalate to Blockchain
    ↓
Execute Pixel Corruption Script
    ↓
Log Event on Smart Contract
    ↓
Notify User
```

**Detection Mechanisms:**

1. **Network Detection**
   - Scapy-based packet inspection
   - Signature matching for OpenAI, Google, Microsoft APIs
   - TLS certificate validation

2. **Pixel Analysis**
   - Cryptographic hash comparison
   - ML model trained on deepfake datasets
   - Real-time computer vision processing

3. **Access Pattern Analysis**
   - Temporal metadata tracking
   - Unusual access pattern detection
   - Behavioral analytics

### 4. Blockchain Layer

**Smart Contract Architecture:**

```
IdentityManager.sol
├── DID Registration
├── Role Assignment
└── Key Management

AssetManager.sol
├── NFT Minting
├── Ownership Records
└── Transfer Management

AccessControl.sol
├── Permission Rules
├── Role Enforcement
└── Delegation Logic

AuditTrail.sol
├── Event Logging
├── Tampering Detection
└── Compliance Records
```

**Event Flow on Blockchain:**

```
User Action (e.g., Image Upload)
    ↓
Cryptographic Processing
    ↓
Smart Contract Validation
    ↓
Access Control Check
    ↓
Transaction Execution
    ↓
Audit Event Recording
    ↓
Blockchain Confirmation
```

## Data Flow

### Image Capture and Protection

```
1. User opens application
   ↓
2. Application authenticates user with DID
   ↓
3. User captures/selects image
   ↓
4. Image is encrypted with AES-256 (user's session key)
   ↓
5. Pixel signature generated (SHA-256 hash of pixels)
   ↓
6. Steganographic watermark embedded
   ↓
7. Metadata created:
   {
     "owner_did": "did:example:abc123",
     "timestamp": 1693123456,
     "image_hash": "0x...",
     "pixel_signature": "0x...",
     "encryption_algorithm": "AES-256",
     "privacy_level": "strict"
   }
   ↓
8. Send to backend for NFT minting
   ↓
9. Smart contract mints NFT linked to DID
   ↓
10. NFT metadata stored on IPFS
    ↓
11. Ownership record on blockchain
    ↓
12. User receives NFT confirmation
```

### Deepfake Detection and Prevention

```
Monitoring Daemon Running (Background)
    ↓
Network packet captured
    ↓
Check for API signatures:
   - OpenAI.com:443
   - Google Cloud:443
   - Azure:443
   - Local ML frameworks (TensorFlow, PyTorch)
    ↓
If API call detected:
   ├── Check whitelist
   ├── Verify consent in blockchain
   └── If unauthorized:
       ├── Trigger pixel corruption
       ├── Log to blockchain
       ├── Notify user
       └── Alert admin
```

## Security Model

### Threat Protection

| Threat | Protection |
|--------|------------|
| Man-in-Middle Attack | TLS + Smart Contract Verification |
| Image Tampering | Cryptographic Hash + Pixel Signature |
| Unauthorized AI Usage | Network Monitor + Permission Gate |
| Single Point of Failure | Blockchain + Distributed Consensus |
| Identity Spoofing | DID Cryptography + Smart Contract |
| Data Breach | AES-256 Encryption + Key Management |

### Cryptographic Standards

- **Symmetric Encryption**: AES-256-CBC
- **Asymmetric Encryption**: RSA-2048
- **Hashing**: SHA-256, BLAKE2
- **Key Derivation**: PBKDF2 (100,000 iterations)
- **Random Number Generation**: /dev/urandom

## Scalability Considerations

1. **Blockchain**: Use Polygon for faster, cheaper transactions
2. **Storage**: IPFS for distributed image metadata storage
3. **Caching**: Redis for session management
4. **Database**: PostgreSQL with sharding for user data
5. **API**: Load balancing with multiple backend instances

## Deployment Architecture

```
┌─────────────────────────────┐
│   Desktop Application       │
│  (Electron + React)         │
└──────────┬──────────────────┘
           │
┌──────────▼──────────────────┐
│   API Gateway               │
│  (Load Balancer)            │
└──────────┬──────────────────┘
           │
┌──────────▼──────────────────┐
│   Backend Services          │
│  ├── Encryption Service     │
│  ├── Detection Service      │
│  ├── Verification Service   │
│  └── Blockchain Service     │
└──────────┬──────────────────┘
           │
     ┌─────┼─────┐
     │     │     │
  ┌──▼─┐ ┌──▼──┐ ┌──▼──────────┐
  │ DB │ │IPFS │ │ Blockchain  │
  │    │ │     │ │ (Polygon)   │
  └────┘ └─────┘ └─────────────┘
```

## Next Steps

1. Implement DID registration module
2. Develop encryption/decryption engine
3. Build detection monitoring daemon
4. Deploy smart contracts
5. Integrate all layers
6. Comprehensive security testing
