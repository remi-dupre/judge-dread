from django.contrib.auth.models import AbstractUser
from django.db import models


# The different languages we have choice to translate in
LANG_CHOICES = (
    ('en', 'English'),
    ('fr', 'French')
)

# The different programming languages allowed
PROGRAMMING_LANG_CHOICE = (
    ('python', 'Python'),
    ('cpp', 'C++')
)


class User(AbstractUser):
    """
    Contain user extra informations.

    This model is built to complement django's built-in authentification.
    """
    # Visible name of the user, if null the first and last name may be shown
    nickname = models.CharField(max_length=16, null=True, default=None)

    def __str__(self):
        if self.nickname is not None:
            return self.nickname
        else:
            return self.first_name + ' ' + self.last_name

# Models related to testcase creation

class Problem(models.Model):
    """
    Represent a problem, which can be linked with tasks, attachments and
    descriptions.
    """
    # The user who added the problem
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    # Dates of creation and modification of the problem
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # General informations about the problem
    name = models.CharField(max_length=200, unique=True)
    # Solution for problem
    soluce_language = models.CharField(
        max_length=10,
        choices=PROGRAMMING_LANG_CHOICE
    )
    soluce_code = models.TextField()

    def __str__(self):
        return self.name


class ProblemDescription(models.Model):
    """
    Represent the description of a problem this allows to add several
    translations of the same problem.
    """
    # Problem this description relates to
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    # The language it is written in
    language = models.CharField(max_length=2, choices=LANG_CHOICES)
    # The content of the description
    content = models.TextField()

    def __str__(self):
        return '%s (%s)' % (self.problem.name, self.language)

    class Meta:
        unique_together = ('problem', 'language')


class Attachment(models.Model):
    """
    Represent a file attached to a problem's description.
    """
    # The problem description this file is attached to
    problem_description = models.ForeignKey(ProblemDescription, models.CASCADE)
    # The name, but also the identifier of the attachment
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=255, blank=True)
    # The content of the attachment
    def file_path(instance, filename):
        return 'attachments/%s/%s' % (instance.problem.name, instance.name)
    file = models.FileField(upload_to=file_path)

    def __str__(self):
        ret = '%s > %s' % (self.problem.name, self.name)

        if language is not None:
            ret += ' (%s)' % self.language

        return ret

    class Meta:
        unique_together = ('problem_description', 'name')


class TestCase(models.Model):
    """
    Represent an input, and the excepted output for it.
    """
    # The problem this testcase is related to
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    # The excepted inputs and outputs
    input = models.TextField()
    output = models.TextField()
    # The testcases will be ordered following the key `order`
    order = models.IntegerField(default=0)

    def __str__(self):
        return '{problem}: {order} -- {size} bytes input'.format(
            problem = str(self.problem),
            order = self.order,
            size = len(self.input.encode('utf-8'))
        )

# Models related to submissions

class Submission(models.Model):
    """
    An user solution to the problem.
    """
    # Solution for problem
    language = models.CharField(
        max_length=10,
        choices=PROGRAMMING_LANG_CHOICE
    )
    code = models.TextField()
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, null=True)
    # Extra informations about the submission
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return '{author}: {problem} -- {language} -- {date}'.format(
            author = self.author,
            problem = self.problem,
            language = self.language,
            date = self.date
        )


class Run(models.Model):
    """
    The result for a testcase.
    """
    # Submission, and testcase it relates to
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    testcase = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    # Result of the submission
    STATUS_CHOICES = (
        ('ok', 'OK'),
        ('err', 'error')
    )
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    raw_output = models.TextField()
    camisole_output = models.TextField()

    def __str__(self):
        return str(self.submission) + ' ' + str(self.status)

    class Meta:
        unique_together = ('submission', 'testcase')
