import datetime
from typing import Optional, Dict, Any, List

import pydantic


class JWToken(pydantic.BaseModel):
    exp: datetime.datetime
    sub: str
    jti: str  # JWT ID for token identification


class JWTUser(pydantic.BaseModel):
    username: str
    email: pydantic.EmailStr
    user_type: str = "CONSUMER"  # Default to CONSUMER
    user_id: int


class DeviceInfo(pydantic.BaseModel):
    android_id: str  # Now required for device identification
    device_id: Optional[str] = None  # Legacy identifier, no longer required
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Android specific fields
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    screen_resolution: Optional[str] = None
    network_type: Optional[str] = None
    device_language: Optional[str] = None
    battery_level: Optional[float] = None
    is_rooted: Optional[bool] = None
    
    # Hardware information
    cpu_info: Optional[str] = None
    total_memory: Optional[str] = None
    available_memory: Optional[str] = None
    total_storage: Optional[str] = None
    available_storage: Optional[str] = None
    
    # Browser specific fields (for web clients)
    browser_name: Optional[str] = None
    browser_version: Optional[str] = None
    
    # Geolocation data (if available and permitted)
    country_code: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Extended device security info
    device_hash: Optional[str] = None  # Unique device identifier hash
    last_security_patch: Optional[str] = None
    
    # Device status
    is_blacklisted: Optional[bool] = None
    blacklist_reason: Optional[str] = None
    
    # Custom client data that can be sent from the device
    client_data: Dict[str, Any] = {}


class DeviceBlacklistRequest(pydantic.BaseModel):
    android_id: str  # Changed from device_id to android_id 
    reason: Optional[str] = None


class DeviceResponse(pydantic.BaseModel):
    device_id: str  # This will actually contain the android_id
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    os_version: Optional[str] = None
    ip_address: Optional[str] = None
    is_blacklisted: bool = False
    last_used_at: Optional[int] = None
    created_at: Optional[int] = None


class JWTResponse(pydantic.BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    device_id: str  # This will contain the android_id in responses
    refresh_token: Optional[str] = None
