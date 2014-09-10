import blitzdb
from flask import current_app

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    print 'in here'
    from flask import _request_ctx_stack as stack


class BlitzDB(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('BLITZDB_DATABASE', './flask-blitzdb.db')
        app.config.setdefault('BLITZDB_TEARDOWN', True)
        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def connect(self):
        print current_app.config['BLITZDB_DATABASE']
        return blitzdb.FileBackend(current_app.config['BLITZDB_DATABASE'])

    def teardown(self, exception):
        if current_app.config['BLITZDB_TEARDOWN']:
            ctx = stack.top
            if hasattr(ctx, 'blitzdb'):
                ctx.blitzdb.commit()

    @property
    def connection(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'blitzdb'):
                ctx.blitzdb = self.connect()
            return ctx.blitzdb