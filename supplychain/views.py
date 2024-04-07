import os

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .ethereum_utils import get_web3_connection, get_contract_instance, send_transaction
from .models import User, Product, Chat, Register
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import AddEntityForm, AddProductForm, LoginForm, RegisterForm


web3 = get_web3_connection()
contract_address = '0x48D248815AAA079DF3DA1773dA7Ec64a34BB631C'
abi_filename = 'myContractABI.json'
project_directory = os.path.dirname(os.path.dirname(__file__))
contracts_directory = os.path.join(project_directory, 'contracts')
abi_path = os.path.join(contracts_directory, abi_filename)
contract = get_contract_instance(web3, contract_address, abi_path)
account_from = {
            "private_key": "8385157bb56738af6c00963de326373848fa55cfbe7082117801f3e96dcaac25",
            "address": '0xb30E2F234958fb7A5D4D3D1c08395B81C7a51803',
        }



def add_entity_to_blockchain(entity_type, address, name, place):
    try:
        function_name = f'add{entity_type}'
        args = [address, name, place]
        tx_hash = send_transaction(web3, contract, function_name, args, account_from['address'], account_from['private_key'])
        return {'success': True, 'transaction_hash': tx_hash}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    

def add_product_to_blockchain(name, description):
    try:
        function_name='addproduct'
        args=[name,description]
        tx_hash = send_transaction(web3, contract, function_name, args, account_from['address'], account_from['private_key'])
        return {'success': True, 'transaction_hash': tx_hash}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def add_product(request):
    if request.method == "POST":
        form = AddProductForm(request.POST)
        if form.is_valid():
            _name = form.cleaned_data['name']
            _description = form.cleaned_data['description']
            Product.objects.create(name=_name,description=_description)

            result = add_product_to_blockchain(_name, _description)
            if result['success']:
                print(result)
                return redirect('success_url')
            else:
                pass
    else:
        form = AddProductForm()
    return render(request, 'add_order.html', {'form': form})

def product_stage_initial(request):
    # This view just renders the template initially without product details.
    # Actual product details are fetched via AJAX using the `show_product_stage` view.
    return render(request, 'product_stage.html')

@require_http_methods(["GET"])
def show_product_stage(request, product_id):
    try:
        product = contract.functions.ProductStock(product_id).call()
        stage_descriptions = {
            0: "Product Ordered",
            1: "Raw Material Supply Stage",
            2: "Manufacturing Stage",
            3: "Distribution Stage",
            4: "Retailing Stage",
            5: "Sold",
        }
        current_stage_number = int(product[7])
        context = {
            'product_id': product[0],
            'product_name': product[1],
            'product_description': product[2],
            'processing_stage': stage_descriptions.get(current_stage_number, "Unknown Stage"),
        }

        # Function to get user details from the blockchain
        def get_user_details(user_id, user_type):
            if user_id == 0:
                return "Empty", "Empty"  # Assuming 0 means no user assigned
            if user_type == 'RMS':
                userdetails = contract.functions.RMS(user_id).call()
            elif user_type == 'MAN':
                userdetails = contract.functions.MAN(user_id).call()
            elif user_type == 'DIS':
                userdetails = contract.functions.DIS(user_id).call()
            elif user_type == 'RET':
                userdetails = contract.functions.RET(user_id).call()
            else:
                return "Invalid Type", "Invalid Type"
            return userdetails[2], userdetails[3]  # Assuming [0] is name and [1] is place

        # Fetch and add user details to context
        rms_id, man_id, dis_id, ret_id = product[3], product[4], product[5], product[6]
        context['RMSname'], context['RMSplace'] = get_user_details(rms_id, 'RMS')
        context['MANname'], context['MANplace'] = get_user_details(man_id, 'MAN')
        context['DISname'], context['DISplace'] = get_user_details(dis_id, 'DIS')
        context['RETname'], context['RETplace'] = get_user_details(ret_id, 'RET')
        print(context)
        return JsonResponse(context)

    except Exception as e:
        context = {'error': str(e)}
        return JsonResponse(context)


def add_entity(request):
    if request.method == "POST":
        form = AddEntityForm(request.POST)
        if form.is_valid():
            entity_type = form.cleaned_data['entity_type']
            address = form.cleaned_data['address']
            name = form.cleaned_data['name']
            place = form.cleaned_data['place']
            User.objects.create(user_type=entity_type, address=address, name=name, place=place)

            result = add_entity_to_blockchain(entity_type, address, name, place)
            if result['success']:
                print(result)
                return redirect('success_url')
            else:
                pass
    else:
        form = AddEntityForm()
        rms = {}
        rms_ctr = contract.functions.rmsCtr().call()
        for i in range(rms_ctr):
            rms[i] = contract.functions.RMS(i + 1).call()
            print(rms[i])

        man = {}
        man_ctr = contract.functions.manCtr().call()
        for i in range(man_ctr):
            man[i] = contract.functions.MAN(i + 1).call()
            print(man[i])

        dis = {}
        dis_ctr = contract.functions.disCtr().call()
        for i in range(dis_ctr):
            dis[i] = contract.functions.DIS(i + 1).call()
            print(dis[i])

        ret = {}
        ret_ctr = contract.functions.retCtr().call()
        for i in range(ret_ctr):
            ret[i] = contract.functions.RET(i + 1).call()
            print(ret[i])

        return render(request, 'register_user.html', {
            'rms': rms,
            'man': man,
            'dis': dis,
            'ret': ret, 'form': form
        })


