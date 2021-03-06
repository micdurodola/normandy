from django.core.management.base import BaseCommand
from django_countries import countries

from normandy.recipes.models import Channel, Country, WindowsVersion


class Command(BaseCommand):
    """
    Adds some helpful initial data to the site's database. If matching
    data already exists, it should _not_ be overwritten, making this
    safe to run multiple times.

    This exists instead of data migrations so that test runs do not load
    this data into the test database.

    If this file grows too big, we should consider finding a library or
    coming up with a more robust way of adding this data.
    """

    help = "Adds initial data to database"

    def handle(self, *args, **options):
        self.add_release_channels()
        self.add_countries()
        self.add_windows_versions()

    def add_release_channels(self):
        self.stdout.write("Adding Release Channels...", ending="")
        channels = {
            "release": "Release",
            "beta": "Beta",
            "aurora": "Developer Edition",
            "nightly": "Nightly",
        }

        for slug, name in channels.items():
            Channel.objects.update_or_create(slug=slug, defaults={"name": name})
        self.stdout.write("Done")

    def add_countries(self):
        self.stdout.write("Adding Countries...", ending="")
        for code, name in countries:
            Country.objects.update_or_create(code=code, defaults={"name": name})
        self.stdout.write("Done")

    def add_windows_versions(self):
        self.stdout.write("Adding Windows Versions...", ending="")
        versions = [
            (6.1, "Windows 7"),
            (6.2, "Windows 8"),
            (6.3, "Windows 8.1"),
            (10.0, "Windows 10"),
        ]

        for nt_version, name in versions:
            WindowsVersion.objects.update_or_create(nt_version=nt_version, defaults={"name": name})
        self.stdout.write("Done")
