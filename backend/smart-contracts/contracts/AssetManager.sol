// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title AssetManager
 * @dev Manages NFT-based digital asset ownership
 */
contract AssetManager is ERC721, AccessControl {
    using Counters for Counters.Counter;

    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant MANAGER_ROLE = keccak256("MANAGER_ROLE");

    // Asset structure
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

    // Storage
    mapping(uint256 => Asset) public assets;
    mapping(bytes32 => uint256[]) public didToAssets;
    Counters.Counter private tokenIdCounter;

    // Events
    event AssetMinted(
        uint256 indexed tokenId,
        bytes32 indexed ownerDID,
        bytes32 pixelSignature,
        uint256 timestamp
    );
    event AssetTransferred(
        uint256 indexed tokenId,
        bytes32 indexed fromDID,
        bytes32 indexed toDID,
        uint256 timestamp
    );
    event AssetVerified(uint256 indexed tokenId, bool isValid, uint256 timestamp);
    event AssetInvalidated(uint256 indexed tokenId, string reason, uint256 timestamp);

    constructor() ERC721("DeepfakeDefenseNFT", "DFDN") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    /**
     * @dev Mint new asset NFT
     */
    function mintAsset(
        bytes32 _ownerDID,
        string memory _assetURI,
        bytes32 _pixelSignature,
        string memory _encryptionAlgorithm,
        bytes32 _encryptionHash
    ) external onlyRole(MANAGER_ROLE) returns (uint256) {
        require(_ownerDID != bytes32(0), "Owner DID cannot be empty");
        require(bytes(_assetURI).length > 0, "Asset URI cannot be empty");

        uint256 newTokenId = tokenIdCounter.current();
        tokenIdCounter.increment();

        // Mint NFT
        _mint(msg.sender, newTokenId);

        // Create asset record
        assets[newTokenId] = Asset({
            tokenId: newTokenId,
            ownerDID: _ownerDID,
            assetURI: _assetURI,
            pixelSignature: _pixelSignature,
            mintedAt: block.timestamp,
            lastModifiedAt: block.timestamp,
            isValid: true,
            encryptionAlgorithm: _encryptionAlgorithm,
            encryptionHash: _encryptionHash
        });

        // Map DID to asset
        didToAssets[_ownerDID].push(newTokenId);

        emit AssetMinted(
            newTokenId,
            _ownerDID,
            _pixelSignature,
            block.timestamp
        );

        return newTokenId;
    }

    /**
     * @dev Get asset details
     */
    function getAsset(uint256 _tokenId)
        external
        view
        returns (Asset memory)
    {
        require(_exists(_tokenId), "Asset does not exist");
        return assets[_tokenId];
    }

    /**
     * @dev Transfer asset ownership
     */
    function transferAsset(
        uint256 _tokenId,
        bytes32 _fromDID,
        bytes32 _toDID
    ) external onlyRole(MANAGER_ROLE) {
        require(_exists(_tokenId), "Asset does not exist");
        require(assets[_tokenId].ownerDID == _fromDID, "Ownership mismatch");
        require(_toDID != bytes32(0), "Invalid recipient DID");

        assets[_tokenId].ownerDID = _toDID;
        assets[_tokenId].lastModifiedAt = block.timestamp;

        emit AssetTransferred(_tokenId, _fromDID, _toDID, block.timestamp);
    }

    /**
     * @dev Verify asset authenticity
     */
    function verifyAsset(uint256 _tokenId)
        external
        view
        returns (bool)
    {
        require(_exists(_tokenId), "Asset does not exist");
        return assets[_tokenId].isValid;
    }

    /**
     * @dev Invalidate asset (on deepfake detection)
     */
    function invalidateAsset(uint256 _tokenId, string memory _reason)
        external
        onlyRole(ADMIN_ROLE)
    {
        require(_exists(_tokenId), "Asset does not exist");
        assets[_tokenId].isValid = false;
        emit AssetInvalidated(_tokenId, _reason, block.timestamp);
    }

    /**
     * @dev Get assets for DID
     */
    function getAssetsByDID(bytes32 _did)
        external
        view
        returns (uint256[] memory)
    {
        return didToAssets[_did];
    }

    /**
     * @dev Get total assets minted
     */
    function getTotalAssets() external view returns (uint256) {
        return tokenIdCounter.current();
    }

    /**
     * @dev Check if NFT exists
     */
    function _exists(uint256 tokenId) internal view returns (bool) {
        return assets[tokenId].tokenId == tokenId && assets[tokenId].isValid;
    }
}
