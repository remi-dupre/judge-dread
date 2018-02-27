from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.template.loader import get_template

from .forms import *
from .models import *


def home(request):
    '''
    Main page.
    '''
    template = get_template('home.html')
    return HttpResponse(template.render({},request))

def problem_display(request, problem_id):
    try:
        problem_description = ProblemDescription.objects.get(pk=problem_id)
    except ProblemDescription.DoesNotExist:
        raise Http404('Problem does not exist')

    # Recover form datas
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
    else:
        form = SubmissionForm()

    # Save form datas and redirect to main page
    if form.is_valid():
        if form.data['code']:
            sub = Submission(
                language = form.cleaned_data['language'],
                code = form.cleaned_data['code'],
                problem = problem_description.problem
            )
        else:
            sub = Submission(
                language = form.cleaned_data['language'],
                code = form.cleaned_data['code'],
                problem = problem_description.problem
            )
        sub.save()
        return redirect(home)

    else:
        template = get_template('problem.html')
        context = {
            'form': form,
            'problem_description': problem_description,
            'problem': problem_description.problem
        }
        return HttpResponse(template.render(context, request))

def problem_admin(request, problem_id):
    try:
        problem = Problem.objects.get(pk=problem_id)
        descriptions = ProblemDescription.objects.filter(
            problem = problem_id
        )
        testcases = TestCase.objects.filter(problem=problem)
    except Problem.DoesNotExist:
        raise Http404('Problem does not exist')

    testcase_default = TestCase(
        problem_id = problem_id,
        input = '',
        output = '',
        order = 42
    )
    if request.method == 'POST':
        add_testcase_form = TestCaseForm(
            request.POST,
            instance = testcase_default
        )
    else:
        add_testcase_form = TestCaseForm(instance=testcase_default)

    template = get_template('problem-admin.html')
    context = {
        'descriptions': descriptions,
        'problem': problem,
        'available_languages': settings.LANGUAGES.keys(),
        'description_languages':
            [description.language for description in descriptions],
        'testcases': testcases,
        'add_testcase_form': add_testcase_form,
    }

    if request.method == 'POST':
        add_testcase_form.save()
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse(template.render(context, request))

def testcase_delete(request, testcase_id):
    try:
        testcase = TestCase.objects.get(pk=testcase_id)
        testcase.delete()
    except testcase.DoesNotExist:
        raise Http404('Test case does not exist')

    return redirect(
        reverse('problem_admin', kwargs={
            'problem_id': testcase.problem.id
        }) + '#testcases-tab'
    )

def description_edit(request, problem_id, lang):
    try:
        description = ProblemDescription.objects.get(
            problem = problem_id,
            language = lang
        )
        attachments = Attachment.objects.filter(
            problem_description = description
        )
    except ProblemDescription.DoesNotExist:
        raise Http404('Description does not exist')

    # Description form
    if request.method == 'POST' and 'save-description' in request.POST:
        description_form = DescriptionForm(
            request.POST,
            instance = description
        )
        description_form.save()
    else:
        description_form = DescriptionForm(instance=description)

    # New attachment form
    if request.method == 'POST' and 'upload-attachment' in request.POST:
        new_attachment = Attachment(problem_description=description)
        new_attachment_form = AttachmentForm(
            request.POST, request.FILES,
            instance = new_attachment
        )

        if new_attachment_form.is_valid():
            new_attachment_form.save()
            new_attachment_form = AttachmentForm()
    else:
        new_attachment_form = AttachmentForm()

    template = get_template('description-edit.html')
    context = {
        'description': description,
        'problem': description.problem,
        'language': lang,
        'attachments': attachments,
        'description_form': description_form,
        'add_attachment_form': new_attachment_form
    }
    return HttpResponse(template.render(context, request))

def attachment_delete(request, attachment_id):
    try:
        attachment = Attachment.objects.get(id=attachment_id)
        http_response = redirect(
            'description_edit',
            problem_id = attachment.problem_description.problem.id,
            lang = attachment.problem_description.language
        )
        attachment.delete()
        return http_response
    except Attachment.DoesNotExist:
        return HttpResponse(
            Http404('This attachment doesn\'t exist')
        )

def description_delete(request, problem_id, lang):
    try:
        description = ProblemDescription.objects.get(
            problem = problem_id,
            language = lang
        )
    except ProblemDescription.DoesNotExist:
        raise Http404('Description does not exist')

    description.delete()
    return redirect('problem_admin', problem_id=problem_id)

def creation(request):
    ''''
    Display a form to create a new task.
    If the form is filled, create the new problem and returns.
    '''
    # Recover form datas
    if request.method == 'POST':
        form = ProblemForm(request.POST, request.FILES)
    else:
        form = ProblemForm()

    # Save form datas and redirect to main page
    if form.is_valid():
        problem = Problem(
            name = form.cleaned_data['name'],
            soluce_language = form.cleaned_data['soluce_language'],
            soluce_code = form.cleaned_data['soluce_code']
        )
        problem.save()
        description = ProblemDescription(
            problem = problem,
            language = form.cleaned_data['language'],
            name = form.cleaned_data['name'],
            content = form.cleaned_data['description']

        )
        description.save()
        return redirect(home)

    else:
        context = {
            'form': form
        }
        template = get_template('creation.html')
        return HttpResponse(template.render(context, request))
