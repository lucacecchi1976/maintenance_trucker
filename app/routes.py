from app import db
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta, timezone
from .models import Equipment, Branch, Maintenance, WorkItem
# from . import db

main = Blueprint('main', __name__)

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

# Configura la cartella di upload
@main.route('/branch/<int:branch_id>/maintenance', methods=['GET', 'POST'])
def maintenance(branch_id):
    branch = Branch.query.get_or_404(branch_id)
    maintenances = Maintenance.query.filter_by(branch_id=branch_id).all()

    if request.method == 'POST':
        type = request.form.get('type')  # Tipo di manutenzione
        maintenance_date = request.form.get('date')  # Data fornita dall'utente

            # Parsing della data dal form
        try:
            maintenance_date = datetime.strptime(maintenance_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash("Errore: Formato data non valido.", "danger")
            return redirect(request.referrer)

        # Salva la foto, se caricata
        file = request.files.get('photo')
        photo_filename = None
        if file and allowed_file(file.filename):
            photo_filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, photo_filename))

        # Crea una nuova manutenzione
        new_maintenance = Maintenance(
            branch_id=branch.id,
            date=maintenance_date,
            type=type,
            status=False,
            photo=photo_filename
        )
        db.session.add(new_maintenance)
        db.session.commit()

        return redirect(url_for('main.maintenance', branch_id=branch.id))

    return render_template('maintenance.html', branch=branch, maintenances=maintenances)


@main.route('/maintenance/<int:maintenance_id>/complete', methods=['POST'])
def complete_maintenance(maintenance_id):
    maintenance = Maintenance.query.get_or_404(maintenance_id)
    maintenance.status = True
    db.session.commit()
    return redirect(url_for('main.maintenance', branch_id=maintenance.branch_id))

def delete_maintenance(maintenance_id):
    # Recupera la manutenzione dal database
    maintenance = Maintenance.query.get_or_404(maintenance_id)
    branch_id = maintenance.branch_id  # Salva l'ID della filiale associata
    # Elimina la manutenzione
    db.session.delete(maintenance)
    db.session.commit()
    # Reindirizza alla pagina delle manutenzioni
    return redirect(url_for('main.maintenance', branch_id=branch_id))

@main.route('/maintenance/<int:maintenance_id>/delete', methods=['POST'])
def delete_maintenance(maintenance_id):
    # Recupera la manutenzione dal database
    maintenance = Maintenance.query.get_or_404(maintenance_id)
    branch_id = maintenance.branch_id  # Salva l'ID della filiale associata
    # Elimina la manutenzione
    db.session.delete(maintenance)
    db.session.commit()
    # Reindirizza alla pagina delle manutenzioni
    return redirect(url_for('main.maintenance', branch_id=branch_id))

@main.route('/', methods=['GET'])
def index():
    
    query = request.args.get('search')  # Recupera il parametro di ricerca
    if query:
        # Filtra le filiali per nome o posizione
        branches = Branch.query.filter(
            (Branch.name.ilike(f'%{query}%')) | (Branch.location.ilike(f'%{query}%'))
        ).all()
    else:
        branches = Branch.query.all()

    upcoming_maintenances = [
        maintenance for maintenance in Maintenance.query.filter_by(status=False).all()
        if maintenance.next_due_date() and maintenance.next_due_date() >= datetime.now(timezone.utc).date()
]   [:3]  # Limita a 3 manutenzioni


    # Recupera le manutenzioni scadute
    expired_maintenances = [
        maintenance for maintenance in Maintenance.query.filter_by(status=False).all()
        if maintenance.next_due_date() and maintenance.next_due_date() < datetime.now(timezone.utc).date()
    ]

    # Ultime tre manutenzioni completate
    completed_maintenances = (
        Maintenance.query.filter_by(status=True)
        .order_by(Maintenance.date.desc())
        .limit(3)
        .all()
    )

    return render_template(
        'index.html',
        branches=branches,
        upcoming_maintenances=upcoming_maintenances,
        expired_maintenances=expired_maintenances,
        completed_maintenances=completed_maintenances
    )



