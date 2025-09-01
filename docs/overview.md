
# Overview

## What is Modi?

Modi is a lightweight dependency injection (DI) framework for Python, heavily inspired by [NestJS](https://nestjs.com/). It brings the familiar decorator-based DI pattern from the TypeScript/JavaScript world to Python, making your applications more modular, testable, and maintainable.

## Motivation

### Why Dependency Injection?

Dependency injection is a design pattern that helps you:

- **Decouple components** - Classes don't need to know how to create their dependencies
- **Improve testability** - Easy to mock dependencies for unit testing
- **Enhance maintainability** - Changes to one component don't cascade to others
- **Enable flexibility** - Swap implementations without changing dependent code

### Why Modi?

While Python has several DI libraries, Modi stands out by providing:

1. **NestJS-inspired API** - Familiar patterns for developers coming from NestJS
2. **Decorator-based** - Clean, readable syntax using Python decorators
3. **Zero dependencies** - Lightweight with no external requirements
4. **Type-safe** - Full support for Python type hints and MyPy
5. **Module system** - Organize your code into logical, reusable modules
6. **Automatic resolution** - Resolve dependencies through type annotations

## Comparison with Alternatives

| Feature                | Modi | dependency-injector | punq | injector |
| ---------------------- | ---- | ------------------- | ---- | -------- |
| **Decorator-based**    | ✅   | ❌                  | ❌   | ✅       |
| **Auto-resolution**    | ✅   | ✅                  | ✅   | ✅       |
| **Module system**      | ✅   | ❌                  | ❌   | ❌       |
| **NestJS-like API**    | ✅   | ❌                  | ❌   | ❌       |
| **Type hints support** | ✅   | ✅                  | ✅   | ✅       |
| **Zero dependencies**  | ✅   | ❌                  | ✅   | ❌       |
| **Scopes support**     | ✅   | ✅                  | ✅   | ✅       |
| **Global modules**     | ✅   | ❌                  | ❌   | ❌       |

### dependency-injector

**Pros:**

- Mature and feature-rich
- Excellent configuration support
- Good performance

**Cons:**

- Complex API with many concepts
- Requires learning provider types
- No decorator-based registration
- Heavy with many dependencies

### punq

**Pros:**

- Simple and lightweight
- Good type hint support
- Zero dependencies

**Cons:**

- No decorator support
- Manual registration required
- No module system
- Limited scope support

### injector

**Pros:**

- Decorator-based like Modi
- Good community support
- Flexible binding system

**Cons:**

- More complex than Modi
- No module system
- Different API style
- Additional dependencies

## When to Use Modi

Modi is ideal for:

- **NestJS developers** moving to Python
- **Modular applications** that benefit from organized code structure
- **Microservices** where clean separation of concerns matters
- **Testing-heavy projects** where mocking dependencies is important
- **Type-safe codebases** using modern Python features

## Core Philosophy

Modi follows these principles:

1. **Simplicity** - Easy to learn and use
2. **Familiarity** - Patterns Python developers already know
3. **Modularity** - Organize code into logical units
4. **Type Safety** - Leverage Python's type system
5. **Zero Magic** - Explicit and predictable behavior

## Architecture Overview

```
Application
    ├── Root Module
    │   ├── Providers (Services, Controllers, etc.)
    │   ├── Imports (Other modules)
    │   └── Exports (Providers available to importing modules)
    └── DI Container
        ├── Provider Registry
        ├── Scope Management
        └── Dependency Resolution
```

Modi organizes your application into **modules** that declare their **providers** (services, controllers, etc.) and manage their dependencies automatically through the **DI container**.

## Next Steps

- [Get started](getting-started.md) with installation and basic usage
- Learn about [core concepts](core-concepts.md) in detail
- Check out [integration guides](integrations/) for your framework
- Browse [examples](examples/) for practical use cases
