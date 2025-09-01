
# FastStream Integration

Modi integrates excellently with FastStream for building event-driven applications and message brokers. This guide shows how to use Modi's dependency injection with FastStream applications.

## Installation

```bash
pip install modi faststream
# Choose your broker
pip install faststream[kafka]    # For Kafka
pip install faststream[rabbit]   # For RabbitMQ
pip install faststream[redis]    # For Redis
pip install faststream[nats]     # For NATS
```

## Basic Integration

### 1. Define Your Services

```python
from modi import injectable
import json
from typing import Dict, Any

@injectable()
class ConfigService:
    def __init__(self):
        self.config = {
            "kafka_url": "localhost:9092",
            "database_url": "postgresql://localhost/myapp",
            "debug": True
        }

    def get(self, key: str):
        return self.config.get(key)

@injectable()
class DatabaseService:
    def __init__(self, config: ConfigService):
        self.config = config
        self.url = config.get("database_url")

    def save_event(self, event_type: str, data: Dict[str, Any]):
        # Simulate saving to database
        print(f"Saving to DB: {event_type} -> {data}")
        return {"saved": True, "id": f"event_{hash(str(data))}"}

@injectable()
class UserService:
    def __init__(self, db: DatabaseService):
        self.db = db
        self.users = {}

    def create_user(self, user_data: Dict[str, Any]):
        user_id = user_data.get("id")
        self.users[user_id] = user_data

        # Save to database
        self.db.save_event("user_created", user_data)

        return user_data

    def update_user(self, user_id: str, updates: Dict[str, Any]):
        if user_id in self.users:
            self.users[user_id].update(updates)
            self.db.save_event("user_updated", {"id": user_id, "updates": updates})
            return self.users[user_id]
        return None

@injectable()
class NotificationService:
    def __init__(self, config: ConfigService):
        self.config = config

    def send_notification(self, user_id: str, message: str, channel: str = "email"):
        # Simulate sending notification
        print(f"Sending {channel} notification to {user_id}: {message}")
        return {"sent": True, "channel": channel, "user_id": user_id}

@injectable()
class EmailService:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def send_welcome_email(self, user_data: Dict[str, Any]):
        return self.notification_service.send_notification(
            user_id=user_data["id"],
            message=f"Welcome {user_data['name']}!",
            channel="email"
        )

    def send_update_email(self, user_id: str, changes: Dict[str, Any]):
        return self.notification_service.send_notification(
            user_id=user_id,
            message=f"Your profile was updated: {list(changes.keys())}",
            channel="email"
        )
```

### 2. Create Event Handlers

```python
@injectable()
class UserEventHandler:
    def __init__(self, user_service: UserService, email_service: EmailService):
        self.user_service = user_service
        self.email_service = email_service

    def handle_user_created(self, message: Dict[str, Any]):
        """Handle user creation events"""
        user_data = message.get("user", {})

        # Create user in our system
        created_user = self.user_service.create_user(user_data)

        # Send welcome email
        self.email_service.send_welcome_email(created_user)

        return {"status": "processed", "user_id": user_data.get("id")}

    def handle_user_updated(self, message: Dict[str, Any]):
        """Handle user update events"""
        user_id = message.get("user_id")
        updates = message.get("updates", {})

        # Update user
        updated_user = self.user_service.update_user(user_id, updates)

        if updated_user:
            # Send update notification
            self.email_service.send_update_email(user_id, updates)
            return {"status": "processed", "user_id": user_id}

        return {"status": "user_not_found", "user_id": user_id}

@injectable()
class AnalyticsHandler:
    def __init__(self, db: DatabaseService):
        self.db = db

    def track_event(self, event_type: str, data: Dict[str, Any]):
        """Track analytics events"""
        analytics_data = {
            "event_type": event_type,
            "timestamp": data.get("timestamp"),
            "user_id": data.get("user_id"),
            "properties": data.get("properties", {})
        }

        return self.db.save_event("analytics_tracked", analytics_data)
```

### 3. Define Modules

```python
from modi import module

@module(providers=[
    ConfigService,
    DatabaseService,
    UserService,
    NotificationService,
    EmailService,
    UserEventHandler,
    AnalyticsHandler
])
class AppModule:
    pass
```

### 4. Create FastStream Application

