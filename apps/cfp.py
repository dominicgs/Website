# encoding=utf-8
from flask import (
    render_template, redirect, request, flash,
    url_for, abort, current_app as app, Blueprint
)
from flask.ext.login import current_user
from flask_mail import Message
from wtforms.validators import Required, Email, ValidationError
from wtforms import (
    BooleanField, StringField, IntegerField,
    TextAreaField, SelectField,
)

from sqlalchemy.exc import IntegrityError

from main import db, mail
from models.user import User, UserDiversity
from models.ticket import TicketType
from models.cfp import (
    TalkProposal, WorkshopProposal, InstallationProposal
)
from .common import feature_flag, create_current_user
from .common.forms import Form

cfp = Blueprint('cfp', __name__)


class ProposalForm(Form):
    name = StringField("Name", [Required()])
    email = StringField("Email", [Email(), Required()])
    title = StringField("Title", [Required()])
    description = TextAreaField("Description", [Required()])
    requirements = StringField("Requirements")
    needs_help = BooleanField("Needs help")
    notice_required = SelectField("Required notice", default="1 week",
                          choices=[('1 week', '1 week'),
                                   ('1 month', '1 month'),
                                   ('> 1 month', 'Longer than 1 month'),
                                  ])

    def validate_email(form, field):
        if current_user.is_anonymous() and User.does_user_exist(field.data):
            field.was_duplicate = True
            raise ValidationError('You already have an account - please log in.')


class TalkProposalForm(ProposalForm):
    type = 'talk'
    length = SelectField("Duration", default='25-45 mins',
                         choices=[('< 10 mins', "Shorter than 10 minutes"),
                                  ('10-25 mins', "10-25 minutes"),
                                  ('25-45 mins', "25-45 minutes"),
                                  ('> 45 mins', "Longer than 45 minutes"),
                                  ])


class WorkshopProposalForm(ProposalForm):
    type = 'workshop'
    length = StringField("Duration", [Required()])
    attendees = StringField("Attendees", [Required()])
    cost = IntegerField("Cost per attendee")


class InstallationProposalForm(ProposalForm):
    type = 'installation'
    size = SelectField('Physical size', default="medium",
                                        choices=[('small', 'Smaller than a wheelie bin'),
                                                 ('medium', 'Smaller than a car'),
                                                 ('large', 'Smaller than a lorry'),
                                                 ('huge', 'Bigger than a lorry'),
                                                ])
    funds = SelectField('Funding', choices=[         ('0', 'No money needed'),
                                                     (u'< £50', u'Less than £50'),
                                                     (u'< £100', u'Less than £100'),
                                                     (u'< £300', u'Less than £300'),
                                                     (u'< £500', u'Less than £500'),
                                                     (u'> £500', u'More than £500'),
                                                    ])


@cfp.route('/cfp')
@cfp.route('/cfp/<string:cfp_type>', methods=['GET', 'POST'])
@feature_flag('CFP')
def main(cfp_type='talk'):
    if cfp_type not in ['talk', 'workshop', 'installation']:
        abort(404)

    forms = [TalkProposalForm(), WorkshopProposalForm(), InstallationProposalForm()]
    (form,) = [f for f in forms if f.type == cfp_type]

    # If the user is already logged in set their name & email for the form
    if current_user.is_authenticated():
        form.name.data = current_user.name
        form.email.data = current_user.email

    if request.method == 'POST':
        app.logger.info('Checking %s proposal for %s (%s)', cfp_type,
                        form.name.data, form.email.data)

    if form.validate_on_submit():
        new_user = False
        if current_user.is_anonymous():
            try:
                create_current_user(form.email.data, form.name.data)
                new_user = True
            except IntegrityError as e:
                app.logger.warn('Adding user raised %r, possible double-click', e)
                flash('An error occurred while creating an account for you. Please try again.')
                return redirect(url_for('.main'))

        if cfp_type == 'talk':
            cfp = TalkProposal()
            cfp.length = form.length.data

        elif cfp_type == 'workshop':
            cfp = WorkshopProposal()
            cfp.length = form.length.data
            cfp.attendees = form.attendees.data
            cfp.cost = form.cost.data

        elif cfp_type == 'installation':
            cfp = InstallationProposal()
            cfp.size = form.size.data
            if form.needs_emf_funds.data:
                cfp.emf_funds = form.funds.data

        cfp.user_id = current_user.id

        cfp.title = form.title.data
        cfp.requirements = form.requirements.data
        cfp.description = form.description.data
        cfp.notice_required = form.notice_required.data

        cfp.needs_help = form.needs_help.data

        db.session.add(cfp)
        db.session.commit()

        # Send confirmation message
        msg = Message('Electromagnetic Field CFP Submission',
                      sender=app.config['CONTENT_EMAIL'],
                      recipients=[current_user.email])

        msg.body = render_template('emails/cfp-submission.txt',
                                   cfp=cfp, type=cfp_type, new_user=new_user)
        mail.send(msg)

        return redirect(url_for('.complete'))

    full_price = TicketType.get_price_cheapest_full()

    has_proposals = current_user.proposals.count() > 0 if hasattr(current_user, 'proposals') else False

    return render_template('cfp.html', full_price=full_price,
                           forms=forms, active_cfp_type=cfp_type,
                           has_errors=bool(form.errors),
                           has_proposals=has_proposals)


class DiversityForm(Form):
    age = StringField('Age')
    gender = StringField('Gender')
    ethnicity = StringField('Ethnicity')


@cfp.route('/cfp/complete', methods=['GET', 'POST'])
@feature_flag('CFP')
def complete():
    form = DiversityForm()
    if form.validate_on_submit():
        if not current_user.diversity:
            current_user.diversity = UserDiversity()
            current_user.diversity.user_id = current_user.id
            db.session.add(current_user.diversity)

        current_user.diversity.age = form.age.data
        current_user.diversity.gender = form.gender.data
        current_user.diversity.ethnicity = form.ethnicity.data

        db.session.commit()
        return redirect(url_for('users.account'))

    return render_template('cfp_complete.html', form=form)


@cfp.route('/cfp/proposals')
@feature_flag('CFP')
def proposals():
    if current_user.is_anonymous():
        return redirect(url_for('.main'))

    proposals = current_user.proposals.all()
    if not proposals:
        return redirect(url_for('.main'))

    return render_template('cfp_proposals.html', proposals=proposals)

@cfp.route('/cfp/guidance')
def guidance():
    return render_template('cfp-guidance.html')
