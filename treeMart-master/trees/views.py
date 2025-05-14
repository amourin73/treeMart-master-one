from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from trees.models import Tree, Rating
from trees.forms import TreeForm

# Create your views here.
def create_tree(request):
    if request.method == "POST":
        form = TreeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('tree_list')
        else:
            # Log form errors for debugging
            print("Form Errors:", form.errors)
    else:
        form = TreeForm()

    return render(request, 'treeform.html', {'form': form})


def update_tree(request, t_id):
    tree_instance = get_object_or_404(Tree, pk=t_id)  # Handle 404 if tree not found
    if request.method == "POST":
        form = TreeForm(request.POST, request.FILES, instance=tree_instance)
        if form.is_valid():
            form.save()
            return redirect('tree_list')
        else:
            # Log form errors for debugging
            print("Form Errors:", form.errors)
    else:
        form = TreeForm(instance=tree_instance)

    return render(request, 'treeform.html', {'form': form})

def delete_tree(request,t_id):
    Tree.objects.get(pk=t_id).delete()
    return redirect('tree_list')



def tree_list(request):
    query = request.GET.get('q', '')  # Get the search query from the request
    if query:
        trees = Tree.objects.filter(name__icontains=query)  # Filter trees by name
    else:
        trees = Tree.objects.all()  # If no query, show all trees
    context = {
        'trees': trees,
        'query': query,
    }
    return render(request, 'tree.html', context)


def photo_list(request):
    photos = Tree.objects.all()
    return render(request, 'photo_list.html', {'photos': photos})

def photo_upload(request):
    if request.method == 'POST':
        form = TreeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('photo_list')
    else:
        form = TreeForm()
    return render(request, 'photo_upload.html', {'form': form})


# Add item to cart
def add_to_cart(request, t_id):
    tree = get_object_or_404(Tree, pk=t_id)

    # Debugging session data to ensure the 'cart' structure is correct
    if not isinstance(request.session.get('cart', {}), dict):
        request.session['cart'] = {}  # Reset cart to an empty dictionary

    # Retrieve the cart from the session
    cart = request.session.get('cart', {})

    # Convert t_id to a string for session storage consistency
    t_id_str = str(t_id)

    # Increment quantity if the item is already in the cart, otherwise set it to 1
    if t_id_str in cart:
        cart[t_id_str] += 1
    else:
        cart[t_id_str] = 1

    # Save the updated cart back to the session
    request.session['cart'] = cart

    return redirect('tree_list')

def clear_cart(request):
    request.session['cart'] = {}
    return redirect("/")

# Display cart
from django.shortcuts import render, redirect
from trees.models import Tree

def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total_price = 0  # Initialize total price

    for t_id, quantity in cart.items():
        tree = Tree.objects.get(pk=int(t_id))
        subtotal = tree.price * quantity
        total_price += subtotal  # Calculate total price
        items.append({
            'tree': tree,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(request, 'cart.html', {'cart_items': items, 'total_price': total_price})


def update_cart_quantity(request, t_id, action):
    """Update the quantity of an item in the cart."""
    cart = request.session.get('cart', {})
    if str(t_id) in cart:
        if action == 'increase':
            cart[str(t_id)] += 1
        elif action == 'decrease' and cart[str(t_id)] > 1:
            cart[str(t_id)] -= 1
        elif action == 'remove':
            del cart[str(t_id)]
        request.session['cart'] = cart

    return redirect('view_cart')

# Remove item from cart
def remove_from_cart(request, t_id):
    cart = request.session.get('cart', {})
    if str(t_id) in cart:
        del cart[str(t_id)]
    request.session['cart'] = cart
    return redirect('view_cart')



def rate_tree(request):
    """Allow a user to rate or update their rating for a tree."""
    if request.method == 'POST' and request.user.is_authenticated:
        tree_id = request.POST.get('tree_id')
        rating_value = int(request.POST.get('rating'))

        if not (1 <= rating_value <= 5):
            return JsonResponse({'success': False, 'error': 'Invalid rating value.'})

        tree = get_object_or_404(Tree, id=tree_id)

        # Check if the user already rated this tree
        rating, created = Rating.objects.get_or_create(user=request.user, tree=tree)
        if not created:
            # Update total_rating by subtracting the old rating first
            tree.total_rating -= rating.rating
        tree.total_rating += rating_value
        rating.rating = rating_value
        rating.save()

        # Update the number of ratings and save the tree
        tree.num_ratings = tree.ratings.count()
        tree.save()

        return JsonResponse({
            'success': True,
            'average_rating': tree.average_rating
        })

    return JsonResponse({'success': False, 'error': 'Invalid request method or user not authenticated.'})