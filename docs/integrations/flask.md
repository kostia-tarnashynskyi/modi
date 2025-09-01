
# Flask Integration

Modi integrates well with Flask applications, providing dependency injection for your services while working alongside Flask's native patterns. This guide shows how to structure Flask applications using Modi DI.

## Installation

```bash
pip install modi flask
```

## Basic Integration

### 1. Define Your Services

```python
from modi import injectable
import sqlite3
from typing import Dict, Any, List, Optional

@injectable()
class ConfigService:
    def __init__(self):
        self.config = {
            "database_path": "app.db",
            "secret_key": "dev-secret-key",
            "debug": True,
            "mail_server": "localhost",
            "mail_port": 587
        }

    def get(self, key: str, default=None):
        return self.config.get(key, default)

@injectable()
class DatabaseService:
    def __init__(self, config: ConfigService):
        self.config = config
        self.db_path = config.get("database_path")
        self._init_db()

    def _init_db(self):
        """Initialize database with tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            conn.commit()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

@injectable()
class UserService:
    def __init__(self, db: DatabaseService):
        self.db = db

    def create_user(self, name: str, email: str) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (name, email)
            )
            user_id = cursor.lastrowid
            conn.commit()

            return self.get_user(user_id)

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, name, email, created_at FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()

            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "created_at": row[3]
                }
            return None

    def get_all_users(self) -> List[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, name, email, created_at FROM users ORDER BY created_at DESC"
            )

            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "created_at": row[3]
                }
                for row in cursor.fetchall()
            ]

    def update_user(self, user_id: int, name: str = None, email: str = None) -> Optional[Dict[str, Any]]:
        updates = []
        params = []

        if name:
            updates.append("name = ?")
            params.append(name)
        if email:
            updates.append("email = ?")
            params.append(email)

        if not updates:
            return self.get_user(user_id)

        params.append(user_id)

        with self.db.get_connection() as conn:
            conn.execute(
                f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
                params
            )
            conn.commit()

            return self.get_user(user_id)

    def delete_user(self, user_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0

@injectable()
class PostService:
    def __init__(self, db: DatabaseService):
        self.db = db

    def create_post(self, title: str, content: str, user_id: int) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
                (title, content, user_id)
            )
            post_id = cursor.lastrowid
            conn.commit()

            return self.get_post(post_id)

    def get_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT p.id, p.title, p.content, p.user_id, p.created_at,
                       u.name as author_name, u.email as author_email
                FROM posts p
                JOIN users u ON p.user_id = u.id
                WHERE p.id = ?
            ''', (post_id,))

            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "title": row[1],
                    "content": row[2],
                    "user_id": row[3],
                    "created_at": row[4],
                    "author": {
                        "name": row[5],
                        "email": row[6]
                    }
                }
            return None

    def get_all_posts(self) -> List[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT p.id, p.title, p.content, p.user_id, p.created_at,
                       u.name as author_name, u.email as author_email
                FROM posts p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.created_at DESC
            ''')

            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "content": row[2],
                    "user_id": row[3],
                    "created_at": row[4],
                    "author": {
                        "name": row[5],
                        "email": row[6]
                    }
                }
                for row in cursor.fetchall()
            ]

    def get_posts_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT p.id, p.title, p.content, p.user_id, p.created_at,
                       u.name as author_name, u.email as author_email
                FROM posts p
                JOIN users u ON p.user_id = u.id
                WHERE p.user_id = ?
                ORDER BY p.created_at DESC
            ''', (user_id,))

            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "content": row[2],
                    "user_id": row[3],
                    "created_at": row[4],
                    "author": {
                        "name": row[5],
                        "email": row[6]
                    }
                }
                for row in cursor.fetchall()
            ]

@injectable()
class EmailService:
    def __init__(self, config: ConfigService):
        self.config = config
        self.mail_server = config.get("mail_server")
        self.mail_port = config.get("mail_port")

    def send_email(self, to: str, subject: str, body: str) -> bool:
        # Simulate sending email
        print(f"Sending email to {to}")
        print(f"Subject: {subject}")
        print(f"Body: {body[:100]}...")
        return True

    def send_welcome_email(self, user: Dict[str, Any]) -> bool:
        return self.send_email(
            to=user["email"],
            subject="Welcome!",
            body=f"Welcome to our platform, {user['name']}!"
        )

    def send_post_notification(self, post: Dict[str, Any], recipients: List[str]) -> bool:
        for email in recipients:
            self.send_email(
                to=email,
                subject=f"New post: {post['title']}",
                body=f"A new post '{post['title']}' has been published by {post['author']['name']}"
            )
        return True
```

