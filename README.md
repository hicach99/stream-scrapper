# stream-scrapper
    1 - Install requirements
            $ pip install -r requirements.txt
    2 - Download chrome-win64 and extract it as chrome-win64/ in the current folder from (stable: chrome-win64/):
            https://googlechromelabs.github.io/chrome-for-testing/ or
            https://chromium.woolyss.com
        (alternative) download chromedriver compatible with current browser https://googlechromelabs.github.io/chrome-for-testing/
    3 - Setup database info "setup/settings.py"
    4 - Generate database (if new)
            $ python manage.py makemigrations
            $ python manage.py migrate
    5 - Create a superuser (if new)
            $ python manage.py createsuperuser
    6 - Run server if a local machine
            $ python manage.py runserver