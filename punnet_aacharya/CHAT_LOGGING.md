# Chat Logging System for Punnet Aacharya Bot

## 📁 Directory Structure

```
punnet_aacharya/
├── chat_logs/                    # Main chat logs directory
│   └── conversations/            # Individual chat files
│       ├── username_userid_date_time.json
│       └── ...
├── logs/                         # General application logs
│   └── punnet_aacharya_YYYYMMDD.log
├── chat_logger.py               # Chat logging system
├── chat_viewer.py               # Chat viewing utility
└── ...
```

## 🔍 How Chat Logging Works

### 1. **File Naming Convention**
Chat files are named using the format:
```
{username}_{user_id}_{date}_{time}.json
```

Example:
```
puneetsinh_1177573677_20250720_100823.json
```

### 2. **What Gets Logged**
- ✅ **User Messages**: All user inputs and commands
- ✅ **Bot Responses**: All bot replies and messages
- ✅ **System Events**: Chart calculations, onboarding completion, etc.
- ✅ **Metadata**: Context, message length, timestamps

### 3. **Chat File Structure**
```json
{
  "chat_id": "puneetsinh_1177573677_20250720_100823",
  "created_at": "2025-07-20T10:08:23.456789",
  "last_updated": "2025-07-20T10:15:45.123456",
  "messages": [
    {
      "timestamp": "2025-07-20T10:08:23.456789",
      "user_id": "1177573677",
      "username": "puneetsinh",
      "message_type": "user",
      "content": "/start",
      "metadata": {
        "context": "command",
        "message_length": 6
      }
    },
    {
      "timestamp": "2025-07-20T10:08:24.123456",
      "user_id": "1177573677",
      "username": "puneetsinh",
      "message_type": "bot",
      "content": "🙏 Namaste! Main hoon Punnet Guruji...",
      "metadata": {
        "context": "welcome",
        "response_length": 150
      }
    }
  ]
}
```

## 🛠️ Using the Chat Viewer

### 1. **List All Users**
```bash
python chat_viewer.py list
```
Shows all users who have chatted with the bot.

### 2. **View User's Chat History**
```bash
python chat_viewer.py view --username puneetsinh --user-id 1177573677
```
Shows summary of all chat sessions for a specific user.

### 3. **View Detailed Chat**
```bash
python chat_viewer.py details --chat-file chat_logs/conversations/puneetsinh_1177573677_20250720_100823.json
```
Shows detailed conversation with timestamps.

### 4. **Export Chat to Text**
```bash
python chat_viewer.py export --username puneetsinh --user-id 1177573677 --output my_chat.txt
```
Exports all chat history to a readable text file.

## 📊 Chat Viewer Output Examples

### List Users
```
👥 Users who have chatted with the bot:
============================================================
👤 puneetsinh (1177573677)
   📝 Chat files: 3
   💬 Total messages: 25

👤 deepak_kumar (1234567890)
   📝 Chat files: 1
   💬 Total messages: 8
```

### View User Chats
```
📱 Chat History for puneetsinh (1177573677)
============================================================
📊 Total chat sessions: 3

📝 Chat Session 1:
   ID: puneetsinh_1177573677_20250720_100823
   Created: 2025-07-20T10:08:23.456789
   Last Updated: 2025-07-20T10:15:45.123456
   Messages: 12
   File: /path/to/chat_logs/conversations/puneetsinh_1177573677_20250720_100823.json
```

### View Chat Details
```
💬 Chat Details: puneetsinh_1177573677_20250720_100823.json
============================================================
📅 Created: 2025-07-20T10:08:23.456789
🔄 Last Updated: 2025-07-20T10:15:45.123456
💬 Total Messages: 12

👤 [10:08:23] User: /start
🤖 [10:08:24] Bot: 🙏 Namaste! Main hoon Punnet Guruji...
👤 [10:08:30] User: Deepak
🤖 [10:08:32] Bot: नमस्ते Deepak जी! आपसे कुछ जानकारी लेनी होगी...
```

## 🔧 Integration with Bot

The chat logging is automatically integrated into the bot handlers:

### 1. **User Messages**
```python
# Logged automatically in handle_onboarding and handle_consultation
self.chat_logger.log_user_message(
    user.id,
    user.username or "unknown",
    user_message,
    "onboarding"  # or "consultation"
)
```

### 2. **Bot Responses**
```python
# Logged automatically after each bot response
self.chat_logger.log_bot_response(
    user.id,
    user.username or "unknown",
    response,
    "onboarding"  # or "consultation", "welcome", etc.
)
```

### 3. **System Events**
```python
# Logged for important events
self.chat_logger.log_system_event(
    user.id,
    user.username or "unknown",
    "chart_calculation_completed",
    {"chart_data": {...}}
)
```

## 📈 Benefits

1. **Complete Conversation History**: Every message is logged with context
2. **User Analysis**: Track user behavior and preferences
3. **Debugging**: Easy to trace issues and user flows
4. **Analytics**: Analyze bot performance and user satisfaction
5. **Compliance**: Maintain records for regulatory requirements
6. **Support**: Help users with their previous conversations

## 🚀 Quick Start

1. **Start the bot** (chat logging is automatic):
   ```bash
   python main.py
   ```

2. **View chat logs**:
   ```bash
   # List all users
   python chat_viewer.py list
   
   # View specific user's chats
   python chat_viewer.py view --username puneetsinh --user-id 1177573677
   
   # Export chat history
   python chat_viewer.py export --username puneetsinh --user-id 1177573677
   ```

3. **Monitor in real-time**:
   ```bash
   # Watch chat logs directory
   ls -la chat_logs/conversations/
   
   # Follow specific user's chat
   tail -f chat_logs/conversations/puneetsinh_1177573677_*.json
   ```

## 🔒 Privacy & Security

- Chat files are stored locally in JSON format
- Usernames are sanitized for filesystem safety
- No sensitive data is logged without user consent
- Chat files can be easily deleted or exported
- All timestamps are in ISO format for consistency

## 📝 Logging Contexts

The system logs different types of interactions:

- **`command`**: User commands like `/start`, `/cancel`
- **`onboarding`**: Birth details collection phase
- **`consultation`**: Astrological consultation phase
- **`welcome`**: Welcome messages
- **`error`**: Error responses
- **`system`**: System events and calculations

This comprehensive logging system ensures you can track every interaction and analyze user behavior effectively! 🎯 