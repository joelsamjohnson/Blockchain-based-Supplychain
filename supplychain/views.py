import os, json, requests
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .ethereum_utils import get_web3_connection, get_contract_instance, send_transaction
from .models import User, Product, Register
from django.shortcuts import render, redirect
from .forms import AddEntityForm, AddProductForm, LoginForm, RegisterForm, CreateUserForm
from web3 import Web3


web3 = get_web3_connection()
def get_project_root():
    return os.path.dirname(os.path.dirname(__file__))

def get_contract_instance(web3, contract_address, abi_filename):
    abi_path = os.path.join(get_project_root(), 'assets', 'contracts', abi_filename)
    try:
        with open(abi_path, 'r') as abi_file:
            contract_abi = json.load(abi_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"ABI file not found at {abi_path}")
    
    return web3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=contract_abi)

account_from = {
            "private_key": "0x1daed4c35596cef9987e4e4bcf45c58d1952dbe7bb679506ead491dbbf2e579f",
            "address": '0x3f46FE5766AA1D350512d75C4A67176611140391',
        }
# Product Contract Setupaw
contract_address = '0xf4BFCE0A5B51afb70F5FA63181644F85637d1c02'
abi_filename = 'TransactionManagementABI.json'
contract = get_contract_instance(web3, contract_address, abi_filename)

@csrf_exempt  # Use cautiously, ensure proper CSRF handling
def pin_image_to_ipfs(request):
    if request.method == 'POST' and request.FILES:
        image_file = request.FILES.get('image_file')
        if image_file:
            url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
            headers = {
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiJkYTk2OTc4ZS02NWJiLTQwOGEtYTAzMS0yZGFhN2ViY2IyMDMiLCJlbWFpbCI6ImpvZWxzYW1qb2huc29uQHlhaG9vLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwaW5fcG9saWN5Ijp7InJlZ2lvbnMiOlt7ImlkIjoiRlJBMSIsImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxfSx7ImlkIjoiTllDMSIsImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxfV0sInZlcnNpb24iOjF9LCJtZmFfZW5hYmxlZCI6ZmFsc2UsInN0YXR1cyI6IkFDVElWRSJ9LCJhdXRoZW50aWNhdGlvblR5cGUiOiJzY29wZWRLZXkiLCJzY29wZWRLZXlLZXkiOiJiYTViNDljZDljOTUyY2JiNzhlYSIsInNjb3BlZEtleVNlY3JldCI6ImY5ZmIzMDg3MTE1Y2Y2MWVkOTk0YWZiOTVhZjYzNWQwZjgyOGUzOGIzNzlhNGViOGE2ZDhhNGQ4OWI0NzJjYjIiLCJpYXQiOjE3MTQ4ODUyNzd9.LnfSkclSo3E5WygrsMwkVieZGot00R0yBlFkxMWF5Sc"  # Replace YOUR_API_KEY with the actual key
            }
            files = {'file': (image_file.name, image_file, image_file.content_type)}
            response = requests.post(url, files=files, headers=headers)
            if response.status_code == 200:
                ipfs_hash = response.json().get('IpfsHash')
                return JsonResponse({'success': True, 'ipfs_hash': ipfs_hash})
            else:
                return JsonResponse({'success': False, 'error': 'Failed to pin image'}, status=500)
        else:
            return JsonResponse({'error': 'No image file provided'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method or no file found'}, status=400)


def add_product(request):
    if request.method == "POST":
        form = AddProductForm(request.POST)
        if form.is_valid():
            _name = form.cleaned_data['name']
            _description = form.cleaned_data['description']
            _price = form.cleaned_data['price']
            _image = request.FILES['image']
            Product.objects.create(name=_name, description=_description, price=_price, image=_image)
    else:
        form = AddProductForm()
    
     # Fetch product details from the blockchain
    products = []
    prod_ctr = contract.functions.productCtr().call()
    for i in range(1, prod_ctr + 1):  # Ensure the range starts at 1
        product = contract.functions.ProductStock(i).call()
        products.append({
            'id': product[0],
            'name': product[1],
            'description': product[2],
            'price': product[3],
            'image_hash': product[4],
            'MANid': product[5],
            'DISid': product[6],
            'RETid': product[7],
            'stage': product[8],
        })

    return render(request, 'add_order.html', {'products': products, 'form': form})

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
        current_stage_number = int(product[8])
        context = {
            'product_id': product[0],
            'product_name': product[1],
            'product_description': product[2],
            'product_price': product[3],
            'product_image_url': f'https://amethyst-realistic-camel-859.mypinata.cloud/ipfs/{product[4]}'+'?pinataGatewayToken=MgL8ssK-torTK_vfvilq04TZ6BpK1cdpQFCc6fRLD-K8dQ4g8f2SplukNJ-sGXrJ',
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
            return userdetails[2], userdetails[3] 

        man_id, dis_id, ret_id = product[5], product[6], product[7]

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
        return redirect('supply_login')
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
    products = []
    prod_ctr = contract.functions.productCtr().call()
    for i in range(1, prod_ctr + 1):  # Ensure the range starts at 1
        product = contract.functions.ProductStock(i).call()
        products.append({
            'id': product[0],
            'name': product[1],
            'description': product[2],
            'price': product[3],
            'image_hash': product[4],
            'MANid': product[5],
            'DISid': product[6],
            'RETid': product[7],
            'stage': product[8],
        })
    return render(request, 'supply.html', {'products':products})

def track_product(request):
    return render(request, 'track_product.html')

def manage(request):
    return render(request, 'view_orders.html')

@login_required(login_url='customer_login')
def customer_home(request):
    product_count = contract.functions.productCtr().call()

    products = []
    for i in range(1, product_count + 1):
        product = contract.functions.ProductStock(i).call()
        if product[8] == 3:  # Assuming stage is returned as int
            product_data = {
                'id': i,
                'name': product[1],
                'price': product[3],
                'imageHash': product[4],
            }
            products.append(product_data)

    return render(request, 'custom_home.html', {'products': products})

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