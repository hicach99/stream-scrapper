# stream-scrapper
    Install requirements
        $ pip install -r requirements.txt
    Setup database info "setup/settings.py"
    Generate database
        $ python manage.py makemigrations
        $ python manage.py migrate
    Create a superuser
        $ python manage.py createsuperuser
    Run server if a local machine
        $ python manage.py runserver