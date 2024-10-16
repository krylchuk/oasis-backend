from flask import Flask, request, jsonify, make_response
from flask_cors import CORS # type: ignore
from flask_mysqldb import MySQL # type: ignore
import base64
import requests # type: ignore
import json
from datetime import datetime
import bcrypt # type: ignore
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)

mysql = MySQL(app)

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT'))


@app.route('/create_budget', methods=['POST'])
def create_budget():
    data = request.json  
    if not data:
        return jsonify({"message": "No data provided"}), 400

    
    customers_name = data.get('customers_name')
    customers_city = data.get('customers_city')
    customers_phone = data.get('customers_phone')
    customers_comment = data.get('customers_comment')
    
    
    services_ids = data.get('services_ids')  
    if not services_ids or not customers_name:
        return jsonify({"message": "Missing customer or service details"}), 400

    cursor = mysql.connection.cursor()

    
    customer_query = """INSERT INTO customers (customers_name, customers_city, customers_phone, customers_comment) 
                        VALUES (%s, %s, %s, %s)"""
    cursor.execute(customer_query, (customers_name, customers_city, customers_phone, customers_comment))
    mysql.connection.commit()
    
    
    customers_id = cursor.lastrowid
    
   
    budgets_number = datetime.now().strftime('%Y%m%d%H%M%S')

    for service_id in services_ids:
        budget_query = """INSERT INTO budgets (budgets_number, budgets_customers_id, budgets_services_id) 
                          VALUES (%s, %s, %s)"""
        cursor.execute(budget_query, (budgets_number, customers_id, service_id))

    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Customer and budget created successfully'}), 201



@app.route('/budgets', methods=['GET'])
def get_budgets():
    cursor = mysql.connection.cursor()
    query = """
    SELECT 
        budgets.budgets_id,
        budgets.budgets_number,
        budgets.budgets_customers_id,
        GROUP_CONCAT(budgets.budgets_services_id) AS budgets_services_ids, 
        budgets.budgets_status,
        customers.customers_name,
        customers.customers_city,
        customers.customers_phone,
        customers.customers_comment
    FROM 
        budgets
    JOIN 
        customers ON budgets.budgets_customers_id = customers.customers_id
    GROUP BY 
        budgets.budgets_id, 
        budgets.budgets_number, 
        budgets.budgets_customers_id,
        budgets.budgets_status,
        customers.customers_name, 
        customers.customers_city, 
        customers.customers_phone,
        customers.customers_comment
    ORDER BY 
        budgets.budgets_number DESC;  -- Сортування за номером бюджету
    """
    cursor.execute(query)
    results = cursor.fetchall()
    
    budgets = []
    for row in results:
        budgets.append({
            'budgets_id': row[0],
            'budgets_number': row[1],
            'budgets_customers_id': row[2],
            'budgets_services_ids': row[3],  
            'budgets_status': row[4],
            'customers_name': row[5],
            'customers_city': row[6],
            'customers_phone': row[7],
            'customers_comment': row[8]
        })

    cursor.close()
    return jsonify(budgets)




