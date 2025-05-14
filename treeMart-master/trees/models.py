# models.py
from django.contrib.auth.models import User
from django.db import models


class Tree(models.Model):
    SEASON_CHOICES = [
        ('summer', 'Summer'),
        ('winter', 'Winter'),
        ('spring', 'Spring'),
        ('autumn', 'Autumn'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    season = models.CharField(max_length=20, choices=SEASON_CHOICES, default='other')
    description = models.TextField(blank=True, null=True)  # Optional description field
    care_tips = models.TextField(blank=True, null=True)  # Optional care tips field
    image = models.ImageField(upload_to='tree_images/', null=True, blank=True)
    total_rating = models.IntegerField(default=0)  # Field to store total rating points
    num_ratings = models.PositiveIntegerField(default=0)




    @property
    def average_rating(self):
        """Calculate and return the average rating."""
        if self.num_ratings > 0:
            return self.total_rating / self.num_ratings
        return 0

def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)




    @property
    def subtotal(self):
        return self.tree.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.tree.name} for {self.user.username}"

    class Meta:
        unique_together = ('user', 'tree')




class Rating(models.Model):
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