### 2. Define Modules

```python
from modi import module

@module(providers=[
    ConfigService,
    DatabaseService,
    UserService,
    PostService,
    EmailService
])
class AppModule:
    pass
```

### 3. Create Flask Application

```python
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from modi import AppFactory
from werkzeug.exceptions import NotFound, BadRequest

def create_app():
    # Create Modi application
    modi_app = AppFactory.create(AppModule)

    # Get config service
    config_service = modi_app.get(ConfigService)

    # Create Flask application
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config_service.get("secret_key")
    app.config["DEBUG"] = config_service.get("debug")

    # Store Modi app in Flask app context
    app.modi_app = modi_app

    # Helper function to get services
    def get_service(service_class):
        return app.modi_app.get(service_class)

    # Routes
    @app.route('/')
    def index():
        post_service = get_service(PostService)
        posts = post_service.get_all_posts()
        return render_template('index.html', posts=posts)

    @app.route('/users')
    def users():
        user_service = get_service(UserService)
        users = user_service.get_all_users()
        return render_template('users.html', users=users)

    @app.route('/users/<int:user_id>')
    def user_detail(user_id):
        user_service = get_service(UserService)
        post_service = get_service(PostService)

        user = user_service.get_user(user_id)
        if not user:
            raise NotFound("User not found")

        posts = post_service.get_posts_by_user(user_id)
        return render_template('user_detail.html', user=user, posts=posts)

    @app.route('/posts/<int:post_id>')
    def post_detail(post_id):
        post_service = get_service(PostService)
        post = post_service.get_post(post_id)

        if not post:
            raise NotFound("Post not found")

        return render_template('post_detail.html', post=post)

    # API Routes
    @app.route('/api/users', methods=['GET'])
    def api_get_users():
        user_service = get_service(UserService)
        users = user_service.get_all_users()
        return jsonify({"users": users})

    @app.route('/api/users', methods=['POST'])
    def api_create_user():
        data = request.get_json()

        if not data or 'name' not in data or 'email' not in data:
            raise BadRequest("Name and email are required")

        user_service = get_service(UserService)
        email_service = get_service(EmailService)

        try:
            user = user_service.create_user(data['name'], data['email'])

            # Send welcome email
            email_service.send_welcome_email(user)

            return jsonify({"user": user}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/api/users/<int:user_id>', methods=['GET'])
    def api_get_user(user_id):
        user_service = get_service(UserService)
        user = user_service.get_user(user_id)

        if not user:
            raise NotFound("User not found")

        return jsonify({"user": user})

    @app.route('/api/users/<int:user_id>', methods=['PUT'])
    def api_update_user(user_id):
        data = request.get_json()
        user_service = get_service(UserService)

        user = user_service.update_user(
            user_id,
            name=data.get('name'),
            email=data.get('email')
        )

        if not user:
            raise NotFound("User not found")

        return jsonify({"user": user})

    @app.route('/api/users/<int:user_id>', methods=['DELETE'])
    def api_delete_user(user_id):
        user_service = get_service(UserService)

        if user_service.delete_user(user_id):
            return '', 204
        else:
            raise NotFound("User not found")

    @app.route('/api/posts', methods=['GET'])
    def api_get_posts():
        post_service = get_service(PostService)
        posts = post_service.get_all_posts()
        return jsonify({"posts": posts})

    @app.route('/api/posts', methods=['POST'])
    def api_create_post():
        data = request.get_json()

        required_fields = ['title', 'content', 'user_id']
        if not data or not all(field in data for field in required_fields):
            raise BadRequest("Title, content, and user_id are required")

        post_service = get_service(PostService)
        user_service = get_service(UserService)
        email_service = get_service(EmailService)

        # Verify user exists
        user = user_service.get_user(data['user_id'])
        if not user:
            raise BadRequest("User not found")

        try:
            post = post_service.create_post(
                data['title'],
                data['content'],
                data['user_id']
            )

            # Notify other users (simplified - get all other users)
            all_users = user_service.get_all_users()
            other_emails = [u['email'] for u in all_users if u['id'] != data['user_id']]

            if other_emails:
                email_service.send_post_notification(post, other_emails)

            return jsonify({"post": post}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/api/posts/<int:post_id>', methods=['GET'])
    def api_get_post(post_id):
        post_service = get_service(PostService)
        post = post_service.get_post(post_id)

        if not post:
            raise NotFound("Post not found")

        return jsonify({"post": post})

    # Form handling routes
    @app.route('/create-user', methods=['GET', 'POST'])
    def create_user_form():
        if request.method == 'GET':
            return render_template('create_user.html')

        # POST request
        user_service = get_service(UserService)
        email_service = get_service(EmailService)

        try:
            user = user_service.create_user(
                request.form['name'],
                request.form['email']
            )

            email_service.send_welcome_email(user)
            flash('User created successfully!', 'success')
            return redirect(url_for('user_detail', user_id=user['id']))

        except Exception as e:
            flash(f'Error creating user: {e}', 'error')
            return render_template('create_user.html')

    @app.route('/create-post', methods=['GET', 'POST'])
    def create_post_form():
        user_service = get_service(UserService)
        users = user_service.get_all_users()

        if request.method == 'GET':
            return render_template('create_post.html', users=users)

        # POST request
        post_service = get_service(PostService)
        email_service = get_service(EmailService)

        try:
            post = post_service.create_post(
                request.form['title'],
                request.form['content'],
                int(request.form['user_id'])
            )

            # Send notifications
            all_users = user_service.get_all_users()
            other_emails = [u['email'] for u in all_users if u['id'] != int(request.form['user_id'])]

            if other_emails:
                email_service.send_post_notification(post, other_emails)

            flash('Post created successfully!', 'success')
            return redirect(url_for('post_detail', post_id=post['id']))

        except Exception as e:
            flash(f'Error creating post: {e}', 'error')
            return render_template('create_post.html', users=users)

    # Health check
    @app.route('/health')
    def health():
        try:
            # Test database connection
            db_service = get_service(DatabaseService)
            with db_service.get_connection():
                pass

            return jsonify({
                "status": "healthy",
                "framework": "Flask + Modi DI",
                "services": list(app.modi_app.container._provider_configs.keys().__len__())
            })
        except Exception as e:
            return jsonify({
                "status": "unhealthy",
                "error": str(e)
            }), 500

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({"error": "Not found"}), 404
        return render_template('404.html'), 404

    @app.errorhandler(400)
    def bad_request(error):
        if request.path.startswith('/api/'):
            return jsonify({"error": str(error)}), 400
        flash(str(error), 'error')
        return redirect(url_for('index'))

    return app

# Application factory
def main():
    app = create_app()

    # Get config from Modi DI
    config_service = app.modi_app.get(ConfigService)
    debug = config_service.get("debug", False)

    app.run(debug=debug, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
```

