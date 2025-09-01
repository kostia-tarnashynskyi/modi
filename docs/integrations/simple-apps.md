
# Simple Python Applications

Modi works excellently with simple Python applications, CLIs, scripts, and console applications. This guide shows how to structure and organize your Python projects using Modi's dependency injection.

## Installation

```bash
pip install modi
```

## Basic Console Application

### Simple Script Structure

```python
# main.py
from modi import injectable, module, AppFactory
import sys
from typing import List, Optional

@injectable()
class ConfigService:
    def __init__(self):
        self.config = {
            "log_level": "INFO",
            "output_format": "json",
            "max_items": 100
        }

    def get(self, key: str, default=None):
        return self.config.get(key, default)

@injectable()
class LoggerService:
    def __init__(self, config: ConfigService):
        self.config = config
        self.level = config.get("log_level", "INFO")

    def info(self, message: str):
        if self.level in ["INFO", "DEBUG"]:
            print(f"[INFO] {message}")

    def error(self, message: str):
        print(f"[ERROR] {message}")

    def debug(self, message: str):
        if self.level == "DEBUG":
            print(f"[DEBUG] {message}")

@injectable()
class FileService:
    def __init__(self, logger: LoggerService):
        self.logger = logger

    def read_file(self, filepath: str) -> Optional[str]:
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            self.logger.info(f"Read file: {filepath}")
            return content
        except FileNotFoundError:
            self.logger.error(f"File not found: {filepath}")
            return None
        except Exception as e:
            self.logger.error(f"Error reading file {filepath}: {e}")
            return None

    def write_file(self, filepath: str, content: str) -> bool:
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            self.logger.info(f"Wrote file: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error writing file {filepath}: {e}")
            return False

@injectable()
class DataProcessor:
    def __init__(self, logger: LoggerService, config: ConfigService):
        self.logger = logger
        self.config = config

    def process_data(self, data: str) -> List[str]:
        self.logger.info("Processing data...")

        # Simple processing: split lines and filter empty
        lines = [line.strip() for line in data.split('\n') if line.strip()]

        max_items = self.config.get("max_items", 100)
        if len(lines) > max_items:
            self.logger.info(f"Limiting output to {max_items} items")
            lines = lines[:max_items]

        self.logger.info(f"Processed {len(lines)} items")
        return lines

@injectable()
class OutputService:
    def __init__(self, config: ConfigService, logger: LoggerService):
        self.config = config
        self.logger = logger
        self.format = config.get("output_format", "text")

    def output_results(self, results: List[str]):
        if self.format == "json":
            import json
            output = json.dumps({"results": results, "count": len(results)}, indent=2)
        else:
            output = "\n".join(f"{i+1}. {item}" for i, item in enumerate(results))

        print(output)
        self.logger.info(f"Output {len(results)} results in {self.format} format")

@injectable()
class Application:
    def __init__(
        self,
        file_service: FileService,
        data_processor: DataProcessor,
        output_service: OutputService,
        logger: LoggerService
    ):
        self.file_service = file_service
        self.data_processor = data_processor
        self.output_service = output_service
        self.logger = logger

    def run(self, input_file: str):
        self.logger.info(f"Starting application with input: {input_file}")

        # Read input file
        content = self.file_service.read_file(input_file)
        if content is None:
            self.logger.error("Failed to read input file")
            return 1

        # Process data
        results = self.data_processor.process_data(content)

        # Output results
        self.output_service.output_results(results)

        self.logger.info("Application completed successfully")
        return 0

@module(providers=[
    ConfigService,
    LoggerService,
    FileService,
    DataProcessor,
    OutputService,
    Application
])
class AppModule:
    pass

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file>")
        return 1

    app_factory = AppFactory.create(AppModule)
    app = app_factory.get(Application)

    return app.run(sys.argv[1])

if __name__ == "__main__":
    exit(main())
```

### Usage

```bash
# Create a test file
echo -e "Line 1\nLine 2\nLine 3\n\nLine 5" > test.txt

# Run the application
python main.py test.txt
```

