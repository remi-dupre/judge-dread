from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *


admin.site.register(UserAdmin, User)
admin.site.register(Problem)
admin.site.register(ProblemDescription)
admin.site.register(Attachment)
admin.site.register(TestCase)
admin.site.register(Submission)
admin.site.register(Run)
