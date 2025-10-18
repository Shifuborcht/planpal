from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import FriendRequest, Friendship
from django.shortcuts import render
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@login_required
@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if to_user != request.user and not FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
        FriendRequest.objects.create(from_user=request.user, to_user=to_user)

        # Notify the recipient
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{to_user.id}",
            {"type": "friend_update", "action": "received_request", "from_user": request.user.username}
        )

    return redirect('suggestions')

@login_required
def accept_friend_request(request, request_id):
    fr = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    
    # Create friendships
    if not Friendship.objects.filter(from_user=fr.from_user, to_user=fr.to_user).exists():
        Friendship.objects.create(from_user=fr.from_user, to_user=fr.to_user)
    if not Friendship.objects.filter(from_user=fr.to_user, to_user=fr.from_user).exists():
        Friendship.objects.create(from_user=fr.to_user, to_user=fr.from_user)

    fr.delete()

    channel_layer = get_channel_layer()
    # Notify the sender
    async_to_sync(channel_layer.group_send)(
        f"user_{fr.from_user.id}",
        {"type": "friend_update", "action": "request_accepted", "by_user": request.user.username}
    )
    # Notify the accepter
    async_to_sync(channel_layer.group_send)(
        f"user_{request.user.id}",
        {"type": "friend_update", "action": "accepted_request", "by_user": fr.from_user.username}
    )

    return redirect('friends')



@login_required
def friends_view(request):
    from django.db.models import Q
    from .models import Friendship, FriendRequest

    # --- Accepted friends ---
    friendships = Friendship.objects.filter(Q(from_user=request.user) | Q(to_user=request.user))
    friends = set()
    for f in friendships:
        if f.from_user == request.user:
            friends.add(f.to_user)
        else:
            friends.add(f.from_user)

    # --- Incoming friend requests (people who sent me a request) ---
    incoming_requests = FriendRequest.objects.filter(to_user=request.user)

    context = {
        'friends': friends,
        'incoming_requests': incoming_requests,
    }

    return render(request, 'connect/friends.html', context)


    return render(request, 'connect/friends.html', context)
@login_required
def unfriend(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    Friendship.objects.filter(
        Q(from_user=request.user, to_user=other_user) |
        Q(from_user=other_user, to_user=request.user)
    ).delete()

    channel_layer = get_channel_layer()
    # Notify the other user
    async_to_sync(channel_layer.group_send)(
        f"user_{other_user.id}",
        {"type": "friend_update", "action": "unfriended", "by_user": request.user.username}
    )
    return redirect('friends')


@login_required
def suggestions(request):
    from .models import Friendship, FriendRequest
    from django.db.models import Q
    from django.contrib.auth.models import User

    # All users except myself
    users = User.objects.exclude(id=request.user.id)

    # Get my friends (both directions)
    friendships = Friendship.objects.filter(Q(from_user=request.user) | Q(to_user=request.user))
    friends = set()
    for f in friendships:
        if f.from_user == request.user:
            friends.add(f.to_user)
        else:
            friends.add(f.from_user)

    # Pending friend requests sent by me
    pending_requests = FriendRequest.objects.filter(from_user=request.user).values_list('to_user', flat=True)

    # Build suggestion list
    suggestions = []
    for user in users:
        if user in friends:
            continue  # Skip friends
        elif user.id in pending_requests:
            status = 'pending'
        else:
            status = 'not_following'
        suggestions.append({'user': user, 'status': status})

    # Show pending first
    suggestions.sort(key=lambda x: 0 if x['status'] == 'pending' else 1)

    return render(request, 'connect/suggestions.html', {'suggestions': suggestions})

    return render(request, 'connect/suggestions.html', {'suggestions': suggestions})
@login_required
def friend_requests(request):
    requests = FriendRequest.objects.filter(to_user=request.user)
    return render(request, 'connect/friend_requests.html', {'requests': requests})

@login_required
def cancel_friend_request(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    # Delete pending request if exists
    FriendRequest.objects.filter(from_user=request.user, to_user=other_user).delete()
    return redirect('suggestions')

@login_required
def decline_friend_request(request, request_id):
    FriendRequest.objects.filter(id=request_id, to_user=request.user).delete()
    return redirect('friends')


def home(request):
    return render(request, "connect/home.html")