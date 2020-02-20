"""
Tests for dataframe method execution plan
"""
import pytest

from dataframe_sql import query
from dataframe_sql.tests.utils import register_env_tables, remove_env_tables


@pytest.fixture(autouse=True, scope="module")
def module_setup_teardown():
    register_env_tables()
    yield
    remove_env_tables()


def test_select_star():
    """
    Tests the simple select * case
    :return:
    """
    frame, plan = query("select * from forest_fires", show_execution_plan=True)
    print(plan)
    assert plan == "FOREST_FIRES"


def test_case_insensitivity():
    """
    Tests to ensure that the sql is case insensitive for table names
    :return:
    """
    frame, plan = query("select * from FOREST_fires", show_execution_plan=True)
    assert plan == "FOREST_FIRES"


def test_select_specific_fields():
    """
    Tests selecting specific fields
    :return:
    """
    frame, plan = query(
        "select temp, RH, wind, rain as water, area from forest_fires",
        show_execution_plan=True,
    )
    assert (
        plan == "FOREST_FIRES.loc[:, ['temp', 'RH', 'wind', 'rain', "
        "'area']].rename("
        "columns={'rain': 'water'})"
    )


def test_type_conversion():
    """
    Tests sql as statements
    :return:
    """
    my_frame, plan = query(
        """select cast(temp as int64),
        cast(RH as float64) my_rh, wind, rain, area,
    cast(2.0 as int64) my_int,
    cast(3 as float64) as my_float,
    cast(7 as object) as my_object,
    cast(0 as bool) as my_bool from forest_fires""",
        show_execution_plan=True,
    )
    assert (
        plan == "FOREST_FIRES.loc[:, ['temp', 'RH', 'wind', 'rain', "
        "'area']].rename(columns={'RH': 'my_rh'}).assign(my_int=2, my_float=3.0, "
        "my_object=7, my_bool=False, ).astype({'temp': 'int64', 'my_rh': 'float64'})"
    )


def test_using_math():
    """
    Test the mathematical operations and order of operations
    :return:
    """
    my_frame, plan = query(
        "select temp, 1 + 2 * 3 as my_number from forest_fires",
        show_execution_plan=True,
    )
    assert plan == "FOREST_FIRES.loc[:, ['temp']].assign(my_number=7, )"


def test_distinct():
    """
    Test use of the distinct keyword
    :return:
    """
    my_frame, plan = query(
        "select distinct area, rain from forest_fires", show_execution_plan=True
    )
    assert (
        plan == "FOREST_FIRES.loc[:, ['area', 'rain']].drop_duplicates("
        "keep='first', inplace=True)"
    )


def test_subquery():
    """
    Test ability to perform subqueries
    :return:
    """
    my_frame, plan = query(
        """select * from (select area, rain from forest_fires)
    rain_area""",
        show_execution_plan=True,
    )

    assert plan == "FOREST_FIRES.loc[:, ['area', 'rain']]"


def test_join_no_inner():
    """
    Test join
    :return:
    """
    frame, plan = query(
        """select * from digimon_mon_list join
            digimon_move_list
            on digimon_mon_list.attribute = digimon_move_list.attribute""",
        show_execution_plan=True,
    )
    assert (
        plan == "DIGIMON_MON_LIST.merge(DIGIMON_MOVE_LIST, how=inner, "
        "left_on=Attribute, right_on=Attribute)"
    )


def test_join_wo_specifying_table():
    """
    Test join where table isn't specified in join
    :return:
    """
    my_frame, plan = query(
        """
        select * from digimon_mon_list join
        digimon_move_list
        on mon_attribute = move_attribute
        """,
        show_execution_plan=True,
    )

    assert (
        plan == "DIGIMON_MON_LIST.merge(DIGIMON_MOVE_LIST, how=inner, "
        "left_on=mon_attribute, right_on=move_attribute)"
    )


