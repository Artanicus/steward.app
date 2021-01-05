from absl import logging
from flask import Blueprint, render_template, flash, redirect, request
from flask_login import login_required, current_user

import grpc
from proto.steward import registry_pb2_grpc
from proto.steward import maintenance_pb2 as m
from proto.steward import asset_pb2 as a
from proto.steward import schedule_pb2 as s

from app.forms import MaintenanceForm, DeleteForm
from app import channels

bp = Blueprint("maintenance", __name__)

logging.set_verbosity(logging.INFO)

maintenance_channel = grpc.insecure_channel(channels.maintenance)
asset_channel = grpc.insecure_channel(channels.asset)
schedule_channel = grpc.insecure_channel(channels.schedule)
maintenances = registry_pb2_grpc.MaintenanceServiceStub(maintenance_channel)
assets = registry_pb2_grpc.AssetServiceStub(asset_channel)
schedules = registry_pb2_grpc.ScheduleServiceStub(schedule_channel)
logging.info('Route({name}) channel(maintenance): {channel}'.format(name=__name__, channel=channels.maintenance))
logging.info('Route({name}) channel(asset): {channel}'.format(name=__name__, channel=channels.asset))
logging.info('Route({name}) channel(schedule): {channel}'.format(name=__name__, channel=channels.schedule))

@bp.route('/maintenances')
@login_required
def maintenance_list():
    return render_template('maintenances.html', maintenances=maintenances.ListMaintenances(m.ListMaintenancesRequest()))

@bp.route('/maintenance/create', methods=['GET', 'POST'])
@bp.route('/maintenance/create/<asset_id>', methods=['GET', 'POST'])
@login_required
def maintenance_create(asset_id=None):
    if asset_id:
        form = MaintenanceForm(asset=asset_id)
    else:
        form = MaintenanceForm()
    form.asset.choices = [(a._id, a.name) for a in get_available_assets(current_user.user.organization_id)]
    form.schedule.choices = [(s._id, s.description) for s in get_available_schedules()]
    if form.validate_on_submit():
        return maintenance_submit(form)
    return render_template('maintenance_edit.html', form=form, view="Create Maintenance")

@bp.route('/maintenance/<maintenance_id>')
@login_required
def maintenance(maintenance_id=None):
    return render_template('maintenance.html', maintenance=maintenances.GetMaintenance(m.GetMaintenanceRequest(_id=maintenance_id)))

@bp.route('/maintenance/edit/<maintenance_id>', methods=['get', 'post'])
@login_required
def maintenance_edit(maintenance_id=None):
    form = MaintenanceForm()
    asset_choices = [(a._id, a.name) for a in get_available_assets(current_user.user.organization_id)]
    schedule_choices = [(s._id, s.description) for s in get_available_schedules()]
    form.asset.choices = asset_choices
    form.schedule.choices = schedule_choices

    if form.validate_on_submit():
        return maintenance_submit(form, maintenance_id)
    else:
        if form.errors:
            logging.info('maintenance edit failed: {}'.format(form.errors))

        # rebuild form to load existing values for editing
        old_maintenance = maintenances.GetMaintenance(m.GetMaintenanceRequest(_id=maintenance_id))
        form = MaintenanceForm(obj=old_maintenance)
        form.asset.choices = asset_choices
        form.schedule.choices = schedule_choices

    return render_template('maintenance_edit.html', form=form, view='edit maintenance')

@bp.route('/maintenance/delete/<maintenance_id>', methods=['get', 'post'])
@login_required
def maintenance_delete(maintenance_id=None):
    form = DeleteForm()
    maintenance = maintenances.GetMaintenance(m.GetMaintenanceRequest(_id=maintenance_id))

    if form.validate_on_submit():
        deleted = maintenances.DeleteMaintenance(m.DeleteMaintenanceRequest(_id=maintenance_id))
        if deleted and deleted.name and not deleted._id:
            flash('Maintenance deleted: {}'.format(deleted.name))
            return redirect('/maintenances')
        else:
            flash('Failed to delete maintenance: {}'.format(deleted))
            logging.error('Failed to delete maintenance: {}'.format(deleted))
            maintenance = 'error'
            return render_template('delete.html', form=form, view='delete', obj_type='Maintenance', obj=None, name='deleted?')
    return render_template('delete.html', form=form, view='delete', obj_type='Maintenance', obj=maintenance, name=maintenance.name)


def maintenance_submit(form, maintenance_id=None):
    maintenance = m.Maintenance()
    maintenance.name = form.name.data
    maintenance.description = form.description.data
    maintenance.enabled = form.enabled.data
    maintenance.asset.MergeFrom(assets.GetAsset(a.GetAssetRequest(_id=form.asset.data)))
    maintenance.schedule.MergeFrom(schedules.GetSchedule(s.GetScheduleRequest(_id=form.schedule.data)))

    if maintenance_id:
        new_maintenance = maintenances.UpdateMaintenance(
                m.UpdateMaintenanceRequest(_id=maintenance_id, maintenance=maintenance)
                )
    else:
        new_maintenance = maintenances.CreateMaintenance(maintenance)
    return redirect('/maintenance/{}'.format(new_maintenance._id))

def get_available_assets(organization_id):
    return assets.ListAssets(a.ListAssetsRequest(organization_id=organization_id))

def get_available_schedules():
    return schedules.ListSchedules(s.ListSchedulesRequest())
