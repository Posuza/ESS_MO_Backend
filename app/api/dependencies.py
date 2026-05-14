from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from typing import Optional, List, Tuple
from functools import wraps
from datetime import datetime

from app.core.orm import get_db
# from app.models.user import user  # OLD - Not used with employee model



# def _validate_token(token: HTTPAuthorizationCredentials, db: Session) -> Tuple[int, str]:
#     """Validate token and return user_id and user_type"""
#     payload = verify_token(token.credentials)
#     if not payload:
#         raise HTTPException(status_code=401, detail="Invalid token")

#     token_obj = db.query(Token).filter(
#         Token.token == token.credentials,
#         Token.is_revoked == False
#     ).first()
    
#     if not token_obj or token_obj.expires_at < datetime.utcnow():
#         raise HTTPException(status_code=401, detail="Token expired or invalid")
    
#     user_id = payload.get("sub")
#     user_type = payload.get("type", "customer")  # Default to customer if not specified
#     if not user_id:
#         raise HTTPException(status_code=401, detail="Invalid token payload")  
#     # Convert to int since we're now using str(user.id) in JWT
#     try:
#         user_id = int(user_id)
#     except (ValueError, TypeError):
#         raise HTTPException(status_code=401, detail="Invalid user ID format")
    
#     # Optional: Verify that token_obj.type matches payload type
#     if token_obj.type != user_type:
#         raise HTTPException(status_code=401, detail="Token type mismatch")
    
#     return user_id, user_type

def _get_active_user(db: Session, user_id: int, user_type: str) -> Tuple[Customer, str]:
    """Internal function to get active user and user type"""
    try:
        # Determine which model to query based on user_type
        #     from app.models.user import users  # OLD - Not used with employee model
            user = db.query(Administrator).filter(Administrator.id == user_id).first()
        else:
            user = db.query(Customer).filter(Customer.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive. Please contact support.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return user, user_type
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )

# def _check_permissions(db: Session, user_id: int, permissions: List[str]) -> bool:
#     """Check if the user has the required permissions"""
#     try:
#         from app.models.user.administrator import Administrator
#         from app.models.user.administrator_permissionMap import AdministratorPermissionMap
#         admin = db.query(Administrator).options(
#             joinedload(Administrator.permissions).joinedload(AdministratorPermissionMap.permission)
#         ).filter(Administrator.id == user_id).first()
#         if not admin:
#             return False
#         # Access permission names through the AdministratorPermissionMap
#         admin_perm_names = [p.permission.name for p in admin.permissions]
#         return all(perm in admin_perm_names for perm in permissions)
#     except Exception:
#         return False

# # ==================== DECORATORS ====================

# def token_required(func):
#     @wraps(func)
#     async def wrapper(*args, **kwargs):
#         token = None
#         db = None
#         for key, value in kwargs.items():
#             if isinstance(value, HTTPAuthorizationCredentials):
#                 token = value
#             elif isinstance(value, Session):
#                 db = value
        
#         if not token or not db:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Missing required dependencies (token or db)"
#             )
        
#         user_id, user_type = _validate_token(token, db)
#         current_user, user_type = _get_active_user(db, user_id, user_type)
#         kwargs['user_id'] = user_id
#         kwargs['user_type'] = user_type
#         return await func(*args, **kwargs)
#     return wrapper

def active_user_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        db = None
        for key, value in kwargs.items():
            if isinstance(value, HTTPAuthorizationCredentials):
                token = value
            elif isinstance(value, Session):
                db = value

        current_user, user_type = _get_active_user(db, user_id, user_type)
        kwargs['current_user'] = current_user
        kwargs['user_type'] = user_type
        
        return await func(*args, **kwargs)
    
    return wrapper

# def roles_required(*allowed_roles):
#     """Decorator to require specific roles - provides current_user and user_type"""
#     def decorator(func):
#         @wraps(func)
#         async def wrapper(*args, **kwargs):
#             token = None
#             db = None
#             for key, value in kwargs.items():
#                 if isinstance(value, HTTPAuthorizationCredentials):
#                     token = value
#                 elif isinstance(value, Session):
#                     db = value
            
#             if not token or not db:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail="Missing required dependencies (token or db)"
#                 )
            
#             user_id, user_type = _validate_token(token, db)
#             current_user, user_type = _get_active_user(db, user_id, user_type)
            
#             # Normalize allowed_roles: support @roles_required(["a","b"]) or @roles_required("a","b")
#             roles = allowed_roles
#             if len(roles) == 1 and isinstance(roles[0], (list, tuple, set)):
#                 roles = tuple(roles[0])
#             # Ensure all items are strings
#             roles = tuple(str(r) for r in roles)
            
#             if current_user.role not in roles:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail=f"Access denied. Required roles: {', '.join(roles)}. Your role: {current_user.role}"
#                 )
            
#             kwargs['current_user'] = current_user
#             kwargs['user_type'] = user_type
#             return await func(*args, **kwargs)
        
#         return wrapper
#     return decorator

# def roles_and_permissions_required(*allowed_roles, permissions: Optional[List[str]] = None):
#     """Decorator to require specific roles and optionally permissions - provides current_user and user_type"""
#     def decorator(func):
#         @wraps(func)
#         async def wrapper(*args, **kwargs):
#             token = None
#             db = None
#             for key, value in kwargs.items():
#                 if isinstance(value, HTTPAuthorizationCredentials):
#                     token = value
#                 elif isinstance(value, Session):
#                     db = value
            
#             if not token or not db:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail="Missing required dependencies (token or db)"
#                 )
            
#             user_id, user_type = _validate_token(token, db)
#             current_user, user_type = _get_active_user(db, user_id, user_type)
            
#             # Normalize allowed_roles: support @roles_and_permissions_required(["a","b"], permissions=...)
#             roles = allowed_roles
#             if len(roles) == 1 and isinstance(roles[0], (list, tuple, set)):
#                 roles = tuple(roles[0])
#             roles = tuple(str(r) for r in roles)
            
#             # Check role
#             if current_user.role not in roles:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail=f"Access denied. Required roles: {', '.join(roles)}. Your role: {current_user.role}"
#                 )
            
#             # Normalize permissions: accept a single string or a list/tuple
#             perms = permissions
#             if isinstance(perms, str):
#                 perms = [perms]
#             if isinstance(perms, (list, tuple, set)):
#                 perms = [str(p) for p in perms]
            
#             # Check permissions if specified
#             if perms:
#                 if not _check_permissions(db, user_id, perms):
#                     raise HTTPException(
#                         status_code=status.HTTP_403_FORBIDDEN,
#                         detail=f"Access denied. Required permissions: {', '.join(perms)}"
#                     )
            
#             kwargs['current_user'] = current_user
#             kwargs['user_type'] = user_type
#             return await func(*args, **kwargs)
        
#         return wrapper
#     return decorator

# Export decorators
__all__ = [
    # "token_required", 
    # "roles_required", 
    # "roles_and_permissions_required",
    "active_user_required",

]