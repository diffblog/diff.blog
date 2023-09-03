from django.core.management.base import BaseCommand, CommandError
from app.models import Topic, UserProfile, UserList, get_user_profile


class Command(BaseCommand):
    help = "Updated the curated lists"

    def update_top_tech_company_engineering_blogs(self):
        topic = Topic.objects.get(display_name="Engineering Team Blogs")
        users = topic.recommended.all()
        hackerkid = get_user_profile("hackerkid")
        user_list, _ = UserList.objects.get_or_create(
            name="Top Engineering Blogs of Tech Companies", created_by=hackerkid
        )

        user_list.description = "These are the top Engineering blogs of Tech Companies in diff.blog. Subscribe, to keep updated with blogs."
        user_list.save()

        for user in users:
            user_list.users.add(user)

    def handle(self, *args, **options):
        self.update_top_tech_company_engineering_blogs()