def test_join_w_inner():
    """
    Test join
    :return:
    """
    my_frame, plan = query(
        """select * from digimon_mon_list inner join
            digimon_move_list
            on digimon_mon_list.attribute = digimon_move_list.attribute""",
        show_execution_plan=True,
    )

    assert (
        plan == "DIGIMON_MON_LIST.merge(DIGIMON_MOVE_LIST, how=inner, "
        "left_on=Attribute, right_on=Attribute)"
    )


def test_outer_join_no_outer():
    """
    Test outer join
    :return:
    """
    my_frame, plan = query(
        """select * from digimon_mon_list full outer join
            digimon_move_list
            on digimon_mon_list.type = digimon_move_list.type""",
        show_execution_plan=True,
    )

    assert (
        plan
        == "DIGIMON_MON_LIST.merge(DIGIMON_MOVE_LIST, how=outer, left_on=Type, right_on=Type)"
    )


def test_outer_join_w_outer():
    """
    Test outer join
    :return:
    """
    my_frame, plan = query(
        """select * from digimon_mon_list full join
            digimon_move_list
            on digimon_mon_list.type = digimon_move_list.type""",
        show_execution_plan=True,
    )

    assert (
        plan == "DIGIMON_MON_LIST.merge(DIGIMON_MOVE_LIST, how=outer, "
        "left_on=Type, right_on=Type)"
    )


def test_left_joins():
    """
    Test right, left, inner, and outer joins
    :return:
    """
    my_frame, plan = query(
        """select * from digimon_mon_list left join
            digimon_move_list
            on digimon_mon_list.type = digimon_move_list.type""",
        show_execution_plan=True,
    )

    assert (
        plan == "DIGIMON_MON_LIST.merge(DIGIMON_MOVE_LIST, how=left, "
        "left_on=Type, right_on=Type)"
    )


def test_left_outer_joins():
    """
    Test right, left, inner, and outer joins
    :return:
    """
    my_frame, plan = query(
        """select * from digimon_mon_list left outer join
            digimon_move_list
            on digimon_mon_list.type = digimon_move_list.type""",
        show_execution_plan=True,
    )

    assert (
        plan == "DIGIMON_MON_LIST.merge(DIGIMON_MOVE_LIST, how=left, "
        "left_on=Type, right_on=Type)"
    )


def test_right_joins():
    """
    Test right, left, inner, and outer joins
    :return:
    """
    my_frame, plan = query(
        """select * from digimon_mon_list right join
            digimon_move_list
            on digimon_mon_list.type = digimon_move_list.type""",
        show_execution_plan=True,
    )

    assert (
        plan == "DIGIMON_MON_LIST.merge(DIGIMON_MOVE_LIST, how=right, "
        "left_on=Type, right_on=Type)"
    )


def test_right_outer_joins():
    """
    Test right, left, inner, and outer joins
    :return:
    """
    my_frame, plan = query(
        """select * from digimon_mon_list right outer join
            digimon_move_list
            on digimon_mon_list.type = digimon_move_list.type""",
        show_execution_plan=True,
    )

    assert (
        plan == "DIGIMON_MON_LIST.merge(DIGIMON_MOVE_LIST, how=right, "
        "left_on=Type, right_on=Type)"
    )


def test_cross_joins():
    """
    Test right, left, inner, and outer joins
    :return:
    """
    my_frame, plan = query(
        """select * from digimon_mon_list cross join
            digimon_move_list
            on digimon_mon_list.type = digimon_move_list.type""",
        show_execution_plan=True,
    )

    assert (
        plan == "DIGIMON_MON_LIST.merge(DIGIMON_MOVE_LIST, how=outer, "
        "left_on=Type, right_on=Type)"
    )


def test_group_by():
    """
    Test group by constraint
    :return:
    """
    my_frame, plan = query(
        """select month, day from forest_fires group by month, day""",
        show_execution_plan=True,
    )
    assert plan == "FOREST_FIRES.loc[:, ['month', 'day']].drop_duplicates(keep='first')"


