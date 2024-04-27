import os
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .ethereum_utils import get_web3_connection, get_contract_instance, send_transaction
from .models import User, Product, Register
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import AddEntityForm, AddProductForm, LoginForm, RegisterForm, CreateUserForm


web3 = get_web3_connection()
contract_address = '0x65cf33Ef7b25d4365FeEcBd292c359E833d9b4DB'
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
    

def add_product_to_blockchain(name, description, price):
    try:
        function_name = 'addproduct'
        args = [name, description, price]
        # Ensure that `send_transaction` is capable of handling the connection and sending data to the blockchain
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
            _price = form.cleaned_data['price']
            # Create a Product instance in Django database
            Product.objects.create(name=_name, description=_description, price=_price)

            # Call blockchain function
            result = add_product_to_blockchain(_name, _description, _price)
            if result['success']:
                print(result)
                return redirect('success_url')  # Make sure 'success_url' is defined in your urls.py
            else:
                # Handle the error, maybe show a message to the user
                pass
    else:
        form = AddProductForm()

    return render(request, 'add_order.html', {'form': form})

def product_details_initial(request):
    # This view just renders the template initially without product details.
    # Actual product details are fetched via AJAX using the `show_product_stage` view.
    return render(request, 'product_details.html')

@require_http_methods(["GET"])
def show_product_details(request, product_id):
    try:
        product = contract.functions.ProductStock(product_id).call()
        stage_descriptions = {
            0: "Product Ordered",
            1: "Manufacturing Stage",
            2: "Distribution Stage",
            3: "Retailing Stage",
            4: "Sold",
        }
        current_stage_number = int(product[7])
        context = {
            'product_id': product[0],
            'product_name': product[1],
            'product_description': product[2],
            'product_price': product[3],
            'processing_stage': stage_descriptions.get(current_stage_number, "Unknown Stage"),
        }

        # Function to get user details from the blockchain
        def get_user_details(user_id, user_type):
            if user_id == 0:
                return "Empty", "Empty"  
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
        man_id, dis_id, ret_id = product[4], product[5], product[6]
        print(f"Product data from blockchain: {product}")
        print(f"Manufacturer ID: {man_id}")

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


def supply_login(request):
    msg = None

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
                    
            except Register.DoesNotExist:
                msg = "Username does not exist."
        else:
            msg = "Please correct the errors below."
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form, 'msg':msg})



def supply(request):
    return render(request, 'supply.html')

def track_product(request):
    return render(request, 'track_product.html')

def manage(request):
    return render(request, 'view_orders.html')

@login_required(login_url='customer_login')
def customer_home(request):
    return render(request, 'custom_home.html')

def customer_register(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            return redirect('customer_login')
    context = {'form':form}
    return render(request, 'accounts/register.html', context)

def customer_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('customer_home')
        else:
            messages.info(request, "Username or Password is incorrect")
    context = {}
    return render(request, 'accounts/login.html', context)

def customer_logout(request):
    print(f"Logging out {request.user.username}")
    logout(request)
    return redirect('customer_login')