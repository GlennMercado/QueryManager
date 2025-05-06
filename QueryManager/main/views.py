from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Question, Answer, Comment, UpVote, DownVote, QuestionAttachment, AnswerAttachment, CommentAttachment, CustomUser
from django.core.paginator import Paginator
from django.contrib import messages
from .forms import AnswerForm, QuestionForm, ProfileForm, CustomUserCreationForm, CommentForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Count, Prefetch
from django.utils import timezone
from django.template.defaultfilters import slugify
from taggit.models import Tag
from django.http import Http404
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse

# Logout
def custom_logout(request):
    logout(request)
    return redirect(settings.LOGIN_URL)
# Question Filter
def get_filtered_questions(q, status_filter, tag_filter, category_filter):
    """Helper function to filter questions based on search and filters."""
    queryset = Question.objects.all().annotate(total_comments=Count('answer__comment')).filter(issue__icontains=q)
    
    if status_filter == 'resolved':
        queryset = queryset.filter(status=True)
    elif status_filter == 'unresolved':
        queryset = queryset.filter(status=False)
    # Automated
    if category_filter == 'HotDocs':
        queryset = queryset.filter(category="HotDocs")
    elif category_filter == 'Document Drafter':
        queryset = queryset.filter(category="Document Drafter")
    # Major works
    elif category_filter == 'Formatting':
        queryset = queryset.filter(category="Formatting")
    elif category_filter == 'Editing':
        queryset = queryset.filter(category="Editing")
    elif category_filter == 'Conversion':
        queryset = queryset.filter(category="Conversion")

    if tag_filter:
        queryset = queryset.filter(tags__name__in=[tag_filter])

    # Prefetch related tags and attachments in a single query to reduce database hits.
    queryset = queryset.prefetch_related('tags', Prefetch('attachments', queryset=QuestionAttachment.objects.all().order_by('-id')))
    
    return queryset.order_by('-id')

def reverse_attachments_for_questions(quests):
    """Helper function to reverse attachments for each question."""
    for quest in quests:
        quest.attachments_reversed = quest.attachments.all()

def handle_question_submission(request):
    """Helper function to handle POST requests for new questions."""
    form = QuestionForm(request.POST)
    if form.is_valid():
        question = form.save(commit=False)
        question.user = request.user
        question.save()

        attachments = [
            QuestionAttachment(question=question, file=file) 
            for file in request.FILES.getlist('attachments')
        ]
        QuestionAttachment.objects.bulk_create(attachments)
        
        form.save_m2m()  # Save tags
        messages.success(request, "Your query has been posted.")
        send_notification_email(question)
        return redirect('home')
    else:
        messages.error(request, 'Please fill in all the required fields correctly.')
        return form

def send_notification_email(question):
    # Generate the full URL
    detail_url = f"{settings.SITE_URL}{reverse('detail', args=[question.id])}"
    
    subject = 'New Query Submitted'
    
    # Plain text message (fallback for email clients that do not support HTML)
    text_message = (
        f"Hello,"
        f"This is a notification to inform you that a new query has been posted on our platform by {question.user.username}.\n\n"
        f"Issue: {question.issue}\n"
        f"Detail: {question.detail}\n"
        f"You can view the query by clicking the link below:\n"
        f"View the question: {detail_url}\n\n"
        f"Please note: This email is for notification purposes only. Replies to this email address are not monitored, and you will not receive a response. "
        f"For further actions or to engage with the query, kindly visit our platform."
        f"Thank you,"
        f"Query Manager"
    )

    # HTML message
    html_message = (
        f"<p>Hello,</p>"
        f"<p>This is a notification to inform you that a new query has been posted on our platform by <strong>{question.user.username}</strong>.</p>"
        f"<p><strong>Issue:</strong> {question.issue}</p>"
        f"<p><strong>Detail:</strong> {question.detail}</p>"
        f"<p>You can view the query by clicking the link below:</p>"
        f"<p><a href='{detail_url}' target='_blank'>View Query</a></p>"
        f"<p><em>Please note:</em> This email is for notification purposes only. Replies to this email address are not monitored, and you will not receive a response.</p>"
        f"<p>For further actions or to engage with the query, kindly visit our platform.</p>"
        f"<p>Thank you,</p>"
        f"<p>Query Manager</p>"
    )
    
    # Get all user emails from the CustomUser model
    user_emails = CustomUser.objects.values_list('email', flat=True)

    # Send the email
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=user_emails
    )
    
    # Attach the HTML message as an alternative
    email.attach_alternative(html_message, "text/html")
    email.send()