## HTML Templates

Create a `templates` directory with the following files:

### base.html

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Flask + Modi Demo</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        margin: 20px;
      }
      .nav {
        margin-bottom: 20px;
      }
      .nav a {
        margin-right: 10px;
        padding: 5px 10px;
        text-decoration: none;
        background: #007bff;
        color: white;
        border-radius: 3px;
      }
      .flash-messages div {
        padding: 10px;
        margin: 10px 0;
        border-radius: 3px;
      }
      .flash-success {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
      }
      .flash-error {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
      }
      .post,
      .user {
        border: 1px solid #ddd;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
      }
      .post h3,
      .user h3 {
        margin-top: 0;
      }
      .meta {
        color: #666;
        font-size: 0.9em;
      }
    </style>
  </head>
  <body>
    <div class="nav">
      <a href="/">Home</a>
      <a href="/users">Users</a>
      <a href="/create-user">Create User</a>
      <a href="/create-post">Create Post</a>
      <a href="/health">Health</a>
    </div>

    <div class="flash-messages">
      {% raw %}{% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %} {% for category, message in messages %}
      <div class="flash-{{ category }}">{{ message }}</div>
      {% endfor %} {% endif %} {% endwith %}{% endraw %}
    </div>

    {% raw %}{% block content %}{% endblock %}{% endraw %}
  </body>
</html>
```

### index.html

```html
{% raw %} {% extends "base.html" %} {% block content %}
<h1>Recent Posts</h1>

{% for post in posts %}
<div class="post">
  <h3><a href="/posts/{{ post.id }}">{{ post.title }}</a></h3>
  <p>
    {{ post.content[:200] }}{% if post.content|length > 200 %}...{% endif %}
  </p>
  <div class="meta">
    By <a href="/users/{{ post.user_id }}">{{ post.author.name }}</a>
    on {{ post.created_at }}
  </div>
</div>
{% endfor %} {% if not posts %}
<p>No posts yet. <a href="/create-post">Create the first post!</a></p>
{% endif %} {% endblock %} {% endraw %}
```

## Flask Blueprints with Modi

```python
# blueprints/api.py
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import NotFound, BadRequest
from modi import AppFactory