## CLI Application with Click

```python
# cli.py
import click
from modi import injectable, module, AppFactory
from typing import Dict, Any, Optional

@injectable()
class DatabaseService:
    def __init__(self):
        self.users = {
            1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
            2: {"id": 2, "name": "Bob", "email": "bob@example.com"}
        }

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.users.get(user_id)

    def list_users(self) -> List[Dict[str, Any]]:
        return list(self.users.values())

    def create_user(self, name: str, email: str) -> Dict[str, Any]:
        new_id = max(self.users.keys()) + 1
        user = {"id": new_id, "name": name, "email": email}
        self.users[new_id] = user
        return user

    def delete_user(self, user_id: int) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

@injectable()
class UserService:
    def __init__(self, db: DatabaseService):
        self.db = db

    def get_user_info(self, user_id: int) -> Optional[str]:
        user = self.db.get_user(user_id)
        if user:
            return f"User {user['id']}: {user['name']} ({user['email']})"
        return None

    def list_all_users(self) -> List[str]:
        users = self.db.list_users()
        return [f"User {u['id']}: {u['name']} ({u['email']})" for u in users]

    def add_user(self, name: str, email: str) -> str:
        user = self.db.create_user(name, email)
        return f"Created user {user['id']}: {user['name']}"

    def remove_user(self, user_id: int) -> str:
        if self.db.delete_user(user_id):
            return f"Deleted user {user_id}"
        return f"User {user_id} not found"

@injectable()
class OutputFormatter:
    def format_user_list(self, users: List[str], format_type: str = "table") -> str:
        if format_type == "json":
            import json
            return json.dumps({"users": users}, indent=2)
        elif format_type == "csv":
            header = "ID,Name,Email"
            rows = []
            for user_str in users:
                # Parse the formatted string back (simple approach)
                parts = user_str.split(": ", 1)[1].split(" (")
                name = parts[0]
                email = parts[1].rstrip(")")
                user_id = user_str.split(":")[0].split()[-1]
                rows.append(f"{user_id},{name},{email}")
            return "\n".join([header] + rows)
        else:  # table format
            return "\n".join(users)

@injectable()
class CLIApplication:
    def __init__(self, user_service: UserService, formatter: OutputFormatter):
        self.user_service = user_service
        self.formatter = formatter

@module(providers=[
    DatabaseService,
    UserService,
    OutputFormatter,
    CLIApplication
])
class CLIModule:
    pass

# Create Modi app globally
modi_app = AppFactory.create(CLIModule)
cli_app = modi_app.get(CLIApplication)

@click.group()
def cli():
    """User management CLI powered by Modi DI"""
    pass

@cli.command()
@click.argument('user_id', type=int)
def get(user_id):
    """Get user by ID"""
    info = cli_app.user_service.get_user_info(user_id)
    if info:
        click.echo(info)
    else:
        click.echo(f"User {user_id} not found", err=True)

@cli.command()
@click.option('--format', type=click.Choice(['table', 'json', 'csv']), default='table')
def list(format):
    """List all users"""
    users = cli_app.user_service.list_all_users()
    output = cli_app.formatter.format_user_list(users, format)
    click.echo(output)

@cli.command()
@click.argument('name')
@click.argument('email')
def add(name, email):
    """Add a new user"""
    result = cli_app.user_service.add_user(name, email)
    click.echo(result)

@cli.command()
@click.argument('user_id', type=int)
def delete(user_id):
    """Delete a user"""
    result = cli_app.user_service.remove_user(user_id)
    click.echo(result)

@cli.command()
def info():
    """Show application info"""
    click.echo("Modi CLI Application")
    click.echo(f"Available services: {len(modi_app.container._provider_configs)}")
    click.echo("Services:")
    for cls in modi_app.container._provider_configs.keys():
        click.echo(f"  - {cls.__name__}")

if __name__ == '__main__':
    cli()
```

### Usage

```bash
# Install Click
pip install click

# Use the CLI
python cli.py list
python cli.py get 1
python cli.py add "Charlie" "charlie@example.com"
python cli.py list --format json
python cli.py delete 3
python cli.py info
```