@login_required
def home(request):
    # Get search and filters
    q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'all')
    tag_filter = request.GET.get('tag', None)
    category_filter = request.GET.get('category', 'all')

    # Get filtered questions
    quests = get_filtered_questions(q, status_filter, tag_filter, category_filter)

    # Reverse attachments for each quest
    reverse_attachments_for_questions(quests)

    # Check if no results
    no_results = not quests.exists()

    # Handle POST request for new questions
    if request.method == 'POST':
        form = handle_question_submission(request)
        if isinstance(form, QuestionForm):
            return render(request, 'home.html', {'form': form, 'quests': quests, 'tag_filter': tag_filter, 'no_results': no_results})
        return redirect('home')

    else:
        form = QuestionForm()

    # Pagination
    paginator = Paginator(quests, 5)
    page_num = request.GET.get('page', 1)
    quests = paginator.page(page_num)

    # Check if the request is an AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'question_list.html', {'quests': quests})

    return render(request, 'home.html', {'form': form, 'quests': quests, 'tag_filter': tag_filter, 'no_results': no_results})

# Search
def search_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = []

    if query:
        questions = Question.objects.filter(issue__icontains=query)[:5]
        for question in questions:
            suggestions.append(question.issue)

        details = Question.objects.filter(detail__icontains=query)[:5]
        for detail in details:
            suggestions.append(detail.detail)

        referenceforms = Question.objects.filter(referenceform__icontains=query)[:5]
        for referenceform in referenceforms:
            suggestions.append(referenceform.referenceform)

        tags = Question.objects.filter(tags__name__icontains=query)[:5]
        for question in tags:
            for tag in question.tags.all():
                suggestions.append(tag.name)

    return JsonResponse(suggestions, safe=False)

# Tag Suggestions 18/2/25
def tag_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = []

    if query:
        tags = Tag.objects.filter(name__icontains=query).values_list('name', flat=True)[:5]
        suggestions = list(tags)

    return JsonResponse(suggestions, safe=False)

# Detail
def detail(request, id):
    quest = get_object_or_404(Question, pk=id)
    tags = quest.tags.all()
    answers = Answer.objects.filter(question=quest).order_by('-add_time')
    answerform = AnswerForm()

    # Get all attachments for the question and answers
    quest.attachments_reversed = quest.attachments.all().order_by('-id')
    for answer in answers:
        answer.attachments_reversed = answer.attachments.all().order_by('-id')

    # Handle POST request for submitting answer
    if request.method == 'POST':
            answerform = AnswerForm(request.POST, request.FILES)
            if answerform.is_valid():
                answer = answerform.save(commit=False)
                answer.question = quest
                answer.user = request.user
                answer.save()

                # Save attachments
                attachments = request.FILES.getlist('attachments')
                for file in attachments:
                    AnswerAttachment.objects.create(answer=answer, file=file)

                messages.success(request, 'Answer has been submitted.')
                return redirect('detail', id=id)
            else:
                messages.error(request, 'Failed to submit the answer.')

    return render(request, 'detail.html', {
        'quest': quest,
        'tags': tags,
        'answers': answers,
        'answerform': answerform
    })

# Update Status
@login_required
def update_status(request, quest_id):
    quest = get_object_or_404(Question, pk=quest_id)
    if request.method == 'POST':
        if request.user == quest.user or request.user.is_superuser:
            status = request.POST.get('status')
            quest.status = bool(int(status))
            quest.save()
            messages.success(request, 'Status updated successfully.')
        else:
            messages.error(request, 'You are not authorized to update this status.')
    return redirect('detail', id=quest_id)

# Save Comment
def save_comment(request):
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        answer_id = request.POST.get('answerid')
        user = request.user

        # Get the answer to which the comment is associated
        answer = Answer.objects.get(id=answer_id)

        # Create and save the comment
        new_comment = Comment.objects.create(
            answer=answer,
            user=user,
            comment=comment_text,
            add_time=timezone.now()
        )

        # Save attachments for the comment
        attachments = request.FILES.getlist('attachments')  # Get all uploaded files
        for file in attachments:
            CommentAttachment.objects.create(comment=new_comment, file=file)

        # Prepare response data with comment details and attachments (if any)
        response_data = {
            'bool': True,
            'comment_id': new_comment.id,
            'username': user.username,
            'profile_picture': user.profile_picture.url if user.profile_picture else '/static/profile_pics/default2.jpg',
            'timestamp': new_comment.add_time.strftime('%Y-%m-%d %H:%M:%S'),
            'can_delete': user == new_comment.user  # User can delete their own comment
        }

        return JsonResponse(response_data)
    
