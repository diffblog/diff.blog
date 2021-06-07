from datetime import timedelta
from django.utils import timezone
from jobs.models import Job
from django.core.management.base import BaseCommand, CommandError
from dateutil import parser as date_parser

from app.models import UserProfile
from jobs.models import Location
from django.utils.text import slugify

import requests

"""

split location


if ";" in location:
    locations = location.split(",")
    for full_location in locations:
        location_parts = full_location.splt(",)
        print(location_parts)
else:
    



Remote - US


San Francisco, CA; Remote - US
Austin, TX; Remote - US
Austin, TX; Remote - US
Paris, France; Remote - France; Remote - EMEA
Austin TX; Remote - US


San Francisco, CA / New York, NY / Remote
San Francisco, CA | Seattle WA
Mountain View, California, US
Atlanta, Georgia, United States, New York, United States, Remote US
Dublin, London, England, United Kingdom, Paris, Remote EMEA
New York City, NY (USA)
San Francisco, CA (USA)
Stamford, Connecticut, United States of America

San Francisco or Atlanta, United States 
New York, Atlanta, or Remote (Chicago)
San Francisco OR Remote (Arizona)


This is a remote job in the United States except that it is not eligible to be performed in Colorado.

"""


class Command(BaseCommand):
    help = "Fetches the top users from GitHub"

    def get_cleaned_locations(self, location_string):
        q = [location_string]
        for split_char in ["/", ";", " or ", " OR ", ",", "|"]:
            locations = []
            for location in q:
                locations.extend(location.split(split_char))
            q = locations
        cleaned_location = []
        for location in set(q):
            stripped_location = location.lstrip().rstrip()
            if len(stripped_location) == 0 or len(stripped_location) >= 200:
                continue
            location = Location.objects.filter(slug=slugify(stripped_location)).last()
            if location is None:
                location = Location.objects.create(name=stripped_location)
            cleaned_location.append(location)
        return cleaned_location

    def add_arguments(self, parser):
        parser.add_argument("--username", action="store", default=None)

    def handle(self, *args, **options):
        if options["username"]:
            user_profiles = UserProfile.objects.filter(
                github_username=options["username"]
            )
        else:
            user_profiles = UserProfile.objects.filter(is_organization=True)

        for user_profile in user_profiles:
            two_days_back = timezone.now() - timedelta(days=2)
            if Job.objects.filter(
                github_username=user_profile.github_username,
                posted_on__gte=two_days_back,
            ).exists():
                continue

            url = "https://boards-api.greenhouse.io/v1/boards/{}/jobs".format(
                user_profile.github_username
            )
            response = requests.get(url)
            print(user_profile.github_username)
            if response.status_code != 200:
                continue
            data = response.json()
            created = False
            for job_dict in data["jobs"]:
                if Job.objects.filter(
                    github_username=user_profile.github_username,
                    global_job_id=job_dict["id"],
                ).exists():
                    continue

                title = job_dict["title"]
                valid_roles = [
                    "engineer",
                    "developer",
                    "programmer",
                    "writer",
                    "project manager",
                    "product manager",
                    "architect",
                    "software",
                    "engineering",
                    "researcher",
                    "tech lead",
                    "sre",
                    "devops",
                    "team lead",
                ]
                is_valid_role = False
                for valid_role in valid_roles:
                    if valid_role in title.lower():
                        is_valid_role = True
                        break
                if not is_valid_role:
                    continue

                job = Job.objects.create(
                    title=title,
                    description_link=job_dict["absolute_url"],
                    github_username=user_profile.github_username,
                    company_name=user_profile.full_name or user_profile.github_username,
                    is_verified=True,
                    global_job_id=job_dict["id"],
                )
                job.posted_on = date_parser.parse(job_dict["updated_at"])
                job.save()
                locations = self.get_cleaned_locations(job_dict["location"]["name"])
                job.locations.set(locations)
                created = True
            if created:
                print("✅ ", user_profile.github_username)
            else:
                print("❌ ", user_profile.github_username)