```python
from faststream import FastStream
from faststream.kafka import KafkaBroker
from modi import AppFactory
import json

# Create Modi application
modi_app = AppFactory.create(AppModule)

# Get configuration
config_service = modi_app.get(ConfigService)
kafka_url = config_service.get("kafka_url")

# Create FastStream app with Kafka broker
broker = KafkaBroker(kafka_url)
app = FastStream(broker)

# Get handlers from Modi DI
user_handler = modi_app.get(UserEventHandler)
analytics_handler = modi_app.get(AnalyticsHandler)

@broker.subscriber("user.created")
async def handle_user_created(message: Dict[str, Any]):
    """Handle user creation events from Kafka"""
    try:
        result = user_handler.handle_user_created(message)
        print(f"User created: {result}")
        return result
    except Exception as e:
        print(f"Error handling user created: {e}")
        raise

@broker.subscriber("user.updated")
async def handle_user_updated(message: Dict[str, Any]):
    """Handle user update events from Kafka"""
    try:
        result = user_handler.handle_user_updated(message)
        print(f"User updated: {result}")
        return result
    except Exception as e:
        print(f"Error handling user updated: {e}")
        raise

@broker.subscriber("analytics.track")
async def handle_analytics(message: Dict[str, Any]):
    """Handle analytics tracking events"""
    try:
        result = analytics_handler.track_event(
            event_type=message.get("event"),
            data=message
        )
        print(f"Analytics tracked: {result}")
        return result
    except Exception as e:
        print(f"Error handling analytics: {e}")
        raise

# Publisher endpoints for testing
@broker.publisher("user.profile.updated")
async def publish_profile_update():
    pass

@app.after_startup
async def startup():
    print("🚀 FastStream + Modi application started!")
    print(f"📊 Available services: {len(modi_app.container._provider_configs)} providers")

if __name__ == "__main__":
    app.run()
```

## Advanced Patterns

### Event Sourcing with Modi

```python
from datetime import datetime
from typing import List

@injectable()
class EventStore:
    def __init__(self, db: DatabaseService):
        self.db = db
        self.events = []

    def append_event(self, stream_id: str, event_type: str, event_data: Dict[str, Any]):
        event = {
            "stream_id": stream_id,
            "event_type": event_type,
            "event_data": event_data,
            "timestamp": datetime.utcnow().isoformat(),
            "version": len([e for e in self.events if e["stream_id"] == stream_id]) + 1
        }

        self.events.append(event)
        self.db.save_event("event_stored", event)
        return event

    def get_events(self, stream_id: str) -> List[Dict[str, Any]]:
        return [e for e in self.events if e["stream_id"] == stream_id]

@injectable()
class UserAggregate:
    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    def create_user(self, user_id: str, name: str, email: str):
        event_data = {"user_id": user_id, "name": name, "email": email}
        return self.event_store.append_event(
            stream_id=f"user-{user_id}",
            event_type="UserCreated",
            event_data=event_data
        )

    def update_user_email(self, user_id: str, new_email: str):
        event_data = {"user_id": user_id, "new_email": new_email}
        return self.event_store.append_event(
            stream_id=f"user-{user_id}",
            event_type="UserEmailUpdated",
            event_data=event_data
        )

    def get_user_state(self, user_id: str) -> Dict[str, Any]:
        events = self.event_store.get_events(f"user-{user_id}")

        state = {}
        for event in events:
            if event["event_type"] == "UserCreated":
                state.update(event["event_data"])
            elif event["event_type"] == "UserEmailUpdated":
                state["email"] = event["event_data"]["new_email"]

        return state
```

### Message Processing Pipeline

```python
@injectable()
class MessageValidator:
    def validate_user_message(self, message: Dict[str, Any]) -> bool:
        required_fields = ["user_id", "action"]
        return all(field in message for field in required_fields)

    def validate_analytics_message(self, message: Dict[str, Any]) -> bool:
        required_fields = ["event", "timestamp"]
        return all(field in message for field in required_fields)

@injectable()
class MessageTransformer:
    def transform_legacy_user_format(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Transform legacy user message format to new format"""
        if "userId" in message:  # Legacy format
            message["user_id"] = message.pop("userId")
        if "userName" in message:
            message["name"] = message.pop("userName")
        return message

@injectable()
class MessageProcessor:
    def __init__(
        self,
        validator: MessageValidator,
        transformer: MessageTransformer,
        user_handler: UserEventHandler
    ):
        self.validator = validator
        self.transformer = transformer
        self.user_handler = user_handler

    def process_user_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # Transform legacy format
        transformed = self.transformer.transform_legacy_user_format(message)

        # Validate
        if not self.validator.validate_user_message(transformed):
            raise ValueError("Invalid message format")

        # Process based on action
        action = transformed.get("action")
        if action == "create":
            return self.user_handler.handle_user_created(transformed)
        elif action == "update":
            return self.user_handler.handle_user_updated(transformed)
        else:
            raise ValueError(f"Unknown action: {action}")
```

