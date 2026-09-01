# API Documentation

## Overview

The Blockchain Identity Deepfake Defense API provides endpoints for image encryption, deepfake detection, identity management, and blockchain operations.

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

All endpoints (except `/auth/login` and `/auth/register`) require JWT authentication:

```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### Register User
- **POST** `/auth/register`
- **Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "secure_password",
    "public_key": "0x..."
  }
  ```
- **Response**: User DID and registration confirmation

#### Login
- **POST** `/auth/login`
- **Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password"
  }
  ```
- **Response**: JWT token

### Images

#### Encrypt Image
- **POST** `/images/encrypt`
- **Body**: Form data with image file and DID
- **Response**: Encryption ID and pixel signature

#### List User Images
- **GET** `/images/list?did=<did>&limit=10`
- **Response**: Array of encrypted images

#### Delete Image
- **DELETE** `/images/delete/<image_id>`
- **Response**: Deletion confirmation

### Verification

#### Verify Image Integrity
- **POST** `/verify/integrity`
- **Body**:
  ```json
  {
    "image_data": "base64_encoded_image",
    "metadata": {},
    "pixel_signature": "0x..."
  }
  ```
- **Response**: Authenticity verdict and confidence score

#### Detect Deepfake
- **POST** `/verify/deepfake`
- **Body**: Form data with image file
- **Response**: Deepfake detection results

#### Analyze Pixels
- **POST** `/verify/pixels`
- **Body**:
  ```json
  {
    "original": "base64_original_image",
    "current": "base64_current_image",
    "sensitivity": 0.7
  }
  ```
- **Response**: Pixel modification analysis

### Blockchain

#### Register Identity
- **POST** `/blockchain/register-identity`
- **Body**:
  ```json
  {
    "did": "did:polygon:...",
    "public_key": "0x...",
    "metadata": "..."
  }
  ```
- **Response**: Transaction hash

#### Mint Asset NFT
- **POST** `/blockchain/mint-asset`
- **Body**:
  ```json
  {
    "owner_did": "did:polygon:...",
    "asset_uri": "ipfs://...",
    "pixel_signature": "0x...",
    "encryption_algorithm": "AES-256-CBC"
  }
  ```
- **Response**: Token ID and transaction hash

#### Get Asset Details
- **GET** `/blockchain/asset/<token_id>`
- **Response**: Asset metadata and ownership

#### Get Audit Log
- **GET** `/blockchain/audit-log/<did>?limit=50`
- **Response**: Audit trail events

### Admin

#### List Users
- **GET** `/admin/users?limit=50&offset=0`
- **Response**: User list (admin only)

#### Assign Role
- **POST** `/admin/assign-role`
- **Body**:
  ```json
  {
    "did": "did:polygon:...",
    "role": "MANAGER"
  }
  ```
- **Response**: Role assignment confirmation

#### Get System Statistics
- **GET** `/admin/system-stats`
- **Response**: System metrics and health status

## Error Responses

### 400 Bad Request
```json
{
  "error": "Bad request",
  "message": "Description of what went wrong"
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid credentials"
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

## Rate Limiting

- Standard rate limit: 100 requests per minute per user
- Encryption endpoints: 10 requests per minute
- Blockchain endpoints: 50 requests per minute

## Webhooks

The API supports webhooks for real-time notifications:

- `deepfake.detected` - When deepfake is detected
- `asset.minted` - When NFT is minted
- `identity.registered` - When new identity is registered

Configure webhooks in dashboard settings.

## Examples

### Encrypt Image
```bash
curl -X POST http://localhost:5000/api/v1/images/encrypt \
  -F "image=@photo.jpg" \
  -F "did=did:polygon:user123" \
  -H "Authorization: Bearer <token>"
```

### Detect Deepfake
```bash
curl -X POST http://localhost:5000/api/v1/verify/deepfake \
  -F "image=@suspicious.jpg" \
  -H "Authorization: Bearer <token>"
```

### Register Identity
```bash
curl -X POST http://localhost:5000/api/v1/blockchain/register-identity \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "did": "did:polygon:user123",
    "public_key": "0x...",
    "metadata": "User Profile"
  }'
```
