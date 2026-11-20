from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'waste_ops.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
db = SQLAlchemy(app)

class Pickup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resident = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30), default='')
    address = db.Column(db.String(250), nullable=False)
    waste_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), default='')
    preferred_date = db.Column(db.String(20), default='')
    status = db.Column(db.String(30), default='Pending')
    team = db.Column(db.String(100), default='Unassigned')
    worker = db.Column(db.String(100), default='')
    weight_kg = db.Column(db.Float, default=0)
    sorted_as = db.Column(db.String(100), default='')
    destination = db.Column(db.String(150), default='')
    notes = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def json(self):
        return {c.name: (getattr(self, c.name).isoformat() if isinstance(getattr(self, c.name), datetime) else getattr(self, c.name)) for c in self.__table__.columns}

@app.get('/api/health')
def health(): return jsonify({'status':'ok','service':'Waste Collection API'})

@app.get('/api/pickups')
def list_pickups():
    q = Pickup.query
    status = request.args.get('status'); waste = request.args.get('waste_type')
    if status and status != 'All': q = q.filter_by(status=status)
    if waste and waste != 'All': q = q.filter_by(waste_type=waste)
    return jsonify([p.json() for p in q.order_by(Pickup.created_at.desc()).all()])

@app.post('/api/pickups')
def create_pickup():
    d = request.get_json() or {}
    required = ['resident','address','waste_type']
    if any(not str(d.get(k,'')).strip() for k in required): return jsonify({'error':'Resident, address and waste type are required'}), 400
    p = Pickup(resident=d['resident'].strip(), phone=d.get('phone',''), address=d['address'].strip(), waste_type=d['waste_type'], description=d.get('description',''), preferred_date=d.get('preferred_date',''))
    db.session.add(p); db.session.commit()
    return jsonify(p.json()), 201

@app.get('/api/pickups/<int:pid>')
def get_pickup(pid):
    p = db.session.get(Pickup,pid)
    return (jsonify(p.json()),200) if p else (jsonify({'error':'Pickup not found'}),404)

@app.patch('/api/pickups/<int:pid>')
def update_pickup(pid):
    p = db.session.get(Pickup,pid)
    if not p: return jsonify({'error':'Pickup not found'}),404
    d = request.get_json() or {}
    allowed = {'status','team','worker','weight_kg','sorted_as','destination','notes','preferred_date'}
    for k,v in d.items():
        if k in allowed: setattr(p,k,v)
    if p.status == 'Completed' and not p.weight_kg: return jsonify({'error':'Enter collected weight before completing a pickup'}),400
    db.session.commit(); return jsonify(p.json())

@app.delete('/api/pickups/<int:pid>')
def delete_pickup(pid):
    p=db.session.get(Pickup,pid)
    if not p:return jsonify({'error':'Pickup not found'}),404
    db.session.delete(p);db.session.commit();return jsonify({'message':'Pickup deleted'})

@app.get('/api/dashboard')
def dashboard():
    total=Pickup.query.count(); completed=Pickup.query.filter_by(status='Completed').count()
    pending=Pickup.query.filter_by(status='Pending').count(); assigned=Pickup.query.filter_by(status='Assigned').count()
    collected=db.session.query(func.coalesce(func.sum(Pickup.weight_kg),0)).scalar() or 0
    by_type=db.session.query(Pickup.waste_type,func.count(Pickup.id)).group_by(Pickup.waste_type).all()
    by_destination=db.session.query(Pickup.destination,func.coalesce(func.sum(Pickup.weight_kg),0)).filter(Pickup.destination!='').group_by(Pickup.destination).all()
    return jsonify({'total':total,'completed':completed,'pending':pending,'assigned':assigned,'in_progress':Pickup.query.filter_by(status='In Progress').count(),'completion_rate':round(completed*100/total,1) if total else 0,'total_weight':round(float(collected),2),'by_type':[{'name':x,'count':n} for x,n in by_type],'by_destination':[{'name':x,'weight':round(float(w),2)} for x,w in by_destination]})

@app.get('/api/teams')
def teams(): return jsonify(['Green Warriors','Eco Collectors','City Clean Team','Blue Planet Crew'])

with app.app_context():
    db.create_all()
    if Pickup.query.count()==0:
        samples=[
          Pickup(resident='Aarav Kumar',phone='9876543210',address='12, Lake View Road',waste_type='Plastic',description='Bottles and packaging',preferred_date='2026-11-22',status='Pending'),
          Pickup(resident='Meera S',phone='9876501234',address='8, Park Street',waste_type='Paper',description='Old newspapers',preferred_date='2026-11-21',status='Assigned',team='Green Warriors',worker='Ravi'),
          Pickup(resident='Karthik R',address='24, Temple Road',waste_type='Organic',description='Kitchen waste',preferred_date='2026-11-20',status='Completed',team='Eco Collectors',worker='Priya',weight_kg=12.5,sorted_as='Compostable',destination='Community Compost Unit'),
          Pickup(resident='Nila P',address='5, Garden Avenue',waste_type='E-waste',description='Small electronics',preferred_date='2026-11-23',status='In Progress',team='Blue Planet Crew',worker='Arun',weight_kg=3.2)
        ]
        db.session.add_all(samples);db.session.commit()

if __name__=='__main__': app.run(debug=True,port=5000)
