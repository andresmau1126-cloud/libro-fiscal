web: cd backend && python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py seed_demo && daphne -b 0.0.0.0 -p $PORT config.asgi:application
