// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title AuditTrail
 * @dev Immutable audit logging for compliance
 */
contract AuditTrail is AccessControl {
    using Counters for Counters.Counter;

    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant AUDITOR_ROLE = keccak256("AUDITOR_ROLE");

    // Audit event types
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

    // Audit event structure
    struct AuditEvent {
        uint256 eventId;
        EventType eventType;
        bytes32 initiatedBy;
        bytes32 targetDID;
        uint256 targetTokenId;
        string details;
        uint256 timestamp;
        uint256 blockNumber;
        bool success;
        bytes32 resultHash;
    }

    // Storage
    mapping(uint256 => AuditEvent) public auditEvents;
    mapping(bytes32 => uint256[]) public didAuditHistory;
    Counters.Counter private eventCounter;

    // Events
    event AuditEventLogged(
        uint256 indexed eventId,
        EventType eventType,
        bytes32 indexed initiatedBy,
        uint256 timestamp
    );
    event AuditTrailExported(
        uint256 startBlock,
        uint256 endBlock,
        uint256 eventCount,
        uint256 timestamp
    );

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    /**
     * @dev Log audit event
     */
    function logEvent(
        EventType _eventType,
        bytes32 _initiatedBy,
        bytes32 _targetDID,
        uint256 _targetTokenId,
        string memory _details,
        bool _success
    ) external onlyRole(ADMIN_ROLE) returns (uint256) {
        uint256 eventId = eventCounter.current();
        eventCounter.increment();

        bytes32 resultHash = keccak256(abi.encodePacked(_details, block.timestamp));

        auditEvents[eventId] = AuditEvent({
            eventId: eventId,
            eventType: _eventType,
            initiatedBy: _initiatedBy,
            targetDID: _targetDID,
            targetTokenId: _targetTokenId,
            details: _details,
            timestamp: block.timestamp,
            blockNumber: block.number,
            success: _success,
            resultHash: resultHash
        });

        didAuditHistory[_targetDID].push(eventId);

        emit AuditEventLogged(eventId, _eventType, _initiatedBy, block.timestamp);

        return eventId;
    }

    /**
     * @dev Get audit event
     */
    function getEvent(uint256 _eventId)
        external
        view
        returns (AuditEvent memory)
    {
        return auditEvents[_eventId];
    }

    /**
     * @dev Get event history for DID
     */
    function getEventHistory(bytes32 _did, uint256 _limit)
        external
        view
        returns (AuditEvent[] memory)
    {
        uint256[] memory eventIds = didAuditHistory[_did];
        uint256 length = eventIds.length > _limit ? _limit : eventIds.length;
        
        AuditEvent[] memory events = new AuditEvent[](length);
        
        for (uint256 i = 0; i < length; i++) {
            events[i] = auditEvents[eventIds[eventIds.length - 1 - i]];
        }
        
        return events;
    }

    /**
     * @dev Verify event integrity
     */
    function verifyEvent(uint256 _eventId) external view returns (bool) {
        AuditEvent storage auditEvent = auditEvents[_eventId];
        bytes32 expectedHash = keccak256(
            abi.encodePacked(auditEvent.details, auditEvent.timestamp)
        );
        return auditEvent.resultHash == expectedHash;
    }

    /**
     * @dev Get total audit events
     */
    function getTotalEvents() external view returns (uint256) {
        return eventCounter.current();
    }

    /**
     * @dev Get audit history length for DID
     */
    function getHistoryLength(bytes32 _did) external view returns (uint256) {
        return didAuditHistory[_did].length;
    }
}
