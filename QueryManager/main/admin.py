from django.contrib import admin
from django.contrib.admin.models import LogEntry
from simple_history.admin import SimpleHistoryAdmin
from .models import *

# Register Question with History Tracking
@admin.register(Question)
class QuestionAdmin(SimpleHistoryAdmin):
    list_display = ('issue', 'user')
    search_fields = ('issue', 'detail')

# Register Answer with History Tracking
@admin.register(Answer)
class AnswerAdmin(SimpleHistoryAdmin):
    list_display = ('question', 'user', 'mark_solution')

# Register Comment with History Tracking
@admin.register(Comment)
class CommentAdmin(SimpleHistoryAdmin):
    list_display = ('answer', 'comment')

# Register CustomUser with History Tracking
@admin.register(CustomUser)
class CustomUserAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'username', 'email', 'region')

# Register UpVote & DownVote
@admin.register(UpVote)
class UpvoteAdmin(admin.ModelAdmin):
    list_display = ('answer', 'user')

@admin.register(DownVote)
class DownvoteAdmin(admin.ModelAdmin):
    list_display = ('answer', 'user')

# Log Entry for Admin Actions
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("action_time", "user", "content_type", "object_repr", "action_flag", "change_message")
    list_filter = ("action_flag", "content_type", "user")
    search_fields = ("object_repr", "change_message")
    date_hierarchy = "action_time"

    # Prevent modification of logs
    def has_add_permission(self, request):
        return False  

    def has_change_permission(self, request, obj=None):
        return False  

    def has_delete_permission(self, request, obj=None):
        return False  