# Save Upvote
def save_upvote(request):
    if request.method == 'POST':
        answer_id = request.POST.get('answerid')
        answer = Answer.objects.get(pk=answer_id)
        user = request.user

        # Check if the user has already upvoted
        upvote = UpVote.objects.filter(answer=answer, user=user).first()

        if (upvote):
            upvote.delete()
            upvote_count = answer.upvote_set.count()
        else:
            UpVote.objects.create(answer=answer, user=user)
            upvote_count = answer.upvote_set.count()

        return JsonResponse({'upvote_count': upvote_count})

# Save Downvote
def save_downvote(request):
    if request.method == 'POST':
        answer_id = request.POST.get('answerid')
        answer = Answer.objects.get(pk=answer_id)
        user = request.user

        downvote = DownVote.objects.filter(answer=answer, user=user).first()

        if downvote:
            downvote.delete()
            downvote_count = answer.downvote_set.count()
        else:
            DownVote.objects.create(answer=answer, user=user)
            downvote_count = answer.downvote_set.count()

        return JsonResponse({'downvote_count': downvote_count})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User has been registered successfully!')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

def tag(request, tag):
    tag_name = tag.replace('-', ' ')  # Replace hyphens with spaces to match tag format in the database

    try:
        # Fetch the tag instance
        tag_instance = Tag.objects.get(name=tag_name)
    except Tag.DoesNotExist:
        raise Http404("No Tag matches the given query.")

    # Fetch questions associated with the tag
    quests = Question.objects.annotate(total_comments=Count('answer__comment')).filter(tags=tag_instance).order_by('-id')

    # Pagination logic
    paginator = Paginator(quests, 5)
    page_num = request.GET.get('page', 1)
    quests = paginator.page(page_num)

    return render(request, 'tag.html', {'quests': quests, 'tag': tag_instance.name})
