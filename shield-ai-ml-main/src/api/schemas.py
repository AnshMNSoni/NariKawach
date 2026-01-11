"""
SHIELD AI - API Schemas
Pydantic models for request/response validation
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class RiskLevelEnum(str, Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyTypeEnum(str, Enum):
    ROUTE_DEVIATION = "route_deviation"
    SPEED_ANOMALY = "speed_anomaly"
    STOP_ANOMALY = "stop_anomaly"
    TIME_ANOMALY = "time_anomaly"
    STALKING_PATTERN = "stalking_pattern"


class InterventionTypeEnum(str, Enum):
    NOTIFICATION = "notification"
    ALERT_GUARDIANS = "alert_guardians"
    SHARE_LOCATION = "share_location"
    EMERGENCY_CALL = "emergency_call"
    FULL_EMERGENCY = "full_emergency"


# ============================================================================
# Base Models
# ============================================================================

class LocationModel(BaseModel):
    """Location coordinates"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = Field(default=None, ge=0)
    altitude: Optional[float] = None
    timestamp: Optional[datetime] = None


class DeviceModel(BaseModel):
    """Nearby device information"""
    device_id: str = Field(..., min_length=1, max_length=255)
    distance_meters: Optional[float] = Field(default=None, ge=0)
    signal_strength: Optional[int] = None
    device_type: Optional[str] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


# ============================================================================
# Risk Assessment
# ============================================================================

class RiskAssessmentRequest(BaseModel):
    """Request for risk assessment"""
    user_id: str = Field(..., min_length=1, max_length=255)
    location: LocationModel
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    nearby_devices: Optional[List[DeviceModel]] = Field(default_factory=list)
    current_route: Optional[List[LocationModel]] = None
    speed: Optional[float] = Field(default=None, ge=0, le=300)
    heading: Optional[float] = Field(default=None, ge=0, le=360)


class RiskFactorModel(BaseModel):
    """Individual risk factor"""
    name: str
    score: float = Field(..., ge=0, le=1)
    weight: float = Field(..., ge=0, le=1)
    contribution: float
    description: Optional[str] = None


class RiskAssessmentResponse(BaseModel):
    """Response from risk assessment"""
    user_id: str
    risk_score: float = Field(..., ge=0, le=1)
    risk_level: RiskLevelEnum
    confidence: float = Field(..., ge=0, le=1)
    risk_components: Dict[str, float]
    risk_breakdown: List[str]
    high_risk_factors: List[str]
    recommendations: Optional[List[str]] = None
    timestamp: datetime


# ============================================================================
# Anomaly Detection
# ============================================================================

class AnomalyDetectionRequest(BaseModel):
    """Request for anomaly detection"""
    user_id: str = Field(..., min_length=1, max_length=255)
    current_location: LocationModel
    route_history: Optional[List[LocationModel]] = None
    expected_route: Optional[List[LocationModel]] = None
    time_context: Optional[Dict[str, Any]] = None


class AnomalyModel(BaseModel):
    """Detected anomaly"""
    anomaly_type: AnomalyTypeEnum
    severity: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    description: str
    location: Optional[LocationModel] = None
    detected_at: datetime


class AnomalyDetectionResponse(BaseModel):
    """Response from anomaly detection"""
    user_id: str
    anomalies_detected: bool
    anomaly_count: int
    anomalies: List[AnomalyModel]
    overall_anomaly_score: float = Field(..., ge=0, le=1)
    recommendations: List[str]
    timestamp: datetime


# ============================================================================
# Stalking Detection
# ============================================================================

class StalkingCheckRequest(BaseModel):
    """Request for stalking pattern check"""
    user_id: str = Field(..., min_length=1, max_length=255)
    current_location: LocationModel
    nearby_devices: List[DeviceModel]
    lookback_hours: Optional[int] = Field(default=168, ge=1, le=720)  # 1 hour to 30 days


class SuspiciousDeviceModel(BaseModel):
    """Suspicious device details"""
    device_id: str
    risk_score: float = Field(..., ge=0, le=1)
    encounter_count: int
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    risk_factors: List[str]


class StalkingCheckResponse(BaseModel):
    """Response from stalking check"""
    user_id: str
    stalking_risk: float = Field(..., ge=0, le=1)
    stalking_detected: bool
    detected_patterns: List[str]
    suspicious_devices: List[SuspiciousDeviceModel]
    confidence: float = Field(..., ge=0, le=1)
    recommendations: List[str]
    timestamp: datetime


# ============================================================================
# Intervention
# ============================================================================

class InterventionRequest(BaseModel):
    """Request for intervention decision"""
    user_id: str = Field(..., min_length=1, max_length=255)
    risk_assessment: RiskAssessmentResponse
    anomaly_detection: Optional[AnomalyDetectionResponse] = None
    stalking_detection: Optional[StalkingCheckResponse] = None
    user_preferences: Optional[Dict[str, Any]] = None


class InterventionAction(BaseModel):
    """Recommended intervention action"""
    action_type: InterventionTypeEnum
    priority: str
    description: str
    auto_execute: bool = False
    requires_confirmation: bool = True
    target_contacts: Optional[List[str]] = None


class InterventionResponse(BaseModel):
    """Response with intervention decision"""
    user_id: str
    intervention_required: bool
    urgency_level: str
    recommended_actions: List[InterventionAction]
    auto_actions_taken: List[str]
    message_to_user: Optional[str] = None
    timestamp: datetime


# ============================================================================
# Emergency
# ============================================================================

class EmergencyActivationRequest(BaseModel):
    """Request to activate emergency protocol"""
    user_id: str = Field(..., min_length=1, max_length=255)
    location: LocationModel
    emergency_type: str
    trigger_source: str  # 'user', 'auto', 'guardian'
    additional_info: Optional[Dict[str, Any]] = None


class EmergencyActivationResponse(BaseModel):
    """Response from emergency activation"""
    user_id: str
    emergency_id: str
    status: str
    actions_initiated: List[str]
    contacts_notified: List[str]
    estimated_response_time: Optional[int] = None  # seconds
    instructions: List[str]
    timestamp: datetime


# ============================================================================
# User Management
# ============================================================================

class UserProfileRequest(BaseModel):
    """User profile data"""
    user_id: str
    name: Optional[str] = None
    emergency_contacts: Optional[List[Dict[str, str]]] = None
    home_location: Optional[LocationModel] = None
    work_location: Optional[LocationModel] = None
    safe_zones: Optional[List[LocationModel]] = None
    preferences: Optional[Dict[str, Any]] = None


class UserHistoryRequest(BaseModel):
    """Request for user history"""
    user_id: str
    history_type: str  # 'risk', 'anomaly', 'stalking', 'all'
    hours: int = Field(default=24, ge=1, le=720)


# ============================================================================
# Health & Status
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    components: Dict[str, Dict[str, Any]]
    environment: str
    version: str


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: Optional[str] = None
    code: Optional[str] = None
    path: Optional[str] = None
    timestamp: datetime


# ============================================================================
# Batch Operations
# ============================================================================

class BatchRiskRequest(BaseModel):
    """Batch risk assessment request"""
    requests: List[RiskAssessmentRequest] = Field(..., max_length=100)


class BatchRiskResponse(BaseModel):
    """Batch risk assessment response"""
    results: List[RiskAssessmentResponse]
    total_processed: int
    failed_count: int
    processing_time_ms: float