def test_avg():
    """
    Test the avg
    :return:
    """
    my_frame, plan = query(
        "select avg(temp) from forest_fires", show_execution_plan=True
    )
    # THIS SHOULD translate to FOREST_FIRES.loc[:, ['temp']].rename('temp',
    # _col1).aggregate({'_col1', 'mean'}).to_frame().transpose()
    assert (
        plan == "FOREST_FIRES.loc[:, ['temp']].assign(__=1).groupby(['__']).agg("
        "**{'_col0': ('temp', 'mean')}).reset_index(drop=True)"
    )


def test_sum():
    """
    Test the sum
    :return:
    """
    my_frame, plan = query(
        "select sum(temp) from forest_fires", show_execution_plan=True
    )
    assert (
        plan == "FOREST_FIRES.loc[:, ['temp']].assign(__=1).groupby(['__']).agg("
        "**{'_col0': ('temp', 'sum')}).reset_index(drop=True)"
    )


def test_max():
    """
    Test the max
    :return:
    """
    my_frame, plan = query(
        "select max(temp) from forest_fires", show_execution_plan=True
    )
    assert (
        plan == "FOREST_FIRES.loc[:, ['temp']].assign(__=1).groupby(['__']).agg("
        "**{'_col0': ('temp', 'max')}).reset_index(drop=True)"
    )


def test_min():
    """
    Test the min
    :return:
    """
    my_frame, plan = query(
        "select min(temp) from forest_fires", show_execution_plan=True
    )
    assert (
        plan == "FOREST_FIRES.loc[:, ['temp']].assign(__=1).groupby(['__']).agg("
        "**{'_col0': ('temp', 'min')}).reset_index(drop=True)"
    )


def test_multiple_aggs():
    """
    Test multiple aggregations
    :return:
    """
    my_frame, plan = query(
        "select min(temp), max(temp), avg(temp), max(wind) from forest_fires",
        show_execution_plan=True,
    )
    assert (
        plan == "FOREST_FIRES.loc[:, ['temp', 'wind']].assign(__=1)"
        ".groupby(['__']).agg(**{'_col0': ('temp', 'min'), "
        "'_col1': ('temp', 'max'), '_col2': ('temp', 'mean'), "
        "'_col3': ('wind', 'max')}).reset_index(drop=True)"
    )


def test_agg_w_groupby():
    """
    Test using aggregates and group by together
    :return:
    """
    my_frame, plan = query(
        "select day, month, min(temp), max(temp) from forest_fires group by day, month",
        show_execution_plan=True,
    )
    assert (
        plan == "FOREST_FIRES.loc[:, ['day', 'month', 'temp']]"
        ".groupby(['day', 'month'])"
        ".aggregate({'_col0': ('temp', 'min'), '_col1': ('temp', 'max')})"
        ".reset_index()"
    )


def test_where_clause():
    """
    Test where clause
    :return:
    """
    my_frame, plan = query(
        """select * from forest_fires where month = 'mar'""", show_execution_plan=True
    )
    assert plan == "FOREST_FIRES.loc[FOREST_FIRES['month']=='mar', :]"


def test_all_boolean_ops_clause():
    """
    Test where clause
    :return:
    """
    my_frame, plan = query(
        """select * from forest_fires where month = 'mar' and temp > 8 and rain >= 0
        and area != 0 and dc < 100 and ffmc <= 90.1
        """,
        show_execution_plan=True,
    )
    assert (
        plan == "FOREST_FIRES.loc[FOREST_FIRES['month']=='mar' "
        "& FOREST_FIRES['temp']>8 "
        "& FOREST_FIRES['rain']>=0 & ~(FOREST_FIRES['area']==0) "
        "& FOREST_FIRES['dc']<100 & FOREST_FIRES['ffmc']<=90.1, :]"
    )


def test_order_by():
    """
    Test order by clause
    :return:
    """
    my_frame, plan = query(
        """select * from forest_fires order by temp desc, wind asc, area""",
        show_execution_plan=True,
    )
    assert (
        plan == "FOREST_FIRES.sort_values(by=['temp', 'wind', 'area'], "
        "ascending=[False, True, True])"
    )


def test_limit():
    """
    Test limit clause
    :return:
    """
    my_frame, plan = query(
        """select * from forest_fires limit 10""", show_execution_plan=True
    )
    assert plan == "FOREST_FIRES.head(10)"


