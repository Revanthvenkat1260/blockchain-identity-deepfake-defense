# Smart Contracts Documentation

## Overview

The platform uses four main smart contracts on the Ethereum/Polygon blockchain:

1. **IdentityManager.sol** - DID and identity management
2. **AssetManager.sol** - NFT minting and ownership
3. **AccessControl.sol** - Role-based permissions
4. **AuditTrail.sol** - Event logging and verification

## 1. IdentityManager.sol

### Purpose
Manages decentralized identities (DIDs) and their registration on blockchain.

### Key Functions

```solidity
// Register new DID
function registerIdentity(
    bytes32 did,
    address publicKeyAddress,
    string memory metadata
) public returns (bool)

// Get identity details
function getIdentity(bytes32 did) public view returns (Identity)

// Update identity metadata
function updateIdentity(bytes32 did, string memory newMetadata) public

// Revoke identity
function revokeIdentity(bytes32 did) public
```

### Data Structure

```solidity
struct Identity {
    bytes32 did;
    address owner;
    bytes32 publicKeyHash;
    uint256 createdAt;
    uint256 updatedAt;
    bool isActive;
    string metadata;
    Role role;
}

enum Role {
    USER,
    MANAGER,
    AUDITOR,
    ADMIN
}
```

## 2. AssetManager.sol

### Purpose
Manages NFT minting and ownership records for digital assets.

### Key Functions

```solidity
// Mint new NFT asset
function mintAsset(
    bytes32 ownerDID,
    string memory assetURI,
    bytes32 pixelSignature,
    string memory encryptionDetails
) public returns (uint256 tokenId)

// Get asset details
function getAsset(uint256 tokenId) public view returns (Asset)

// Transfer asset ownership
function transferAsset(
    uint256 tokenId,
    bytes32 fromDID,
    bytes32 toDID
) public

// Verify asset authenticity
function verifyAsset(uint256 tokenId) public view returns (bool)
```

### Data Structure

```solidity
struct Asset {
    uint256 tokenId;
    bytes32 ownerDID;
    string assetURI;
    bytes32 pixelSignature;
    uint256 mintedAt;
    uint256 lastModifiedAt;
    bool isValid;
    string encryptionAlgorithm;
    bytes32 encryptionHash;
}
```

## 3. AccessControl.sol

### Purpose
Implements Role-Based Access Control (RBAC) for the platform.

### Key Functions

```solidity
// Assign role to identity
function assignRole(
    bytes32 did,
    Role newRole
) public onlyAdmin

// Grant permission
function grantPermission(
    bytes32 did,
    string memory permission,
    bool isAllowed
) public onlyAdmin

// Check permission
function hasPermission(
    bytes32 did,
    string memory permission
) public view returns (bool)

// Delegate access
function delegateAccess(
    bytes32 from,
    bytes32 to,
    string memory resource,
    uint256 expiresAt
) public
```

### Permission Matrix

```
                    USER    MANAGER   AUDITOR   ADMIN
Capture Image        ✓        ✓         ✗        ✓
View Own Assets      ✓        ✓         ✗        ✓
Transfer Asset       ✓        ✓         ✗        ✓
Mint NFT             ✗        ✓         ✗        ✓
Manage Users         ✗        ✓         ✗        ✓
View Audit Trail     ✗        ✗         ✓        ✓
Manage Roles         ✗        ✗         ✗        ✓
Deploy Contracts     ✗        ✗         ✗        ✓
```

## 4. AuditTrail.sol

### Purpose
Records all operations immutably on the blockchain for compliance and verification.

### Key Functions

```solidity
// Log event
function logEvent(
    string memory eventType,
    bytes32 did,
    string memory details,
    bool success
) public

// Get event history
function getEventHistory(
    bytes32 did,
    uint256 limit
) public view returns (AuditEvent[])

// Verify event integrity
function verifyEvent(
    uint256 eventId
) public view returns (bool)

// Export audit trail
function exportAuditTrail(
    uint256 startBlock,
    uint256 endBlock
) public view returns (AuditEvent[])
```

### Data Structure

```solidity
struct AuditEvent {
    uint256 eventId;
    string eventType; // "IDENTITY_CREATED", "ASSET_MINTED", etc.
    bytes32 initiatedBy;
    bytes32 targetDID;
    uint256 targetTokenId;
    string details;
    uint256 timestamp;
    uint256 blockNumber;
    bool success;
    string resultHash;
}

enum EventType {
    IDENTITY_CREATED,
    IDENTITY_UPDATED,
    IDENTITY_REVOKED,
    ASSET_MINTED,
    ASSET_TRANSFERRED,
    ASSET_VERIFIED,
    PERMISSION_GRANTED,
    PERMISSION_REVOKED,
    DEEPFAKE_DETECTED,
    PIXEL_CORRUPTED,
    AUTHORIZATION_FAILED,
    AUDIT_LOG_EXPORTED
}
```

## Deployment Instructions

### Prerequisites
```bash
npm install -g hardhat
npm install @openzeppelin/contracts
```

### Compile
```bash
cd backend/smart-contracts
npx hardhat compile
```

### Deploy to Polygon Testnet
```bash
npx hardhat run scripts/deploy.js --network polygonMumbai
```

### Deploy to Polygon Mainnet
```bash
npx hardhat run scripts/deploy.js --network polygon
```

## Security Considerations

1. **Access Control**: Use OpenZeppelin's AccessControl for secure role management
2. **Reentrancy**: Implement checks-effects-interactions pattern
3. **Integer Overflow**: Use SafeMath library
4. **Timestamp Dependence**: Minimize reliance on block.timestamp
5. **External Calls**: Validate all inputs before calling external contracts

## Gas Optimization

- Use immutable variables where possible
- Batch operations to reduce transaction count
- Implement event indexing for efficient querying
- Use storage packing for optimal gas usage

## Upgradability

Use UUPS (Universal Upgradeable Proxy Standard) for contract upgrades:

```solidity
import "@openzeppelin/contracts/proxy/utils/UUPSUpgradeable.sol";

contract IdentityManager is UUPSUpgradeable {
    function _authorizeUpgrade(address newImplementation)
        internal
        onlyAdmin
        override
    {}
}
```

## Testing

```bash
npx hardhat test
npx hardhat test --grep "specific test"
npx hardhat coverage
```

## Integration with Backend

The backend will interact with deployed contracts via Web3.py:

```python
from web3 import Web3
from web3.contract import Contract

w3 = Web3(Web3.HTTPProvider('https://rpc-mumbai.maticvigil.com'))
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Call contract function
result = contract.functions.getIdentity(did_hash).call()
```
