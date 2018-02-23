from django.contrib import admin

from .models import *


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


admin.site.register(Compilation)
admin.site.register(Run, RunAdmin)
