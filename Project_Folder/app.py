from flask import Flask, render_template, request,redirect,url_for , jsonify, session , abort
import qrcode , datetime,random,os
import firebase_admin
from firebase_admin import credentials , firestore
from google.cloud import firestore



app = Flask(__name__)
app.secret_key = 'secret_key'

config = {
    'apiKey': "",
    'authDomain': "",
    'projectId': "",
    'storageBucket': "",
    'messagingSenderId': "",
    'appId': "",
    'measurementId': "",
    'databaseURL' : "",
    'serviceAccount' : ""
}

cred = credentials.Certificate("Your PAth\service_key.json")

firebase_admin.initialize_app(cred , config)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "Your Path\service_key.json"
db = firestore.Client()

admin_password = "Admin@12345"

qr_img = qrcode.make("Your Host Address/?table_num=1")
qr_img.save('qr-img.JPG')

qr_img_2 = qrcode.make("Your Host Address/?table_num=24")
qr_img_2.save('qr-img-2.JPG')

@app.route('/')
def index():
    global table_number
    table_number = request.args.get('table_num')

    return render_template('index.html')

@app.route('/order', methods=['POST'])
def order():
    now = datetime.datetime.now()
    ct = now.strftime("%d/%m/%Y, %H:%M:%S")
    
    food_items_dict = db.collection('foods').document('foods_and_prices').collection('foods_and_prices').get()
    for doc in food_items_dict:
        food_items = doc.to_dict()

    total_cost = 0
    selected_items = []
    #table_num = request.form['table_no']
    name = request.form['customer_name'].lower()
    mobile_num = request.form['mobile_no']


    for food in food_items:
        if request.form.get(food):
            qty = int(request.form.get(food + '_quantity'))
            if qty > 0:
                selected_items.append((food , qty))
                total_cost = total_cost + (food_items[food] * qty)

    #print(selected_items)


    db.collection('foods').document('all_orders').collection('test_orders').add({'id' : random.randint(1111,9999), 'Name':'{}'.format(name), 'Mobile_Number':'{}'.format(mobile_num) ,'Table_No': '{}'.format(table_number), 'Items' : '{}'.format(selected_items), 'Total' : '{}'.format(total_cost), 'Ordered_time': '{}'.format(ct), 'Status' : 'Pending','Order_Review' : ''})
    
    return redirect(url_for('v_order'))

@app.route('/view-order', methods=['POST','GET'])
def v_order():
    if request.method == "POST":
        name = request.form['cus_name'].lower()
        mobile_num = request.form['mobile_no']
        order_list = []
        prev_order = []

        query = db.collection('foods').document('all_orders').collection('test_orders').where('Name', '==', name).where('Mobile_Number', '==', mobile_num).where('Status', '==', 'Pending')
        docs = query.stream()

        for doc in docs:
            order_list.append(doc.to_dict())

        query_2 = db.collection('foods').document('all_orders').collection('test_orders').where('Name', '==', name).where('Mobile_Number', '==', mobile_num).where('Status', '==', 'Completed').where('Order_Review', '==' , '')
        docs_2 = query_2.stream()

        for doc_2 in docs_2:
            prev_order.append(doc_2.to_dict())
        
        return render_template('order_summary.html', orders = order_list, prev_ord_list = prev_order)
    
    else:
        return render_template('view.html')
    

@app.route('/admin-enter')
def admin_enter():
    msg = "Enter Password To Enter as Admin"
    return render_template('admin_enter.html', msg = msg)

@app.route('/auth-admin', methods=['POST'])
def auth_admin():
    pwsd = request.form['admin_pw']
    if pwsd == admin_password:
        session['authenticated'] = True
        return redirect('/admin')
    else:
        msg = "Invalid Password"
        return render_template('admin_enter.html', msg = msg)




@app.route('/admin')
def admin():
    if session.get('authenticated'):

        docs = db.collection('foods').document('all_orders').collection('test_orders').get()
        doc_list = []
        for doc in docs:
            ordered_time_str = doc.to_dict().get('Ordered_time')

            if isinstance(ordered_time_str,str):

                ordered_time = datetime.datetime.strptime(ordered_time_str, '%d/%m/%Y, %H:%M:%S')
                
                doc.reference.update({'Ordered_time': ordered_time})
            '''doc_list.append(doc.to_dict())
            print(doc.to_dict())'''

        docs1 = db.collection('foods').document('all_orders').collection('test_orders').order_by('Ordered_time', direction=firestore.Query.DESCENDING).get()
        for document in docs1:
            doc_list.append(document.to_dict())
            print(document.to_dict())



        return render_template('admin.html' , lis = doc_list)
    else:
        abort(401)

@app.before_request
def require_authentication():
    if request.path == '/admin' and not session.get('authenticated'):
        return redirect('/')
    
    if request.path == '/admin/data' and not session.get('authenticated'):
        return redirect('/')

@app.route('/admin/data')
def admin_data():
    docs = db.collection('foods').document('all_orders').collection('test_orders').order_by('Ordered_time', direction=firestore.Query.DESCENDING).get()
    doc_list = []
    for doc in docs:
        doc_list.append(doc.to_dict())


    return jsonify(doc_list)



@app.route('/admin/<int:id>/complete', methods=['POST'])
def complete_order(id):
    query = db.collection('foods').document('all_orders').collection('test_orders').where('id', '==', id)

    docs = query.stream()

    for doc in docs:
        doc.reference.update({'Status': 'Completed'})


    return redirect(url_for('admin'))



@app.route('/admin/<int:id>/cancel', methods=['POST'])
def cancel_order(id):
    query = db.collection('foods').document('all_orders').collection('test_orders').where('id', '==', id)

    docs = query.stream()

    for doc in docs:
        doc.reference.update({'Status': 'Cancelled'})

    return redirect(url_for('admin'))

@app.route('/submit/<int:id>', methods=['POST'])
def submit(id):
    review = request.form.get('review_area')

    query = db.collection('foods').document('all_orders').collection('test_orders').where('id', '==', id)
    docs = query.stream()

    for doc in docs:
        doc.reference.update({'Order_Review' : review})

    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
