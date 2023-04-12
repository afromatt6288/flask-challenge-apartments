#!/usr/bin/env python3

from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Lease, Tenant, Apartment

app = Flask( __name__ )
app.secret_key = b'w\xda\xf8\x96$=B\xe7\x0e\xfb\xf3\x14S1\xd5\xc7'
app.config[ 'SQLALCHEMY_DATABASE_URI' ] = 'sqlite:///apartments.db'
app.config[ 'SQLALCHEMY_TRACK_MODIFICATIONS' ] = False
app.json.compact = False

CORS(app)
migrate = Migrate( app, db )
db.init_app( app )
api = Api(app)

class Home(Resource):
    def get(self):
        response_dict = {
            "message": "Welcome to the Leases RESTful API",
        }
        response = make_response(jsonify(response_dict), 200)  ## sometimes remove the jsonify? ##
        return response
    
api.add_resource(Home, '/')

class Apartments(Resource):
    def get(self):      
        response_dict_list = []
        for apartment in Apartment.query.all(): 
            response_dict_list.append(apartment.to_dict(only=('id', 'number',)))
        if response_dict_list != []:
            response = make_response(jsonify(response_dict_list), 200)
            return response
        else:
            return_obj = {"valid": False, "Reason": "Can't query Apartment data"}                 
            return make_response(return_obj,500)  

    def post(self): 
        try:                                            
            new_apartment = Apartment(    
                number=int(request.form.get('number')),
                )
            db.session.add(new_apartment)
            db.session.commit()
        except Exception as e:
            return make_response({"errors": [e.__str__()]}, 422)
        response_dict = new_apartment.to_dict(only=('id', 'number',))
        response = make_response(jsonify(response_dict), 201) 
        return response 
    
api.add_resource(Apartments, '/apartments')

class ApartmentsById(Resource):
    def get(self, id):      
        apartment = Apartment.query.filter(Apartment.id == id).first()
        if apartment:
            response_dict = apartment.to_dict(only=('id', 'number',))
            response = make_response(jsonify(response_dict, 200))
            return response
        return make_response(jsonify({"error": "Apartment Record not found"}), 404)

    def patch(self, id):
        apartment = Apartment.query.filter(Apartment.id == id).first()
        if apartment:
            try:                              
                for attr in request.form:
                    setattr(apartment, attr, request.form.get(attr))      
                db.session.add(apartment)                                 
                db.session.commit()                                   
            except Exception as e:
                return make_response({"errors": [e.__str__()]}, 422)
            response_dict = apartment.to_dict(only=('id', 'number',))
            response = make_response(jsonify(response_dict), 201)
            return response 
        return make_response(jsonify({"error": "Apartment Record not found"}), 404)

    def delete(self, id):
        apartment = Apartment.query.filter(Apartment.id == id).first()
        if apartment:
            db.session.delete(apartment)
            db.session.commit()
            response_dict = {"message": "Apartment Record successfully deleted"}
            return make_response(response_dict, 200)
        return make_response(jsonify({"error": "Apartment Record not found"}), 404)

api.add_resource(ApartmentsById, '/apartments/<int:id>')

class Tenants(Resource):
    def get(self):     
        response_dict_list = []
        for tenant in Tenant.query.all():
            response_dict_list.append(tenant.to_dict(only=('id', 'name', 'age',)))
        if response_dict_list != []:
            response = make_response(jsonify(response_dict_list), 200)
            return response
        else:
            return_obj = {"valid": False, "Reason": "Can't query Tenant data"}                 
            return make_response(return_obj,500)
        
    def post(self): 
        try:                                     
            new_tenant = Tenant(
                name=request.form.get('name'),           
                age=int(request.form.get('age')),   
                )
            db.session.add(new_tenant)
            db.session.commit()
        except Exception as e:
            return make_response({"errors": [e.__str__()]}, 422)
        response = make_response(jsonify(new_tenant.to_dict()), 201) 
        return response 

api.add_resource(Tenants, '/tenants')

class TenantsById(Resource):
    def get(self, id):   
        tenant = Tenant.query.filter(Tenant.id == id).first()
        if tenant:
            response_dict = tenant.to_dict(only=('id', 'name', 'age',))
            response = make_response(jsonify(response_dict, 200))
            return response
        return make_response(jsonify({"error": "Tenant Record not found"}), 404)
    
    def patch(self, id):
        tenant = Tenant.query.filter(Tenant.id == id).first()
        if tenant:
            try:                                      
                for attr in request.form:
                    setattr(tenant, attr, request.form.get(attr))       
                db.session.add(tenant)                                   
                db.session.commit()                                       
            except Exception as e:
                return make_response({"errors": [e.__str__()]}, 422)
            response_dict = tenant.to_dict()
            response = make_response(jsonify(response_dict), 201)
            return response 
        return make_response(jsonify({"error": "Tenant Record not found"}), 404)

    def delete(self, id):
        tenant = Tenant.query.filter(Tenant.id == id).first()
        if tenant:
            db.session.delete(tenant)
            db.session.commit()
            response_dict = {"message": "Tenant Record successfully deleted"}
            return make_response(response_dict, 200)
        return make_response(jsonify({"error": "Tenant Record not found"}), 404)

api.add_resource(TenantsById, '/tenants/<int:id>')

class Leases(Resource):
    def get(self):
        response_dict_list = []
        for lease in Lease.query.all():
            response_dict_list.append(lease.to_dict(only=('id', 'rent', 'apartment_id', 'tenant_id')))
        if response_dict_list != []:
            response = make_response(jsonify(response_dict_list), 200)
            return response
        else:
            return_obj = {"valid": False, "Reason": "Can't query Lease data"}                 
            return make_response(return_obj,500) 
        
    def post(self): 
        try:                                            
            new_record = Lease(
                rent=request.form.get('rent'),  
                tenant_id=int(request.form.get('tenant_id')),          
                apartment_id=int(request.form.get('apartment_id')),   
                )
            db.session.add(new_record)
            db.session.commit()
        except Exception as e:
            return make_response({"errors": [e.__str__()]}, 422)
        response = make_response(jsonify(new_record.to_dict()), 201) 
        return response 

api.add_resource(Leases, '/leases')

class LeaseById(Resource):
    def get(self, id):    
        lease = Lease.query.filter(Lease.id == id).first()
        if lease:
            response_dict = lease.to_dict(only=('id', 'rent', 'apartment_id', 'tenant_id'))
            response = make_response(jsonify(response_dict, 200))
            return response
        return make_response(jsonify({"error": "Lease Record not found"}), 404)

    def patch(self, id):
        lease = Lease.query.filter(Lease.id == id).first()
        if lease:
            try:                          
                for attr in request.form:
                    setattr(lease, attr, request.form.get(attr))   
                db.session.add(lease)                                 
                db.session.commit()                                    
            except Exception as e:
                return make_response({"errors": [e.__str__()]}, 422)
            response_dict = lease.to_dict()
            response = make_response(jsonify(response_dict), 201)
            return response 
        return make_response(jsonify({"error": "Lease Record not found"}), 404)

    def delete(self, id):
        lease = Lease.query.filter(Lease.id == id).first()
        if lease:
            db.session.delete(lease)
            db.session.commit()
            response_dict = {"message": "Lease Record successfully deleted"}
            return make_response(response_dict, 200)
        return make_response(jsonify({"error": "Lease Record not found"}), 404)

api.add_resource(LeaseById, '/leases/<int:id>')

if __name__ == '__main__':
    app.run( port = 3000, debug = True )