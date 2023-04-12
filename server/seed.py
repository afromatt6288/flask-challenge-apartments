#!/usr/bin/env python3
    ## Setting up imports ##
from random import randint, choice as rc    
from faker import Faker                    
from app import app 
from models import db, Lease, Tenant, Apartment

fake = Faker()

with app.app_context():
    print("Deleting Classname(Lease) data...")
    Lease.query.delete()
    print("Deleting Classname(Tenant) data...")     
    Tenant.query.delete() 
    print("Deleting Classname(Apartment) data...")      
    Apartment.query.delete() 

    print("Seeding Classname(Tenant) data...")     
    tenants = []
    for n in range(50):
        tenant = Tenant(name=fake.name(), age=randint(18, 60))
        tenants.append(tenant)

    db.session.add_all(tenants)

    print("Seeding Classname(Apartment) data...")  
    apartments = []
    for n in range(100):
        apartment = Apartment(number=n+1)
        apartments.append(apartment)

    db.session.add_all(apartments)

    print("Seeding Classname(Apartment) data...") 
    leases = []
    for tenant in tenants:
        for i in range(randint(1, 30)):
            lease = Lease(
                rent=randint(400, 1000),
                tenant_id=randint(1, 50),
                apartment_id=randint(1, 50))
            leases.append(lease)

    db.session.add_all(leases)

    print("Just collating Data, as they say...")
    db.session.commit()

    print("Seeding done!")