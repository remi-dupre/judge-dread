from django.db import models

import judge.models


class Compilation(models.Model):
    """
    The result of the last compilation of a submission.
    """
    submission = models.OneToOneField(
        judge.models.Submission,
        on_delete = models.CASCADE,
        primary_key = True
    )
    # Status of the compilation
    STATUS_CHOICES = (
        ('ok', 'ok'),
        ('error', 'error')
    )
    status = models.CharField(max_length=8)
    errors = models.TextField()
    # Raw formatted result of the submission
    camisole_output = models.TextField()


class Run(models.Model):
    """
    The result for a submission of its last run on a testcase.
    """
    # Submission, and testcase it relates to
    submission = models.ForeignKey(judge.models.Submission, on_delete=models.CASCADE)
    testcase = models.ForeignKey(judge.models.TestCase, on_delete=models.CASCADE)
    # State informations deduced from camisole's output
    STATUS_CHOICES = (
        ('ok', 'ok'),
        ('error', 'error'),
        ('failed', 'failed')
    )
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    REASON_CHOICES = (
        ('match', 'Right answer'),
        ('segfault', 'Segmentation fault'),
        ('timeout', 'Time limit exeeded'),
        ('memory', 'Memory usage exeeded'),
        ('unknown', 'Unknown reason'),
        ('wrong', 'Wrong answer')
    )
    reason = models.CharField(max_length=8, blank=True, choices=REASON_CHOICES)
    # Output of the program
    output = models.TextField()
    # Ressouces used by the program
    time = models.DecimalField(max_digits=9, decimal_places=3)
    mem = models.IntegerField()
    # Raw formatted result of the submission
    camisole_output = models.TextField()

    class Meta:
        unique_together = ('submission', 'testcase')
