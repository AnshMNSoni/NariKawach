"""
SHIELD AI - API Endpoints
REST API endpoints for safety services
"""

from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .schemas import (
    RiskAssessmentRequest, RiskAssessmentResponse,
    AnomalyDetectionRequest, AnomalyDetectionResponse,
    StalkingCheckRequest, StalkingCheckResponse,
    InterventionRequest, InterventionResponse,
    EmergencyActivationRequest, EmergencyActivationResponse,
    UserProfileRequest, UserHistoryRequest,
    HealthResponse, ErrorResponse,
    BatchRiskRequest, BatchRiskResponse,
    LocationModel, RiskLevelEnum
)

from ...utils.logger import setup_logger
from ...config.settings import settings

logger = setup_logger(__name__)

# Create router
router = APIRouter()

# Security
security = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """Verify API token (optional for some endpoints)"""
    if credentials is None:
        return None
    
    token = credentials.credentials
    
    # In production, validate against database or auth service
    if not token.startswith("shield_"):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    return token


async def require_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Require valid API token"""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = credentials.credentials
    
    if not token.startswith("shield_"):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return token


# Import components (these will be initialized by fastapi_server.py)
# We use a getter pattern to avoid circular imports
def get_risk_calculator():
    from .fastapi_server import risk_calculator
    return risk_calculator

def get_risk_predictor():
    from .fastapi_server import risk_predictor
    return risk_predictor

def get_route_detector():
    from .fastapi_server import route_detector
    return route_detector

def get_stalking_detector():
    from .fastapi_server import stalking_detector
    return stalking_detector

def get_intervention_agent():
    from .fastapi_server import intervention_agent
    return intervention_agent

def get_emergency_coordinator():
    from .fastapi_server import emergency_coordinator
    return emergency_coordinator


# ============================================================================
# Risk Assessment Endpoints
# ============================================================================

@router.post(
    "/risk/assess",
    response_model=RiskAssessmentResponse,
    tags=["Risk Assessment"],
    summary="Assess user risk",
    description="Calculate comprehensive risk score based on location and context"
)
async def assess_risk(
    request: RiskAssessmentRequest,
    background_tasks: BackgroundTasks,
    token: Optional[str] = Depends(verify_token)
):
    """
    Assess risk for a user based on:
    - Current location
    - Environmental factors
    - Temporal factors
    - Behavioral patterns
    - Social context
    """
    try:
        risk_calculator = get_risk_calculator()
        
        if risk_calculator is None:
            raise HTTPException(status_code=503, detail="Risk calculator not available")
        
        # Build context from request
        context = {
            'latitude': request.location.latitude,
            'longitude': request.location.longitude,
            'speed': request.speed,
            **request.context
        }
        
        # Add nearby devices if provided
        if request.nearby_devices:
            context['nearby_devices'] = [d.model_dump() for d in request.nearby_devices]
        
        # Calculate risk
        result = risk_calculator.calculate_risk(request.user_id, context)
        
        # Build response
        response = RiskAssessmentResponse(
            user_id=result['user_id'],
            risk_score=result['risk_score'],
            risk_level=RiskLevelEnum(result['risk_level'].value if hasattr(result['risk_level'], 'value') else result['risk_level']),
            confidence=result['confidence'],
            risk_components=result['risk_components'],
            risk_breakdown=result['risk_breakdown'],
            high_risk_factors=result['high_risk_factors'],
            recommendations=result.get('recommendations'),
            timestamp=datetime.now()
        )
        
        logger.info(f"Risk assessment for {request.user_id}: {result['risk_level']}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in risk assessment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/risk/history/{user_id}",
    tags=["Risk Assessment"],
    summary="Get risk history"
)
async def get_risk_history(
    user_id: str,
    hours: int = Query(default=24, ge=1, le=168),
    token: str = Depends(require_token)
):
    """Get risk assessment history for a user"""
    try:
        risk_calculator = get_risk_calculator()
        
        if risk_calculator is None:
            raise HTTPException(status_code=503, detail="Service unavailable")
        
        history = risk_calculator.get_risk_history(user_id, hours)
        
        return {
            "user_id": user_id,
            "hours": hours,
            "history": history,
            "count": len(history),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting risk history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/risk/trend/{user_id}",
    tags=["Risk Assessment"],
    summary="Get risk trend"
)
async def get_risk_trend(
    user_id: str,
    hours: int = Query(default=6, ge=1, le=24),
    token: str = Depends(require_token)
):
    """Get risk trend analysis for a user"""
    try:
        risk_calculator = get_risk_calculator()
        
        if risk_calculator is None:
            raise HTTPException(status_code=503, detail="Service unavailable")
        
        trend = risk_calculator.calculate_risk_trend(user_id, hours)
        
        return {
            "user_id": user_id,
            "trend_analysis": trend,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting risk trend: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Anomaly Detection Endpoints
# ============================================================================

@router.post(
    "/anomalies/detect",
    response_model=AnomalyDetectionResponse,
    tags=["Anomaly Detection"],
    summary="Detect route anomalies"
)
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    token: Optional[str] = Depends(verify_token)
):
    """
    Detect anomalies in user's route and behavior:
    - Route deviations
    - Speed anomalies
    - Unexpected stops
    - Time pattern anomalies
    """
    try:
        route_detector = get_route_detector()
        
        if route_detector is None:
            raise HTTPException(status_code=503, detail="Anomaly detector not available")
        
        # Convert location to dict
        current_location = {
            'latitude': request.current_location.latitude,
            'longitude': request.current_location.longitude
        }
        
        # Convert route history if provided
        route_history = None
        if request.route_history:
            route_history = [
                {'latitude': loc.latitude, 'longitude': loc.longitude}
                for loc in request.route_history
            ]
        
        # Detect anomalies
        result = route_detector.detect_anomalies(
            user_id=request.user_id,
            current_location=current_location,
            route_history=route_history
        )
        
        # Build response
        response = AnomalyDetectionResponse(
            user_id=request.user_id,
            anomalies_detected=result.get('anomalies_detected', False),
            anomaly_count=result.get('anomaly_count', 0),
            anomalies=result.get('anomalies', []),
            overall_anomaly_score=result.get('overall_anomaly_score', 0.0),
            recommendations=result.get('recommendations', []),
            timestamp=datetime.now()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in anomaly detection: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Stalking Detection Endpoints
# ============================================================================

@router.post(
    "/stalking/check",
    response_model=StalkingCheckResponse,
    tags=["Stalking Detection"],
    summary="Check for stalking patterns"
)
async def check_stalking(
    request: StalkingCheckRequest,
    background_tasks: BackgroundTasks,
    token: Optional[str] = Depends(verify_token)
):
    """
    Analyze proximity patterns for potential stalking:
    - Device coincidence patterns
    - Route following detection
    - Temporal correlation analysis
    - Multi-day pattern detection
    """
    try:
        stalking_detector = get_stalking_detector()
        
        if stalking_detector is None:
            raise HTTPException(status_code=503, detail="Stalking detector not available")
        
        # Convert request data
        current_location = {
            'latitude': request.current_location.latitude,
            'longitude': request.current_location.longitude
        }
        
        nearby_devices = [
            {
                'device_id': d.device_id,
                'distance_meters': d.distance_meters or 0,
                'signal_strength': d.signal_strength
            }
            for d in request.nearby_devices
        ]
        
        # Detect stalking patterns
        result = stalking_detector.detect_stalking_patterns(
            user_id=request.user_id,
            current_location=current_location,
            nearby_devices=nearby_devices
        )
        
        # Build response
        response = StalkingCheckResponse(
            user_id=request.user_id,
            stalking_risk=result.get('stalking_risk', 0.0),
            stalking_detected=result.get('stalking_detected', False),
            detected_patterns=result.get('detected_patterns', []),
            suspicious_devices=result.get('suspicious_devices', []),
            confidence=result.get('confidence', 0.0),
            recommendations=result.get('recommendations', []),
            timestamp=datetime.now()
        )
        
        # Log high-risk detections
        if response.stalking_detected:
            logger.warning(
                f"Stalking detected for user {request.user_id}: "
                f"risk={response.stalking_risk:.2f}"
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in stalking detection: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stalking/history/{user_id}",
    tags=["Stalking Detection"],
    summary="Get stalking detection history"
)
async def get_stalking_history(
    user_id: str,
    token: str = Depends(require_token)
):
    """Get stalking detection history for a user"""
    try:
        stalking_detector = get_stalking_detector()
        
        if stalking_detector is None:
            raise HTTPException(status_code=503, detail="Service unavailable")
        
        history = stalking_detector.get_user_stalking_history(user_id)
        
        return {
            "user_id": user_id,
            "history": history,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stalking history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Intervention Endpoints
# ============================================================================

@router.post(
    "/intervention/decide",
    response_model=InterventionResponse,
    tags=["Intervention"],
    summary="Decide on safety intervention"
)
async def decide_intervention(
    request: InterventionRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(require_token)
):
    """
    Decide on appropriate safety intervention based on:
    - Risk assessment
    - Anomaly detection
    - Stalking detection
    - User preferences
    """
    try:
        intervention_agent = get_intervention_agent()
        
        if intervention_agent is None:
            raise HTTPException(status_code=503, detail="Intervention agent not available")
        
        # Build context
        context = {
            'risk_assessment': request.risk_assessment.model_dump(),
            'anomaly_detection': request.anomaly_detection.model_dump() if request.anomaly_detection else None,
            'stalking_detection': request.stalking_detection.model_dump() if request.stalking_detection else None,
            'user_preferences': request.user_preferences
        }
        
        # Get intervention decision
        result = intervention_agent.decide_intervention(
            user_id=request.user_id,
            context=context
        )
        
        response = InterventionResponse(
            user_id=request.user_id,
            intervention_required=result.get('intervention_required', False),
            urgency_level=result.get('urgency_level', 'low'),
            recommended_actions=result.get('recommended_actions', []),
            auto_actions_taken=result.get('auto_actions_taken', []),
            message_to_user=result.get('message_to_user'),
            timestamp=datetime.now()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in intervention decision: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Emergency Endpoints
# ============================================================================

@router.post(
    "/emergency/activate",
    response_model=EmergencyActivationResponse,
    tags=["Emergency"],
    summary="Activate emergency protocol"
)
async def activate_emergency(
    request: EmergencyActivationRequest,
    background_tasks: BackgroundTasks,
    token: Optional[str] = Depends(verify_token)
):
    """
    Activate emergency response protocol:
    - Alert emergency contacts
    - Share location with guardians
    - Initiate emergency services (if configured)
    - Log emergency event
    """
    try:
        emergency_coordinator = get_emergency_coordinator()
        
        if emergency_coordinator is None:
            raise HTTPException(status_code=503, detail="Emergency coordinator not available")
        
        # Activate emergency
        result = emergency_coordinator.activate_emergency(
            user_id=request.user_id,
            location={
                'latitude': request.location.latitude,
                'longitude': request.location.longitude
            },
            emergency_type=request.emergency_type,
            trigger_source=request.trigger_source,
            additional_info=request.additional_info
        )
        
        response = EmergencyActivationResponse(
            user_id=request.user_id,
            emergency_id=result.get('emergency_id', ''),
            status=result.get('status', 'activated'),
            actions_initiated=result.get('actions_initiated', []),
            contacts_notified=result.get('contacts_notified', []),
            estimated_response_time=result.get('estimated_response_time'),
            instructions=result.get('instructions', []),
            timestamp=datetime.now()
        )
        
        logger.warning(
            f"EMERGENCY ACTIVATED for user {request.user_id}: "
            f"type={request.emergency_type}, source={request.trigger_source}"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating emergency: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/emergency/deactivate/{emergency_id}",
    tags=["Emergency"],
    summary="Deactivate emergency"
)
async def deactivate_emergency(
    emergency_id: str,
    user_id: str,
    reason: str = "user_cancelled",
    token: str = Depends(require_token)
):
    """Deactivate an active emergency"""
    try:
        emergency_coordinator = get_emergency_coordinator()
        
        if emergency_coordinator is None:
            raise HTTPException(status_code=503, detail="Service unavailable")
        
        result = emergency_coordinator.deactivate_emergency(
            emergency_id=emergency_id,
            user_id=user_id,
            reason=reason
        )
        
        return {
            "emergency_id": emergency_id,
            "status": "deactivated",
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating emergency: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health & Info Endpoints
# ============================================================================

@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check"
)
async def health_check():
    """Check system health and component status"""
    try:
        # Import here to avoid circular import
        from .fastapi_server import check_component_health
        
        health_status = await check_component_health()
        
        return HealthResponse(
            status="healthy" if health_status['overall_healthy'] else "degraded",
            timestamp=datetime.now(),
            components=health_status['components'],
            environment=settings.ENVIRONMENT,
            version="2.0.0"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            components={},
            environment=settings.ENVIRONMENT,
            version="2.0.0"
        )


@router.get(
    "/info",
    tags=["System"],
    summary="API information"
)
async def api_info():
    """Get API information"""
    return {
        "service": "SHIELD AI Safety API",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "features": {
            "risk_assessment": True,
            "anomaly_detection": settings.ENABLE_ROUTE_ANOMALY,
            "stalking_detection": settings.ENABLE_STALKING_DETECTION,
            "emergency_protocol": settings.ENABLE_EMERGENCY_PROTOCOL
        },
        "timestamp": datetime.now().isoformat()
    }
