# PAIN — AI-Powered Real-Time Chat Application

A full-stack real-time chat application built with Django, Django Channels, and WebSockets, enhanced with an integrated AI assistant powered by Groq's LLaMA models.

## Features

### 💬 Real-Time Messaging
- Instant one-on-one conversations powered by WebSockets (Django Channels)
- Messages are delivered live with no page refresh required
- Persistent chat history stored in MySQL

### 🔐 Authentication & Security
- Email-based registration and login
- Strong password validation using Django's built-in validators
- Duplicate email protection
- Session-based authentication with `@login_required` protection on all sensitive views
- Users can only access their own conversations (participant-based access control)

### 👥 Multi-User Chat System
- Open messaging — any registered user can start a conversation with any other user
- Conversations are created automatically on first message
- Inbox view showing all active conversations with last-message previews
- Permanent chat deletion (removes conversation and all messages for both participants)

### 🤖 AI Assistant
- Dedicated AI chat page accessible from the navbar
- Powered by Groq's LLaMA 3.3 70B model for fast inference
- Maintains conversation context/history per user
- Ask questions, get explanations, or have general conversations

### 📝 AI Chat Summarization
- Summarize any past conversation by selecting a specific date
- AI generates a concise summary of that day's messages
- Scoped strictly to conversations the requesting user is a participant in

### 🎨 Modern UI/UX
- Clean, Apple/ChatGPT-inspired design
- Responsive navbar with mobile hamburger menu
- Glassmorphism effects, smooth animations, and gradient glows
- Custom-styled chat bubbles, floating cards, and AI assistant window

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.0 |
| Real-time | Django Channels, Daphne (ASGI) |
| Database | MySQL |
| AI | Groq API (LLaMA 3.3 70B) |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Auth | Django's built-in auth system (customized) |

## Project Structure

```
main/
├── chat/           # One-to-one messaging app (models, consumers, views)
├── user/           # Authentication, profiles
├── ai_app/         # AI assistant + chat summarization
├── main/           # Project settings, ASGI config, root URLs
├── templates/       # Shared base template
└── manage.py
```

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd main
```

### 2. Create a virtual environment
```bash
python -m venv myenv
myenv\Scripts\activate      # Windows
source myenv/bin/activate   # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up MySQL database
```sql
CREATE DATABASE chatapp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Create a `.env` file in the project root
```
SECRET_KEY=your-django-secret-key
DEBUG=True
DB_NAME=chatapp_db
DB_USER=your-mysql-user
DB_PASSWORD=your-mysql-password
DB_HOST=localhost
DB_PORT=3306
GROQ_API_KEY=your-groq-api-key
```

### 6. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a superuser (optional, for admin access)
```bash
python manage.py createsuperuser
```

### 8. Run the development server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## Key Design Decisions

- **In-memory channel layer for local development** — avoids Windows-specific async Redis connectivity issues; swap to `channels_redis` for production/multi-process deployments.
- **Security-first data access** — every AI-related query (chat summarization, general assistant) is scoped to `request.user`, preventing cross-user data leakage.
- **Environment-based configuration** — all secrets (DB credentials, API keys, Django secret key) are loaded via `python-decouple` from a `.env` file, never hardcoded.

## Future Improvements

- Email verification on signup
- Group chat support
- Typing indicators and read receipts
- Online/offline presence indicators

## License

This project is open for personal and educational use.
