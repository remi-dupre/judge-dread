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


class RunAdmin(admin.ModelAdmin):
    testcase__order = lambda run: run.testcase.order
    testcase__problem = lambda admin, run: run.testcase.problem
    submission__author = lambda admin, run: run.submission.author
    submission__date = lambda admin, run: run.submission.date

    testcase__problem.short_description = 'Testcase\'s problem'
    submission__author.short_description = 'Submission\'s author'
    submission__date.short_description = 'Submission\'s date'

    ordering = ['status', 'testcase__order', 'submission']
    list_display = ['testcase__problem', 'submission__author', 'status', 'reason', 'submission__date', 'time', 'mem']


admin.site.register(User, UserAdmin)
admin.site.register(Problem)
admin.site.register(ProblemDescription)
admin.site.register(Attachment)
admin.site.register(TestCase)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Run, RunAdmin)