@main.route('/branch/<int:branch_id>')
def branch_details(branch_id):
    branch = Branch.query.get_or_404(branch_id)  # Recupera la filiale o restituisce 404
    equipment = Equipment.query.filter_by(branch_id=branch.id).all()  # Recupera le apparecchiature della filiale
    # Recupera le manutenzioni associate
    maintenances = Maintenance.query.filter_by(branch_id=branch_id).order_by(Maintenance.date.desc()).all()

    return render_template('branch_details.html', branch=branch, equipment=equipment, maintenances=maintenances)



    if request.method == 'POST':
        if 'equipment_submit' in request.form:
            branch_id = request.form.get('branch_id')
            name = request.form.get('equipment_name')
            model = request.form.get('equipment_model')
            serial_number = request.form.get('equipment_serial_number')
            installation_date = request.form.get('installation_date')

            # Converte la stringa in un oggetto datetime.date
            if installation_date:
                installation_date = datetime.strptime(installation_date, '%Y-%m-%d').date()

            # Crea una nuova apparecchiatura
            new_equipment = Equipment(
                branch_id=int(branch_id),
                name=name,
                model=model,
                serial_number=serial_number,
                installation_date=installation_date
            )
            db.session.add(new_equipment)
            db.session.commit()

            return redirect(url_for('main.populate'))

    branches = Branch.query.all()
    return render_template('populate.html', branches=branches)
@main.route('/populate', methods=['GET', 'POST'])
def populate():
    if request.method == 'POST':
        if 'branch_submit' in request.form:
            # Recupera i dati del form per la filiale
            name = request.form.get('branch_name')
            location = request.form.get('branch_location')

            if name and location:
                # Crea una nuova filiale
                new_branch = Branch(name=name, location=location)
                db.session.add(new_branch)
                db.session.commit()
                return redirect(url_for('main.populate'))

        if 'equipment_submit' in request.form:
            # Logica esistente per aggiungere apparecchiature
            branch_id = request.form.get('branch_id')
            name = request.form.get('equipment_name')
            model = request.form.get('equipment_model')
            serial_number = request.form.get('equipment_serial_number')
            installation_date = request.form.get('installation_date')

            if installation_date:
                installation_date = datetime.strptime(installation_date, '%Y-%m-%d').date()

            new_equipment = Equipment(
                branch_id=int(branch_id),
                name=name,
                model=model,
                serial_number=serial_number,
                installation_date=installation_date
            )
            db.session.add(new_equipment)
            db.session.commit()

            return redirect(url_for('main.populate'))

    # Recupera tutte le filiali per mostrarle nella pagina di popolamento
    branches = Branch.query.all()
    return render_template('populate.html', branches=branches)

@main.route('/delete_branch/<int:branch_id>', methods=['POST'])
def delete_branch(branch_id):
    branch = Branch.query.get_or_404(branch_id)
    
    # Elimina le apparecchiature associate
    Equipment.query.filter_by(branch_id=branch.id).delete()
    
    # Elimina la filiale
    db.session.delete(branch)
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/delete_equipment/<int:equipment_id>', methods=['POST'])
def delete_equipment(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    db.session.delete(equipment)
    db.session.commit()
    return redirect(url_for('main.branch_details', branch_id=equipment.branch_id))

@main.route('/branch/<int:branch_id>/add_work', methods=['POST'])
def add_work(branch_id):
    description = request.form.get('description')

    if not description:
        flash("La descrizione non può essere vuota.", "danger")
        return redirect(request.referrer)

    new_work = WorkItem(
        branch_id=branch_id,
        description=description,
        status=False
    )
    db.session.add(new_work)
    db.session.commit()

    flash("Lavoro aggiunto con successo.", "success")
    return redirect(request.referrer)

@main.route('/work/<int:work_id>/toggle_status', methods=['POST'])
def toggle_work_status(work_id):
    work = WorkItem.query.get_or_404(work_id)
    work.status = not work.status
    db.session.commit()

    flash("Stato del lavoro aggiornato.", "success")
    return redirect(request.referrer)

@main.route('/work/<int:work_id>/delete', methods=['POST'])
def delete_work(work_id):
    work = WorkItem.query.get_or_404(work_id)
    db.session.delete(work)
    db.session.commit()

    flash("Lavoro eliminato con successo.", "success")
    return redirect(request.referrer)

