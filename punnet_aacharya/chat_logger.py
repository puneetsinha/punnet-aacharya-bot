import logging
import os
import json
from datetime import datetime
from pathlib import Path

class ChatLogger:
    def __init__(self, base_dir="chat_logs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Create subdirectories
        self.conversations_dir = self.base_dir / "conversations"
        self.conversations_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"ChatLogger initialized with base directory: {self.base_dir}")
    
    def _sanitize_filename(self, filename):
        """Sanitize filename to be filesystem safe"""
        import re
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        return filename
    
    def _get_chat_file_path(self, username, user_id, timestamp=None):
        """Get the chat file path for a user"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Create safe filename
        safe_username = self._sanitize_filename(str(username))
        date_str = timestamp.strftime("%Y%m%d")
        time_str = timestamp.strftime("%H%M%S")
        
        filename = f"{safe_username}_{user_id}_{date_str}_{time_str}.json"
        return self.conversations_dir / filename
    
    def log_message(self, user_id, username, message_type, content, metadata=None):
        """Log a single message"""
        timestamp = datetime.now()
        
        # Get or create chat file
        chat_file = self._get_chat_file_path(username, user_id, timestamp)
        
        # Create message entry
        message_entry = {
            "timestamp": timestamp.isoformat(),
            "user_id": user_id,
            "username": username,
            "message_type": message_type,  # 'user', 'bot', 'system'
            "content": content,
            "metadata": metadata or {}
        }
        
        # Load existing chat or create new
        chat_data = self._load_chat_file(chat_file)
        chat_data["messages"].append(message_entry)
        chat_data["last_updated"] = timestamp.isoformat()
        
        # Save chat file
        self._save_chat_file(chat_file, chat_data)
        
        # Also log to general log
        self.logger.info(f"Chat logged - User: {username} ({user_id}), Type: {message_type}, Content: {content[:100]}...")
        
        return chat_file
    
    def log_user_message(self, user_id, username, message, context=None):
        """Log a user message"""
        metadata = {
            "context": context or "general",
            "message_length": len(message)
        }
        return self.log_message(user_id, username, "user", message, metadata)
    
    def log_bot_response(self, user_id, username, response, context=None):
        """Log a bot response"""
        metadata = {
            "context": context or "general",
            "response_length": len(response)
        }
        return self.log_message(user_id, username, "bot", response, metadata)
    
    def log_system_event(self, user_id, username, event, details=None):
        """Log a system event"""
        metadata = {
            "event": event,
            "details": details or {}
        }
        return self.log_message(user_id, username, "system", f"System event: {event}", metadata)
    
    def _load_chat_file(self, chat_file):
        """Load existing chat file or create new"""
        if chat_file.exists():
            try:
                with open(chat_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Create new chat file
        return {
            "chat_id": chat_file.stem,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "messages": []
        }
    
    def _save_chat_file(self, chat_file, chat_data):
        """Save chat file"""
        try:
            with open(chat_file, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving chat file {chat_file}: {e}")
    
    def get_user_chats(self, username, user_id):
        """Get all chat files for a user"""
        safe_username = self._sanitize_filename(str(username))
        pattern = f"{safe_username}_{user_id}_*.json"
        
        chat_files = list(self.conversations_dir.glob(pattern))
        return sorted(chat_files, key=lambda x: x.stat().st_mtime, reverse=True)
    
    def get_chat_summary(self, username, user_id):
        """Get a summary of user's chat history"""
        chat_files = self.get_user_chats(username, user_id)
        
        summary = {
            "username": username,
            "user_id": user_id,
            "total_chats": len(chat_files),
            "chats": []
        }
        
        for chat_file in chat_files:
            try:
                with open(chat_file, 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)
                
                chat_summary = {
                    "chat_id": chat_data.get("chat_id"),
                    "created_at": chat_data.get("created_at"),
                    "last_updated": chat_data.get("last_updated"),
                    "message_count": len(chat_data.get("messages", [])),
                    "file_path": str(chat_file)
                }
                summary["chats"].append(chat_summary)
                
            except Exception as e:
                self.logger.error(f"Error reading chat file {chat_file}: {e}")
        
        return summary
    
    def get_recent_messages(self, username, user_id, limit=10):
        """Get recent messages for a user"""
        chat_files = self.get_user_chats(username, user_id)
        recent_messages = []
        
        for chat_file in chat_files[:3]:  # Check last 3 chat files
            try:
                with open(chat_file, 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)
                
                messages = chat_data.get("messages", [])
                for msg in messages[-limit:]:  # Get last messages from this chat
                    recent_messages.append({
                        "timestamp": msg.get("timestamp"),
                        "message_type": msg.get("message_type"),
                        "content": msg.get("content"),
                        "chat_file": chat_file.name
                    })
                
            except Exception as e:
                self.logger.error(f"Error reading chat file {chat_file}: {e}")
        
        # Sort by timestamp and return recent ones
        recent_messages.sort(key=lambda x: x["timestamp"], reverse=True)
        return recent_messages[:limit]
    
    def export_chat_to_text(self, username, user_id, output_file=None):
        """Export user's chat history to a text file"""
        chat_files = self.get_user_chats(username, user_id)
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_username = self._sanitize_filename(str(username))
            output_file = self.base_dir / f"{safe_username}_{user_id}_export_{timestamp}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Chat Export for {username} ({user_id})\n")
            f.write("=" * 50 + "\n\n")
            
            for chat_file in chat_files:
                try:
                    with open(chat_file, 'r', encoding='utf-8') as chat_f:
                        chat_data = json.load(chat_f)
                    
                    f.write(f"Chat Session: {chat_data.get('chat_id')}\n")
                    f.write(f"Created: {chat_data.get('created_at')}\n")
                    f.write("-" * 30 + "\n")
                    
                    for msg in chat_data.get("messages", []):
                        timestamp = msg.get("timestamp", "")
                        msg_type = msg.get("message_type", "")
                        content = msg.get("content", "")
                        
                        if msg_type == "user":
                            f.write(f"[{timestamp}] User: {content}\n")
                        elif msg_type == "bot":
                            f.write(f"[{timestamp}] Bot: {content}\n")
                        elif msg_type == "system":
                            f.write(f"[{timestamp}] System: {content}\n")
                    
                    f.write("\n" + "=" * 50 + "\n\n")
                    
                except Exception as e:
                    f.write(f"Error reading chat file {chat_file}: {e}\n\n")
        
        self.logger.info(f"Chat export completed: {output_file}")
        return output_file 