## Data Processing Pipeline

```python
# pipeline.py
from modi import injectable, module, AppFactory, Scope
from typing import List, Dict, Any, Callable, Generator
import csv
import json
from datetime import datetime
from abc import ABC, abstractmethod

# Abstract interfaces
class DataSource(ABC):
    @abstractmethod
    def read_data(self) -> Generator[Dict[str, Any], None, None]:
        pass

class DataSink(ABC):
    @abstractmethod
    def write_data(self, data: List[Dict[str, Any]]) -> bool:
        pass

class DataTransformer(ABC):
    @abstractmethod
    def transform(self, item: Dict[str, Any]) -> Dict[str, Any]:
        pass

# Concrete implementations
@injectable()
class CSVDataSource(DataSource):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def read_data(self) -> Generator[Dict[str, Any], None, None]:
        with open(self.filepath, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                yield dict(row)

@injectable()
class JSONDataSink(DataSink):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def write_data(self, data: List[Dict[str, Any]]) -> bool:
        try:
            with open(self.filepath, 'w') as jsonfile:
                json.dump(data, jsonfile, indent=2)
            return True
        except Exception as e:
            print(f"Error writing JSON: {e}")
            return False

@injectable()
class DataValidationService:
    def validate_item(self, item: Dict[str, Any], required_fields: List[str]) -> bool:
        return all(field in item and item[field] for field in required_fields)

    def clean_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        # Remove empty values and strip strings
        cleaned = {}
        for key, value in item.items():
            if isinstance(value, str):
                value = value.strip()
            if value:  # Only keep non-empty values
                cleaned[key] = value
        return cleaned

@injectable()
class DataEnrichmentService:
    def __init__(self):
        self.lookup_data = {
            "department_codes": {
                "ENG": "Engineering",
                "MKT": "Marketing",
                "SAL": "Sales",
                "HR": "Human Resources"
            }
        }

    def enrich_employee_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        # Add full department name
        dept_code = item.get("department")
        if dept_code in self.lookup_data["department_codes"]:
            item["department_name"] = self.lookup_data["department_codes"][dept_code]

        # Add processing timestamp
        item["processed_at"] = datetime.utcnow().isoformat()

        # Calculate age from birth_year if present
        if "birth_year" in item:
            try:
                current_year = datetime.now().year
                item["age"] = current_year - int(item["birth_year"])
            except (ValueError, TypeError):
                pass

        return item

@injectable()
class EmployeeDataTransformer(DataTransformer):
    def __init__(self, validation: DataValidationService, enrichment: DataEnrichmentService):
        self.validation = validation
        self.enrichment = enrichment

    def transform(self, item: Dict[str, Any]) -> Dict[str, Any]:
        # Clean the data
        cleaned = self.validation.clean_item(item)

        # Validate required fields
        required_fields = ["name", "email", "department"]
        if not self.validation.validate_item(cleaned, required_fields):
            raise ValueError(f"Invalid item: missing required fields in {cleaned}")

        # Enrich the data
        enriched = self.enrichment.enrich_employee_data(cleaned)

        return enriched

@injectable()
class StatisticsService:
    def __init__(self):
        self.stats = {
            "processed_count": 0,
            "error_count": 0,
            "departments": {},
            "start_time": None,
            "end_time": None
        }

    def start_processing(self):
        self.stats["start_time"] = datetime.utcnow()

    def end_processing(self):
        self.stats["end_time"] = datetime.utcnow()

    def record_processed(self, item: Dict[str, Any]):
        self.stats["processed_count"] += 1

        # Track department statistics
        dept = item.get("department_name", "Unknown")
        self.stats["departments"][dept] = self.stats["departments"].get(dept, 0) + 1

    def record_error(self):
        self.stats["error_count"] += 1

    def get_summary(self) -> Dict[str, Any]:
        duration = None
        if self.stats["start_time"] and self.stats["end_time"]:
            duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()

        return {
            **self.stats,
            "duration_seconds": duration,
            "success_rate": (
                self.stats["processed_count"] /
                (self.stats["processed_count"] + self.stats["error_count"])
                if (self.stats["processed_count"] + self.stats["error_count"]) > 0
                else 0
            )
        }

@injectable()
class DataPipeline:
    def __init__(
        self,
        transformer: EmployeeDataTransformer,
        stats: StatisticsService
    ):
        self.transformer = transformer
        self.stats = stats

    def process(
        self,
        source: DataSource,
        sink: DataSink,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        self.stats.start_processing()

        try:
            batch = []
            all_processed = []

            for item in source.read_data():
                try:
                    transformed = self.transformer.transform(item)
                    batch.append(transformed)
                    self.stats.record_processed(transformed)

                    if len(batch) >= batch_size:
                        all_processed.extend(batch)
                        batch = []

                except Exception as e:
                    print(f"Error processing item {item}: {e}")
                    self.stats.record_error()

            # Process remaining items
            if batch:
                all_processed.extend(batch)

            # Write all data
            success = sink.write_data(all_processed)

            self.stats.end_processing()

            summary = self.stats.get_summary()
            summary["write_success"] = success

            return summary

        except Exception as e:
            self.stats.end_processing()
            raise e

# Application factory for different configurations
@injectable()
class PipelineFactory:
    def __init__(self, validation: DataValidationService, enrichment: DataEnrichmentService):
        self.validation = validation
        self.enrichment = enrichment

    def create_employee_pipeline(self) -> DataPipeline:
        transformer = EmployeeDataTransformer(self.validation, self.enrichment)
        stats = StatisticsService()
        return DataPipeline(transformer, stats)

    def create_csv_source(self, filepath: str) -> CSVDataSource:
        return CSVDataSource(filepath)

    def create_json_sink(self, filepath: str) -> JSONDataSink:
        return JSONDataSink(filepath)

@module(providers=[
    DataValidationService,
    DataEnrichmentService,
    EmployeeDataTransformer,
    StatisticsService,
    DataPipeline,
    PipelineFactory
])
class PipelineModule:
    pass

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Data processing pipeline")
    parser.add_argument("input_csv", help="Input CSV file")
    parser.add_argument("output_json", help="Output JSON file")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for processing")

    args = parser.parse_args()

    # Create Modi application
    app = AppFactory.create(PipelineModule)
    factory = app.get(PipelineFactory)

    # Create pipeline components
    source = factory.create_csv_source(args.input_csv)
    sink = factory.create_json_sink(args.output_json)
    pipeline = factory.create_employee_pipeline()

    # Run pipeline
    try:
        summary = pipeline.process(source, sink, args.batch_size)

        print("Pipeline completed!")
        print(f"Processed: {summary['processed_count']} items")
        print(f"Errors: {summary['error_count']} items")
        print(f"Success rate: {summary['success_rate']:.2%}")
        print(f"Duration: {summary['duration_seconds']:.2f} seconds")
        print(f"Departments: {summary['departments']}")
        print(f"Write success: {summary['write_success']}")

    except Exception as e:
        print(f"Pipeline failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
```

