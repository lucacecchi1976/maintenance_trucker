from datetime import datetime, timedelta, timezone
from . import db

class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)

    

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    installation_date = db.Column(db.Date)

class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())  # Solo data in UTC
    type = db.Column(db.String(50), nullable=False)  # Tipo: Bimestrale, Semestrale, Annuale
    status = db.Column(db.Boolean, default=False)  # Stato: Completata o meno
    photo = db.Column(db.String(200))  # Percorso della foto caricata
    branch = db.relationship('Branch', backref=db.backref('maintenances', lazy=True))

    def next_due_date(self):
        """Calcola la prossima data di manutenzione basata sul tipo."""
        base_date = self.date  # `self.date` è già un oggetto `date`
        if self.type == "Bimestrale":
            return base_date + timedelta(days=60)
        elif self.type == "Semestrale":
            return base_date + timedelta(days=180)
        elif self.type == "Annuale":
            return base_date + timedelta(days=365)
        return None

class WorkItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Boolean, default=False)  # False = Da fare, True = Eseguito

    branch = db.relationship('Branch', backref=db.backref('work_items', lazy=True))

    