def test_having_one_condition():
    """
    Test having clause
    :return:
    """
    my_frame, plan = query(
        "select min(temp) from forest_fires having min(temp) > 2",
        show_execution_plan=True,
    )
    assert (
        plan == "FOREST_FIRES.loc[:, ['temp']].assign(__=1).groupby(['__'])"
        ".agg(**{'_col0': ('temp', 'min')}).reset_index(drop=True)"
        ".loc[FOREST_FIRES.aggregate({'temp': 'min'}).to_frame()"
        ".transpose()[temp]>2, :]"
    )


def test_having_with_group_by():
    """
    Test having clause
    :return:
    """
    my_frame, plan = query(
        "select day, min(temp) from forest_fires group by day having min(temp) > 5",
        show_execution_plan=True,
    )
    assert (
        plan == "FOREST_FIRES.loc[:, ['day', 'temp']].groupby(['day'])"
        ".aggregate({'_col0': ('temp', 'min')}).reset_index()"
        ".loc[FOREST_FIRES.groupby(['day']).aggregate({'temp': 'min'})"
        ".reset_index()[temp]>5, :]"
    )


# def test_operations_between_columns_and_numbers():
#     """
#     Tests operations between columns
#     :return:
#     """
#     my_frame = query("""select temp * wind + rain / dmc + 37 from forest_fires""")
#     pandas_frame = FOREST_FIRES.copy()
#     pandas_frame["temp_mul_wind_add_rain_div_dmc_add_37"] = (
#         pandas_frame["temp"] * pandas_frame["wind"]
#         + pandas_frame["rain"] / pandas_frame["DMC"]
#         + 37
#     )
#     pandas_frame = pandas_frame["temp_mul_wind_add_rain_div_dmc_add_37"].to_frame()
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_select_star_from_multiple_tables():
#     """
#     Test selecting from two different tables
#     :return:
#     """
#     my_frame, plan = query("""select * from forest_fires, digimon_mon_list""",
#                            show_execution_plan=True)
#     print(plan)


# def test_select_columns_from_two_tables_with_same_column_name():
#     """
#     Test selecting tables
#     :return:
#     """
#     my_frame = query("""select * from forest_fires table1, forest_fires table2""")
#     table1 = FOREST_FIRES.copy()
#     table2 = FOREST_FIRES.copy()
#     table1["_temp_id"] = 1
#     table2["_temp_id"] = 1
#     pandas_frame = merge(table1, table2, on="_temp_id").drop(columns=["_temp_id"])
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_maintain_case_in_query():
#     """
#     Test nested subqueries
#     :return:
#     """
#     my_frame = query("""select wind, rh from forest_fires""")
#     pandas_frame = FOREST_FIRES.copy()[["wind", "RH"]].rename(columns={"RH": "rh"})
#     tm.assert_frame_equal(pandas_frame, my_frame)
#


def test_nested_subquery():
    """
    Test nested subqueries
    :return:
    """
    my_frame, plan = query(
        """select * from
            (select wind, rh from
              (select * from forest_fires) fires) wind_rh""",
        show_execution_plan=True,
    )

    assert plan == "FOREST_FIRES.loc[:, ['wind', 'RH']].rename(columns={'RH': 'rh'})"


