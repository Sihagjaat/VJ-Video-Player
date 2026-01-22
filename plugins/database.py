# VJ Video Player - Database Helper
# YouTube: @Tech_VJ | Telegram: @VJ_Bots | GitHub: @VJBots

import pymongo
import logging
from datetime import datetime
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class Database:
    """MongoDB Database Handler"""
    
    def __init__(self, uri: str, database_name: str):
        """Initialize database connection"""
        try:
            self.client = pymongo.MongoClient(uri)
            self.db = self.client[database_name]
            
            # Collections
            self.users = self.db.users
            self.files = self.db.files
            self.earnings = self.db.earnings
            self.withdrawals = self.db.withdrawals
            
            # Create indexes for better performance
            self._create_indexes()
            
            logger.info("✅ Database connected successfully")
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def _create_indexes(self):
        """Create database indexes"""
        try:
            # User indexes
            self.users.create_index("user_id", unique=True)
            
            # File indexes
            self.files.create_index("file_id", unique=True)
            self.files.create_index("user_id")
            
            # Earnings indexes
            self.earnings.create_index([("user_id", 1), ("date", -1)])
            
            logger.info("✅ Database indexes created")
        except Exception as e:
            logger.error(f"Index creation error: {e}")
    
    # ==================== USER METHODS ====================
    
    async def add_user(self, user_id: int, name: str, username: str = None) -> bool:
        """Add new user to database"""
        try:
            user_data = {
                "user_id": user_id,
                "name": name,
                "username": username,
                "joined_date": datetime.now(),
                "total_files": 0,
                "total_views": 0,
                "total_earnings": 0.0,
                "balance": 0.0,
                "business_name": "",
                "channel_link": ""
            }
            
            result = self.users.update_one(
                {"user_id": user_id},
                {"$setOnInsert": user_data},
                upsert=True
            )
            
            return result.upserted_id is not None
            
        except Exception as e:
            logger.error(f"Add user error: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user data"""
        try:
            return self.users.find_one({"user_id": user_id})
        except Exception as e:
            logger.error(f"Get user error: {e}")
            return None
    
    async def update_user(self, user_id: int, data: Dict) -> bool:
        """Update user data"""
        try:
            result = self.users.update_one(
                {"user_id": user_id},
                {"$set": data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Update user error: {e}")
            return False
    
    async def get_all_users(self) -> List[Dict]:
        """Get all users"""
        try:
            return list(self.users.find({}))
        except Exception as e:
            logger.error(f"Get all users error: {e}")
            return []
    
    async def total_users_count(self) -> int:
        """Get total users count"""
        try:
            return self.users.count_documents({})
        except Exception as e:
            logger.error(f"Count users error: {e}")
            return 0
    
    # ==================== FILE METHODS ====================
    
    async def add_file(self, file_data: Dict) -> bool:
        """Add file to database"""
        try:
            file_doc = {
                "file_id": file_data.get("file_id"),
                "user_id": file_data.get("user_id"),
                "message_id": file_data.get("message_id"),
                "file_name": file_data.get("file_name"),
                "file_size": file_data.get("file_size"),
                "mime_type": file_data.get("mime_type"),
                "duration": file_data.get("duration", 0),
                "uploaded_date": datetime.now(),
                "views": 0,
                "earnings": 0.0
            }
            
            result = self.files.insert_one(file_doc)
            
            # Update user's total files
            self.users.update_one(
                {"user_id": file_data.get("user_id")},
                {"$inc": {"total_files": 1}}
            )
            
            return result.inserted_id is not None
            
        except Exception as e:
            logger.error(f"Add file error: {e}")
            return False
    
    async def get_file(self, file_id: str) -> Optional[Dict]:
        """Get file data"""
        try:
            return self.files.find_one({"file_id": file_id})
        except Exception as e:
            logger.error(f"Get file error: {e}")
            return None
    
    async def get_user_files(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's files"""
        try:
            return list(
                self.files.find({"user_id": user_id})
                .sort("uploaded_date", -1)
                .limit(limit)
            )
        except Exception as e:
            logger.error(f"Get user files error: {e}")
            return []
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file from database"""
        try:
            result = self.files.delete_one({"file_id": file_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Delete file error: {e}")
            return False
    
    async def increment_views(self, file_id: str, cpm_rate: float = 3.5) -> bool:
        """Increment file views and update earnings"""
        try:
            # Get file data
            file_data = await self.get_file(file_id)
            
            if not file_data:
                return False
            
            # Calculate earnings for this view
            earning_per_view = cpm_rate / 1000
            
            # Update file views and earnings
            self.files.update_one(
                {"file_id": file_id},
                {
                    "$inc": {
                        "views": 1,
                        "earnings": earning_per_view
                    }
                }
            )
            
            # Update user stats
            user_id = file_data.get("user_id")
            self.users.update_one(
                {"user_id": user_id},
                {
                    "$inc": {
                        "total_views": 1,
                        "total_earnings": earning_per_view,
                        "balance": earning_per_view
                    }
                }
            )
            
            # Record earning
            self.earnings.insert_one({
                "user_id": user_id,
                "file_id": file_id,
                "amount": earning_per_view,
                "date": datetime.now(),
                "type": "view"
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Increment views error: {e}")
            return False
    
    # ==================== EARNINGS METHODS ====================
    
    async def get_user_earnings(self, user_id: int, days: int = 30) -> List[Dict]:
        """Get user's earnings history"""
        try:
            from datetime import timedelta
            start_date = datetime.now() - timedelta(days=days)
            
            return list(
                self.earnings.find({
                    "user_id": user_id,
                    "date": {"$gte": start_date}
                }).sort("date", -1)
            )
        except Exception as e:
            logger.error(f"Get earnings error: {e}")
            return []
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        try:
            user = await self.get_user(user_id)
            
            if not user:
                return {}
            
            total_files = user.get("total_files", 0)
            total_views = user.get("total_views", 0)
            total_earnings = user.get("total_earnings", 0.0)
            balance = user.get("balance", 0.0)
            
            # Get today's stats
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_earnings = self.earnings.aggregate([
                {
                    "$match": {
                        "user_id": user_id,
                        "date": {"$gte": today}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$amount"},
                        "count": {"$sum": 1}
                    }
                }
            ])
            
            today_data = list(today_earnings)
            today_views = today_data[0]["count"] if today_data else 0
            today_amount = today_data[0]["total"] if today_data else 0.0
            
            return {
                "total_files": total_files,
                "total_views": total_views,
                "total_earnings": round(total_earnings, 2),
                "balance": round(balance, 2),
                "today_views": today_views,
                "today_earnings": round(today_amount, 2)
            }
            
        except Exception as e:
            logger.error(f"Get user stats error: {e}")
            return {}
    
    # ==================== WITHDRAWAL METHODS ====================
    
    async def create_withdrawal(self, user_id: int, amount: float, method: str, details: str) -> bool:
        """Create withdrawal request"""
        try:
            # Check user balance
            user = await self.get_user(user_id)
            
            if not user or user.get("balance", 0) < amount:
                return False
            
            withdrawal_data = {
                "user_id": user_id,
                "amount": amount,
                "method": method,
                "details": details,
                "status": "pending",
                "requested_date": datetime.now(),
                "processed_date": None
            }
            
            result = self.withdrawals.insert_one(withdrawal_data)
            
            # Deduct from balance
            if result.inserted_id:
                self.users.update_one(
                    {"user_id": user_id},
                    {"$inc": {"balance": -amount}}
                )
            
            return result.inserted_id is not None
            
        except Exception as e:
            logger.error(f"Create withdrawal error: {e}")
            return False
    
    async def get_pending_withdrawals(self) -> List[Dict]:
        """Get all pending withdrawals"""
        try:
            return list(
                self.withdrawals.find({"status": "pending"})
                .sort("requested_date", -1)
            )
        except Exception as e:
            logger.error(f"Get withdrawals error: {e}")
            return []
    
    async def update_withdrawal_status(self, withdrawal_id, status: str) -> bool:
        """Update withdrawal status"""
        try:
            result = self.withdrawals.update_one(
                {"_id": withdrawal_id},
                {
                    "$set": {
                        "status": status,
                        "processed_date": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Update withdrawal error: {e}")
            return False
