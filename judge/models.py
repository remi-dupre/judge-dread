import re
import json

from django.contrib.auth.models import AbstractUser
from django.db import models

from .tools.markdown import load_markdown_module
from .tools.camisole import run as camisole_run


# The different languages we have choice to translate in
LANG_CHOICES = (
    ('en', 'English'),
    ('fr', 'Français')
)

# The different programming languages allowed
PROGRAMMING_LANG_CHOICE = (
    ('ada', 'Ada'),
    ('c#', 'C#'),
    ('c', 'C'),
    ('c++', 'C++'),
    ('haskell', 'Haskell'),
    ('java', 'Java'),
    ('javascript', 'JavaScript'),
    ('lua', 'Lua'),
    ('ocaml', 'OCaml'),
    ('pascal', 'Pascal'),
    ('perl', 'Perl'),
    ('php', 'PHP'),
    ('python', 'Python 3'),
    ('ruby', 'Ruby'),
    ('rust', 'Rust'),
    ('scheme', 'Scheme')
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
        elif self.first_name + self.last_name != '':
            return self.first_name + ' ' + self.last_name
        else:
            return self.username

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

    def make_camisole_input(self):
        """
        Return the description of this problem's testcases in camisole's format
        """
        ret = []
        testcases = TestCase.objects.filter(problem=self).order_by('order')

        for test in testcases:
            ret.append({
                'name': str(test.id),
                'stdin': test.input
            })

        return ret

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
    # The translated title of the problem
    # If left to null, the default name will be prompt
    name = models.CharField(max_length=200, null=True)
    # The content of the description
    content = models.TextField()

    def __str__(self):
        return '{name} ({language})'.format(
            name = self.name if self.name is not None else self.problem.name,
            language = self.language
        )

    class Meta:
        unique_together = ('problem', 'language')

    def content_as_html(self):
        """
        Format the description's core content as html.
        """
        def url_finder(name):
            # Get the right attachment, and extracts his url
            try:
                attachment = Attachment.objects.get(
                    name = name,
                    problem_description = self
                )
                return attachment.file.url
            except Attachment.DoesNotExist:
                print(name, 'not found')

                return '404.html'

        markdown = load_markdown_module(attachment_url_writer=url_finder)
        return markdown(self.content)


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
        return 'attachments/%s/%s' % (instance.problem_description, instance.name)
    file = models.FileField(upload_to=file_path)

    def __str__(self):
        return '%s > %s' % (self.problem_description, self.name)

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

    def valid_output(self, text):
        """
        Check if an output is valid by comparing it to self.output.
        """
        def normalized(text):
            """
            Return a normalized version of the text.
            """
            text = re.sub('( |\t)+', ' ', text)
            text = re.sub('\n+', '\n', text)

            if text and text[-1] == '\n':
                text = text[:-1]

            return text

        return normalized(text) == normalized(self.output)

    def __str__(self):
        return '{problem}: {order} -- {size} bytes input'.format(
            problem = self.problem,
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

    def status(self):
        """
        Return the status of the submission.

        The return value is a string, it can only be theses values:
         - 'pending': the task has not been run yet
         - 'success': all testcases went ok
         - 'failed' : some testcases had mistakes
         - 'error'  : something went wrong during the execution 
        """
        runs = Run.objects.filter(submission=self)

        if not runs:
            return 'pending'
        elif runs.filter(status='error'):
            return 'error'
        elif runs.filter(status='failed'):
            return 'failed'
        else:
            return 'success'

    def run(self):
        """
        Launch the test of the submission.

        If a run was already launched, its datas will be erased.
        """
        camisole_ret = camisole_run(
            lang = self.language,
            source = self.code,
            tests = self.problem.make_camisole_input()
        )
        print(camisole_ret)

        # Delete all related runs
        Run.objects.filter(submission=self).delete()

        if 'tests' in camisole_ret.keys():
            for test_result in camisole_ret['tests']:
                testcase = TestCase.objects.get(pk=int(test_result['name']))
                print(testcase)

                if test_result['meta']['status'] == 'OK' and testcase.valid_output(test_result['stdout']):
                    status = 'ok'
                else:
                    status = 'failed'

                run = Run.from_camisole_output(
                    submission = self,
                    testcase = testcase,
                    # status = status,
                    # output = test_result['stdout'],
                    camisole_output = test_result
                )
                run.save()
        else:
            pass
            # testcases = TestCase.objects.filter(problem=self.problem)
            # run = Run(
            #     submission = self,
            #     testcase = testcases.order_by('order').first(),
            #     status = 'error',
            #     camisole_output = json.dumps(camisole_ret)
            # )
            # run.save()

    def __str__(self):
        return 'submission from {author} on "{problem}" using {language}'.format(
            author = self.author,
            problem = self.problem,
            language = self.language,
            date = self.date
        )


class Run(models.Model):
    """
    The result for a testcase.
    """
    def from_camisole_output(testcase, camisole_output, **kwargs):
        """
        Construct status fields given camisole's output
        """
        meta = camisole_output['meta']
        output_matches = testcase.valid_output(camisole_output['stdout'])

        if meta['status'] != 'OK':
            if meta['exitsig'] == 11:
                status = 'failed'
                reason = 'segfault'
            elif meta['status'] == 'TIMED_OUT':
                status = 'failed'
                reason = 'timeout'
            else:
                status = 'error'
                reason = 'unknown'
        elif output_matches:
            status = 'ok'
            reason = 'match'
        else:
            status = 'failed'
            reason = 'wrong'

        return Run(
            status = status,
            reason = reason,
            output = camisole_output['stdout'],
            time = meta['time'],
            mem = meta['cg-mem'],
            testcase = testcase,
            camisole_output = json.dumps(camisole_output),
            **kwargs
        )

    # Submission, and testcase it relates to
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    testcase = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    # Result of the submission
    camisole_output = models.TextField()
    # State informations deduced from camisole's output
    STATUS_CHOICES = (
        ('ok', 'ok'),
        ('error', 'error'),
        ('failed', 'failed')
    )
    status = models.CharField(max_length=6, choices=STATUS_CHOICES)
    REASON_CHOICES = (
        ('match', 'Right answer'),
        ('segfault', 'Segmentation fault'),
        ('timeout', 'Time limit exeeded'),
        ('unknown', 'Unknown reason'),
        ('wrong', 'Wrong answer')
    )
    reason = models.CharField(max_length=255, blank=True, choices=REASON_CHOICES)
    # Output of the program
    output = models.TextField()
    # Ressouces used by the program
    time = models.DecimalField(max_digits=9, decimal_places=3)
    mem = models.IntegerField()

    class Meta:
        unique_together = ('submission', 'testcase')
