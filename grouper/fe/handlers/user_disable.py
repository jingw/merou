from grouper.constants import USER_ADMIN, USER_DISABLE
from grouper.fe.util import GrouperHandler
from grouper.models.audit_log import AuditLog
from grouper.models.user import User
from grouper.service_account import can_manage_service_account
from grouper.user import disable_user
from grouper.user_permissions import user_has_permission


class UserDisable(GrouperHandler):
    @staticmethod
    def check_access(session, actor, target):
        return (
            user_has_permission(session, actor, USER_ADMIN) or
            user_has_permission(session, actor, USER_DISABLE, argument=target.name) or
            (target.role_user and can_manage_role_account(session, actor, tgroup=target))
        )

    def post(self, user_id=None, name=None):

        user = User.get(self.session, user_id, name)
        if not user:
            return self.notfound()

        if not self.check_access(self.session, self.current_user, user):
            return self.forbidden()

        disable_user(self.session, user)
        self.session.commit()

        AuditLog.log(self.session, self.current_user.id, 'disable_user',
                     'Disabled user.', on_user_id=user.id)

        return self.redirect("/users/{}?refresh=yes".format(user.name))
