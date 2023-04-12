from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import MetaData

metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
      })
	
db = SQLAlchemy(metadata=metadata)

class Lease(db.Model, SerializerMixin):
    __tablename__ = 'leases'

    serialize_rules = ('-tenant.leases', '-apartment.leases', '-created_at', '-updated_at',)
            ## the "," at the end is necessary to make it a tuple. Otherwise there will be an error ##

    id = db.Column(db.Integer, primary_key=True)
    rent = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())       ## Common additions to most tables to keep track of data! 
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())             ## We don't need to add when we are creating our seeds

    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'))
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartments.id'))

    # @validates('rent')
    # def validate_rent(self, key, rent):
    #     if len(str(rent)) != 4:
    #         raise ValueError("Rent must be 4 digits.")
    #     return rent

    @validates('tenant_id')
    def validate_tenant_id(self, key, tenant_id):
        tenants = Tenant.query.all()
        ids = [tenant.id for tenant in tenants]
        if not tenant_id:
            raise ValueError("Leases must have a tenant_id")
        elif not tenant_id in ids:
            raise ValueError('Tenant must exist.')
        # elif any(lease for lease in Lease.query.filter_by(tenant_id=tenant_id)):
        #     raise ValueError("Tenant cannot accept the same lease twice")
        return tenant_id
    
    @validates('apartment_id')
    def validate_planet_id(self, key, apartment_id):
        apartments = Apartment.query.all()
        ids = [apartment.id for apartment in apartments]
        if not apartment_id:
            raise ValueError("Leases must have a apartment_id")
        elif not apartment_id in ids:
            raise ValueError('apartment must exist.')
        return apartment_id

    def __repr__(self):
        return f'<Lease: Rent: {self.rent}, Tenant: {self.tenant.name}, Apartment: {self.apartment.name}>'

class Tenant(db.Model, SerializerMixin):
    __tablename__ = 'tenants'

    serialize_rules = ('-leases.tenant', '-created_at', '-updated_at',)        ## if needed to prevent recursion ##

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)    
    age = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

## cascade is added to allow the deletion of a tenant to also delete the Lease they are associated with ##
    ## Should only be used if the "Lease Object" relies on the existence of the "Tenant Object" ##
    leases = db.relationship('Lease', backref='tenant', cascade="all, delete, delete-orphan")
## This was in the solution code, but I do not know what it is or means... ##
    apartments = association_proxy('leases', 'apartment')
  
    @validates('name')
    def validate_name(self, key, name):
        tenants = Tenant.query.all()
        names = [tenant.name for tenant in tenants]
        if not name:
            raise ValueError("Tenant must have a name")
        elif name in names:
            raise ValueError("Name must be unique")
        return name
    
    @validates('age')
    def validate_age(self, key, age):
        print(type(age))
        if not age:
            raise ValueError("Tenant must have an age.")
        elif int(age) < 18:
            raise ValueError("Tenant too young.")
        elif int(age) > 60:
            raise ValueError("Tenant too old.")
        return age
    
    def __repr__(self):
        return f'''
            <Tenant: Name: {self.name}, Age: {self.age}, >
            '''
    
class Apartment(db.Model, SerializerMixin):
    __tablename__ = 'apartments'

    serialize_rules = ('-leases.apartment', '-created_at', '-updated_at',)

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

## cascade is added to allow the deletion of a Apartment to also delete the Lease it is associated with ##
    leases = db.relationship('Lease', backref='apartment', cascade="all, delete, delete-orphan")
## This was in the solution code, but I do not know what it is or means... ##
    tenants = association_proxy('leases', 'tenant')

    @validates('number')
    def validate_number(self, key, number):
        if not number:
            raise ValueError("Apartment must have a number")
        if len(str(number)) >= 4:
            raise ValueError("Apartment Number must be less than 5 digits.")
        return number
    def __repr__(self):
        return f'<Apartment: Number: {self.number},>'
