from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from tracklist.views import (
    tracklist_form,
    view_assigned_tasks,
    update_task_status,
    success_page,
)

# ✅ Import all required views
from models.views import index, live_video_feed, predict_waste

urlpatterns = [
    path("", include("accounts.urls")),
    path("leaderboard/", include("leaderboard.urls")),
    path("admin/", admin.site.urls),

    # Tracklist-related
    path("tracklist/", tracklist_form, name="tracklist"),
    path("assigned_tasks/", view_assigned_tasks, name="assigned_tasks"),
    path("update_task_status/<int:task_id>/", update_task_status, name="update_task_status"),
    path("success_page/", success_page, name="success"),

    # Litter detection & video
    path("litter/", index, name="litter"),
    path("live_feed/", live_video_feed, name="live_video_feed"),

    # ✅ Waste Classification
    path("predict_waste/", predict_waste, name="predict_waste"),
]

# Static & media file serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
