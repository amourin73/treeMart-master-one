
from django.db import models

from django.contrib.auth.models import User

from django.db.models.signals import post_save

from django.dispatch import receiver





# Profile model that extends the User model

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)



    # Differentiating user roles

    USER_TYPE_CHOICES = [

        ('admin', 'Admin'),

        ('seller', 'Seller'),

        ('buyer', 'Buyer'),

    ]

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='buyer')



    bio = models.TextField(blank=True)

    location = models.CharField(max_length=100, blank=True)

    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)



    def __str__(self):

        return f"{self.user.username} ({self.get_user_type_display()})"



    # Method to check if the user is a seller

    def is_seller(self):

        return self.user_type == 'seller'

    def is_buyer(self):
        return self.user_type == 'buyer'

    # Method to check if the user is an admin

    def is_admin(self):

        return self.user_type == 'admin'






    class Meta:

        permissions = [

            ("can_add_profile", "Can add profile"),

            ("can_change_profile", "Can change profile"),

            ("can_delete_profile", "Can delete profile"),

            ("can_view_profile", "Can view profile"),

        ]





# Signal to create or update the profile when the User is saved

@receiver(post_save, sender=User)

def create_or_update_user_profile(sender, instance, created, **kwargs):



    if created:

        # Create profile when a new user is created

        Profile.objects.create(user=instance)

    else:

        # Update the profile when the user is updated

        instance.profile.save()



def get_user_type_display(self):

    return dict(self.USER_TYPES).get(self.user_type, 'Unknown')