def create_api_blueprint(modi_app):
    api = Blueprint('api', __name__, url_prefix='/api/v1')

    def get_service(service_class):
        return modi_app.get(service_class)

    @api.route('/users', methods=['GET'])
    def get_users():
        user_service = get_service(UserService)
        users = user_service.get_all_users()
        return jsonify({
            "users": users,
            "count": len(users)
        })

    @api.route('/users', methods=['POST'])
    def create_user():
        data = request.get_json()

        if not data or 'name' not in data or 'email' not in data:
            raise BadRequest("Name and email are required")

        user_service = get_service(UserService)

        try:
            user = user_service.create_user(data['name'], data['email'])
            return jsonify({"user": user}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @api.route('/posts', methods=['GET'])
    def get_posts():
        post_service = get_service(PostService)
        user_id = request.args.get('user_id', type=int)

        if user_id:
            posts = post_service.get_posts_by_user(user_id)
        else:
            posts = post_service.get_all_posts()

        return jsonify({
            "posts": posts,
            "count": len(posts)
        })

    return api

# Usage in main app
def create_app():
    modi_app = AppFactory.create(AppModule)
    app = Flask(__name__)

    # Register blueprints
    api_blueprint = create_api_blueprint(modi_app)
    app.register_blueprint(api_blueprint)

    return app
```

## Testing Flask + Modi Applications

```python
# test_app.py
import pytest
import json
from app import create_app, AppModule
from modi import AppFactory

@pytest.fixture
def modi_app():
    return AppFactory.create(AppModule)

@pytest.fixture
def app(modi_app):
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_create_user_api(client):
    user_data = {
        "name": "Test User",
        "email": "test@example.com"
    }

    response = client.post(
        '/api/users',
        data=json.dumps(user_data),
        content_type='application/json'
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['user']['name'] == 'Test User'
    assert data['user']['email'] == 'test@example.com'

def test_get_users_api(client):
    response = client.get('/api/users')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'users' in data

def test_dependency_injection(modi_app):
    # Test Modi services directly
    user_service = modi_app.get(UserService)
    db_service = modi_app.get(DatabaseService)

    # Test that UserService has DatabaseService injected
    assert user_service.db is db_service

def test_post_creation(client):
    # First create a user
    user_data = {
        "name": "Author",
        "email": "author@example.com"
    }

    user_response = client.post(
        '/api/users',
        data=json.dumps(user_data),
        content_type='application/json'
    )

    user = json.loads(user_response.data)['user']

    # Then create a post
    post_data = {
        "title": "Test Post",
        "content": "This is a test post.",
        "user_id": user['id']
    }

    post_response = client.post(
        '/api/posts',
        data=json.dumps(post_data),
        content_type='application/json'
    )

    assert post_response.status_code == 201
    post = json.loads(post_response.data)['post']
    assert post['title'] == 'Test Post'
    assert post['author']['name'] == 'Author'
```

## Production Configuration

```python
# config.py
import os
from modi import injectable

@injectable()
class ProductionConfigService:
    def __init__(self):
        self.config = {
            "database_path": os.getenv("DATABASE_PATH", "production.db"),
            "secret_key": os.getenv("SECRET_KEY") or self._generate_secret_key(),
            "debug": os.getenv("FLASK_DEBUG", "false").lower() == "true",
            "mail_server": os.getenv("MAIL_SERVER", "smtp.gmail.com"),
            "mail_port": int(os.getenv("MAIL_PORT", "587")),
            "mail_username": os.getenv("MAIL_USERNAME"),
            "mail_password": os.getenv("MAIL_PASSWORD")
        }

    def _generate_secret_key(self):
        import secrets
        return secrets.token_hex(16)

    def get(self, key: str, default=None):
        return self.config.get(key, default)

# wsgi.py for production deployment
from app import create_app

application = create_app()

if __name__ == "__main__":
    application.run()
```

## Best Practices

1. **Service Layer**: Keep business logic in Modi services, not in Flask routes
2. **Dependency Access**: Store Modi app in Flask app context for easy service access
3. **Error Handling**: Implement proper error handlers for both API and web routes
4. **Testing**: Test Modi services independently from Flask routing
5. **Configuration**: Use Modi's ConfigService for centralized configuration
6. **Blueprints**: Use Flask blueprints for large applications with Modi service injection
7. **Database**: Use connection-per-request pattern with proper cleanup
8. **Security**: Don't expose sensitive configuration in API responses
