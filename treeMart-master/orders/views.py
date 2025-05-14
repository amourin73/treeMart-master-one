from django.shortcuts import render

# Create your views here.
# views.py (inside the 'orders' app)

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Order, OrderItem
# from trees.models import Cart  # Assuming cart items are in the 'cart' app
from django.contrib.auth.decorators import login_required
from trees.models import Tree

@login_required
def place_order(request):
    # Fetch cart items from session
    cart = request.session.get('cart', {})

    if not cart:
        return HttpResponse("Your cart is empty.", status=400)

    # Calculate the total price
    total_price = 0
    order_items = []  # List to store order items

    # Iterate through the cart and prepare order items
    for t_id, quantity in cart.items():
        tree = Tree.objects.get(id=int(t_id))
        subtotal = tree.price * quantity
        total_price += subtotal
        order_items.append({
            'tree': tree,
            'quantity': quantity,
            'subtotal': subtotal
        })

    # Create an order for the user
    order = Order.objects.create(user=request.user, total_price=total_price)

    # Add items to the order
    for item in order_items:
        OrderItem.objects.create(
            order=order,
            tree=item['tree'],
            quantity=item['quantity'],
            subtotal=item['subtotal']
        )

    # Optionally, clear the cart after placing the order
    request.session['cart'] = {}

    return redirect('order_confirmation', order_id=order.id)
@login_required
def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})