### Test Data

Create a test CSV file:

```csv
name,email,department,birth_year,salary
John Doe,john@example.com,ENG,1990,75000
Jane Smith,jane@example.com,MKT,1985,65000
Bob Johnson,bob@example.com,SAL,1988,70000
Alice Brown,alice@example.com,HR,1992,60000
```

### Usage

```bash
python pipeline.py employees.csv employees.json --batch-size 50
```

## Configuration Management

```python
# config_app.py
from modi import injectable, module, AppFactory
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

@injectable()
class EnvironmentConfigLoader:
    def load(self) -> Dict[str, Any]:
        return {
            "database_url": os.getenv("DATABASE_URL", "sqlite:///app.db"),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "api_key": os.getenv("API_KEY"),
            "port": int(os.getenv("PORT", "8000"))
        }

@injectable()
class FileConfigLoader:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)

    def load(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            return {}

        with open(self.config_path) as f:
            return json.load(f)

@injectable()
class ConfigService:
    def __init__(self, env_loader: EnvironmentConfigLoader, file_loader: FileConfigLoader):
        self.env_config = env_loader.load()
        self.file_config = file_loader.load()

        # Merge configs (environment variables take precedence)
        self.config = {**self.file_config, **self.env_config}

    def get(self, key: str, default=None) -> Any:
        return self.config.get(key, default)

    def get_database_url(self) -> str:
        return self.get("database_url")

    def is_debug_mode(self) -> bool:
        return self.get("debug", False)

    def get_log_level(self) -> str:
        return self.get("log_level", "INFO")

    def dump_config(self) -> Dict[str, Any]:
        # Return config without sensitive data
        safe_config = self.config.copy()
        if "api_key" in safe_config:
            safe_config["api_key"] = "***hidden***"
        return safe_config

@injectable()
class SecureConfigService:
    def __init__(self, config: ConfigService):
        self.config = config

    def get_api_key(self) -> Optional[str]:
        key = self.config.get("api_key")
        if not key:
            raise ValueError("API key not configured")
        return key

    def get_database_credentials(self) -> Dict[str, str]:
        url = self.config.get_database_url()
        # Parse database URL (simplified)
        if url.startswith("postgresql://"):
            return {"type": "postgresql", "url": url}
        elif url.startswith("sqlite://"):
            return {"type": "sqlite", "url": url}
        else:
            raise ValueError(f"Unsupported database type: {url}")

@module(providers=[
    EnvironmentConfigLoader,
    FileConfigLoader,
    ConfigService,
    SecureConfigService
])
class ConfigModule:
    pass

def main():
    app = AppFactory.create(ConfigModule)

    config = app.get(ConfigService)
    secure_config = app.get(SecureConfigService)

    print("Application Configuration:")
    print(json.dumps(config.dump_config(), indent=2))

    print(f"\nDebug mode: {config.is_debug_mode()}")
    print(f"Log level: {config.get_log_level()}")

    try:
        db_creds = secure_config.get_database_credentials()
        print(f"Database type: {db_creds['type']}")
    except ValueError as e:
        print(f"Database config error: {e}")

    try:
        api_key = secure_config.get_api_key()
        print(f"API key configured: {'Yes' if api_key else 'No'}")
    except ValueError as e:
        print(f"API key error: {e}")

if __name__ == "__main__":
    main()
```

