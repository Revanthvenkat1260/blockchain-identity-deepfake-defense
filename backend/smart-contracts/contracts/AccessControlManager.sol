// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title AccessControlManager
 * @dev Implements Role-Based Access Control (RBAC)
 */
contract AccessControlManager is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant MANAGER_ROLE = keccak256("MANAGER_ROLE");
    bytes32 public constant AUDITOR_ROLE = keccak256("AUDITOR_ROLE");
    bytes32 public constant USER_ROLE = keccak256("USER_ROLE");

    // Permission storage
    mapping(bytes32 => mapping(string => bool)) public permissions;
    mapping(bytes32 => mapping(address => uint256)) public delegations;

    // Events
    event PermissionGranted(
        bytes32 indexed did,
        string permission,
        uint256 timestamp
    );
    event PermissionRevoked(
        bytes32 indexed did,
        string permission,
        uint256 timestamp
    );
    event AccessDelegated(
        bytes32 indexed from,
        address indexed to,
        string resource,
        uint256 expiresAt
    );

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    /**
     * @dev Grant permission
     */
    function grantPermission(
        bytes32 _did,
        string memory _permission
    ) external onlyRole(ADMIN_ROLE) {
        permissions[_did][_permission] = true;
        emit PermissionGranted(_did, _permission, block.timestamp);
    }

    /**
     * @dev Revoke permission
     */
    function revokePermission(
        bytes32 _did,
        string memory _permission
    ) external onlyRole(ADMIN_ROLE) {
        permissions[_did][_permission] = false;
        emit PermissionRevoked(_did, _permission, block.timestamp);
    }

    /**
     * @dev Check permission
     */
    function hasPermission(
        bytes32 _did,
        string memory _permission
    ) external view returns (bool) {
        return permissions[_did][_permission];
    }

    /**
     * @dev Delegate access
     */
    function delegateAccess(
        bytes32 _from,
        address _to,
        string memory _resource,
        uint256 _expiresAt
    ) external onlyRole(ADMIN_ROLE) {
        require(_to != address(0), "Invalid delegate address");
        require(_expiresAt > block.timestamp, "Expiration in past");

        delegations[_from][_to] = _expiresAt;
        emit AccessDelegated(_from, _to, _resource, _expiresAt);
    }

    /**
     * @dev Check if delegation is valid
     */
    function isDelegationValid(
        bytes32 _from,
        address _to
    ) external view returns (bool) {
        return delegations[_from][_to] > block.timestamp;
    }
}
