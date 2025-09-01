from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging
from .models import UserInfo, SessionInfo, UserRole
from ..config.settings import settings

logger = logging.getLogger(__name__)


class UserManager:
    """Simple in-memory user management system for pilot phase."""
    
    def __init__(self):
        # In-memory storage (replace with database in production)
        self._users: Dict[str, UserInfo] = {}
        self._sessions: Dict[str, SessionInfo] = {}
        self._user_sessions: Dict[str, List[str]] = {}  # user_id -> [session_ids]
    
    async def create_or_update_user(self, user_info: UserInfo) -> UserInfo:
        """Create new user or update existing user."""
        try:
            # Check if user exists
            existing_user = self._users.get(user_info.user_id)
            
            if existing_user:
                # Update existing user
                updated_user = existing_user.copy(update={
                    "name": user_info.name or existing_user.name,
                    "picture": user_info.picture or existing_user.picture,
                    "role": user_info.role,
                    "institution": user_info.institution,
                    "last_login": datetime.utcnow(),
                    "metadata": {**existing_user.metadata, **user_info.metadata}
                })
                self._users[user_info.user_id] = updated_user
                logger.info(f"Updated user: {updated_user.email}")
                return updated_user
            else:
                # Create new user
                new_user = user_info.copy(update={
                    "created_at": datetime.utcnow(),
                    "last_login": datetime.utcnow()
                })
                self._users[user_info.user_id] = new_user
                self._user_sessions[user_info.user_id] = []
                logger.info(f"Created new user: {new_user.email}")
                return new_user
                
        except Exception as e:
            logger.error(f"Failed to create/update user {user_info.user_id}: {str(e)}")
            raise
    
    async def get_user(self, user_id: str) -> Optional[UserInfo]:
        """Get user by ID."""
        return self._users.get(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[UserInfo]:
        """Get user by email address."""
        for user in self._users.values():
            if user.email.lower() == email.lower():
                return user
        return None
    
    async def update_user_role(self, user_id: str, role: UserRole, institution: Optional[str] = None) -> Optional[UserInfo]:
        """Update user role and institution."""
        user = self._users.get(user_id)
        if not user:
            return None
        
        updated_user = user.copy(update={
            "role": role,
            "institution": institution,
            "last_login": datetime.utcnow()
        })
        self._users[user_id] = updated_user
        
        logger.info(f"Updated user role: {user.email} -> {role.value}")
        return updated_user
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user and all associated sessions."""
        if user_id not in self._users:
            return False
        
        try:
            # Delete all user sessions
            session_ids = self._user_sessions.get(user_id, [])
            for session_id in session_ids:
                self._sessions.pop(session_id, None)
            
            # Delete user
            user = self._users.pop(user_id)
            self._user_sessions.pop(user_id, None)
            
            logger.info(f"Deleted user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {str(e)}")
            return False
    
    async def create_session(self, session_info: SessionInfo) -> SessionInfo:
        """Create new user session."""
        try:
            self._sessions[session_info.session_id] = session_info
            
            # Add to user's session list
            if session_info.user_id not in self._user_sessions:
                self._user_sessions[session_info.user_id] = []
            self._user_sessions[session_info.user_id].append(session_info.session_id)
            
            logger.info(f"Created session {session_info.session_id} for user {session_info.user_id}")
            return session_info
            
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session by ID."""
        session = self._sessions.get(session_id)
        
        # Check if session is expired
        if session and session.expires_at < datetime.utcnow():
            await self.delete_session(session_id)
            return None
        
        return session
    
    async def update_session_activity(self, session_id: str) -> Optional[SessionInfo]:
        """Update session last activity timestamp."""
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        updated_session = session.copy(update={
            "last_activity": datetime.utcnow()
        })
        self._sessions[session_id] = updated_session
        return updated_session
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete specific session."""
        session = self._sessions.pop(session_id, None)
        if not session:
            return False
        
        # Remove from user's session list
        user_sessions = self._user_sessions.get(session.user_id, [])
        if session_id in user_sessions:
            user_sessions.remove(session_id)
        
        logger.info(f"Deleted session {session_id}")
        return True
    
    async def delete_user_sessions(self, user_id: str) -> int:
        """Delete all sessions for a user."""
        session_ids = self._user_sessions.get(user_id, []).copy()
        deleted_count = 0
        
        for session_id in session_ids:
            if await self.delete_session(session_id):
                deleted_count += 1
        
        logger.info(f"Deleted {deleted_count} sessions for user {user_id}")
        return deleted_count
    
    async def get_user_sessions(self, user_id: str) -> List[SessionInfo]:
        """Get all active sessions for a user."""
        session_ids = self._user_sessions.get(user_id, [])
        sessions = []
        
        for session_id in session_ids.copy():
            session = await self.get_session(session_id)
            if session:
                sessions.append(session)
            else:
                # Remove expired/deleted session from user's list
                session_ids.remove(session_id)
        
        return sessions
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        now = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session in self._sessions.items():
            if session.expires_at < now:
                expired_sessions.append(session_id)
        
        deleted_count = 0
        for session_id in expired_sessions:
            if await self.delete_session(session_id):
                deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired sessions")
        
        return deleted_count
    
    async def get_users_by_institution(self, institution_id: str) -> List[UserInfo]:
        """Get all users from a specific institution."""
        return [
            user for user in self._users.values()
            if user.institution == institution_id
        ]
    
    async def get_users_by_role(self, role: UserRole) -> List[UserInfo]:
        """Get all users with a specific role."""
        return [
            user for user in self._users.values()
            if user.role == role
        ]
    
    async def get_user_stats(self) -> Dict:
        """Get user statistics."""
        total_users = len(self._users)
        total_sessions = len(self._sessions)
        active_sessions = sum(
            1 for session in self._sessions.values()
            if session.expires_at > datetime.utcnow()
        )
        
        role_counts = {}
        for role in UserRole:
            role_counts[role.value] = len(await self.get_users_by_role(role))
        
        institution_counts = {}
        for user in self._users.values():
            if user.institution:
                institution_counts[user.institution] = institution_counts.get(user.institution, 0) + 1
        
        return {
            "total_users": total_users,
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "role_distribution": role_counts,
            "institution_distribution": institution_counts,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def export_users(self) -> List[Dict]:
        """Export user data (for backup/migration)."""
        return [user.dict() for user in self._users.values()]
    
    async def import_users(self, user_data: List[Dict]) -> int:
        """Import user data (for backup/migration)."""
        imported_count = 0
        
        for user_dict in user_data:
            try:
                user_info = UserInfo(**user_dict)
                await self.create_or_update_user(user_info)
                imported_count += 1
            except Exception as e:
                logger.error(f"Failed to import user {user_dict.get('user_id', 'unknown')}: {str(e)}")
        
        logger.info(f"Imported {imported_count} users")
        return imported_count


# Global user manager instance
user_manager = UserManager()