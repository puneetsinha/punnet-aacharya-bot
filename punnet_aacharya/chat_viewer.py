#!/usr/bin/env python
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from chat_logger import ChatLogger

def view_user_chats(username, user_id):
    """View all chats for a specific user"""
    chat_logger = ChatLogger()
    
    print(f"\n📱 Chat History for {username} ({user_id})")
    print("=" * 60)
    
    # Get chat summary
    summary = chat_logger.get_chat_summary(username, user_id)
    
    if not summary["chats"]:
        print("❌ No chat history found for this user.")
        return
    
    print(f"📊 Total chat sessions: {summary['total_chats']}")
    print()
    
    for i, chat in enumerate(summary["chats"], 1):
        print(f"📝 Chat Session {i}:")
        print(f"   ID: {chat['chat_id']}")
        print(f"   Created: {chat['created_at']}")
        print(f"   Last Updated: {chat['last_updated']}")
        print(f"   Messages: {chat['message_count']}")
        print(f"   File: {chat['file_path']}")
        print()

def view_chat_details(chat_file_path):
    """View detailed messages from a specific chat file"""
    chat_file = Path(chat_file_path)
    
    if not chat_file.exists():
        print(f"❌ Chat file not found: {chat_file_path}")
        return
    
    print(f"\n💬 Chat Details: {chat_file.name}")
    print("=" * 60)
    
    try:
        with open(chat_file, 'r', encoding='utf-8') as f:
            chat_data = json.load(f)
        
        print(f"📅 Created: {chat_data.get('created_at')}")
        print(f"🔄 Last Updated: {chat_data.get('last_updated')}")
        print(f"💬 Total Messages: {len(chat_data.get('messages', []))}")
        print()
        
        for i, msg in enumerate(chat_data.get("messages", []), 1):
            timestamp = msg.get("timestamp", "")
            msg_type = msg.get("message_type", "")
            content = msg.get("content", "")
            
            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted_time = dt.strftime("%H:%M:%S")
            except:
                formatted_time = timestamp
            
            if msg_type == "user":
                print(f"👤 [{formatted_time}] User: {content}")
            elif msg_type == "bot":
                print(f"🤖 [{formatted_time}] Bot: {content}")
            elif msg_type == "system":
                print(f"⚙️  [{formatted_time}] System: {content}")
            
            print()
    
    except Exception as e:
        print(f"❌ Error reading chat file: {e}")

def list_all_users():
    """List all users who have chatted with the bot"""
    chat_logger = ChatLogger()
    conversations_dir = chat_logger.conversations_dir
    
    if not conversations_dir.exists():
        print("❌ No chat logs found.")
        return
    
    users = {}
    
    # Scan all chat files
    for chat_file in conversations_dir.glob("*.json"):
        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
            
            for msg in chat_data.get("messages", []):
                user_id = msg.get("user_id")
                username = msg.get("username", "unknown")
                
                if user_id and username:
                    if user_id not in users:
                        users[user_id] = {
                            "username": username,
                            "chat_files": [],
                            "total_messages": 0
                        }
                    
                    if chat_file not in users[user_id]["chat_files"]:
                        users[user_id]["chat_files"].append(chat_file)
                    
                    users[user_id]["total_messages"] += 1
        
        except Exception as e:
            print(f"⚠️  Error reading {chat_file}: {e}")
    
    if not users:
        print("❌ No users found in chat logs.")
        return
    
    print("\n👥 Users who have chatted with the bot:")
    print("=" * 60)
    
    for user_id, data in sorted(users.items()):
        print(f"👤 {data['username']} ({user_id})")
        print(f"   📝 Chat files: {len(data['chat_files'])}")
        print(f"   💬 Total messages: {data['total_messages']}")
        print()

def export_user_chat(username, user_id, output_file=None):
    """Export user's chat history to text file"""
    chat_logger = ChatLogger()
    
    try:
        output_path = chat_logger.export_chat_to_text(username, user_id, output_file)
        print(f"✅ Chat export completed: {output_path}")
    except Exception as e:
        print(f"❌ Error exporting chat: {e}")

def main():
    parser = argparse.ArgumentParser(description="Chat Viewer for Punnet Aacharya Bot")
    parser.add_argument("command", choices=["view", "list", "export", "details"], 
                       help="Command to execute")
    parser.add_argument("--username", help="Username to filter by")
    parser.add_argument("--user-id", help="User ID to filter by")
    parser.add_argument("--chat-file", help="Specific chat file to view")
    parser.add_argument("--output", help="Output file for export")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_all_users()
    
    elif args.command == "view":
        if not args.username or not args.user_id:
            print("❌ Please provide both --username and --user-id for view command")
            sys.exit(1)
        view_user_chats(args.username, args.user_id)
    
    elif args.command == "details":
        if not args.chat_file:
            print("❌ Please provide --chat-file for details command")
            sys.exit(1)
        view_chat_details(args.chat_file)
    
    elif args.command == "export":
        if not args.username or not args.user_id:
            print("❌ Please provide both --username and --user-id for export command")
            sys.exit(1)
        export_user_chat(args.username, args.user_id, args.output)

if __name__ == "__main__":
    main() 