def register(request):
    if request.method=='POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            Register.objects.create(email=email,password=password)
        return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form':form})

def admin_home_page(request):
    return render(request, 'admin_home.html')

def user_home_page(request):
    return render(request, 'user_home.html')


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = Register.objects.get(email=email)
                if user.email == 'admin@gmail.com' and password == 'admin123':
                    # Set admin-specific session variables
                    request.session['_auth_user_id'] = user.pk  # Assuming admin's ID is still treated specially
                    return redirect('admin_home')
                elif password == user.password:
                    # Regular user login
                    request.session['_auth_user_id'] = user.pk
                    request.session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
                    return redirect('user_home')  # Redirect to a success page.
                else:
                    msg = "Username or Password is incorrect."
                    return render(request, 'error.html', {'msg': msg})
            except Register.DoesNotExist:
                msg = "Username does not exist."
                return render(request, 'error.html', {'msg': msg})
    else:
        form = LoginForm()
        return render(request, 'login.html', {'form': form})



def supply(request):
    return render(request, 'supply.html')

def track_product(request):
    return render(request, 'track_product.html')

def manage(request):
    return render(request, 'view_orders.html')

def chatuser(request):
    try:
        # Assuming the admin has a specific user_id or a distinguishing attribute
        # Replace `admin_id` with the actual admin identification logic
        admin_user = User.objects.get(email='admin@gmail.com') # Example: identifying admin by email
        current_user = User.objects.get(pk=request.session.get('_auth_user_id'))

        # Fetch messages where the current user is the sender or receiver, involving the admin
        chats = Chat.objects.filter(sender=current_user, receiver=admin_user) | Chat.objects.filter(sender=admin_user, receiver=current_user)
        chats = chats.order_by('timestamp')  # Ensure messages are in chronological order

    except User.DoesNotExist:
        return redirect('login')  # Redirect to login if user not found

    return render(request, 'chat_user.html', {'chats': chats, 'admin_user': admin_user, 'current_user': current_user})


def addchat_user(request):
    if request.method == 'POST':
        try:
            admin_user = User.objects.get(email='admin@gmail.com') # Example: identifying admin by email
            current_user = User.objects.get(pk=request.session.get('_auth_user_id'))

            message = request.POST.get('message')

            # Create and save the new chat instance
            Chat.objects.create(sender=current_user, receiver=admin_user, message=message)
        except User.DoesNotExist:
            # Redirect to login if either user not found
            return redirect('login')

    return redirect(reverse('chatuser'))


def user_search(request):
    query = request.GET.get('query', '')
    if query:
        users = Register.objects.filter(name__icontains=query)
    else:
        users = Register.objects.none()
    
    return render(request, 'chat.html', {'users': users})


def viewchat(request):
    user_id = request.session.get('_auth_user_id', None)
    if request.session.get('user_id') == 11:
        users = Register.objects.exclude(email="admin@gmail.com")
        print(users)
        return render(request, 'chat.html', {'users': users})
    elif user_id:
        try:
            current_user = Register.objects.get(pk=user_id)
            # Assuming we want to show admin in the list for regular users
            users = Register.objects.filter(email='admin@gmail.com')
            # Optionally, show other users too for product requests, excluding the current user
            # users = Register.objects.exclude(pk=user_id)
            return render(request, 'chat.html', {'users': users})
        except Register.DoesNotExist:
            # User not found, maybe logout or handle appropriately
            return redirect('login')
    else:
        # No user is logged in
        return redirect('login')

# def viewchatuser(request, user_id):
#     # Handling chat between the current user and the selected user
#     chats = Chat.objects.filter(sender=request.user, receiver_id=user_id) | Chat.objects.filter(sender_id=user_id, receiver=request.user)
#     chats = chats.order_by('timestamp')
#     receiver = User.objects.get(id=user_id)
#     return render(request, 'chat_user.html', {'chats': chats, 'receiver': receiver})


def chatadmin(request, user_id):
    user = Register.objects.get(id=user_id)
    chats = Chat.objects.filter(sender=user) | Chat.objects.filter(receiver=user)
    chats = chats.order_by('timestamp')  # Ensure messages are ordered by time
    
    return render(request, 'chatpage_admin.html', {
        'chats': chats,
        'username': user.name,
        'user_id': user_id
    })
    

def addchat_admin(request):
    if request.method == 'POST':

        user_id = request.POST.get('user_id') 
        message = request.POST.get('message')
        admin_user = Register.objects.first() 
        user = Register.objects.get(id=user_id)
        Chat.objects.create(sender=admin_user, receiver=user, message=message)
        
        return redirect(reverse('chatadmin', user_id=user_id))
    
    return redirect(reverse('chatadmin'))