from django.urls import path
from django.contrib import admin
#from django.conf import settings
from django.conf.urls.static import static
#from django.contrib.auth import views as auth_views
from . import views
from .views import (
    home, search_suggestions, tag_suggestions, edit_query,
    mark_as_solution, edit_answer, remove_attachment,
    edit_comment, remove_comment_attachment, remove_question_attachment
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('QueryManager/', views.home, name='home'),
    path('QueryManager/detail/<int:id>/', views.detail, name='detail'),
    path('QueryManager/save-comment', views.save_comment, name='save-comment'),
    path('QueryManager/save-upvote', views.save_upvote, name='save-upvote'),
    path('QueryManager/save-downvote', views.save_downvote, name='save-downvote'),
    # User Register
    path('QueryManager/accounts/register/', views.register, name='register'),
    # Profile
    path('QueryManager/accounts/profile/', views.profile, name='profile'),
    # Search Suggestions
    path('search_suggestions/', search_suggestions, name='search_suggestions'),
    # Tags Suggestions changes 18/2/25
    path('tag_suggestions/', tag_suggestions, name='tag_suggestions'),
    # Tag Page
    path('QueryManager/tag/<slug:tag>/', views.tag, name='tag'), 
    # Tags Page
    path('QueryManager/tags/', views.tags, name='tags'), 
    # Logout
    path('QueryManager/accounts/logout/', views.custom_logout, name='logout'),
    # Update status
    path('update-status/<int:quest_id>/', views.update_status, name='update-status'),
    # Delete Question
    path('QueryManager/delete-question/<int:question_id>/', views.delete_question, name='delete-question'),
    # Delete Answer
    path('QueryManager/delete-answer/<int:answer_id>/', views.delete_answer, name='delete-answer'),
    # Delete Comment
    path('QueryManager/delete-comment/<int:comment_id>/', views.delete_comment, name='delete-comment'),
    # Mark as solution 21/2/25
    path('mark-as-solution/<int:answer_id>/', mark_as_solution, name='mark-as-solution'),
    # Edit answer 21/2/25
    path('edit_answer/<int:answer_id>/', edit_answer, name='edit_answer'),
    # Remove Answer attachment 21/2/25
    path('remove-attachment/<int:attachment_id>/', remove_attachment, name='remove_attachment'),
    # Edit Comment 21/2/25
    path('edit-comment/<int:comment_id>/', edit_comment, name='edit_comment'),
    # Remove Comment attachment 21/2/25
    path('remove-comment-attachment/<int:attachment_id>/', remove_comment_attachment, name='remove_comment_attachment'),
    # Edit Query 24/2/25
    path("edit/<int:quest_id>/", edit_query, name="edit_query"),
    # Remove Question attachment 24/2/25
    path('remove-question-attachment/<int:attachment_id>/', remove_question_attachment, name='remove_question_attachment'),
    # Help
    path('QueryManager/help/', views.help, name='help'),
    #path('QueryManager/accounts/password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    #path('QueryManager/accounts/password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='main/password_reset_done.html'), name='password_reset_done'),
    #path('QueryManager/accounts/password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='main/password_reset_confirm.html'), name='password_reset_confirm'),
    #path('QueryManager/accounts/password-reset-complete', auth_views.PasswordResetCompleteView.as_view(template_name='main/password_reset_complete.html'), name='password_reset_complete'),
]

#+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
#   static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)