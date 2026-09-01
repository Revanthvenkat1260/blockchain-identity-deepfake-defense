// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title IdentityManager
 * @dev Manages decentralized identities (DIDs) on blockchain
 */
contract IdentityManager is AccessControl {
    using Counters for Counters.Counter;

    // Role definitions
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant MANAGER_ROLE = keccak256("MANAGER_ROLE");
    bytes32 public constant AUDITOR_ROLE = keccak256("AUDITOR_ROLE");
    bytes32 public constant USER_ROLE = keccak256("USER_ROLE");

    // Identity structure
    struct Identity {
        bytes32 did;
        address owner;
        bytes32 publicKeyHash;
        uint256 createdAt;
        uint256 updatedAt;
        bool isActive;
        string metadata;
        bytes32 role;
    }

    // Storage
    mapping(bytes32 => Identity) public identities;
    mapping(address => bytes32) public addressToDID;
    Counters.Counter private identityCounter;

    // Events
    event IdentityCreated(
        bytes32 indexed did,
        address indexed owner,
        bytes32 role,
        uint256 timestamp
    );
    event IdentityUpdated(
        bytes32 indexed did,
        string newMetadata,
        uint256 timestamp
    );
    event IdentityRevoked(bytes32 indexed did, uint256 timestamp);
    event RoleAssigned(
        bytes32 indexed did,
        bytes32 newRole,
        uint256 timestamp
    );

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    /**
     * @dev Register new DID
     */
    function registerIdentity(
        bytes32 _did,
        address _owner,
        bytes32 _publicKeyHash,
        string memory _metadata,
        bytes32 _role
    ) external onlyRole(ADMIN_ROLE) returns (bytes32) {
        require(_did != bytes32(0), "DID cannot be empty");
        require(_owner != address(0), "Owner cannot be zero address");
        require(
            identities[_did].owner == address(0),
            "DID already registered"
        );

        identities[_did] = Identity({
            did: _did,
            owner: _owner,
            publicKeyHash: _publicKeyHash,
            createdAt: block.timestamp,
            updatedAt: block.timestamp,
            isActive: true,
            metadata: _metadata,
            role: _role
        });

        addressToDID[_owner] = _did;
        identityCounter.increment();

        emit IdentityCreated(_did, _owner, _role, block.timestamp);
        return _did;
    }

    /**
     * @dev Get identity details
     */
    function getIdentity(bytes32 _did)
        external
        view
        returns (Identity memory)
    {
        require(identities[_did].owner != address(0), "Identity not found");
        return identities[_did];
    }

    /**
     * @dev Update identity metadata
     */
    function updateIdentity(bytes32 _did, string memory _newMetadata)
        external
        onlyRole(ADMIN_ROLE)
    {
        require(identities[_did].owner != address(0), "Identity not found");
        require(identities[_did].isActive, "Identity is not active");

        identities[_did].metadata = _newMetadata;
        identities[_did].updatedAt = block.timestamp;

        emit IdentityUpdated(_did, _newMetadata, block.timestamp);
    }

    /**
     * @dev Assign role to identity
     */
    function assignRole(bytes32 _did, bytes32 _newRole)
        external
        onlyRole(ADMIN_ROLE)
    {
        require(identities[_did].owner != address(0), "Identity not found");
        identities[_did].role = _newRole;
        emit RoleAssigned(_did, _newRole, block.timestamp);
    }

    /**
     * @dev Revoke identity
     */
    function revokeIdentity(bytes32 _did) external onlyRole(ADMIN_ROLE) {
        require(identities[_did].owner != address(0), "Identity not found");
        identities[_did].isActive = false;
        identities[_did].updatedAt = block.timestamp;
        emit IdentityRevoked(_did, block.timestamp);
    }

    /**
     * @dev Get DID for address
     */
    function getDIDForAddress(address _owner)
        external
        view
        returns (bytes32)
    {
        return addressToDID[_owner];
    }

    /**
     * @dev Check if identity is active
     */
    function isIdentityActive(bytes32 _did) external view returns (bool) {
        return identities[_did].isActive;
    }

    /**
     * @dev Get total identities
     */
    function getTotalIdentities() external view returns (uint256) {
        return identityCounter.current();
    }
}