# Profile
@login_required
def profile(request):
    quests = Question.objects.filter(user=request.user).order_by('-id')
    answers = Answer.objects.filter(user=request.user).order_by('-id')
    comments = Comment.objects.filter(user=request.user).order_by('-id')
    upvotes = UpVote.objects.filter(user=request.user).order_by('-id')
    downvotes = DownVote.objects.filter(user=request.user).order_by('-id')

    profile_form = ProfileForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        if 'profile_form' in request.POST:
            profile_form = ProfileForm(request.POST, request.FILES, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile has been updated.')
                return redirect('profile')
        elif 'password_form' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password has been updated.')
                return redirect('profile')

    return render(request, 'registration/profile.html', {
        'quests': quests,
        'answers': answers,
        'comments': comments,
        'upvotes': upvotes,
        'downvotes': downvotes,
        'profile_form': profile_form,
        'password_form': password_form,
    })

# Tags Page
def tags(request):
    quests = Question.objects.all()
    tags = []
    for quest in quests:
        # Get tags for each question and make sure they are unique
        qtags = [tag.name for tag in quest.tags.all()]
        tags.extend(qtags)

    # Count the occurrences of each tag
    tag_with_count = []
    for tag in set(tags):  # Use set to remove duplicates
        tag_data = {
            'name': tag,
            'count': Question.objects.filter(tags__name=tag).count()
        }
        tag_with_count.append(tag_data)

    return render(request, 'tags.html', {'tags': tag_with_count})

@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.user == question.user or request.user.is_superuser:
        if request.method == 'POST':
            question.delete()
            messages.success(request, 'Question deleted successfully.')
            return redirect('home')
    else:
        messages.error(request, 'You are not authorized to delete this question.')
        return redirect('detail', id=question_id)

@login_required
def delete_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    if request.user == answer.user or request.user.is_superuser:
        if request.method == 'POST':
            question_id = answer.question.id
            answer.delete()
            messages.success(request, 'Answer deleted successfully.')
            return redirect('detail', id=question_id)
    else:
        messages.error(request, 'You are not authorized to delete this answer.')
        return redirect('detail', id=answer.question.id)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.user or request.user.is_superuser:
        if request.method == 'POST':
            question_id = comment.answer.question.id
            comment.delete()
            messages.success(request, 'Comment deleted successfully.')
            return redirect('detail', id=question_id)
    else:
        messages.error(request, 'You are not authorized to delete this comment.')
        return redirect('detail', id=comment.answer.question.id)
def help(request):
    return render(request, 'help.html')

# Changes 24/2/25

@login_required
def mark_as_solution(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    
    if request.method == 'POST':
        if request.user == answer.question.user or request.user.is_superuser:
            mark_solution = request.POST.get('mark_solution')
            answer.mark_solution = bool(int(mark_solution))
            answer.save()
            messages.success(request, 'Answer marked as solution.')
        else:
            messages.error(request, 'You are not authorized to update this answer.')
    
    return redirect('detail', id=answer.question.id)

@login_required
def edit_query(request, quest_id):
    """Handle updating an existing query."""
    quest = get_object_or_404(Question, id=quest_id)

    # Ensure only the owner or superuser can edit
    if request.user != quest.user and not request.user.is_superuser:
        messages.error(request, "You do not have permission to edit this query.")
        return redirect('home')

    if request.method == "POST":
        form = QuestionForm(request.POST, instance=quest)
        if form.is_valid():
            quest = form.save(commit=False)
            quest.save()

            # Handle new file uploads
            if 'attachments' in request.FILES:
                attachments = [
                    QuestionAttachment(question=quest, file=file)
                    for file in request.FILES.getlist('attachments')
                ]
                QuestionAttachment.objects.bulk_create(attachments)

            form.save_m2m()  # Save tags to the Question instance

            messages.success(request, "Your query has been updated successfully.")
            return redirect('detail', id=quest.id)
        else:
            messages.error(request, "Please fill in all required fields correctly.")
    else:
        form = QuestionForm(instance=quest)

    # Pass the tags to the template for rendering
    tags = quest.tags.all()
    return render(request, "detail.html", {"form": form, "quest": quest, "tags": tags})

@login_required
@require_http_methods(["POST"])
def remove_question_attachment(request, attachment_id):
    attachment = get_object_or_404(QuestionAttachment, pk=attachment_id)
    attachment.delete()
    return JsonResponse({"success": True})

@login_required
@require_http_methods(["POST"])
def edit_answer(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id, user=request.user)
    answerform = AnswerForm(request.POST, request.FILES, instance=answer)

    if answerform.is_valid():
        updated_answer = answerform.save(commit=False)
        updated_answer.save()

        # Handle new file uploads
        attachments = request.FILES.getlist('attachments')
        for file in attachments:
            AnswerAttachment.objects.create(answer=updated_answer, file=file)

        messages.success(request, 'Answer updated successfully.')
        return redirect('detail', id=answer.question.id)

    messages.error(request, 'Answer update failed.')
    return redirect('detail', id=answer.question.id)

@login_required
@require_http_methods(["POST"])
def remove_attachment(request, attachment_id):
    attachment = get_object_or_404(AnswerAttachment, pk=attachment_id, answer__user=request.user)
    attachment.delete()
    return JsonResponse({"success": True})

@login_required
@require_http_methods(["POST"])
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, user=request.user)
    comment_form = CommentForm(request.POST, request.FILES, instance=comment)

    if comment_form.is_valid():
        updated_comment = comment_form.save(commit=False)
        updated_comment.save()

        # Handle new file uploads
        attachments = request.FILES.getlist('attachments')
        for file in attachments:
            CommentAttachment.objects.create(comment=updated_comment, file=file)

        messages.success(request, 'Comment updated successfully.')
        return redirect('detail', id=comment.answer.question.id)

    messages.error(request, 'Comment update failed.')
    return redirect('detail', id=comment.answer.question.id)

@login_required
@require_http_methods(["POST"])
def remove_comment_attachment(request, attachment_id):
    attachment = get_object_or_404(CommentAttachment, pk=attachment_id, comment__user=request.user)
    attachment.delete()
    return JsonResponse({"success": True})


# @login_required
# def email_distribution(request):
#     if request.method == 'POST':
#         form = ProfileForm(request.POST, instance=request.user.profile)
#         if form.is_valid():
#             form.save()
#             # Add a success message
#             messages.success(request, 'Your email has been updated successfully!')
#             return redirect('profile')  # Redirect after saving
#         else:
#             # Add an error message if the form is not valid
#             messages.error(request, 'There was an error with the form. Please check your input.')
#     else:
#         form = ProfileForm(instance=request.user.profile)  # Load current profile data

#     return render(request, 'profile.html', {'form': form})