from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *


class SubmissionAdmin(admin.ModelAdmin):
    ordering = ['-date']
    list_display = ['problem', 'status', 'author', 'language', 'date']
    actions = ['run_submission']

    def run_submission(self, request, queryset):
        """Run a set of submissions"""
        for submission in queryset:
            submission.run()

    run_submission.short_description = 'Run submissions on testcases'


admin.site.register(User, UserAdmin)
admin.site.register(Problem)
admin.site.register(ProblemDescription)
admin.site.register(Attachment)
admin.site.register(TestCase)
admin.site.register(Submission, SubmissionAdmin)
