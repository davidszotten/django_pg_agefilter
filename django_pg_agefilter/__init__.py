from django.db.models.constants import LOOKUP_SEP
from django.db.models.sql.where import AND
from django.db.models import Q


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

    def __init__(
            self,
            operator,
            value,
            field1_column,
            field1_alias,
            field2_column,
            field2_alias
        ):
        self.operator = operator
        self.value = value
        self.field1_column = field1_column
        self.field1_alias = field1_alias
        self.field2_column = field2_column
        self.field2_alias = field2_alias

    def as_sql(self, qn=None, connection=None):
        sql = self.AGE_QUERY_TEMPLATE.format(
            field1_column=self.field1_column,
            field1_alias=self.field1_alias,
            field2_column=self.field2_column,
            field2_alias=self.field2_alias,
        ) + self.operator
        params = [self.value]

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

    def add_to_query(self, query, alias):
        alias = query.get_initial_alias()

        opts = query.get_meta()

        field1_name = self._field1_name
        field2_name = self._field2_name
        operator = self._operator
        value = self._value

        field1_parts = field1_name.split(LOOKUP_SEP)
        field2_parts = field2_name.split(LOOKUP_SEP)

        field1, _, _, joins1, _, _ = query.setup_joins(
            field1_parts, opts, alias, dupe_multis=False, allow_many=True)

        field2, _, _, joins2, _, _ = query.setup_joins(
            field2_parts, opts, alias, dupe_multis=False, allow_many=True)

        field1_alias = joins1[-1]
        field2_alias = joins2[-1]

        query.where.add(AgeConstraintNode(
            operator,
            value,
            field1.column,
            field1_alias,
            field2.column,
            field2_alias,
        ), AND)