@app.route('/budgets/<int:budgets_id>', methods=['PUT'])
def update_budget_status(budgets_id):
    data = request.json
    budgets_status = data.get('budgets_status')

    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE budgets
        SET budgets_status = %s
        WHERE budgets_id = %s
    """, (budgets_status, budgets_id))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Budget status updated successfully'}), 200



@app.route('/blogs', methods=['POST'])
def add_blog():
    data = request.form
    image_file = request.files.get('blogs_image')

    if not all([data.get('blogs_title'), data.get('blogs_content'), data.get('blogs_author')]):
        return jsonify({"message": "Missing blog details"}), 400

    
    image_url = None
    if image_file:
        CLIENT_ID = 'a7483308fd5ddf8'  
        headers = {'Authorization': f'Client-ID {CLIENT_ID}'}
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
        response = requests.post("https://api.imgur.com/3/image", headers=headers, data={'image': image_data})

        if response.status_code == 200:
            image_url = json.loads(response.text)['data']['link']
        else:
            return jsonify({"message": "Image upload failed", "error": response.text}), response.status_code

    
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO blogs (blogs_title, blogs_content, blogs_author, blogs_date, blogs_image_url) VALUES (%s, %s, %s, %s, %s)",
        (data['blogs_title'], data['blogs_content'], data['blogs_author'], datetime.now(), image_url)
    )
    mysql.connection.commit()
    blogs_id = cur.lastrowid
    cur.close()

    return jsonify({'message': 'Blog added', 'blogs_id': blogs_id}), 201


@app.route('/blogs', methods=['GET'])
def get_blogs():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT blogs_id, blogs_title, blogs_content, blogs_author, blogs_date, blogs_image_url FROM blogs")
    blogs = cursor.fetchall()
    cursor.close()

    blogs_list = []
    for blog in blogs:
        blogs_list.append({
            "blogs_id": blog[0],
            "blogs_title": blog[1],
            "blogs_content": blog[2],
            "blogs_author": blog[3],
            "blogs_date": blog[4],
            "blogs_image_url": blog[5]
        })

    return jsonify(blogs_list), 200

@app.route('/blogs/<int:id>', methods=['GET'])
def get_blog_by_id(id):
    try:
        cur = mysql.connection.cursor()
        
        query = "SELECT blogs_id, blogs_title, blogs_content, blogs_author, blogs_date, blogs_image_url FROM blogs WHERE blogs_id = %s"
        cur.execute(query, (id,))
        blog = cur.fetchone()

        if blog:
            
            blog_data = {
                'blogs_id': blog[0],
                'blogs_title': blog[1],
                'blogs_content': blog[2],
                'blogs_author': blog[3],
                'blogs_date': blog[4].strftime('%Y-%m-%d %H:%M:%S'),  
                'blogs_image_url': blog[5]
            }
            return jsonify(blog_data), 200
        else:
            return jsonify({'message': 'Blog not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()






@app.route('/services/<int:services_id>', methods=['GET'])
def get_service(services_id):
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM services WHERE services_id = %s"
    cursor.execute(query, (services_id,))
    service = cursor.fetchone()
    cursor.close()

    if service:
        service_data = {
            "services_id": service[0],
            "services_name": service[1],
            "services_large_description": service[2],
            "services_image_url": service[3]
        }
        return jsonify(service_data), 200
    else:
        return jsonify({"message": "Service not found"}), 404



    


@app.route('/check-admin', methods=['GET'])
def check_admin():
    admin_cookie = request.cookies.get('admin')
    
    if admin_cookie == 'true':
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False}), 403




@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password required'}), 400

    try:
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM admins WHERE admins_email = %s"
        cursor.execute(query, (email,))
        admin = cursor.fetchone()

        if admin:
            stored_password = admin[3]  
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                admin_data = {
                    'admins_id': admin[0],
                    'admins_name': admin[1],
                    'admins_email': admin[2]
                }
                return jsonify({'success': True, 'admin': admin_data}), 200
            else:
                return jsonify({'success': False, 'message': 'Invalid password'}), 401
        else:
            return jsonify({'success': False, 'message': 'Admin not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': 'Database error'}), 500





@app.route('/add_admin', methods=['POST'])
def add_admin():
    try:
        data = request.json  
        admin_name = data.get('name')
        admin_email = data.get('email')
        admin_password = data.get('password')

        hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO admins (admins_name, admins_email, admins_password) VALUES (%s, %s, %s)",
                       (admin_name, admin_email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        return "Admin added successfully!", 200
    except Exception as e:
        return str(e), 500
    



@app.route('/admins/<int:admins_id>', methods=['PUT'])
def update_admin(admins_id):
    data = request.json
    admins_name = data.get('admins_name')
    admins_email = data.get('admins_email')
    admins_password = data.get('admins_password')

    cursor = mysql.connection.cursor()
    query = """
    UPDATE admins 
    SET admins_name = %s, admins_email = %s, admins_password = %s 
    WHERE admins_id = %s
    """
    cursor.execute(query, (admins_name, admins_email, admins_password, admins_id))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Admin profile updated successfully'}), 200





@app.route('/admins/<int:admins_id>', methods=['DELETE'])
def delete_admin(admins_id):
    cursor = mysql.connection.cursor()
    query = "DELETE FROM admins WHERE admins_id = %s"
    cursor.execute(query, (admins_id,))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Admin profile deleted successfully'}), 200



@app.route('/services', methods=['POST'])
def create_service():
    data = request.form
    image_file = request.files.get('services_image')  

    name = data.get('services_name')
    description = data.get('services_large_description')

    if not name or not description:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    image_url = None
    
    
    if image_file:
        CLIENT_ID = 'a7483308fd5ddf8'  
        headers = {'Authorization': f'Client-ID {CLIENT_ID}'}
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
        response = requests.post("https://api.imgur.com/3/image", headers=headers, data={'image': image_data})

        if response.status_code == 200:
            image_url = response.json()['data']['link']  
        else:
            return jsonify({"success": False, "message": "Image upload failed", "error": response.text}), response.status_code
    

    try:
        cursor = mysql.connection.cursor()
        image_url = image_url if image_url else ''  

        cursor.execute(
            "INSERT INTO services (services_name, services_large_description, services_image_url) VALUES (%s, %s, %s)",
            (name, description, image_url)
        )
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True, 'message': 'Service created successfully'}), 201

    except Exception as e:
        return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500

@app.route('/services', methods=['GET'])
def get_services():
    try:
        cursor = mysql.connection.cursor()

       
        cursor.execute("SELECT services_id, services_name, services_large_description, services_image_url FROM services")
        services = cursor.fetchall()
        
        
        services_list = []
        for service in services:
            service_data = {
                'services_id': service[0],
                'services_name': service[1],
                'services_large_description': service[2],
                'services_image_url': service[3]
            }
            services_list.append(service_data)

        cursor.close()
        return jsonify({'success': True, 'services': services_list}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True)