## Testing Simple Applications

```python
# test_app.py
import pytest
from modi import AppFactory
from your_app import AppModule, UserService, DatabaseService

@pytest.fixture
def app():
    return AppFactory.create(AppModule)

def test_user_service(app):
    user_service = app.get(UserService)

    # Test getting user info
    info = user_service.get_user_info(1)
    assert info is not None
    assert "Alice" in info

def test_database_service(app):
    db_service = app.get(DatabaseService)

    # Test user creation
    user = db_service.create_user("Test User", "test@example.com")
    assert user["name"] == "Test User"
    assert user["email"] == "test@example.com"

    # Test user retrieval
    retrieved = db_service.get_user(user["id"])
    assert retrieved == user

def test_dependency_injection(app):
    # Test that dependencies are properly injected
    user_service = app.get(UserService)
    db_service = app.get(DatabaseService)

    # UserService should have DatabaseService injected
    assert user_service.db is db_service

def test_singleton_behavior(app):
    # Test that services are singletons by default
    service1 = app.get(UserService)
    service2 = app.get(UserService)

    assert service1 is service2
```

## Best Practices for Simple Applications

1. **Keep it Simple**: Don't over-engineer small applications
2. **Use Type Hints**: Enable better IDE support and error detection
3. **Separate Concerns**: Keep business logic separate from I/O operations
4. **Configuration**: Use dependency injection for configuration
5. **Error Handling**: Implement proper error handling and logging
6. **Testing**: Test business logic independently from I/O
7. **Entry Points**: Use clear entry points and argument parsing
8. **Documentation**: Add docstrings to your services and methods
