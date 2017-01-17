import django
from django.db.models import Q
from django.db.models.constants import LOOKUP_SEP
from django.db.models.sql.where import AND


class AgeConstraintNode(object):
    """ Node to add age filter

    The main point is `relabel_aliases` which is called if we end up embedded
    in a subquery, in which case we need to rewrite our aliases
    """

    AGE_QUERY_TEMPLATE = """
    CAST(
        EXTRACT(
            "year" FROM age(
                {field1_alias}.{field1_column},
                {field2_alias}.{field2_column}
            )
        ) as int8
    )
    """
    contains_aggregate = False

    def __init__(
            self,
            operator,
            value,
            field1_column,
            field1_alias,
            field2_column,
            field2_alias,
            negated,
    ):
        self.operator = operator
        self.value = value
        self.field1_column = field1_column
        self.field1_alias = field1_alias
        self.field2_column = field2_column
        self.field2_alias = field2_alias
        self.negated = negated

    def as_sql(self, qn=None, connection=None):
        sql = self.AGE_QUERY_TEMPLATE.format(
            field1_column=self.field1_column,
            field1_alias=self.field1_alias,
            field2_column=self.field2_column,
            field2_alias=self.field2_alias,
        ) + self.operator
        params = [self.value]

        if self.negated:
            sql = "NOT (%s)" % sql

        return sql, params

    def relabel_aliases(self, change_map, node=None):
        if self.field1_alias in change_map:
            self.field1_alias = change_map[self.field1_alias]
        if self.field2_alias in change_map:
            self.field2_alias = change_map[self.field2_alias]


class AgeFilter(Q):
    """ Q subclass for adding age based queries

    Arguments:
        field1_name (will follow relationships)
        field2_name (will follow relationships)
        operator (should include value placeholder, e.g.  "< %s"
        value

    Usage:
        queryset = queryset.filter(
            AgeFilter(
                'related__model__field',
                'other__field',
                '> %s'
                18,
            )
        )
    """

    def __init__(self, field1_name, field2_name, operator, value):
        self._field1_name = field1_name
        self._field2_name = field2_name
        self._operator = operator
        self._value = value

        super(AgeFilter, self).__init__()

    def add_to_query(self, query, used_aliases=None, negate=False):
        alias = query.get_initial_alias()

        opts = query.get_meta()

        field1_name = self._field1_name
        field2_name = self._field2_name
        operator = self._operator
        value = self._value

        field1_parts = field1_name.split(LOOKUP_SEP)
        field2_parts = field2_name.split(LOOKUP_SEP)

        field1, _, _, joins1, _ = query.setup_joins(field1_parts, opts, alias)
        field2, _, _, joins2, _ = query.setup_joins(field2_parts, opts, alias)

        field1_alias = joins1[-1]
        field2_alias = joins2[-1]

        constraint = AgeConstraintNode(
            operator,
            value,
            field1.column,
            field1_alias,
            field2.column,
            field2_alias,
            negate,
        )

        query.where.add(constraint, AND)


def get_age_mixin(field1, field2):
    class AgeFilterQuerysetMixin(object):
        def _filter_or_exclude(self, negate, *args, **kwargs):
            """ Override the default filter to add age__ operators """
            kwarg, op = get_age_filter(kwargs)
            if kwarg is not None:
                self.query = self.query.clone()
                value = kwargs.pop(kwarg)
                AgeFilter(
                    field1,
                    field2,
                    op,
                    value,
                ).add_to_query(self.query, negate=negate)
            return super(AgeFilterQuerysetMixin, self)._filter_or_exclude(
                negate, *args, **kwargs)

    return AgeFilterQuerysetMixin


def get_age_filter(kwargs):
    operators = {
        'exact': '= %s',
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
    }
    age_operators = dict(('age__%s' % key, val)
        for key, val in operators.items())

    for kwarg, op in age_operators.items():
        if kwarg in kwargs:
            return kwarg, op

    return None, None
