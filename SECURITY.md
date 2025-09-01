# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depend on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

Please report (suspected) security vulnerabilities to **kostia.tarnashynskyi@example.com**. You will receive a response from us within 48 hours. If the issue is confirmed, we will release a patch as soon as possible depending on complexity but historically within a few days.

## Security Best Practices

When using Modi in production:

1. **Validate Inputs**: Always validate data before injecting it into your services
2. **Principle of Least Privilege**: Only expose the services that need to be public
3. **Keep Dependencies Updated**: Regularly update Modi and its dependencies
4. **Monitor Dependencies**: Use tools like `pip-audit` to check for known vulnerabilities

## Dependency Security

Modi has minimal dependencies to reduce the attack surface. We regularly monitor our dependencies for security issues.

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine the affected versions
2. Audit code to find any potential similar problems
3. Prepare fixes for all releases still under maintenance
4. Release new versions as soon as possible

## Comments on this Policy

If you have suggestions on how this process could be improved please submit a pull request.