### Multi-Broker Support

```python
from faststream.kafka import KafkaBroker
from faststream.rabbit import RabbitBroker

@injectable()
class BrokerFactory:
    def __init__(self, config: ConfigService):
        self.config = config

    def create_kafka_broker(self):
        return KafkaBroker(self.config.get("kafka_url"))

    def create_rabbit_broker(self):
        return RabbitBroker(self.config.get("rabbitmq_url"))

# Create multiple FastStream apps
kafka_broker = modi_app.get(BrokerFactory).create_kafka_broker()
rabbit_broker = modi_app.get(BrokerFactory).create_rabbit_broker()

kafka_app = FastStream(kafka_broker)
rabbit_app = FastStream(rabbit_broker)

# Kafka handlers
@kafka_broker.subscriber("user.events")
async def handle_user_events(message: Dict[str, Any]):
    processor = modi_app.get(MessageProcessor)
    return processor.process_user_message(message)

# RabbitMQ handlers
@rabbit_broker.subscriber("notifications")
async def handle_notifications(message: Dict[str, Any]):
    notification_service = modi_app.get(NotificationService)
    return notification_service.send_notification(
        user_id=message["user_id"],
        message=message["content"],
        channel=message.get("channel", "email")
    )
```

## Complete Example: Order Processing System

```python
from faststream import FastStream
from faststream.kafka import KafkaBroker
from modi import injectable, module, AppFactory
from typing import Dict, Any, List
import json
from datetime import datetime

# Domain Services
@injectable()
class OrderService:
    def __init__(self, db: DatabaseService):
        self.db = db
        self.orders = {}

    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        order_id = order_data["id"]
        order = {
            **order_data,
            "status": "created",
            "created_at": datetime.utcnow().isoformat()
        }

        self.orders[order_id] = order
        self.db.save_event("order_created", order)
        return order

    def update_order_status(self, order_id: str, status: str) -> Dict[str, Any]:
        if order_id in self.orders:
            self.orders[order_id]["status"] = status
            self.orders[order_id]["updated_at"] = datetime.utcnow().isoformat()

            self.db.save_event("order_status_updated", {
                "order_id": order_id,
                "status": status
            })

            return self.orders[order_id]
        return None

@injectable()
class InventoryService:
    def __init__(self, db: DatabaseService):
        self.db = db
        self.inventory = {
            "product_1": 100,
            "product_2": 50,
            "product_3": 25
        }

    def check_availability(self, product_id: str, quantity: int) -> bool:
        return self.inventory.get(product_id, 0) >= quantity

    def reserve_inventory(self, product_id: str, quantity: int) -> bool:
        if self.check_availability(product_id, quantity):
            self.inventory[product_id] -= quantity
            self.db.save_event("inventory_reserved", {
                "product_id": product_id,
                "quantity": quantity,
                "remaining": self.inventory[product_id]
            })
            return True
        return False

@injectable()
class PaymentService:
    def __init__(self, db: DatabaseService):
        self.db = db

    def process_payment(self, order_id: str, amount: float) -> Dict[str, Any]:
        # Simulate payment processing
        success = amount > 0  # Simple validation

        result = {
            "order_id": order_id,
            "amount": amount,
            "success": success,
            "transaction_id": f"txn_{hash(order_id)}" if success else None
        }

        self.db.save_event("payment_processed", result)
        return result

# Event Handlers
@injectable()
class OrderEventHandler:
    def __init__(
        self,
        order_service: OrderService,
        inventory_service: InventoryService,
        payment_service: PaymentService
    ):
        self.order_service = order_service
        self.inventory_service = inventory_service
        self.payment_service = payment_service

    def handle_order_created(self, message: Dict[str, Any]) -> Dict[str, Any]:
        order_data = message["order"]

        # Create order
        order = self.order_service.create_order(order_data)

        # Check inventory
        product_id = order_data["product_id"]
        quantity = order_data["quantity"]

        if not self.inventory_service.check_availability(product_id, quantity):
            self.order_service.update_order_status(order["id"], "inventory_unavailable")
            return {"status": "failed", "reason": "insufficient_inventory"}

        # Reserve inventory
        if self.inventory_service.reserve_inventory(product_id, quantity):
            self.order_service.update_order_status(order["id"], "inventory_reserved")
            return {"status": "inventory_reserved", "order_id": order["id"]}

        return {"status": "failed", "reason": "reservation_failed"}

    def handle_payment_requested(self, message: Dict[str, Any]) -> Dict[str, Any]:
        order_id = message["order_id"]
        amount = message["amount"]

        # Process payment
        payment_result = self.payment_service.process_payment(order_id, amount)

        if payment_result["success"]:
            self.order_service.update_order_status(order_id, "paid")
            return {"status": "payment_successful", "order_id": order_id}
        else:
            self.order_service.update_order_status(order_id, "payment_failed")
            return {"status": "payment_failed", "order_id": order_id}

# Module
@module(providers=[
    ConfigService,
    DatabaseService,
    OrderService,
    InventoryService,
    PaymentService,
    OrderEventHandler
])
class OrderModule:
    pass

# FastStream Application
modi_app = AppFactory.create(OrderModule)
config = modi_app.get(ConfigService)

broker = KafkaBroker(config.get("kafka_url"))
app = FastStream(broker)

order_handler = modi_app.get(OrderEventHandler)

@broker.subscriber("orders.created")
async def handle_order_created(message: Dict[str, Any]):
    try:
        result = order_handler.handle_order_created(message)
        print(f"Order created: {result}")

        # If inventory reserved, request payment
        if result.get("status") == "inventory_reserved":
            await broker.publish(
                {
                    "order_id": result["order_id"],
                    "amount": message["order"]["total_amount"]
                },
                topic="payments.requested"
            )

        return result
    except Exception as e:
        print(f"Error handling order created: {e}")
        raise

@broker.subscriber("payments.requested")
async def handle_payment_requested(message: Dict[str, Any]):
    try:
        result = order_handler.handle_payment_requested(message)
        print(f"Payment processed: {result}")

        # Publish order completion event
        if result.get("status") == "payment_successful":
            await broker.publish(
                {"order_id": result["order_id"]},
                topic="orders.completed"
            )

        return result
    except Exception as e:
        print(f"Error handling payment: {e}")
        raise

@broker.subscriber("orders.completed")
async def handle_order_completed(message: Dict[str, Any]):
    try:
        order_id = message["order_id"]
        order_service = modi_app.get(OrderService)

        # Mark order as completed
        order_service.update_order_status(order_id, "completed")

        print(f"Order {order_id} completed successfully!")
        return {"status": "completed", "order_id": order_id}
    except Exception as e:
        print(f"Error completing order: {e}")
        raise

if __name__ == "__main__":
    app.run()
```

