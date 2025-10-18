from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

class Friendship(models.Model):
    from_user = models.ForeignKey(User, related_name='friendships_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friendships_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username}"


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def can_view(self, viewer):
        return viewer == self.user or viewer in self.user.get_friends()


# ✅ Add this part at the bottom of the file:
def get_friends(self):
    friendships = Friendship.objects.filter(
        Q(from_user=self) | Q(to_user=self)
    )
    friends = []
    for f in friendships:
        if f.from_user == self:
            friends.append(f.to_user)
        else:
            friends.append(f.from_user)
    return friends

User.add_to_class("get_friends", get_friends)

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username}"
