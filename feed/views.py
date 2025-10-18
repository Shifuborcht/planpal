# feed/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from connect.models import Friendship  # or wherever your friend model lives
from .models import Activity

@login_required
def create_activity(request):
    if request.method == "POST":
        content = request.POST.get("content")
        activity = Activity.objects.create(user=request.user, content=content)

        # Send update to all friends through WebSockets
        channel_layer = get_channel_layer()
        friends = Friendship.objects.filter(from_user=request.user).values_list('to_user', flat=True)

        for friend_id in friends:
            async_to_sync(channel_layer.group_send)(
                f"user_{friend_id}",
                {
                    "type": "feed_update",
                    "message": f"{request.user.username} posted a new activity!",
                    "activity": {
                        "user": request.user.username,
                        "content": content,
                    },
                }
            )

        return redirect("feed_view")

    return render(request, "feed/create_activity.html")


# feed/views.py
@login_required
def feed_view(request):
    friends = Friendship.objects.filter(from_user=request.user).values_list('to_user', flat=True)
    activities = Activity.objects.filter(user__in=list(friends) + [request.user]).order_by('-created_at')
    return render(request, 'feed/feed.html', {'activities': activities})