# def test_union():
#     """
#     Test union in queries
#     :return:
#     """
#     my_frame = query(
#         """
#     select * from forest_fires order by wind desc limit 5
#     union
#     select * from forest_fires order by wind asc limit 5
#     """
#     )
#     pandas_frame1 = (
#         FOREST_FIRES.copy().sort_values(by=["wind"], ascending=[False]).head(5)
#     )
#     pandas_frame2 = (
#         FOREST_FIRES.copy().sort_values(by=["wind"], ascending=[True]).head(5)
#     )
#     pandas_frame = (
#         concat([pandas_frame1, pandas_frame2], ignore_index=True)
#         .drop_duplicates()
#         .reset_index(drop=True)
#     )
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_union_distinct():
#     """
#     Test union distinct in queries
#     :return:
#     """
#     my_frame = query(
#         """
#         select * from forest_fires order by wind desc limit 5
#          union distinct
#         select * from forest_fires order by wind asc limit 5
#         """
#     )
#     pandas_frame1 = (
#         FOREST_FIRES.copy().sort_values(by=["wind"], ascending=[False]).head(5)
#     )
#     pandas_frame2 = (
#         FOREST_FIRES.copy().sort_values(by=["wind"], ascending=[True]).head(5)
#     )
#     pandas_frame = (
#         concat([pandas_frame1, pandas_frame2], ignore_index=True)
#         .drop_duplicates()
#         .reset_index(drop=True)
#     )
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_union_all():
#     """
#     Test union distinct in queries
#     :return:
#     """
#     my_frame = query(
#         """
#         select * from forest_fires order by wind desc limit 5
#          union all
#         select * from forest_fires order by wind asc limit 5
#         """
#     )
#     pandas_frame1 = (
#         FOREST_FIRES.copy().sort_values(by=["wind"], ascending=[False]).head(5)
#     )
#     pandas_frame2 = (
#         FOREST_FIRES.copy().sort_values(by=["wind"], ascending=[True]).head(5)
#     )
#     pandas_frame = concat(
#         [pandas_frame1, pandas_frame2], ignore_index=True
#     ).reset_index(drop=True)
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_intersect_distinct():
#     """
#     Test union distinct in queries
#     :return:
#     """
#     my_frame = query(
#         """
#             select * from forest_fires order by wind desc limit 5
#              intersect distinct
#             select * from forest_fires order by wind desc limit 3
#             """
#     )
#     pandas_frame1 = (
#         FOREST_FIRES.copy().sort_values(by=["wind"], ascending=[False]).head(5)
#     )
#     pandas_frame2 = (
#         FOREST_FIRES.copy().sort_values(by=["wind"], ascending=[False]).head(3)
#     )
#     pandas_frame = merge(
#         left=pandas_frame1,
#         right=pandas_frame2,
#         how="inner",
#         on=list(pandas_frame1.columns),
#     )
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_except_distinct():
#     """
#     Test except distinct in queries
#     :return:
#     """
#     my_frame = query(
#         """
#                 select * from forest_fires order by wind desc limit 5
#                  except distinct
#                 select * from forest_fires order by wind desc limit 3
#                 """
#     )
#     pandas_frame1 = (
#         FOREST_FIRES.copy().sort_values(by=["wind"], ascending=[False]).head(5)
#     )
#     pandas_frame2 = (
#         FOREST_FIRES.copy().sort_values(by=["wind"], ascending=[False]).head(3)
#     )
#     pandas_frame = (
#         pandas_frame1[~pandas_frame1.isin(pandas_frame2).all(axis=1)]
#         .drop_duplicates()
#         .reset_index(drop=True)
#     )
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_except_all():
#     """
#     Test except distinct in queries
#     :return:
#     """
#     my_frame = query(
#         """
#                 select * from forest_fires order by wind desc limit 5
#                  except all
#                 select * from forest_fires order by wind desc limit 3
#                 """
#     )
#     pandas_frame1 = (
#         FOREST_FIRES.copy().sort_values(by=["wind"], ascending=[False]).head(5)
#     )
#     pandas_frame2 = (
#         FOREST_FIRES.copy().sort_values(by=["wind"], ascending=[False]).head(3)
#     )
#     pandas_frame = pandas_frame1[
#         ~pandas_frame1.isin(pandas_frame2).all(axis=1)
#     ].reset_index(drop=True)
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_between_operator():
#     """
#     Test using between operator
#     :return:
#     """
#     my_frame = query(
#         """
#     select * from forest_fires
#     where wind between 5 and 6
#     """
#     )
#     pandas_frame = FOREST_FIRES.copy()
#     pandas_frame = pandas_frame[
#         (pandas_frame.wind >= 5) & (pandas_frame.wind <= 6)
#     ].reset_index(drop=True)
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_in_operator():
#     """
#     Test using in operator in a sql query
#     :return:
#     """
#     my_frame = query(
#         """
#     select * from forest_fires where day in ('fri', 'sun')
#     """
#     )
#     pandas_frame = FOREST_FIRES.copy()
#     pandas_frame = pandas_frame[pandas_frame.day.isin(("fri", "sun"))].reset_index(
#         drop=True
#     )
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_in_operator_expression_numerical():
#     """
#     Test using in operator in a sql query
#     :return:
#     """
#     my_frame = query(
#         """
#     select * from forest_fires where X + 1 in (5, 9)
#     """
#     )
#     pandas_frame = FOREST_FIRES.copy()
#     pandas_frame = pandas_frame[(pandas_frame["X"] + 1).isin((5, 9))].reset_index(
#         drop=True
#     )
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_not_in_operator():
#     """
#     Test using in operator in a sql query
#     :return:
#     """
#     my_frame = query(
#         """
#     select * from forest_fires where day not in ('fri', 'sun')
#     """
#     )
#     pandas_frame = FOREST_FIRES.copy()
#     pandas_frame = pandas_frame[~pandas_frame.day.isin(("fri", "sun"))].reset_index(
#         drop=True
#     )
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_case_statement_w_name():
#     """
#     Test using case statements
#     :return:
#     """
#     my_frame = query(
#         """
#         select case when wind > 5 then 'strong'
#         when wind = 5 then 'mid'
#         else 'weak' end as wind_strength
#         from
#         forest_fires
#         """
#     )
#     pandas_frame = FOREST_FIRES.copy()[["wind"]]
#     pandas_frame.loc[pandas_frame.wind > 5, "wind_strength"] = "strong"
#     pandas_frame.loc[pandas_frame.wind == 5, "wind_strength"] = "mid"
#     pandas_frame.loc[
#         ~((pandas_frame.wind == 5) | (pandas_frame.wind > 5)), "wind_strength"
#     ] = "weak"
#     pandas_frame.drop(columns=["wind"], inplace=True)
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_case_statement_w_no_name():
#     """
#     Test using case statements
#     :return:
#     """
#     my_frame = query(
#         """
#         select case when wind > 5 then 'strong' when wind = 5 then 'mid' else 'weak' end
#         from forest_fires
#         """
#     )
#     pandas_frame = FOREST_FIRES.copy()[["wind"]]
#     pandas_frame.loc[pandas_frame.wind > 5, "_expression0"] = "strong"
#     pandas_frame.loc[pandas_frame.wind == 5, "_expression0"] = "mid"
#     pandas_frame.loc[
#         ~((pandas_frame.wind == 5) | (pandas_frame.wind > 5)), "_expression0"
#     ] = "weak"
#     pandas_frame.drop(columns=["wind"], inplace=True)
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_case_statement_w_other_columns_as_reult():
#     """
#     Test using case statements
#     :return:
#     """
#     my_frame = query(
#         """
#         select case when wind > 5 then month when wind = 5 then 'mid' else day end
#         from forest_fires
#         """
#     )
#     pandas_frame = FOREST_FIRES.copy()[["wind"]]
#     pandas_frame.loc[pandas_frame.wind > 5, "_expression0"] = FOREST_FIRES["month"]
#     pandas_frame.loc[pandas_frame.wind == 5, "_expression0"] = "mid"
#     pandas_frame.loc[
#         ~((pandas_frame.wind == 5) | (pandas_frame.wind > 5)), "_expression0"
#     ] = FOREST_FIRES["day"]
#     pandas_frame.drop(columns=["wind"], inplace=True)
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_rank_statement_one_column():
#     """
#     Test rank statement
#     :return:
#     """
#     my_frame = query(
#         """
#     select wind, rank() over(order by wind) as wind_rank
#     from forest_fires
#     """
#     )
#     pandas_frame = FOREST_FIRES.copy()[["wind"]]
#     pandas_frame["wind_rank"] = pandas_frame.wind.rank(method="min").astype("int")
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_rank_statement_many_columns():
#     """
#     Test rank statement
#     :return:
#     """
#     my_frame = query(
#         """
#     select wind, rain, month, rank() over(order by wind desc, rain asc, month) as rank
#     from forest_fires
#     """
#     )
#     pandas_frame = FOREST_FIRES.copy()[["wind", "rain", "month"]]
#     pandas_frame.sort_values(
#         by=["wind", "rain", "month"], ascending=[False, True, True], inplace=True
#     )
#     pandas_frame.reset_index(inplace=True)
#     rank_map = {}
#     rank_counter = 1
#     rank_offset = 0
#     pandas_frame["rank"] = 0
#     rank_series = pandas_frame["rank"].copy()
#     for row_num, row in enumerate(pandas_frame.iterrows()):
#         key = "".join(map(str, list(list(row)[1])[1:4]))
#         if rank_map.get(key):
#             rank_offset += 1
#             rank = rank_map[key]
#         else:
#             rank = rank_counter + rank_offset
#             rank_map[key] = rank
#             rank_counter += 1
#         rank_series[row_num] = rank
#     pandas_frame["rank"] = rank_series
#     pandas_frame.sort_values(by="index", ascending=True, inplace=True)
#     pandas_frame.drop(columns=["index"], inplace=True)
#     pandas_frame.reset_index(drop=True, inplace=True)
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_dense_rank_statement_many_columns():
#     """
#     Test dense_rank statement
#     :return:
#     """
#     my_frame = query(
#         """
#     select wind, rain, month,
#     dense_rank() over(order by wind desc, rain asc, month) as rank
#     from forest_fires
#     """
#     )
#     pandas_frame = FOREST_FIRES.copy()[["wind", "rain", "month"]]
#     pandas_frame.sort_values(
#         by=["wind", "rain", "month"], ascending=[False, True, True], inplace=True
#     )
#     pandas_frame.reset_index(inplace=True)
#     rank_map = {}
#     rank_counter = 1
#     pandas_frame["rank"] = 0
#     rank_series = pandas_frame["rank"].copy()
#     for row_num, row in enumerate(pandas_frame.iterrows()):
#         key = "".join(map(str, list(list(row)[1])[1:4]))
#         if rank_map.get(key):
#             rank = rank_map[key]
#         else:
#             rank = rank_counter
#             rank_map[key] = rank
#             rank_counter += 1
#         rank_series[row_num] = rank
#     pandas_frame["rank"] = rank_series
#     pandas_frame.sort_values(by="index", ascending=True, inplace=True)
#     pandas_frame.drop(columns=["index"], inplace=True)
#     pandas_frame.reset_index(drop=True, inplace=True)
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_rank_over_partition_by():
#     """
#     Test rank partition by statement
#     :return:
#     """
#     my_frame = query(
#         """
#     select wind, rain, month, day,
#     rank() over(partition by day order by wind desc, rain asc, month) as rank
#     from forest_fires
#     """
#     )
#     pandas_frame = FOREST_FIRES.copy()[["wind", "rain", "month", "day"]]
#     partition_slice = 4
#     rank_map = {}
#     partition_rank_counter = {}
#     partition_rank_offset = {}
#     pandas_frame.sort_values(
#         by=["wind", "rain", "month"], ascending=[False, True, True], inplace=True
#     )
#     pandas_frame.reset_index(inplace=True)
#     pandas_frame["rank"] = 0
#     rank_series = pandas_frame["rank"].copy()
#     for row_num, series_tuple in enumerate(pandas_frame.iterrows()):
#         row = series_tuple[1]
#         row_list = list(row)[1:partition_slice]
#         partition_list = list(row)[partition_slice:5]
#         key = str(row_list)
#         partition_key = str(partition_list)
#         if rank_map.get(partition_key):
#             if rank_map[partition_key].get(key):
#                 partition_rank_counter[partition_key] += 1
#                 rank = rank_map[partition_key][key]
#             else:
#                 partition_rank_counter[partition_key] += 1
#                 rank = (
#                     partition_rank_counter[partition_key]
#                     + partition_rank_offset[partition_key]
#                 )
#                 rank_map[partition_key][key] = rank
#         else:
#             rank = 1
#             rank_map[partition_key] = {}
#             partition_rank_counter[partition_key] = 1
#             partition_rank_offset[partition_key] = 0
#             rank_map[partition_key][key] = rank
#         rank_series[row_num] = rank
#     pandas_frame["rank"] = rank_series
#     pandas_frame.sort_values(by="index", ascending=True, inplace=True)
#     pandas_frame.drop(columns=["index"], inplace=True)
#     pandas_frame.reset_index(drop=True, inplace=True)
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_dense_rank_over_partition_by():
#     """
#     Test rank partition by statement
#     :return:
#     """
#     my_frame = query(
#         """
#     select wind, rain, month, day,
#     dense_rank() over(partition by day order by wind desc, rain asc, month) as rank
#     from forest_fires
#     """
#     )
#     pandas_frame = FOREST_FIRES.copy()[["wind", "rain", "month", "day"]]
#     partition_slice = 4
#     rank_map = {}
#     partition_rank_counter = {}
#     pandas_frame.sort_values(
#         by=["wind", "rain", "month"], ascending=[False, True, True], inplace=True
#     )
#     pandas_frame.reset_index(inplace=True)
#     pandas_frame["rank"] = 0
#     rank_series = pandas_frame["rank"].copy()
#     for row_num, series_tuple in enumerate(pandas_frame.iterrows()):
#         row = series_tuple[1]
#         row_list = list(row)[1:partition_slice]
#         partition_list = list(row)[partition_slice:]
#         key = str(row_list)
#         partition_key = str(partition_list)
#         if rank_map.get(partition_key):
#             if rank_map[partition_key].get(key):
#                 rank = rank_map[partition_key][key]
#             else:
#                 partition_rank_counter[partition_key] += 1
#                 rank = partition_rank_counter[partition_key]
#                 rank_map[partition_key][key] = rank
#         else:
#             rank = 1
#             rank_map[partition_key] = {}
#             partition_rank_counter[partition_key] = 1
#             rank_map[partition_key][key] = rank
#         rank_series[row_num] = rank
#     pandas_frame["rank"] = rank_series
#     pandas_frame.sort_values(by="index", ascending=True, inplace=True)
#     pandas_frame.drop(columns=["index"], inplace=True)
#     pandas_frame.reset_index(drop=True, inplace=True)
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_set_string_value_as_column_value():
#     """
#     Select a string like 'Yes' as a column value
#     :return:
#     """
#     my_frame = query(
#         """
#     select wind, 'yes' as wind_yes from forest_fires"""
#     )
#     pandas_frame = FOREST_FIRES.copy()
#     pandas_frame["wind_yes"] = "yes"
#     pandas_frame = pandas_frame[["wind", "wind_yes"]]
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_date_cast():
#     """
#     Select casting a string as a date
#     :return:
#     """
#     my_frame = query(
#         """
#     select wind, cast('2019-01-01' as datetime64) as my_date from forest_fires"""
#     )
#     pandas_frame = FOREST_FIRES.copy()
#     pandas_frame["my_date"] = datetime.strptime("2019-01-01", "%Y-%m-%d")
#     pandas_frame = pandas_frame[["wind", "my_date"]]
#     tm.assert_frame_equal(pandas_frame, my_frame)
#
#
# def test_timestamps():
#     """
#     Select now() as date
#     :return:
#     """
#     with freeze_time(datetime.now()):
#         my_frame = query(
#             """
#         select wind, now(), today(), timestamp('2019-01-31', '23:20:32')
#         from forest_fires"""
#         )
#         pandas_frame = FOREST_FIRES.copy()[["wind"]]
#         pandas_frame["now()"] = datetime.now()
#         pandas_frame["today()"] = date.today()
#         pandas_frame["_literal0"] = datetime(2019, 1, 31, 23, 20, 32)
#         tm.assert_frame_equal(pandas_frame, my_frame)

if __name__ == "__main__":
    register_env_tables()

    test_nested_subquery()

    remove_env_tables()
