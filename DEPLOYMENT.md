# DoorsAndDrawers - Production Deployment Guide

This guide explains how to deploy the DoorsAndDrawers Django application in production using Waitress WSGI server.

## Prerequisites

1. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure the database is set up:
   ```bash
   python manage.py migrate
   ```

3. Collect static files for production:
   ```bash
   python manage.py collectstatic
   ```

## Production Configuration

The application has been configured for production deployment:

- **DEBUG mode**: Disabled (`DEBUG = False`)
- **WSGI Server**: Waitress added to requirements
- **ALLOWED_HOSTS**: Configured for localhost deployment
- **Static files**: Configured with STATIC_ROOT and WhiteNoise middleware for serving static files in production

## Running in Production

### Option 1: Using the Production Script (Recommended)

Run the provided production script:

```bash
python run_production.py
```

This will start the server on `http://localhost:8080` with optimized settings for production.

### Option 2: Using Waitress Directly

You can also run waitress directly from the command line:

```bash
waitress-serve --host=0.0.0.0 --port=8080 DoorsAndDrawers.wsgi:application
```

### Option 3: Custom Configuration

For custom deployment, modify the `run_production.py` script or use waitress with your preferred settings:

```python
from waitress import serve
from DoorsAndDrawers.wsgi import application

serve(application, host='your-host', port=your-port)
```

## Production Considerations

1. **ALLOWED_HOSTS**: Update the `ALLOWED_HOSTS` setting in `DoorsAndDrawers/settings.py` to include your production domain(s).

2. **SECRET_KEY**: In a real production environment, move the SECRET_KEY to an environment variable.

3. **Database**: Consider using a production database like PostgreSQL instead of SQLite.

4. **HTTPS**: Configure SSL/TLS certificates and update `SESSION_COOKIE_SECURE = True` in settings.

5. **Static Files**: Static files are automatically served by WhiteNoise middleware. Ensure `collectstatic` has been run before deployment.

## Server Configuration

The production script is configured with the following default settings:
- Host: `0.0.0.0` (all interfaces)
- Port: `8080`
- Threads: `6`
- Connection limit: `1000`
- Cleanup interval: `30` seconds

These can be modified in the `run_production.py` script as needed.

## Troubleshooting

### Static Files 404 Error

If you encounter a 404 error when accessing static files (e.g., `/static/css/tailwind.css`):

1. **Check the correct port**: The production server runs on port `8080`, not `8000`. Access static files at:
   ```
   http://localhost:8080/static/css/tailwind.css
   ```

2. **Run collectstatic**: Ensure you've collected static files for production:
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Verify WhiteNoise**: The application uses WhiteNoise middleware to serve static files in production. This is automatically configured in the settings.

4. **Check static files exist**: Verify that static files are present in both `static/` and `staticfiles/` directories.