## Testing FastStream + Modi Applications

```python
import pytest
from faststream.testing import TestClient

@pytest.fixture
def modi_app():
    return AppFactory.create(OrderModule)

@pytest.fixture
def test_broker():
    return KafkaBroker()

async def test_order_processing(modi_app, test_broker):
    async with TestClient(test_broker) as client:
        # Test order creation
        order_message = {
            "order": {
                "id": "order_123",
                "product_id": "product_1",
                "quantity": 2,
                "total_amount": 99.99
            }
        }

        # Publish test message
        await client.publish(order_message, topic="orders.created")

        # Verify message was processed
        messages = await client.get_messages("payments.requested")
        assert len(messages) == 1

        payment_message = messages[0]
        assert payment_message["order_id"] == "order_123"
        assert payment_message["amount"] == 99.99

def test_order_service_directly(modi_app):
    # Test Modi services directly
    order_service = modi_app.get(OrderService)
    inventory_service = modi_app.get(InventoryService)

    # Test inventory check
    assert inventory_service.check_availability("product_1", 10) == True
    assert inventory_service.check_availability("product_1", 1000) == False

    # Test order creation
    order_data = {
        "id": "test_order",
        "product_id": "product_2",
        "quantity": 1
    }

    order = order_service.create_order(order_data)
    assert order["status"] == "created"
    assert order["id"] == "test_order"
```

## Best Practices

1. **Separate Business Logic**: Keep business logic in Modi services, use FastStream only for message handling
2. **Use Type Hints**: Leverage Python type hints for both Modi DI and FastStream message schemas
3. **Error Handling**: Implement proper error handling in message handlers
4. **Testing**: Test Modi services independently from message brokers
5. **Configuration**: Use Modi's ConfigService for centralized configuration
6. **Monitoring**: Add logging and metrics to track message processing
7. **Idempotency**: Make message handlers idempotent when possible
8. **Dead Letter Queues**: Implement DLQ patterns for failed messages
