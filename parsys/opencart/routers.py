class OpencartRouter:
    route_app_labels = {'opencart'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'opencart'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'opencart'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
                obj1._meta.app_label in self.route_app_labels or
                obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'opencart' or app_label in self.route_app_labels:
            return False
        else:
            return True
